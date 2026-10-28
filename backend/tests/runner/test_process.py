from __future__ import annotations

import io
import subprocess
from unittest.mock import MagicMock

from runner.util.process import communicate_capped


def _process(stdout: bytes = b"", stderr: bytes = b"", *, hang: bool = False) -> MagicMock:
    """
    Fake Popen: real BytesIO pipes plus a mocked wait/kill.

    hang=True makes wait() raise TimeoutExpired, like a process that never exits.
    """
    proc = MagicMock()
    proc.stdout = io.BytesIO(stdout)
    proc.stderr = io.BytesIO(stderr)
    if hang:
        proc.wait.side_effect = subprocess.TimeoutExpired(cmd="fake", timeout=0.01)
    else:
        proc.wait.return_value = 0
    return proc


def test_communicate_capped_returns_output() -> None:
    proc = _process(stdout=b"hello", stderr=b"warn")
    stdout, stderr, timed_out, truncated = communicate_capped(proc, max_bytes=64, timeout_seconds=1)
    assert stdout == b"hello"
    assert stderr == b"warn"
    assert timed_out is False
    assert truncated is False
    proc.kill.assert_not_called()


def test_communicate_capped_kills_when_output_exceeds_cap() -> None:
    proc = _process(stdout=b"x" * 50)
    stdout, stderr, timed_out, truncated = communicate_capped(proc, max_bytes=8, timeout_seconds=1)
    assert truncated is True
    assert timed_out is False
    assert stdout == b"xxxxxxxx"
    proc.kill.assert_called()


def test_communicate_capped_times_out() -> None:
    proc = _process(stdout=b"partial", hang=True)
    stdout, stderr, timed_out, truncated = communicate_capped(proc, max_bytes=64, timeout_seconds=0.01)
    assert timed_out is True
    assert truncated is False
    assert stdout == b"partial"
    proc.kill.assert_called()
    proc.wait.assert_called()
