"""Emails command group."""

from __future__ import annotations

from cyclopts import App

from apollo_cli.context import ctx
from apollo_cli.formatters.generic import list_table
from apollo_cli.output import output_list

emails_app = App(name="emails", help="Email activity.")

EMAIL_LIST_COLUMNS = [
    ("ID", "id"),
    ("Subject", "subject"),
    ("From", "from_email"),
    ("To", "to_email"),
    ("Status", "status"),
    ("Created", "created_at"),
]


@emails_app.command
async def search() -> None:
    """Search email activities."""
    async with ctx.client() as client:
        result = await client.search_emails(page=ctx.page, limit=ctx.limit)

    output_list(
        items=result.items,
        total=result.total,
        page=result.page,
        limit=ctx.limit,
        ctx=ctx,
        format_fn=lambda items, **kw: list_table(items, EMAIL_LIST_COLUMNS, title="Emails", **kw),
        resource_name="Emails",
    )
