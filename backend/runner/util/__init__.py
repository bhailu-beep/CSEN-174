"""Helpers that are not application services."""

from .process import communicate_capped
from .text import decode, normalize_newlines

__all__ = ["communicate_capped", "decode", "normalize_newlines"]
