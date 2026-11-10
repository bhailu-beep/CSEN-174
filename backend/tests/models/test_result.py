from config import COMPILE_EXIT, COMPILE_TIMEOUT_EXIT, GNU_TIMEOUT_EXIT
from models.result import RunResult, Stage, submission_result
from models.tests import TestResult


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


def _result(
    *tests: TestResult,
    stage: Stage = Stage.RUN,
    timed_out: bool = False,
    stderr: str = "",
    message: str = "",
) -> RunResult:
    return RunResult(
        ok=stage is Stage.RUN and not timed_out,
        stage=stage,
        stdout="",
        stderr=stderr,
        exit_code=0,
        timed_out=timed_out,
        message=message,
        tests=tests,
    )


def test_submission_is_passed_when_every_test_passes() -> None:
    submission = submission_result(
        _result(TestResult(True, "3", "3"), TestResult(True, "0", "0"))
    )

    assert submission.status == "passed"
    assert [test.passed for test in submission.tests] == [True, True]
    assert submission.compiler_output is None


def test_submission_is_failed_when_any_test_fails() -> None:
    submission = submission_result(
        _result(TestResult(True, "3", "3"), TestResult(False, "4", "0"))
    )

    assert submission.status == "failed"
    assert submission.tests[1].expected == "4"
    assert submission.tests[1].actual == "0"


def test_submission_is_failed_when_the_only_test_fails() -> None:
    assert submission_result(_result(TestResult(False, "4", "0"))).status == "failed"


def test_submission_is_compilation_error_and_carries_compiler_output() -> None:
    submission = submission_result(
        _result(stage=Stage.COMPILE, stderr="expected ';'", message="Compilation failed.")
    )

    assert submission.status == "compilation_error"
    assert submission.compiler_output == "expected ';'"
    assert submission.message == "Compilation failed."
    assert submission.tests == []


def test_submission_is_timeout_when_the_program_times_out() -> None:
    submission = submission_result(
        _result(timed_out=True, message="Program timed out.", stderr="secret")
    )

    assert submission.status == "timeout"
    assert submission.compiler_output is None


def test_compile_timeout_is_reported_as_timeout_not_compilation_error() -> None:
    submission = submission_result(_result(stage=Stage.COMPILE, timed_out=True, stderr="slow"))

    assert submission.status == "timeout"
    assert submission.compiler_output is None


def test_submission_is_execution_error_when_no_tests_were_scored() -> None:
    crashed = RunResult.from_exit(139, "", "Segmentation fault")
    killed = RunResult.from_exit(137, "", "")
    docker_down = RunResult.error("Docker is not available.")

    for result in (crashed, killed, docker_down):
        submission = submission_result(result)
        assert submission.status == "execution_error"
        assert submission.tests == []
        assert submission.compiler_output is None


def test_submission_without_tests_is_never_passed() -> None:
    assert submission_result(_result()).status == "execution_error"


def test_submission_result_dump_has_no_internal_fields() -> None:
    dumped = submission_result(_result(TestResult(True, "3", "3"))).model_dump()

    assert set(dumped) == {"status", "tests", "message", "compiler_output"}
    assert set(dumped["tests"][0]) == {"passed", "expected", "actual"}
