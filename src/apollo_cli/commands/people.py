"""People database search command group."""

from __future__ import annotations

from typing import Annotated

from cyclopts import App, Parameter

from apollo_cli.context import ctx
from apollo_cli.output import output
from apollo_cli.util import parse_comma_list

people_app = App(name="people", help="People database search.")


@people_app.command
async def search(
    *,
    keywords: Annotated[str | None, Parameter(name="--keywords", help="Search keywords")] = None,
    titles: Annotated[str | None, Parameter(name="--titles", help="Comma-separated job titles")] = None,
    locations: Annotated[str | None, Parameter(name="--locations", help="Comma-separated locations")] = None,
) -> None:
    """Search Apollo's global people database."""
    filters: dict = {}
    if keywords:
        filters["q_keywords"] = keywords
    if titles:
        filters["person_titles"] = parse_comma_list(titles)
    if locations:
        filters["person_locations"] = parse_comma_list(locations)

    async with ctx.client() as client:
        result = await client.search_people(**filters)

    output(result, ctx=ctx)
