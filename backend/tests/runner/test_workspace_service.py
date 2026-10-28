from pathlib import Path
import pytest

from runner.services.workspace_service import INPUT_FILENAME, SOURCE_FILENAME, WorkspaceService


def test_write_files_normalizes_newlines(tmp_path: Path) -> None:
    workspace = WorkspaceService()
    workspace.write_files(tmp_path, "int main() {\r\n}\r", "a\r\nb")

    source = (tmp_path / SOURCE_FILENAME).read_text(encoding="utf-8")
    stdin = (tmp_path / INPUT_FILENAME).read_text(encoding="utf-8")
    assert source == "int main() {\n}\n"
    assert stdin == "a\nb"


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


def test_write_files_creates_both_files_even_with_empty_stdin(tmp_path: Path) -> None:
    WorkspaceService().write_files(tmp_path, "int main() { return 0; }\n", "")

    assert (tmp_path / SOURCE_FILENAME).is_file()
    assert (tmp_path / INPUT_FILENAME).is_file()
    assert (tmp_path / INPUT_FILENAME).read_text(encoding="utf-8") == ""