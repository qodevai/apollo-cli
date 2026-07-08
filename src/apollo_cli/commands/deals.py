"""Deals command group."""

from __future__ import annotations

from typing import Annotated, Any

from cyclopts import App, Parameter

from apollo_cli.context import ctx
from apollo_cli.formatters.deals import format_deal_detail, format_deal_list
from apollo_cli.formatters.generic import list_table
from apollo_cli.output import error, output, output_list
from apollo_cli.util import resolve_stage_id

deals_app = App(name="deals", help="Manage deals/opportunities.")


@deals_app.command
async def search(
    *,
    query: Annotated[str, Parameter(name=["--query", "-q"], help="Search keyword")] = "",
    stage_id: Annotated[str | None, Parameter(name="--stage-id", help="Filter by deal stage ID")] = None,
    stage_name: Annotated[
        str | None,
        Parameter(
            name="--stage-name", help="Filter by stage name (resolved to an ID; avoids a `pipelines stages` lookup)"
        ),
    ] = None,
) -> None:
    """Search deals by keyword or filter."""
    filters: dict = {}
    if query:
        filters["q_keywords"] = query
    stage_ids: list[str] = []
    if stage_id:
        stage_ids.append(stage_id)

    async with ctx.client() as client:
        if stage_name:
            all_stages = await client.list_all_stages()
            stage_ids.append(resolve_stage_id(stage_name, all_stages.items, kind="deal stage"))
        if stage_ids:
            filters["opportunity_stage_ids"] = stage_ids
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


ROLE_TYPE_COLUMNS = [("ID", "id"), ("Name", "name"), ("Display Order", "display_order")]


@deals_app.command(name="role-types")
async def role_types() -> None:
    """List the available opportunity contact role types (e.g. Decision Maker, Champion)."""
    async with ctx.client() as client:
        result = await client.list_opportunity_contact_role_types()

    output_list(
        items=result.items,
        total=result.total,
        page=1,
        limit=len(result.items) or 1,
        ctx=ctx,
        format_fn=lambda items, **kw: list_table(items, ROLE_TYPE_COLUMNS, title="Role Types", **kw),
        resource_name="Role Types",
    )


def _existing_roles(deal: Any) -> list[dict]:
    """Flatten a deal's current opportunity_contact_roles into update_roles entries."""
    roles: list[dict] = []
    for r in getattr(deal, "opportunity_contact_roles", []) or []:
        role_type_id = None
        if r.role:
            role_type_id = r.role[0].opportunity_contact_role_type_id
        roles.append(
            {
                "contact_id": r.contact_id,
                "opportunity_contact_role_type_id": role_type_id,
                "is_primary": bool(r.is_primary),
            }
        )
    return roles


@deals_app.command(name="set-role")
async def set_role(
    id: Annotated[str, Parameter(help="Deal ID")],
    *,
    contact_id: Annotated[str, Parameter(name="--contact-id", help="Contact ID to add/update on the deal")],
    role_type: Annotated[
        str | None,
        Parameter(name="--role-type", help="Role type ID or name (e.g. 'Decision Maker'); resolved to an ID"),
    ] = None,
    primary: Annotated[
        bool,
        Parameter(name="--primary", help="Mark this contact as the primary contact (unsets any other primary)"),
    ] = False,
) -> None:
    """Set or update a contact's role on a deal.

    Reads the deal's current contact roles, applies the change, and writes the full
    set back (Apollo's update_roles replaces all roles). Add ``--primary`` to make
    this contact the single primary contact.
    """
    async with ctx.client() as client:
        deal = await client.get_deal(id)
        roles = _existing_roles(deal)

        role_type_id: str | None = None
        if role_type:
            role_type_id = role_type
            # Resolve a human name to an ID when it isn't already an ID.
            rt_result = await client.list_opportunity_contact_role_types()
            names = {rt.name.lower(): rt.id for rt in rt_result.items if rt.name}
            ids = {rt.id for rt in rt_result.items}
            if role_type not in ids:
                resolved = names.get(role_type.lower())
                if resolved is None:
                    error(
                        f"No role type {role_type!r}. Available: "
                        + ", ".join(sorted(rt.name for rt in rt_result.items if rt.name)),
                        ctx=ctx,
                        code="unknown_role_type",
                        exit_code=2,
                    )
                    return
                role_type_id = resolved

        entry = next((r for r in roles if r["contact_id"] == contact_id), None)
        if entry is None:
            entry = {"contact_id": contact_id, "opportunity_contact_role_type_id": None, "is_primary": False}
            roles.append(entry)
        if role_type_id is not None:
            entry["opportunity_contact_role_type_id"] = role_type_id
        if primary:
            for r in roles:
                r["is_primary"] = r["contact_id"] == contact_id

        updated = await client.update_opportunity_roles(id, roles)

    output(updated, ctx=ctx, format_fn=format_deal_detail)
