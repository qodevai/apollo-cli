"""Calls command group."""

from __future__ import annotations

from typing import Annotated

from cyclopts import App, Parameter

from apollo_cli.context import ctx
from apollo_cli.formatters.generic import list_table
from apollo_cli.output import output_json, output_list, output_markdown

calls_app = App(name="calls", help="Call activity.")

CALL_LIST_COLUMNS = [
    ("ID", "id"),
    ("Contact ID", "contact_id"),
    ("Status", "status"),
    ("Duration", "duration"),
    ("Start", "start_time"),
    ("Note", "note"),
]


@calls_app.command
async def search() -> None:
    """Search call activities."""
    async with ctx.client() as client:
        result = await client.search_calls(page=ctx.page, limit=ctx.limit)

    output_list(
        items=result.items,
        total=result.total,
        page=result.page,
        limit=ctx.limit,
        ctx=ctx,
        format_fn=lambda items, **kw: list_table(items, CALL_LIST_COLUMNS, title="Calls", **kw),
        resource_name="Calls",
    )


@calls_app.command(name="list")
async def list_contact_calls(
    contact_id: Annotated[str, Parameter(help="Contact ID")],
) -> None:
    """List calls for a specific contact."""
    async with ctx.client() as client:
        result = await client.list_contact_calls(contact_id)

    if ctx.json_mode:
        output_json(result)
    else:
        md = list_table(result, CALL_LIST_COLUMNS, title="Contact Calls", total=len(result), page=1)
        output_markdown(md)
