"""Shared utility helpers for CLI commands."""

from __future__ import annotations


def parse_csv(raw: str) -> list[str]:
    """Parse a comma-separated CLI argument into a list of stripped, non-empty tokens.

    Handles trailing/leading commas, embedded empty segments, and whitespace-only
    tokens by dropping them — so `"a,,b, ,c"` returns `["a", "b", "c"]` rather
    than propagating empty strings to the Apollo API (which 400s on them).
    """
    return [token.strip() for token in raw.split(",") if token.strip()]
