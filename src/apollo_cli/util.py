"""Shared utility helpers for CLI commands."""

from __future__ import annotations


def parse_comma_list(raw: str) -> list[str]:
    """Parse a comma-separated CLI argument into a list of stripped, non-empty tokens.

    - `"a,b,c"` → `["a", "b", "c"]`
    - `"a, ,b"`, `"a,,b"`, `",a,b,"` → `["a", "b"]` (drops empty/whitespace-only tokens,
      forgiving of typos)
    - `""` or `"   "` → `[]` (no meaningful input, treat as "flag not provided")
    - `",,,"` → raises `ValueError` (user typed *something* but it collapsed to
      nothing — that's broken input, not "empty", so fail loud rather than silently
      omit the flag)

    Not a real CSV parser — no quoting or escaping, just comma-split-and-strip.
    """
    tokens = [t.strip() for t in raw.split(",") if t.strip()]
    if not tokens and raw.strip():
        raise ValueError(f"expected comma-separated values, got only separators: {raw!r}")
    return tokens
