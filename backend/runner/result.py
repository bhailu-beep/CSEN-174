"""Result type returned after compiling or running student C++."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .config import COMPILE_EXIT, COMPILE_TIMEOUT_EXIT, GNU_TIMEOUT_EXIT


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


def error_result(message: str, stdout: str = "", stderr: str = "") -> RunResult:
    return RunResult(
        ok=False,
        stage=Stage.ERROR,
        stdout=stdout,
        stderr=stderr,
        exit_code=None,
        timed_out=False,
        message=message,
    )


def result_from_exit(exit_code: int | None, stdout: str, stderr: str) -> RunResult:
    if exit_code is None:
        return error_result("The sandbox exited without a status code.", stdout, stderr)

    if exit_code == COMPILE_TIMEOUT_EXIT:
        return RunResult(
            ok=False,
            stage=Stage.COMPILE,
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
            timed_out=True,
            message="Compilation timed out.",
        )

    if exit_code == COMPILE_EXIT:
        return RunResult(
            ok=False,
            stage=Stage.COMPILE,
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
            timed_out=False,
            message="Compilation failed.",
        )

    if exit_code == GNU_TIMEOUT_EXIT:
        return RunResult(
            ok=False,
            stage=Stage.RUN,
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
            timed_out=True,
            message="Program timed out.",
        )

    if exit_code == 125:
        return error_result("Docker failed to start the sandbox container.", stdout, stderr)

    if exit_code in (126, 127):
        return error_result("The sandbox could not start the runner.", stdout, stderr)

    if exit_code == 137:
        return RunResult(
            ok=False,
            stage=Stage.RUN,
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
            timed_out=False,
            message="Program was killed.",
        )

    return RunResult(
        ok=True,
        stage=Stage.RUN,
        stdout=stdout,
        stderr=stderr,
        exit_code=exit_code,
        timed_out=False,
        message="",
    )
