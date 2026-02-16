"""Contacts command group."""

from __future__ import annotations

from typing import Annotated

from cyclopts import App, Parameter

from apollo_cli.context import ctx
from apollo_cli.formatters.contacts import (
    format_contact_detail,
    format_contact_list,
    format_stages_list,
)
from apollo_cli.output import output, output_list

contacts_app = App(name="contacts", help="Manage contacts.")


@contacts_app.command
async def search(
    *,
    query: Annotated[str, Parameter(name=["--query", "-q"], help="Search keyword")] = "",
    stage_id: Annotated[str | None, Parameter(name="--stage-id", help="Filter by stage ID")] = None,
    linkedin_url: Annotated[str | None, Parameter(name="--linkedin-url", help="Filter by LinkedIn URL")] = None,
) -> None:
    """Search contacts by keyword or filter."""
    filters: dict = {}
    if query:
        filters["q_keywords"] = query
    if stage_id:
        filters["contact_stage_ids"] = [stage_id]
    if linkedin_url:
        filters["linkedin_url"] = linkedin_url

    async with ctx.client() as client:
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
        fields["label_ids"] = [lid.strip() for lid in label_ids.split(",")]

    async with ctx.client() as client:
        result = await client.update_contact(id, **fields)

    output(result, ctx=ctx, format_fn=format_contact_detail)


@contacts_app.command(name="find-by-linkedin")
async def find_by_linkedin(
    url: Annotated[str, Parameter(help="LinkedIn profile URL")],
    *,
    name: Annotated[str | None, Parameter(name="--name", help="Person's full name (for fallback search)")] = None,
    create_flag: Annotated[bool, Parameter(name="--create", help="Auto-create if not found", negative="")] = False,
    stage_id: Annotated[str | None, Parameter(name="--stage-id", help="Stage ID for auto-created contact")] = None,
) -> None:
    """Find a contact by LinkedIn URL with fallback strategies."""
    async with ctx.client() as client:
        contact_id = await client.find_contact_by_linkedin_url(
            linkedin_url=url,
            person_name=name,
            create_if_missing=create_flag,
            contact_stage_id=stage_id,
        )

    if contact_id:
        output({"contact_id": contact_id}, ctx=ctx)
    else:
        from apollo_cli.output import error

        error("Contact not found.", ctx=ctx, code="not_found", exit_code=1)


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
