"""Accounts command group."""

from __future__ import annotations

from typing import Annotated

from cyclopts import App, Parameter

from apollo_cli.context import ctx
from apollo_cli.formatters.accounts import format_account_detail, format_account_list
from apollo_cli.output import output, output_list

accounts_app = App(name="accounts", help="Manage accounts/companies.")


@accounts_app.command
async def search(
    *,
    query: Annotated[str, Parameter(name=["--query", "-q"], help="Search by organization name")] = "",
    stage_id: Annotated[str | None, Parameter(name="--stage-id", help="Filter by account stage ID")] = None,
) -> None:
    """Search accounts by keyword or filter."""
    filters: dict = {}
    if query:
        filters["q_organization_name"] = query
    if stage_id:
        filters["account_stage_ids"] = [stage_id]

    async with ctx.client() as client:
        result = await client.search_accounts(page=ctx.page, limit=ctx.limit, **filters)

    output_list(
        items=result.items,
        total=result.total,
        page=result.page,
        limit=ctx.limit,
        ctx=ctx,
        format_fn=format_account_list,
        resource_name="Accounts",
    )


@accounts_app.command
async def get(
    id: Annotated[str, Parameter(help="Account ID")],
) -> None:
    """Get account details by ID."""
    async with ctx.client() as client:
        account = await client.get_account(id)

    output(account, ctx=ctx, format_fn=format_account_detail)
