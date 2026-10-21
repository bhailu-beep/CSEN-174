from contextlib import nullcontext
from pathlib import Path
from unittest.mock import create_autospec, patch

from runner.config import DEFAULT_RUN_TIMEOUT_SECONDS, MAX_SOURCE_BYTES
from runner.domain.result import RunResult, Stage
from runner.services.cpp_runner_service import CppRunnerService
from runner.services.docker_service import DockerService
from runner.services.workspace_service import SOURCE_FILENAME, WorkspaceService


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


def test_rejects_non_positive_timeout() -> None:
    docker = _docker_mock()
    result = CppRunnerService(docker=docker).run("int main(){}", timeout_seconds=0)
    assert result.ok is False
    assert result.stage is Stage.ERROR
    assert "positive" in result.message
    docker.check_available.assert_not_called()
    docker.run_container.assert_not_called()


def test_rejects_oversized_source() -> None:
    docker = _docker_mock()
    result = CppRunnerService(docker=docker).run("x" * (MAX_SOURCE_BYTES + 1))
    assert result.ok is False
    assert result.stage is Stage.ERROR
    assert "byte limit" in result.message
    docker.check_available.assert_not_called()


def test_returns_docker_unavailable_without_running() -> None:
    docker = _docker_mock()
    docker.check_available.return_value = RunResult.error("Docker is not available.")
    result = CppRunnerService(docker=docker).run("int main(){}")
    assert result.message == "Docker is not available."
    docker.ensure_image.assert_not_called()
    docker.run_container.assert_not_called()


def test_returns_image_error_without_running() -> None:
    docker = _docker_mock()
    docker.ensure_image.return_value = RunResult.error("Failed to build the C++ sandbox image.")
    result = CppRunnerService(docker=docker).run("int main(){}")
    assert "Failed to build" in result.message
    docker.run_container.assert_not_called()


def test_writes_files_and_delegates_to_docker() -> None:
    docker = _docker_mock()
    result = CppRunnerService(docker=docker, workspace=WorkspaceService()).run(
        "#include <iostream>\n",
        stdin="World\n",
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
        CppRunnerService(docker=docker, workspace=workspace).run("int main() { return 0; }\n")

    assert (tmp_path / SOURCE_FILENAME).read_text(encoding="utf-8") == "int main() { return 0; }\n"
    docker.run_container.assert_called_once_with(tmp_path, DEFAULT_RUN_TIMEOUT_SECONDS)
