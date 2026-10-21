from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import Mock

from runner.config import (
    COMPILE_TIMEOUT_SECONDS,
    DOCKER_GRACE_SECONDS,
    IMAGE_NAME,
    OUTPUT_CAP_BYTES,
    SANDBOX_DIR,
)
from runner.domain.result import Stage
from runner.services.docker_service import DockerService


def _completed(command: list[str], returncode: int = 0, stdout: bytes = b"", stderr: bytes = b""):
    """Build the object `subprocess.run` returns, so Docker CLI mocks can look real."""
    return subprocess.CompletedProcess(command, returncode, stdout=stdout, stderr=stderr)


def test_docker_path_uses_forward_slashes(tmp_path: Path) -> None:
    path = tmp_path / "sub" / "dir"
    path.mkdir(parents=True)
    converted = DockerService.docker_path(path)
    assert "\\" not in converted
    assert converted.endswith("/sub/dir") or converted.endswith("sub/dir")


def test_check_available_missing_binary() -> None:
    run = Mock(side_effect=FileNotFoundError())
    result = DockerService(run=run).check_available()
    assert result is not None
    assert result.stage is Stage.ERROR
    assert "not installed" in result.message
    run.assert_called_once()


def test_check_available_timeout() -> None:
    run = Mock(side_effect=subprocess.TimeoutExpired(cmd="docker", timeout=15))
    result = DockerService(run=run).check_available()
    assert result is not None
    assert "Timed out" in result.message


def test_check_available_nonzero_status() -> None:
    run = Mock(return_value=_completed(["docker", "version"], returncode=1, stderr=b"daemon down"))
    result = DockerService(run=run).check_available()
    assert result is not None
    assert "daemon down" in result.message
    run.assert_called_once_with(["docker", "version"], capture_output=True, timeout=15)


def test_check_available_ok() -> None:
    run = Mock(return_value=_completed(["docker", "version"]))
    assert DockerService(run=run).check_available() is None


def test_ensure_image_skips_build_when_present() -> None:
    run = Mock(return_value=_completed(["docker", "image", "inspect", IMAGE_NAME]))
    assert DockerService(run=run).ensure_image() is None
    run.assert_called_once_with(
        ["docker", "image", "inspect", IMAGE_NAME],
        capture_output=True,
        timeout=15,
    )


def test_ensure_image_builds_when_missing() -> None:
    inspect = _completed(["docker", "image", "inspect", IMAGE_NAME], returncode=1)
    build = _completed(["docker", "build", "-t", IMAGE_NAME, str(SANDBOX_DIR)])
    run = Mock(side_effect=[inspect, build])

    assert DockerService(run=run).ensure_image() is None
    assert run.call_args_list[1].args[0] == ["docker", "build", "-t", IMAGE_NAME, str(SANDBOX_DIR)]


def test_ensure_image_reports_build_failure() -> None:
    inspect = _completed(["docker", "image", "inspect", IMAGE_NAME], returncode=1)
    build = _completed(["docker", "build"], returncode=1, stderr=b"apt failed")
    run = Mock(side_effect=[inspect, build])

    result = DockerService(run=run).ensure_image()
    assert result is not None
    assert result.stage is Stage.ERROR
    assert "Failed to build" in result.message
    assert "apt failed" in result.stderr


def test_build_run_command_includes_sandbox_flags(tmp_path: Path) -> None:
    command = DockerService().build_run_command(tmp_path, "completec-test", 2.0)
    assert command[0:2] == ["docker", "run"]
    assert "--network=none" in command
    assert "--read-only" in command
    assert "--cap-drop=ALL" in command
    assert f"{DockerService.docker_path(tmp_path)}:/src:ro" in command
    assert "RUN_TIMEOUT=2.0" in command
    assert IMAGE_NAME in command


def test_run_container_success(tmp_path: Path) -> None:
    proc = Mock()
    proc.returncode = 0
    run = Mock(return_value=_completed(["docker", "rm", "-f", "completec-fixed"]))
    popen = Mock(return_value=proc)
    communicate = Mock(return_value=(b"Hello, World!\n", b"", False, False))

    service = DockerService(
        run=run,
        popen=popen,
        communicate=communicate,
        new_container_name=Mock(return_value="completec-fixed"),
    )
    result = service.run_container(tmp_path, 2.0)

    assert result.ok is True
    assert result.stdout == "Hello, World!\n"
    assert result.stage is Stage.RUN
    popen.assert_called_once()
    run.assert_called_once_with(
        ["docker", "rm", "-f", "completec-fixed"],
        capture_output=True,
        timeout=15,
    )


def test_run_container_timeout(tmp_path: Path) -> None:
    communicate = Mock(return_value=(b"", b"", True, False))
    result = DockerService(
        run=Mock(return_value=_completed(["docker", "rm"])),
        popen=Mock(return_value=Mock(returncode=None)),
        communicate=communicate,
    ).run_container(tmp_path, 1.0)

    assert result.timed_out is True
    assert result.ok is False
    assert result.stage is Stage.RUN
    communicate.assert_called_once()


def test_run_container_truncated(tmp_path: Path) -> None:
    proc = Mock()
    proc.returncode = 137
    result = DockerService(
        run=Mock(return_value=_completed(["docker", "rm"])),
        popen=Mock(return_value=proc),
        communicate=Mock(return_value=(b"x" * 10, b"", False, True)),
    ).run_container(tmp_path, 1.0)

    assert result.ok is False
    assert str(OUTPUT_CAP_BYTES) in result.message


def test_run_container_popen_missing(tmp_path: Path) -> None:
    popen = Mock(side_effect=FileNotFoundError())
    result = DockerService(popen=popen).run_container(tmp_path, 1.0)
    assert result is not None
    assert "not installed" in result.message
    popen.assert_called_once()


def test_run_container_passes_wall_timeout(tmp_path: Path) -> None:
    communicate = Mock(return_value=(b"", b"", False, False))
    DockerService(
        run=Mock(return_value=_completed(["docker", "rm"])),
        popen=Mock(return_value=Mock(returncode=0)),
        communicate=communicate,
    ).run_container(tmp_path, 2.0)

    communicate.assert_called_once()
    assert communicate.call_args.kwargs["max_bytes"] == OUTPUT_CAP_BYTES
    assert communicate.call_args.kwargs["timeout_seconds"] == (
        COMPILE_TIMEOUT_SECONDS + 2.0 + DOCKER_GRACE_SECONDS
    )


def test_remove_container_swallows_errors() -> None:
    run = Mock(side_effect=FileNotFoundError())
    DockerService(run=run).remove_container("completec-x")
    run.assert_called_once()
