"""Calls command group."""

from __future__ import annotations

from cyclopts import App

from apollo_cli.context import ctx
from apollo_cli.formatters.generic import list_table
from apollo_cli.output import output_list

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
