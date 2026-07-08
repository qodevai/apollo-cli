"""Conversations command group."""

from __future__ import annotations

from typing import Annotated

from cyclopts import App, Parameter

from apollo_cli.context import ctx
from apollo_cli.formatters.conversations import format_conversation_detail, format_conversation_list
from apollo_cli.output import output, output_list

conversations_app = App(name="conversations", help="Recorded conversations (Zoom/Teams/Meet).")


@conversations_app.command
async def search(
    *,
    query: Annotated[str, Parameter(name=["--query", "-q"], help="Search keyword (topic/title)")] = "",
) -> None:
    """Search recorded conversations."""
    filters: dict = {}
    if query:
        filters["q_keywords"] = query

    async with ctx.client() as client:
        result = await client.search_conversations(page=ctx.page, limit=ctx.limit, **filters)

    output_list(
        items=result.items,
        total=result.total,
        page=result.page,
        limit=ctx.limit,
        ctx=ctx,
        format_fn=format_conversation_list,
        resource_name="Conversations",
    )


@conversations_app.command
async def get(
    id: Annotated[str, Parameter(help="Conversation ID")],
) -> None:
    """Get conversation details by ID (includes transcript and AI summary)."""
    async with ctx.client() as client:
        conversation = await client.get_conversation(id)

    output(conversation, ctx=ctx, format_fn=format_conversation_detail)
