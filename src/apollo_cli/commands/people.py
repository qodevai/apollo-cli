"""People database search command group."""

from __future__ import annotations

from typing import Annotated

from cyclopts import App, Parameter

from apollo_cli.context import ctx
from apollo_cli.formatters.people import format_people_list
from apollo_cli.output import output_list
from apollo_cli.util import parse_comma_list

people_app = App(name="people", help="People database search.")


@people_app.command
async def search(
    *,
    keywords: Annotated[str | None, Parameter(name="--keywords", help="Search keywords")] = None,
    titles: Annotated[str | None, Parameter(name="--titles", help="Comma-separated job titles")] = None,
    seniorities: Annotated[
        str | None,
        Parameter(name="--seniorities", help="Comma-separated seniorities (e.g. owner,vp,director,manager)"),
    ] = None,
    locations: Annotated[str | None, Parameter(name="--locations", help="Comma-separated person locations")] = None,
    organization_domains: Annotated[
        str | None,
        Parameter(
            name=["--organization-domains", "--domains"],
            help="Comma-separated company domains — find people at these companies (e.g. acme.com,globex.com)",
        ),
    ] = None,
) -> None:
    """Search Apollo's global people database.

    Respects the global ``--limit`` / ``--page`` options for pagination.
    """
    filters: dict = {"page": ctx.page, "per_page": ctx.limit}
    if keywords:
        filters["q_keywords"] = keywords
    if titles:
        filters["person_titles"] = parse_comma_list(titles)
    if seniorities:
        filters["person_seniorities"] = parse_comma_list(seniorities)
    if locations:
        filters["person_locations"] = parse_comma_list(locations)
    if organization_domains:
        filters["q_organization_domains_list"] = parse_comma_list(organization_domains)

    async with ctx.client() as client:
        result = await client.search_people(**filters)

    # search_people returns the raw Apollo dict. Results live under "people"; matched
    # CRM records come back under "contacts". Merge both so we never silently drop half.
    items = [*(result.get("people") or []), *(result.get("contacts") or [])]
    pagination = result.get("pagination", {})
    total = pagination.get("total_entries", len(items))

    output_list(
        items=items,
        total=total,
        page=ctx.page,
        limit=ctx.limit,
        ctx=ctx,
        format_fn=format_people_list,
        resource_name="People",
    )
