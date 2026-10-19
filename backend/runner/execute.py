"""Orchestrate a sandboxed C++ compile-and-run."""

from __future__ import annotations

import tempfile
from pathlib import Path

from .config import DEFAULT_RUN_TIMEOUT_SECONDS, MAX_SOURCE_BYTES
from .docker import docker_run, ensure_image, require_docker
from .result import RunResult, Stage
from .text import normalize_newlines


def run_cpp(
    source: str,
    stdin: str = "",
    *,
    timeout_seconds: float = DEFAULT_RUN_TIMEOUT_SECONDS,
) -> RunResult:
    """Compile and run C++ source with the given stdin inside Docker."""
    if timeout_seconds <= 0:
        return RunResult(
            ok=False,
            stage=Stage.ERROR,
            stdout="",
            stderr="",
            exit_code=None,
            timed_out=False,
            message="timeout_seconds must be positive.",
        )

    source_bytes = source.encode("utf-8")
    if len(source_bytes) > MAX_SOURCE_BYTES:
        return RunResult(
            ok=False,
            stage=Stage.ERROR,
            stdout="",
            stderr="",
            exit_code=None,
            timed_out=False,
            message=f"Source exceeds the {MAX_SOURCE_BYTES} byte limit.",
        )

    docker_error = require_docker()
    if docker_error:
        return docker_error

    image_error = ensure_image()
    if image_error:
        return image_error

    with tempfile.TemporaryDirectory(prefix="completec-") as tmp:
        workdir = Path(tmp)
        source_file = workdir / "main.cpp"
        input_file = workdir / "input.txt"
        source_file.write_text(normalize_newlines(source), encoding="utf-8")
        input_file.write_text(normalize_newlines(stdin), encoding="utf-8")
        return docker_run(workdir, timeout_seconds)
