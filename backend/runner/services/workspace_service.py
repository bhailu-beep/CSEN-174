"""Host-side temp workspace for student source and stdin files."""

from __future__ import annotations

import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from ..util.text import normalize_newlines

SOURCE_FILENAME = "main.cpp"
INPUT_FILENAME = "input.txt"

class WorkspaceService:
    """Create a throwaway directory and write the files Docker bind-mounts."""

    @contextmanager
    def open(self) -> Iterator[Path]:
        with tempfile.TemporaryDirectory(prefix="completec-") as tmp:
            yield Path(tmp)

    def write_files(self, workdir: Path, source: str, stdin: str) -> None:
        source_file = workdir / SOURCE_FILENAME
        input_file = workdir / INPUT_FILENAME
        source_file.write_text(normalize_newlines(source), encoding="utf-8")
        input_file.write_text(normalize_newlines(stdin), encoding="utf-8")
