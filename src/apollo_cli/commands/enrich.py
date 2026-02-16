"""Enrichment command group."""

from __future__ import annotations

from typing import Annotated

from cyclopts import App, Parameter

from apollo_cli.context import ctx
from apollo_cli.output import output

enrich_app = App(name="enrich", help="Enrichment operations.")


@enrich_app.command
async def org(
    domain: Annotated[str, Parameter(help="Company domain (e.g. apollo.io)")],
) -> None:
    """Enrich organization data by domain (FREE)."""
    async with ctx.client() as client:
        result = await client.enrich_organization(domain)

    output(result, ctx=ctx)


@enrich_app.command
async def person(
    email: Annotated[str, Parameter(help="Person's email address")],
) -> None:
    """Enrich person data by email (costs 1 credit)."""
    async with ctx.client() as client:
        result = await client.enrich_person(email)

    output(result, ctx=ctx)
