"""Notes command group."""

from __future__ import annotations

from typing import Annotated

from cyclopts import App, Parameter

from apollo_cli.context import ctx
from apollo_cli.formatters.generic import list_table
from apollo_cli.output import output, output_list

notes_app = App(name="notes", help="Notes management.")

NOTE_LIST_COLUMNS = [
    ("ID", "id"),
    ("Content", "content"),
    ("Contact ID", "contact_id"),
    ("Account ID", "account_id"),
    ("Created", "created_at"),
]


@notes_app.command
async def search(
    *,
    contact_id: Annotated[str | None, Parameter(name="--contact-id", help="Filter by contact ID")] = None,
    account_id: Annotated[str | None, Parameter(name="--account-id", help="Filter by account ID")] = None,
) -> None:
    """Search notes by contact or account."""
    filters: dict = {}
    if contact_id:
        filters["contact_ids"] = [contact_id]
    if account_id:
        filters["account_ids"] = [account_id]

    async with ctx.client() as client:
        result = await client.search_notes(page=ctx.page, limit=ctx.limit, **filters)

    output_list(
        items=result.items,
        total=result.total,
        page=result.page,
        limit=ctx.limit,
        ctx=ctx,
        format_fn=lambda items, **kw: list_table(items, NOTE_LIST_COLUMNS, title="Notes", **kw),
        resource_name="Notes",
    )


@notes_app.command
async def create(
    *,
    content: Annotated[str, Parameter(name="--content", help="Note content")],
    contact_ids: Annotated[str | None, Parameter(name="--contact-ids", help="Comma-separated contact IDs")] = None,
    account_ids: Annotated[str | None, Parameter(name="--account-ids", help="Comma-separated account IDs")] = None,
) -> None:
    """Create a new note."""
    kwargs: dict = {}
    if contact_ids:
        kwargs["contact_ids"] = [cid.strip() for cid in contact_ids.split(",")]
    if account_ids:
        kwargs["account_ids"] = [aid.strip() for aid in account_ids.split(",")]

    async with ctx.client() as client:
        result = await client.create_note(content, **kwargs)

    output(result, ctx=ctx)
