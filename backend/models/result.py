"""Result type returned after compiling or running student C++."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel

from config import COMPILE_EXIT, COMPILE_TIMEOUT_EXIT, GNU_TIMEOUT_EXIT
from models.tests import TestResult

RunStatus = Literal["passed", "failed", "compilation_error", "timeout", "execution_error"]


class Stage(StrEnum):
    COMPILE = "compile"
    RUN = "run"
    ERROR = "error"


@dataclass
class RunResult:
    ok: bool
    stage: Stage
    stdout: str
    stderr: str
    exit_code: int | None
    timed_out: bool
    message: str
    tests: tuple[TestResult, ...] = ()

    @classmethod
    def error(cls, message: str, stdout: str = "", stderr: str = "") -> RunResult:
        return cls(
            ok=False,
            stage=Stage.ERROR,
            stdout=stdout,
            stderr=stderr,
            exit_code=None,
            timed_out=False,
            message=message,
        )

    @classmethod
    def from_exit(cls, exit_code: int | None, stdout: str, stderr: str) -> RunResult:
        if exit_code is None:
            return cls.error("The sandbox exited without a status code.", stdout, stderr)

        if exit_code == COMPILE_TIMEOUT_EXIT:
            return cls(
                ok=False,
                stage=Stage.COMPILE,
                stdout=stdout,
                stderr=stderr,
                exit_code=exit_code,
                timed_out=True,
                message="Compilation timed out.",
            )

        if exit_code == COMPILE_EXIT:
            return cls(
                ok=False,
                stage=Stage.COMPILE,
                stdout=stdout,
                stderr=stderr,
                exit_code=exit_code,
                timed_out=False,
                message="Compilation failed.",
            )

        if exit_code == GNU_TIMEOUT_EXIT:
            return cls(
                ok=False,
                stage=Stage.RUN,
                stdout=stdout,
                stderr=stderr,
                exit_code=exit_code,
                timed_out=True,
                message="Program timed out.",
            )

        if exit_code == 125:
            return cls.error("Docker failed to start the sandbox container.", stdout, stderr)

        if exit_code in (126, 127):
            return cls.error("The sandbox could not start the runner.", stdout, stderr)

        if exit_code == 137:
            return cls(
                ok=False,
                stage=Stage.RUN,
                stdout=stdout,
                stderr=stderr,
                exit_code=exit_code,
                timed_out=False,
                message="Program was killed.",
            )

        return cls(
            ok=True,
            stage=Stage.RUN,
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
            timed_out=False,
            message="",
        )


class ScoredTest(BaseModel):
    passed: bool
    expected: str
    actual: str


class SubmissionResult(BaseModel):
    """The run response. Internal exit codes and stages stay off this object."""

    status: RunStatus
    tests: list[ScoredTest]
    message: str
    compiler_output: str | None = None


def submission_result(result: RunResult) -> SubmissionResult:
    tests = [ScoredTest(passed=test.passed, expected=test.expected, actual=test.actual) for test in result.tests]
    if result.timed_out:
        status: RunStatus = "timeout"
    elif result.stage == Stage.COMPILE:
        status = "compilation_error"
    elif tests and all(test.passed for test in tests):
        status = "passed"
    elif tests:
        status = "failed"
    else:
        status = "execution_error"
    return SubmissionResult(
        status=status,
        tests=tests,
        message=result.message,
        compiler_output=result.stderr if status == "compilation_error" else None,
    )
