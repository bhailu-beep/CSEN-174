"""Talk to Docker: ensure the image exists, run a sandbox container, clean up."""

from __future__ import annotations

import subprocess
import uuid
from pathlib import Path

from .config import (
    COMPILE_TIMEOUT_SECONDS,
    CPUS,
    DOCKER_GRACE_SECONDS,
    IMAGE_NAME,
    MEMORY_MB,
    OUTPUT_CAP_BYTES,
    PIDS_LIMIT,
    SANDBOX_DIR,
    SANDBOX_USER,
    TMPFS_SIZE,
)
from .output import communicate_capped
from .result import RunResult, Stage, error_result, result_from_exit
from .text import decode


def docker_path(path: Path) -> str:
    return str(path.resolve()).replace("\\", "/")


def require_docker() -> RunResult | None:
    try:
        completed = subprocess.run(
            ["docker", "version"],
            capture_output=True,
            timeout=15,
        )
    except FileNotFoundError:
        return error_result("Docker is not installed or not on PATH. Install Docker Desktop and try again.")
    except subprocess.TimeoutExpired:
        return error_result("Timed out while checking Docker. Is Docker Desktop running?")

    if completed.returncode != 0:
        stderr = decode(completed.stderr).strip()
        return error_result(
            "Docker is not available. Start Docker Desktop and try again."
            + (f" {stderr}" if stderr else "")
        )
    return None


def ensure_image() -> RunResult | None:
    try:
        inspect = subprocess.run(
            ["docker", "image", "inspect", IMAGE_NAME],
            capture_output=True,
            timeout=15,
        )
    except subprocess.TimeoutExpired:
        return error_result("Timed out while checking for the C++ sandbox image.")

    if inspect.returncode == 0:
        return None

    try:
        build = subprocess.run(
            ["docker", "build", "-t", IMAGE_NAME, str(SANDBOX_DIR)],
            capture_output=True,
            timeout=600,
        )
    except subprocess.TimeoutExpired:
        return error_result("Timed out while building the C++ sandbox image.")

    if build.returncode != 0:
        return error_result(
            "Failed to build the C++ sandbox image.",
            stdout=decode(build.stdout),
            stderr=decode(build.stderr),
        )
    return None


def docker_run(workdir: Path, timeout_seconds: float) -> RunResult:
    container_name = f"completec-{uuid.uuid4().hex[:12]}"
    wall_timeout = COMPILE_TIMEOUT_SECONDS + timeout_seconds + DOCKER_GRACE_SECONDS
    command = [
        "docker",
        "run",
        "--name",
        container_name,
        "--rm",
        "--network=none",
        f"--memory={MEMORY_MB}m",
        f"--memory-swap={MEMORY_MB}m",
        f"--cpus={CPUS}",
        f"--pids-limit={PIDS_LIMIT}",
        "--read-only",
        f"--tmpfs=/tmp:rw,size={TMPFS_SIZE},exec,nosuid,nodev,mode=1777",
        f"--user={SANDBOX_USER}",
        "--cap-drop=ALL",
        "--security-opt=no-new-privileges:true",
        "--ulimit",
        "nofile=1024:1024",
        "-e",
        "HOME=/tmp",
        "-e",
        "TMPDIR=/tmp",
        "-e",
        f"COMPILE_TIMEOUT={int(COMPILE_TIMEOUT_SECONDS)}",
        "-e",
        f"RUN_TIMEOUT={timeout_seconds}",
        "-v",
        f"{docker_path(workdir)}:/src:ro",
        IMAGE_NAME,
    ]

    try:
        proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError:
        return error_result("Docker is not installed or not on PATH. Install Docker Desktop and try again.")
    except OSError as exc:
        return error_result(f"Failed to start Docker: {exc}")

    try:
        stdout, stderr, timed_out, truncated = communicate_capped(
            proc,
            max_bytes=OUTPUT_CAP_BYTES,
            timeout_seconds=wall_timeout,
        )
    finally:
        force_remove_container(container_name)

    stdout_text = decode(stdout)
    stderr_text = decode(stderr)

    if timed_out:
        return RunResult(
            ok=False,
            stage=Stage.RUN,
            stdout=stdout_text,
            stderr=stderr_text,
            exit_code=None,
            timed_out=True,
            message="Execution timed out.",
        )

    if truncated:
        return RunResult(
            ok=False,
            stage=Stage.RUN,
            stdout=stdout_text,
            stderr=stderr_text,
            exit_code=proc.returncode,
            timed_out=False,
            message=f"Program output exceeded the {OUTPUT_CAP_BYTES} byte limit.",
        )

    return result_from_exit(proc.returncode, stdout_text, stderr_text)


def force_remove_container(container_name: str) -> None:
    try:
        subprocess.run(
            ["docker", "rm", "-f", container_name],
            capture_output=True,
            timeout=15,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return
