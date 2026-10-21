"""Orchestrate validation, workspace setup, and a sandboxed Docker run."""

from __future__ import annotations

from ..config import DEFAULT_RUN_TIMEOUT_SECONDS, MAX_SOURCE_BYTES
from ..domain.result import RunResult, Stage
from .docker_service import DockerService
from .workspace_service import WorkspaceService


class CppRunnerService:
    def __init__(
        self,
        docker: DockerService | None = None,
        workspace: WorkspaceService | None = None,
    ) -> None:
        self.docker = docker or DockerService()
        self.workspace = workspace or WorkspaceService()

    def run(
        self,
        source: str,
        stdin: str = "",
        *,
        timeout_seconds: float = DEFAULT_RUN_TIMEOUT_SECONDS,
    ) -> RunResult:
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

        docker_error = self.docker.check_available()
        if docker_error:
            return docker_error

        image_error = self.docker.ensure_image()
        if image_error:
            return image_error

        with self.workspace.open() as workdir:
            self.workspace.write_files(workdir, source, stdin)
            return self.docker.run_container(workdir, timeout_seconds)
