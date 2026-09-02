"""Shared utility helpers for CLI commands."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from zoneinfo import ZoneInfo

# Jan's local timezone — the assumed zone for a --due-at value with no offset of
# its own (a bare date, or a date+time with no trailing Z/+HH:MM).
_LOCAL_TZ = ZoneInfo("Europe/Berlin")


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


def parse_due_at(raw: str) -> str:
    """Parse a ``--due-at`` CLI value into a UTC ISO 8601 string (``...Z``) for the API.

    Accepts:
    - ``YYYY-MM-DD`` — a bare date defaults to **09:00 Europe/Berlin**.
    - ``YYYY-MM-DDTHH:MM`` (optionally with seconds) and **no** offset — assumed
      Europe/Berlin.
    - A full ISO 8601 datetime carrying its own offset (trailing ``Z`` or
      ``+HH:MM``/``-HH:MM``) — used as given, just converted to UTC.

    Args:
        raw: The raw ``--due-at`` string.

    Returns:
        UTC datetime as ``YYYY-MM-DDTHH:MM:SSZ``.

    Raises:
        ValueError: ``raw`` doesn't parse as a date or datetime.
    """
    value = raw.strip()
    try:
        if len(value) == 10:
            # Bare date: YYYY-MM-DD.
            dt = datetime.strptime(value, "%Y-%m-%d").replace(hour=9, minute=0, tzinfo=_LOCAL_TZ)
        else:
            # datetime.fromisoformat only accepts "+00:00", not a trailing "Z", for
            # the UTC offset until Python 3.11 — normalise it ourselves either way.
            iso_value = f"{value[:-1]}+00:00" if value.endswith("Z") else value
            dt = datetime.fromisoformat(iso_value)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=_LOCAL_TZ)
    except ValueError as exc:
        raise ValueError(
            f"Invalid --due-at {raw!r}: expected YYYY-MM-DD, YYYY-MM-DDTHH:MM, or a "
            f"full ISO 8601 datetime with a timezone offset."
        ) from exc
    return dt.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
