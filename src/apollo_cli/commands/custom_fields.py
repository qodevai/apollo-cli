"""Custom fields command group."""

from __future__ import annotations

from typing import Annotated

from cyclopts import App, Parameter

from apollo_cli.context import ctx
from apollo_cli.formatters.generic import list_table
from apollo_cli.output import output_list

custom_fields_app = App(name="custom-fields", help="Custom field definitions.")

CUSTOM_FIELD_COLUMNS = [
    ("ID", "id"),
    ("Modality", "modality"),
    ("Name", "name"),
    ("Type", "type"),
    ("CRM Field", "mapped_crm_field"),
]


@custom_fields_app.command(name="list")
async def list_fields(
    *,
    modality: Annotated[
        str | None,
        Parameter(name="--modality", help="Filter by modality: contact, account, or opportunity"),
    ] = None,
) -> None:
    """List custom field definitions across contacts, accounts, and opportunities."""
    async with ctx.client() as client:
        fields = await client.list_custom_fields()

    if modality:
        target = modality.strip().lower()
        fields = [f for f in fields if (f.modality or "").lower() == target]

    output_list(
        items=fields,
        total=len(fields),
        page=1,
        limit=len(fields) or 1,
        ctx=ctx,
        format_fn=lambda items, **kw: list_table(items, CUSTOM_FIELD_COLUMNS, title="Custom Fields", **kw),
        resource_name="Custom Fields",
    )
