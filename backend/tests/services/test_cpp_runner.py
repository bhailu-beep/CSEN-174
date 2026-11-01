from contextlib import nullcontext
from pathlib import Path
from unittest.mock import create_autospec, patch

from config import DEFAULT_RUN_TIMEOUT_SECONDS, MAX_SOURCE_BYTES
from models.result import RunResult, Stage
from models.tests import TestCase, TestResult, parse_tests
from services.cpp_runner import CppRunnerService
from services.docker import DockerService
from services.workspace import STUDENT_FILENAME, TESTS_FILENAME, WorkspaceService


def _success() -> RunResult:
    """A finished student program: compiled, ran, printed Hello, World!"""
    return RunResult(
        ok=True,
        stage=Stage.RUN,
        stdout="Hello, World!\n",
        stderr="",
        exit_code=0,
        timed_out=False,
        message="",
    )


def _docker_mock() -> DockerService:
    """Autospec DockerService that is available, has an image, and returns _success()."""
    docker = create_autospec(DockerService, instance=True)
    docker.check_available.return_value = None
    docker.ensure_image.return_value = None
    docker.run_container.return_value = _success()
    return docker


def _run(service: CppRunnerService, source: str = "int main(){}", **kwargs: object) -> RunResult:
    kwargs.setdefault("tester", "int main() { return 0; }\n")
    kwargs.setdefault("tests", [])
    return service.run(source, **kwargs)  # type: ignore[arg-type]


def test_rejects_non_positive_timeout() -> None:
    docker = _docker_mock()
    result = _run(CppRunnerService(docker=docker), timeout_seconds=0)
    assert result.ok is False
    assert result.stage is Stage.ERROR
    assert "positive" in result.message
    docker.check_available.assert_not_called()
    docker.run_container.assert_not_called()


def test_rejects_oversized_source() -> None:
    docker = _docker_mock()
    result = _run(CppRunnerService(docker=docker), "x" * (MAX_SOURCE_BYTES + 1))
    assert result.ok is False
    assert result.stage is Stage.ERROR
    assert "byte limit" in result.message
    docker.check_available.assert_not_called()


def test_returns_docker_unavailable_without_running() -> None:
    docker = _docker_mock()
    docker.check_available.return_value = RunResult.error("Docker is not available.")
    result = _run(CppRunnerService(docker=docker), "int main(){}")
    assert result.message == "Docker is not available."
    docker.ensure_image.assert_not_called()
    docker.run_container.assert_not_called()


def test_returns_image_error_without_running() -> None:
    docker = _docker_mock()
    docker.ensure_image.return_value = RunResult.error("Failed to build the C++ sandbox image.")
    result = _run(CppRunnerService(docker=docker), "int main(){}")
    assert "Failed to build" in result.message
    docker.run_container.assert_not_called()


def test_writes_files_and_delegates_to_docker() -> None:
    docker = _docker_mock()
    result = CppRunnerService(docker=docker, workspace=WorkspaceService()).run(
        "#include <iostream>\n",
        tester="int main() { return 0; }\n",
        tests=[],
        timeout_seconds=1.5,
    )

    assert result.ok is True
    assert result.stdout == "Hello, World!\n"
    docker.run_container.assert_called_once()
    workdir, timeout_seconds = docker.run_container.call_args.args
    assert timeout_seconds == 1.5
    assert not workdir.exists()


def test_workspace_receives_source(tmp_path: Path) -> None:
    docker = _docker_mock()
    workspace = WorkspaceService()

    with patch.object(workspace, "open", return_value=nullcontext(tmp_path)):
        CppRunnerService(docker=docker, workspace=workspace).run(
            "int main() { return 0; }\n",
            tester="int main() { return 0; }\n",
            tests=[],
        )

    assert (tmp_path / STUDENT_FILENAME).read_text(encoding="utf-8") == "int main() { return 0; }\n"
    docker.run_container.assert_called_once_with(tmp_path, DEFAULT_RUN_TIMEOUT_SECONDS)


def test_scores_a_clean_run_and_keeps_expected_answers_out_of_the_sandbox(tmp_path: Path) -> None:
    docker = _docker_mock()
    docker.run_container.return_value = RunResult(
        ok=True,
        stage=Stage.RUN,
        stdout=(
            "debug from the student\n"
            '{"actual":"3"}\n'
            '{"actual":"0"}\n'
        ),
        stderr="",
        exit_code=0,
        timed_out=False,
        message="",
    )
    workspace = WorkspaceService()
    tests = parse_tests("input: 1\ninput: 2\nexpected: 3\n\ninput: -1\ninput: 5\nexpected: 4\n")

    with patch.object(workspace, "open", return_value=nullcontext(tmp_path)):
        result = CppRunnerService(docker=docker, workspace=workspace).run(
            "int sum(int a, int b) { return a + b; }\n",
            tester="int main() { return 0; }\n",
            tests=tests,
        )

    sandbox_tests = (tmp_path / TESTS_FILENAME).read_text(encoding="utf-8")
    assert "expected" not in sandbox_tests
    assert "input: 1" in sandbox_tests
    assert result.tests == (
        TestResult(passed=True, expected="3", actual="3"),
        TestResult(passed=False, expected="4", actual="0"),
    )


def test_compile_failure_does_not_score_stdout(tmp_path: Path) -> None:
    docker = _docker_mock()
    docker.run_container.return_value = RunResult.from_exit(
        254,
        '{"actual":"3"}\n',
        "syntax error",
    )
    workspace = WorkspaceService()

    with patch.object(workspace, "open", return_value=nullcontext(tmp_path)):
        result = CppRunnerService(docker=docker, workspace=workspace).run(
            "int sum(",
            tester="int main() { return 0; }\n",
            tests=[TestCase(inputs=("1", "2"), expected="3")],
        )

    assert result.stage is Stage.COMPILE
    assert result.tests == ()
