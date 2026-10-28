from runner.config import COMPILE_EXIT, COMPILE_TIMEOUT_EXIT, GNU_TIMEOUT_EXIT
from runner.domain.result import RunResult, Stage


def test_error_sets_error_stage() -> None:
    result = RunResult.error("no docker", stdout="out", stderr="err")
    assert result.ok is False
    assert result.stage is Stage.ERROR
    assert result.exit_code is None
    assert result.timed_out is False
    assert result.message == "no docker"
    assert result.stdout == "out"
    assert result.stderr == "err"


def test_from_exit_none_is_error() -> None:
    result = RunResult.from_exit(None, "out", "err")
    assert result.stage is Stage.ERROR
    assert result.ok is False


def test_from_exit_compile_timeout() -> None:
    result = RunResult.from_exit(COMPILE_TIMEOUT_EXIT, "", "slow")
    assert result.stage is Stage.COMPILE
    assert result.timed_out is True
    assert result.ok is False


def test_from_exit_compile_failure() -> None:
    result = RunResult.from_exit(COMPILE_EXIT, "", "syntax error")
    assert result.stage is Stage.COMPILE
    assert result.timed_out is False
    assert result.message == "Compilation failed."


def test_from_exit_run_timeout() -> None:
    result = RunResult.from_exit(GNU_TIMEOUT_EXIT, "partial", "")
    assert result.stage is Stage.RUN
    assert result.timed_out is True


def test_from_exit_docker_failed_to_start() -> None:
    result = RunResult.from_exit(125, "", "daemon error")
    assert result.stage is Stage.ERROR
    assert "Docker failed" in result.message


def test_from_exit_runner_missing() -> None:
    for code in (126, 127):
        result = RunResult.from_exit(code, "", "")
        assert result.stage is Stage.ERROR


def test_from_exit_oom_kill() -> None:
    result = RunResult.from_exit(137, "", "")
    assert result.stage is Stage.RUN
    assert result.ok is False
    assert "killed" in result.message.lower()


def test_from_exit_success_including_nonzero_student_code() -> None:
    result = RunResult.from_exit(1, "done\n", "")
    assert result.ok is True
    assert result.stage is Stage.RUN
    assert result.exit_code == 1
    assert result.message == ""
