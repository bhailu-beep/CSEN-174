"""Read subprocess stdout/stderr with a size and time cap."""

from __future__ import annotations

import subprocess
import threading
from typing import IO


def communicate_capped(
    proc: subprocess.Popen[bytes],
    max_bytes: int,
    timeout_seconds: float,
) -> tuple[bytes, bytes, bool, bool]:
    """
    Wait for a process and capture stdout/stderr, with hard limits.

    Reads both pipes on background threads so a full pipe cannot deadlock.
    If either stream exceeds max_bytes, the process is killed and truncated
    is True. If wait() exceeds timeout_seconds, the process is killed and
    timed_out is True.

    Returns (stdout, stderr, timed_out, truncated).
    """
    stdout_buf = bytearray()
    stderr_buf = bytearray()
    truncated = False
    lock = threading.Lock()

    def _read(pipe: IO[bytes] | None, buf: bytearray) -> None:
        nonlocal truncated
        if pipe is None:
            return
        try:
            while True:
                chunk = pipe.read(4096)
                if not chunk:
                    return
                with lock:
                    if truncated:
                        return
                    room = max_bytes - len(buf)
                    if room <= 0 or len(chunk) > room:
                        if room > 0:
                            buf.extend(chunk[:room])
                        truncated = True
                        proc.kill()
                        return
                    buf.extend(chunk)
        except (OSError, ValueError):
            return

    threads = [
        threading.Thread(target=_read, args=(proc.stdout, stdout_buf), daemon=True),
        threading.Thread(target=_read, args=(proc.stderr, stderr_buf), daemon=True),
    ]
    for thread in threads:
        thread.start()

    timed_out = False
    try:
        proc.wait(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        timed_out = True
        proc.kill()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pass

    for thread in threads:
        thread.join(timeout=2)

    return bytes(stdout_buf), bytes(stderr_buf), timed_out, truncated
