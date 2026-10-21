"""Docker CLI wrapper used to compile and run student C++ in a sandbox."""

from __future__ import annotations

import subprocess
import uuid
from collections.abc import Callable
from pathlib import Path

from ..config import (COMPILE_TIMEOUT_SECONDS, CPUS, DOCKER_GRACE_SECONDS,
                      IMAGE_NAME, MEMORY_MB, OUTPUT_CAP_BYTES, PIDS_LIMIT,
                      SANDBOX_DIR, SANDBOX_USER, TMPFS_SIZE)
from ..domain.result import RunResult, Stage
from ..util.process import communicate_capped
from ..util.text import decode

RunFn = Callable[..., subprocess.CompletedProcess[bytes]]
PopenFn = Callable[..., subprocess.Popen[bytes]]
CommunicateFn = Callable[..., tuple[bytes, bytes, bool, bool]]


class DockerService:
    def __init__(
        self,
        *,
        run: RunFn | None = None,
        popen: PopenFn | None = None,
        communicate: CommunicateFn | None = None,
        new_container_name: Callable[[], str] | None = None,
    ) -> None:
        self._run = run or subprocess.run
        self._popen = popen or subprocess.Popen
        self._communicate = communicate or communicate_capped
        self._new_container_name = new_container_name or (
            lambda: f"completec-{uuid.uuid4().hex[:12]}"
        )

    @staticmethod
    def docker_path(path: Path) -> str:
        return str(path.resolve()).replace("\\", "/")

    def check_available(self) -> RunResult | None:
        try:
            completed = self._run(
                ["docker", "version"],
                capture_output=True,
                timeout=15,
            )
        except FileNotFoundError:
            return RunResult.error("Docker is not installed or not on PATH. Install Docker Desktop and try again.")
        except subprocess.TimeoutExpired:
            return RunResult.error("Timed out while checking Docker. Is Docker Desktop running?")

        if completed.returncode != 0:
            stderr = decode(completed.stderr).strip()
            return RunResult.error(
                "Docker is not available. Start Docker Desktop and try again."
                + (f" {stderr}" if stderr else "")
            )
        return None

    def ensure_image(self) -> RunResult | None:
        try:
            inspect = self._run(
                ["docker", "image", "inspect", IMAGE_NAME],
                capture_output=True,
                timeout=15,
            )
        except subprocess.TimeoutExpired:
            return RunResult.error("Timed out while checking for the C++ sandbox image.")

        if inspect.returncode == 0:
            return None

        try:
            build = self._run(
                ["docker", "build", "-t", IMAGE_NAME, str(SANDBOX_DIR)],
                capture_output=True,
                timeout=600,
            )
        except subprocess.TimeoutExpired:
            return RunResult.error("Timed out while building the C++ sandbox image.")

        if build.returncode != 0:
            return RunResult.error(
                "Failed to build the C++ sandbox image.",
                stdout=decode(build.stdout),
                stderr=decode(build.stderr),
            )
        return None

    def build_run_command(
        self,
        workdir: Path,
        container_name: str,
        timeout_seconds: float,
    ) -> list[str]:
        return [
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
            f"{self.docker_path(workdir)}:/src:ro",
            IMAGE_NAME,
        ]

    def run_container(self, workdir: Path, timeout_seconds: float) -> RunResult:
        container_name = self._new_container_name()
        full_timeout = COMPILE_TIMEOUT_SECONDS + timeout_seconds + DOCKER_GRACE_SECONDS
        command = self.build_run_command(workdir, container_name, timeout_seconds)

        try:
            proc = self._popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except FileNotFoundError:
            return RunResult.error("Docker is not installed or not on PATH. Install Docker Desktop and try again.")
        except OSError as exc:
            return RunResult.error(f"Failed to start Docker: {exc}")

        try:
            stdout, stderr, timed_out, truncated = self._communicate(
                proc,
                max_bytes=OUTPUT_CAP_BYTES,
                timeout_seconds=full_timeout,
            )
        finally:
            self.remove_container(container_name)

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

        return RunResult.from_exit(proc.returncode, stdout_text, stderr_text)

    def remove_container(self, container_name: str) -> None:
        try:
            self._run(
                ["docker", "rm", "-f", container_name],
                capture_output=True,
                timeout=15,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            return
