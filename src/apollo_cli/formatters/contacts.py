"""Contact-specific formatters."""

from __future__ import annotations

from typing import Any

from apollo_cli.formatters.generic import detail_table, list_table

CONTACT_DETAIL_FIELDS = [
    ("ID", "id"),
    ("Name", "name"),
    ("Email", "email"),
    ("Title", "title"),
    ("Company", "organization_name"),
    ("LinkedIn", "linkedin_url"),
    ("Phone", "sanitized_phone"),
    ("Stage ID", "contact_stage_id"),
    ("City", "city"),
    ("State", "state"),
    ("Country", "country"),
    ("Source", "source"),
    ("Owner ID", "owner_id"),
    ("Created", "created_at"),
    ("Updated", "updated_at"),
    ("Last Activity", "last_activity_date"),
]

CONTACT_LIST_COLUMNS = [
    ("Name", "name"),
    ("Title", "title"),
    ("Company", "organization_name"),
    ("Email", "email"),
    ("LinkedIn", "linkedin_url"),
]


def format_contact_detail(data: Any) -> str:
    """Format a single contact as a markdown detail view."""
    name = data.name if hasattr(data, "name") else data.get("name", "Unknown")
    md = detail_table(data, CONTACT_DETAIL_FIELDS, title=f"Contact: {name}")

    # Phone numbers section
    phones = data.phone_numbers if hasattr(data, "phone_numbers") else data.get("phone_numbers", [])
    if phones:
        md += "\n\n## Phone Numbers\n"
        for p in phones:
            if hasattr(p, "sanitized_number"):
                num = p.sanitized_number or p.number
                ptype = p.type or "unknown"
            else:
                num = p.get("sanitized_number") or p.get("number", "")
                ptype = p.get("type", "unknown")
            md += f"\n- {num} ({ptype})"

    # Employment history (detail endpoint only)
    history = getattr(data, "employment_history", None)
    if history:
        md += "\n\n## Employment History\n"
        for entry in history:
            org = entry.organization_name or "Unknown"
            title = entry.title or "Unknown"
            current = " (current)" if entry.current else ""
            md += f"\n- **{title}** at {org}{current}"

    return md


def format_contact_list(items: list[Any], *, total: int = 0, page: int = 1) -> str:
    """Format a list of contacts as a markdown table."""
    return list_table(items, CONTACT_LIST_COLUMNS, title="Contacts", total=total, page=page)


def format_stages_list(stages: list[Any], *, total: int = 0, page: int = 1) -> str:
    """Format contact stages."""
    columns = [
        ("ID", "id"),
        ("Name", "name"),
        ("Display Order", "display_order"),
    ]
    return list_table(stages, columns, title="Contact Stages", total=total, page=page)
