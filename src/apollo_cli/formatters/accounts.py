"""Account-specific formatters."""

from __future__ import annotations

from typing import Any

from apollo_cli.formatters.generic import detail_table, list_table

ACCOUNT_DETAIL_FIELDS = [
    ("ID", "id"),
    ("Name", "name"),
    ("Domain", "domain"),
    ("Phone", "phone"),
    ("Industry", "industry"),
    ("Employees", "estimated_num_employees"),
    ("Revenue", "annual_revenue_printed"),
    ("LinkedIn", "linkedin_url"),
    ("Website", "website_url"),
    ("City", "city"),
    ("State", "state"),
    ("Country", "country"),
    ("Stage ID", "account_stage_id"),
    ("Owner ID", "owner_id"),
    ("Contacts", "num_contacts"),
    ("Founded", "founded_year"),
    ("Description", "short_description"),
    ("Created", "created_at"),
    ("Last Activity", "last_activity_date"),
]

ACCOUNT_LIST_COLUMNS = [
    ("Name", "name"),
    ("Domain", "domain"),
    ("Industry", "industry"),
    ("Employees", "estimated_num_employees"),
    ("City", "city"),
]


def format_account_detail(data: Any) -> str:
    """Format a single account as a markdown detail view."""
    name = data.name if hasattr(data, "name") else data.get("name", "Unknown")
    md = detail_table(data, ACCOUNT_DETAIL_FIELDS, title=f"Account: {name}")

    # Technology stack (detail endpoint)
    tech = getattr(data, "technology_names", None) or (data.get("technology_names") if isinstance(data, dict) else None)
    if tech:
        md += "\n\n## Technology Stack\n"
        md += "\n" + ", ".join(tech)

    # Keywords
    keywords = getattr(data, "keywords", None) or (data.get("keywords") if isinstance(data, dict) else None)
    if keywords:
        md += "\n\n## Keywords\n"
        md += "\n" + ", ".join(keywords)

    return md


def format_account_list(items: list[Any], *, total: int = 0, page: int = 1) -> str:
    """Format a list of accounts as a markdown table."""
    return list_table(items, ACCOUNT_LIST_COLUMNS, title="Accounts", total=total, page=page)
