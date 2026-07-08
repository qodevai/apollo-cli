"""People-search formatters."""

from __future__ import annotations

from typing import Any

from apollo_cli.formatters.generic import list_table

# People objects nest their company under `organization`; `list_table` reads dot paths.
PEOPLE_LIST_COLUMNS = [
    ("Name", "name"),
    ("Title", "title"),
    ("Company", "organization.name"),
    ("Email", "email"),
    ("LinkedIn", "linkedin_url"),
]


def format_people_list(items: list[Any], *, total: int = 0, page: int = 1) -> str:
    """Format people-database search results as a markdown table."""
    return list_table(items, PEOPLE_LIST_COLUMNS, title="People", total=total, page=page)
