"""Shared utility helpers for CLI commands."""

from __future__ import annotations

from typing import Any


def _field(item: Any, key: str) -> Any:
    """Read ``key`` from either a Pydantic model (attr) or a dict."""
    return item.get(key) if isinstance(item, dict) else getattr(item, key, None)


def resolve_stage_id(name: str, stages: list[Any], *, kind: str = "stage") -> str:
    """Resolve a stage *name* (case-insensitive) to its ID from a list of stages.

    ``stages`` items may be Pydantic models or dicts exposing ``name`` and ``id``.
    Raises ``ValueError`` (surfaced by the CLI as a validation error) listing the
    available names when there is no match.
    """
    target = name.strip().lower()
    match = next((s for s in stages if (_field(s, "name") or "").lower() == target), None)
    if match is None:
        names = sorted(n for s in stages if (n := _field(s, "name")))
        raise ValueError(f"No {kind} named {name!r}. Available: {_preview(names)}")
    return _field(match, "id")


def _preview(names: list[str], limit: int = 15) -> str:
    """Render a name list for an error message, capped so it can't get huge."""
    if not names:
        return "(none)"
    if len(names) <= limit:
        return ", ".join(names)
    return f"{', '.join(names[:limit])}, … (+{len(names) - limit} more)"


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
