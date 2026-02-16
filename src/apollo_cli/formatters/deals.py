"""Deal-specific formatters."""

from __future__ import annotations

from typing import Any

from apollo_cli.formatters.generic import detail_table, list_table

DEAL_DETAIL_FIELDS = [
    ("ID", "id"),
    ("Name", "name"),
    ("Amount", "amount"),
    ("Stage", "stage_name"),
    ("Pipeline ID", "opportunity_pipeline_id"),
    ("Probability", "probability"),
    ("Close Date", "closed_date"),
    ("Won", "is_won"),
    ("Closed", "is_closed"),
    ("Account ID", "account_id"),
    ("Owner ID", "owner_id"),
    ("Source", "source"),
    ("Next Step", "next_step"),
    ("Next Step Date", "next_step_date"),
    ("Forecast Category", "forecast_category"),
    ("Created", "created_at"),
    ("Last Activity", "last_activity_date"),
]

DEAL_LIST_COLUMNS = [
    ("Name", "name"),
    ("Amount", "amount"),
    ("Stage", "stage_name"),
    ("Close Date", "closed_date"),
    ("Won", "is_won"),
]


def format_deal_detail(data: Any) -> str:
    """Format a single deal as a markdown detail view."""
    name = data.name if hasattr(data, "name") else data.get("name", "Unknown")
    return detail_table(data, DEAL_DETAIL_FIELDS, title=f"Deal: {name}")


def format_deal_list(items: list[Any], *, total: int = 0, page: int = 1) -> str:
    """Format a list of deals as a markdown table."""
    return list_table(items, DEAL_LIST_COLUMNS, title="Deals", total=total, page=page)
