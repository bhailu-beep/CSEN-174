from pathlib import Path
import pytest

from services.workspace import (
    STUDENT_FILENAME,
    TESTER_FILENAME,
    TESTS_FILENAME,
    WorkspaceService,
)


def test_write_files_normalizes_newlines(tmp_path: Path) -> None:
    workspace = WorkspaceService()
    workspace.write_files(tmp_path, "int main() {\r\n}\r", "int main() {\r\n}\r", "name: a\r\n")

    source = (tmp_path / STUDENT_FILENAME).read_text(encoding="utf-8")
    tester = (tmp_path / TESTER_FILENAME).read_text(encoding="utf-8")
    tests = (tmp_path / TESTS_FILENAME).read_text(encoding="utf-8")
    assert source == "int main() {\n}\n"
    assert tester == "int main() {\n}\n"
    assert tests == "name: a\n"


def test_open_creates_and_deletes_directory() -> None:
    workspace = WorkspaceService()
    with workspace.open() as workdir:
        assert workdir.is_dir()
        marker = workdir / "keep.txt"
        marker.write_text("x", encoding="utf-8")
        saved = workdir

    assert not saved.exists()

def test_open_cleans_up_directory_when_an_error_is_raised() -> None:
    workspace = WorkspaceService()
    saved: list[Path] = []

    with pytest.raises(RuntimeError):
        with workspace.open() as workdir:
            saved.append(workdir)
            (workdir / "leftover.txt").write_text("student code", encoding="utf-8")
            raise RuntimeError("boom")

    assert len(saved) == 1
    assert not saved[0].exists()


def test_open_gives_each_call_its_own_directory() -> None:
    workspace = WorkspaceService()

    with workspace.open() as first, workspace.open() as second:
        assert first != second
        assert first.name.startswith("completec-")
        assert second.name.startswith("completec-")

        (first / "marker.txt").write_text("only in first", encoding="utf-8")
        assert not (second / "marker.txt").exists()


def test_write_files_creates_the_sandbox_files(tmp_path: Path) -> None:
    WorkspaceService().write_files(tmp_path, "int main() { return 0; }\n", "int main() { return 0; }\n", "")

    assert (tmp_path / STUDENT_FILENAME).is_file()
    assert (tmp_path / TESTER_FILENAME).is_file()
    assert (tmp_path / TESTS_FILENAME).read_text(encoding="utf-8") == ""
    assert (tmp_path / "harness.h").is_file()