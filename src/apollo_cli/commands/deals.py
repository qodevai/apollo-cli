"""Deals command group."""

from __future__ import annotations

from typing import Annotated

from cyclopts import App, Parameter

from apollo_cli.context import ctx
from apollo_cli.formatters.deals import format_deal_detail, format_deal_list
from apollo_cli.output import output, output_list

deals_app = App(name="deals", help="Manage deals/opportunities.")


@deals_app.command
async def search(
    *,
    query: Annotated[str, Parameter(name=["--query", "-q"], help="Search keyword")] = "",
    stage_id: Annotated[str | None, Parameter(name="--stage-id", help="Filter by deal stage ID")] = None,
) -> None:
    """Search deals by keyword or filter."""
    filters: dict = {}
    if query:
        filters["q_keywords"] = query
    if stage_id:
        filters["opportunity_stage_ids"] = [stage_id]

    async with ctx.client() as client:
        result = await client.search_deals(page=ctx.page, limit=ctx.limit, **filters)

    output_list(
        items=result.items,
        total=result.total,
        page=result.page,
        limit=ctx.limit,
        ctx=ctx,
        format_fn=format_deal_list,
        resource_name="Deals",
    )


@deals_app.command
async def get(
    id: Annotated[str, Parameter(help="Deal ID")],
) -> None:
    """Get deal details by ID."""
    async with ctx.client() as client:
        deal = await client.get_deal(id)

    output(deal, ctx=ctx, format_fn=format_deal_detail)
