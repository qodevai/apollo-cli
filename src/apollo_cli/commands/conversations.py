"""Conversations command group."""

from __future__ import annotations

from typing import Annotated

from cyclopts import App, Parameter

from apollo_cli.context import ctx
from apollo_cli.formatters.conversations import (
    format_conversation_detail,
    format_conversation_list,
    format_transcript,
)
from apollo_cli.output import output, output_json, output_list, output_markdown

conversations_app = App(name="conversations", help="Recorded conversations (Zoom/Teams/Meet).")


@conversations_app.command
async def search(
    *,
    query: Annotated[str, Parameter(name=["--query", "-q"], help="Search keyword (topic/title)")] = "",
) -> None:
    """Search recorded conversations."""
    filters: dict = {}
    if query:
        # `q_keywords` is Apollo's universal keyword-search param (contacts/accounts/deals/
        # people all use it). The conversations/search endpoint is undocumented and we
        # haven't confirmed it honours the filter server-side — if a search returns
        # everything unfiltered, this is the param to revisit.
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


@conversations_app.command
async def transcript(
    id: Annotated[str, Parameter(help="Conversation ID")],
) -> None:
    """Print just the transcript of a conversation (no metadata or summary)."""
    async with ctx.client() as client:
        conversation = await client.get_conversation(id)

    segments = getattr(conversation, "transcript", None) or []
    if ctx.json_mode:
        output_json(segments)
    else:
        output_markdown(format_transcript(conversation))
