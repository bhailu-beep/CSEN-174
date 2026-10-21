from pathlib import Path

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
