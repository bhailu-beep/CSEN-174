"""Host-side temp workspace for one submission."""

from __future__ import annotations

import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from config import SANDBOX_DIR
from utils.text import normalize_newlines

STUDENT_FILENAME = "student.cpp"
TESTER_FILENAME = "tester.cpp"
TESTS_FILENAME = "tests.txt"
HARNESS_FILENAME = "harness.h"


class WorkspaceService:
    """Create a throwaway directory and write the files Docker bind-mounts."""

    @contextmanager
    def open(self) -> Iterator[Path]:
        with tempfile.TemporaryDirectory(prefix="completec-") as tmp:
            yield Path(tmp)

    def write_files(self, workdir: Path, source: str, tester: str, tests: str) -> None:
        (workdir / STUDENT_FILENAME).write_text(normalize_newlines(source), encoding="utf-8")
        (workdir / TESTER_FILENAME).write_text(normalize_newlines(tester), encoding="utf-8")
        (workdir / TESTS_FILENAME).write_text(normalize_newlines(tests), encoding="utf-8")
        harness = (SANDBOX_DIR / HARNESS_FILENAME).read_text(encoding="utf-8")
        (workdir / HARNESS_FILENAME).write_text(harness, encoding="utf-8")
