"""Tasks command group."""

from __future__ import annotations

from typing import Annotated

from cyclopts import App, Parameter

from apollo_cli.context import ctx
from apollo_cli.formatters.generic import list_table
from apollo_cli.output import output, output_list
from apollo_cli.util import parse_comma_list

tasks_app = App(name="tasks", help="Task management.")

TASK_LIST_COLUMNS = [
    ("ID", "id"),
    ("Subject", "subject"),
    ("Type", "type"),
    ("Priority", "priority"),
    ("Status", "status"),
    ("Due", "due_at"),
]


@tasks_app.command
async def search(
    *,
    type: Annotated[str | None, Parameter(name="--type", help="Filter by task type (call, action_item, etc.)")] = None,
    contact_id: Annotated[str | None, Parameter(name="--contact-id", help="Filter by contact ID")] = None,
) -> None:
    """Search tasks."""
    filters: dict = {}
    if type:
        filters["task_type_cds"] = [type]
    if contact_id:
        filters["contact_ids"] = [contact_id]

    async with ctx.client() as client:
        result = await client.search_tasks(page=ctx.page, limit=ctx.limit, **filters)

    output_list(
        items=result.items,
        total=result.total,
        page=result.page,
        limit=ctx.limit,
        ctx=ctx,
        format_fn=lambda items, **kw: list_table(items, TASK_LIST_COLUMNS, title="Tasks", **kw),
        resource_name="Tasks",
    )


@tasks_app.command
async def create(
    *,
    contact_ids: Annotated[str, Parameter(name="--contact-ids", help="Comma-separated contact IDs")],
    note: Annotated[str, Parameter(name="--note", help="Task description")],
    type: Annotated[str, Parameter(name="--type", help="Task type")] = "action_item",
    priority: Annotated[str, Parameter(name="--priority", help="Priority (high, medium, low)")] = "medium",
) -> None:
    """Create a new task."""
    ids = parse_comma_list(contact_ids)

    async with ctx.client() as client:
        result = await client.create_task(contact_ids=ids, note=note, type=type, priority=priority)

    output(result, ctx=ctx)


@tasks_app.command
async def complete(
    id: Annotated[str, Parameter(help="Task ID")],
    *,
    note: Annotated[str | None, Parameter(name="--note", help="Completion note")] = None,
) -> None:
    """Mark a task as completed."""
    async with ctx.client() as client:
        result = await client.complete_task(id, note=note)

    output(result, ctx=ctx)
