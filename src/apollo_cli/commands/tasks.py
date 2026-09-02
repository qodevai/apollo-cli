"""Tasks command group."""

from __future__ import annotations

from typing import Annotated

from cyclopts import App, Parameter

from apollo_cli.context import ctx
from apollo_cli.formatters.generic import list_table
from apollo_cli.output import output, output_list
from apollo_cli.util import parse_comma_list, parse_due_at

tasks_app = App(name="tasks", help="Task management.")

DUE_AT_HELP = (
    "Due date/time: YYYY-MM-DD (09:00 Europe/Berlin), YYYY-MM-DDTHH:MM (assumed "
    "Europe/Berlin), or a full ISO 8601 datetime with its own timezone offset."
)


def _task_extras(*, user_id: str | None, due_at: str | None, title: str | None) -> dict[str, str]:
    """Collect the optional task fields, omitting the ones left unset."""
    extra: dict[str, str] = {}
    if user_id is not None:
        extra["user_id"] = user_id
    if due_at is not None:
        extra["due_at"] = parse_due_at(due_at)
    if title is not None:
        extra["title"] = title
    return extra


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
    note: Annotated[str | None, Parameter(name="--note", help="Task description")] = None,
    type: Annotated[str, Parameter(name="--type", help="Task type")] = "action_item",
    priority: Annotated[str, Parameter(name="--priority", help="Priority (high, medium, low)")] = "medium",
    user_id: Annotated[
        str | None,
        Parameter(name="--user-id", help="Task owner. Apollo rejects creation without a valid owner"),
    ] = None,
    due_at: Annotated[str | None, Parameter(name="--due-at", help=DUE_AT_HELP)] = None,
    title: Annotated[
        str | None, Parameter(name="--title", help="Task title shown in Apollo (internal, never sent)")
    ] = None,
) -> None:
    """Create a new task."""
    ids = parse_comma_list(contact_ids)
    extra = _task_extras(user_id=user_id, due_at=due_at, title=title)

    async with ctx.client() as client:
        result = await client.create_task(contact_ids=ids, note=note, type=type, priority=priority, **extra)

    output(result, ctx=ctx)


@tasks_app.command
async def connect(
    *,
    contact_id: Annotated[str, Parameter(name="--contact-id", help="Contact to send the request to")],
    note: Annotated[
        str | None,
        Parameter(name="--note", help="Text sent WITH the invitation. Omitted (default) = no message"),
    ] = None,
    user_id: Annotated[
        str | None,
        Parameter(name="--user-id", help="Task owner. Apollo rejects creation without a valid owner"),
    ] = None,
    due_at: Annotated[str | None, Parameter(name="--due-at", help=DUE_AT_HELP)] = None,
    title: Annotated[
        str | None, Parameter(name="--title", help="Task title shown in Apollo (internal, never sent)")
    ] = None,
    priority: Annotated[str, Parameter(name="--priority", help="Priority (high, medium, low)")] = "high",
) -> None:
    """Queue a LinkedIn connection request, by default without a message.

    On a linkedin_step_connect task the note travels with the invitation, so
    --note is omitted by default and anything you pass there is seen by the
    recipient. Put internal context in --title; the contact never sees it.
    """
    extra = _task_extras(user_id=user_id, due_at=due_at, title=title)

    async with ctx.client() as client:
        result = await client.create_task(
            contact_ids=[contact_id],
            note=note,
            type="linkedin_step_connect",
            priority=priority,
            **extra,
        )

    output(result, ctx=ctx)


@tasks_app.command
async def update(
    id: Annotated[str, Parameter(help="Task ID")],
    *,
    note: Annotated[str | None, Parameter(name="--note", help="Task description")] = None,
    due_at: Annotated[str | None, Parameter(name="--due-at", help=DUE_AT_HELP)] = None,
    status: Annotated[str | None, Parameter(name="--status", help="Task status (scheduled, complete, ...)")] = None,
    priority: Annotated[str | None, Parameter(name="--priority", help="Priority (high, medium, low)")] = None,
) -> None:
    """Update a task's fields."""
    fields: dict[str, str] = {}
    if note is not None:
        fields["note"] = note
    if due_at is not None:
        fields["due_at"] = parse_due_at(due_at)
    if status is not None:
        fields["status"] = status
    if priority is not None:
        fields["priority"] = priority

    async with ctx.client() as client:
        result = await client.update_task(id, **fields)

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
