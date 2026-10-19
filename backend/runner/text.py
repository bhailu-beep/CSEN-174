"""Small text helpers for source, stdin, and captured output."""


def normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def decode(data: bytes) -> str:
    return data.decode("utf-8", errors="replace")
