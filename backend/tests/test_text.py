from runner.util.text import decode, normalize_newlines


def test_normalize_newlines_converts_windows_and_old_mac() -> None:
    assert normalize_newlines("a\r\nb\rc") == "a\nb\nc"


def test_normalize_newlines_leaves_unix_alone() -> None:
    assert normalize_newlines("a\nb\n") == "a\nb\n"


def test_decode_replaces_invalid_utf8() -> None:
    assert decode(b"ok") == "ok"
    assert "\ufffd" in decode(b"\xff")
