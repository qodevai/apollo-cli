"""Contacts command group."""

from __future__ import annotations

from typing import Annotated, Any

from cyclopts import App, Parameter

from apollo_cli.context import ctx
from apollo_cli.formatters.contacts import (
    format_contact_detail,
    format_contact_list,
    format_stages_list,
)
from apollo_cli.linkedin import apollo_canonical_linkedin_url
from apollo_cli.output import error, output, output_list
from apollo_cli.util import parse_comma_list, resolve_stage_id

contacts_app = App(name="contacts", help="Manage contacts.")


@contacts_app.command
async def search(
    *,
    query: Annotated[str, Parameter(name=["--query", "-q"], help="Search keyword")] = "",
    stage_id: Annotated[str | None, Parameter(name="--stage-id", help="Filter by stage ID")] = None,
    stage_name: Annotated[
        str | None,
        Parameter(
            name="--stage-name", help="Filter by stage name (resolved to an ID; avoids a `contacts stages` lookup)"
        ),
    ] = None,
    linkedin_url: Annotated[str | None, Parameter(name="--linkedin-url", help="Filter by LinkedIn URL")] = None,
) -> None:
    """Search contacts by keyword or filter."""
    filters: dict = {}
    if query:
        filters["q_keywords"] = query
    if stage_id:
        filters["contact_stage_ids"] = [stage_id]
    if linkedin_url:
        # Apollo exact-matches its stored http://www.linkedin.com/in/<slug> form, so
        # canonicalize or the filter silently returns nothing.
        filters["linkedin_url"] = apollo_canonical_linkedin_url(linkedin_url)

    async with ctx.client() as client:
        if stage_name:
            stages_ = await client.get_contact_stages()
            filters.setdefault("contact_stage_ids", []).append(
                resolve_stage_id(stage_name, stages_, kind="contact stage")
            )
        result = await client.search_contacts(page=ctx.page, limit=ctx.limit, **filters)

    output_list(
        items=result.items,
        total=result.total,
        page=result.page,
        limit=ctx.limit,
        ctx=ctx,
        format_fn=format_contact_list,
        resource_name="Contacts",
    )


@contacts_app.command
async def get(
    id: Annotated[str, Parameter(help="Contact ID")],
) -> None:
    """Get contact details by ID."""
    async with ctx.client() as client:
        contact = await client.get_contact(id)

    output(contact, ctx=ctx, format_fn=format_contact_detail)


@contacts_app.command
async def create(
    *,
    first_name: Annotated[str, Parameter(name="--first-name", help="First name")],
    last_name: Annotated[str, Parameter(name="--last-name", help="Last name")],
    email: Annotated[str | None, Parameter(name="--email", help="Email address")] = None,
    title: Annotated[str | None, Parameter(name="--title", help="Job title")] = None,
    company: Annotated[str | None, Parameter(name="--company", help="Company name")] = None,
    linkedin_url: Annotated[str | None, Parameter(name="--linkedin-url", help="LinkedIn URL")] = None,
) -> None:
    """Create a new contact."""
    fields: dict = {}
    if email:
        fields["email"] = email
    if title:
        fields["title"] = title
    if company:
        fields["company_name"] = company
    if linkedin_url:
        fields["linkedin_url"] = linkedin_url

    async with ctx.client() as client:
        result = await client.create_contact(first_name, last_name, **fields)

    output(result, ctx=ctx)


@contacts_app.command
async def update(
    id: Annotated[str, Parameter(help="Contact ID")],
    *,
    title: Annotated[str | None, Parameter(name="--title", help="New job title")] = None,
    label_ids: Annotated[str | None, Parameter(name="--label-ids", help="Comma-separated label IDs")] = None,
) -> None:
    """Update a contact's fields."""
    fields: dict = {}
    if title:
        fields["title"] = title
    if label_ids:
        fields["label_ids"] = parse_comma_list(label_ids)

    async with ctx.client() as client:
        result = await client.update_contact(id, **fields)

    output(result, ctx=ctx, format_fn=format_contact_detail)


def _format_upsert_result(data: dict[str, Any]) -> str:
    status = "Created new contact" if data["created"] else "Found existing contact"
    return f"**{status}**\n\n{format_contact_detail(data['contact'])}"


@contacts_app.command(name="upsert-by-linkedin")
async def upsert_by_linkedin(
    url: Annotated[str, Parameter(help="LinkedIn profile URL")],
    *,
    name: Annotated[
        str | None,
        Parameter(name="--name", help="Full name 'First Last' — required to create the contact if it doesn't exist"),
    ] = None,
    title: Annotated[str | None, Parameter(name="--title", help="Job title (used only when creating)")] = None,
    company: Annotated[str | None, Parameter(name="--company", help="Company name (used only when creating)")] = None,
    stage_id: Annotated[str | None, Parameter(name="--stage-id", help="Stage ID (used only when creating)")] = None,
) -> None:
    """Get or create a contact by LinkedIn URL (upsert).

    Resolves the URL to an existing contact and returns it, or — if none exists —
    creates one (requires ``--name``) and returns it. The result carries a ``created``
    flag. For a read-only lookup that never writes, use ``contacts search --linkedin-url``.
    """
    canonical = apollo_canonical_linkedin_url(url)
    async with ctx.client() as client:
        # 1. Exact-match lookup on Apollo's canonical URL.
        result = await client.search_contacts(linkedin_url=canonical, limit=1)
        existing = result.items[0] if result.items else None

        # 2. Name fallback — catch a contact stored under a drifted/numeric URL so we
        #    don't create a duplicate; accept only an exact canonical-URL identity match.
        #    First match wins: upsert just needs to know one exists (unlike the old client,
        #    we intentionally don't treat >1 match as ambiguous).
        if existing is None and name:
            by_name = await client.search_contacts(q_keywords=name, limit=10)
            existing = next(
                (
                    c
                    for c in by_name.items
                    if c.linkedin_url and apollo_canonical_linkedin_url(c.linkedin_url) == canonical
                ),
                None,
            )

        if existing is not None:
            output({"created": False, "contact": existing}, ctx=ctx, format_fn=_format_upsert_result)
            return

        # 3. Create — Apollo needs both a first and a last name.
        first, _, last = name.strip().partition(" ") if name else ("", "", "")
        if not (first and last):
            error(
                'No contact for that LinkedIn URL. Pass --name "First Last" to create one.',
                ctx=ctx,
                code="name_required",
                exit_code=2,
            )
            return
        fields: dict = {"linkedin_url": canonical}
        if title:
            fields["title"] = title
        if company:
            fields["company_name"] = company
        if stage_id:
            fields["contact_stage_id"] = stage_id
        created = await client.create_contact(first, last, **fields)

    output({"created": True, "contact": created}, ctx=ctx, format_fn=_format_upsert_result)


@contacts_app.command
async def stages() -> None:
    """List contact pipeline stages."""
    async with ctx.client() as client:
        result = await client.get_contact_stages()

    if ctx.json_mode:
        from apollo_cli.output import output_json

        output_json(result)
    else:
        from apollo_cli.output import output_markdown

        md = format_stages_list(result, total=len(result), page=1)
        output_markdown(md)
