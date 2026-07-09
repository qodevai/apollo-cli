"""Deals command group."""

from __future__ import annotations

from typing import Annotated, Any, cast

from cyclopts import App, Parameter
from qodev_apollo_api import RoleAssignment

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


@deals_app.command
async def create(
    *,
    name: Annotated[str, Parameter(name="--name", help="Deal name (required)")],
    owner_id: Annotated[str | None, Parameter(name="--owner-id", help="Deal owner (team member) ID")] = None,
    account_id: Annotated[str | None, Parameter(name="--account-id", help="Target account/company ID")] = None,
    amount: Annotated[float | None, Parameter(name="--amount", help="Deal value (no currency symbol)")] = None,
    stage_id: Annotated[str | None, Parameter(name="--stage-id", help="Deal stage ID")] = None,
    stage_name: Annotated[
        str | None,
        Parameter(name="--stage-name", help="Deal stage name (resolved to an ID; avoids a `pipelines stages` lookup)"),
    ] = None,
    closed_date: Annotated[str | None, Parameter(name="--closed-date", help="Expected close date (YYYY-MM-DD)")] = None,
) -> None:
    """Create a new deal/opportunity.

    Requires a master Apollo API key (non-master keys get a 403). ``--name`` is the
    only required field. Use ``--stage-name`` to set the stage by name instead of ID.
    """
    if stage_id and stage_name:
        error("Pass either --stage-id or --stage-name, not both.", ctx=ctx, code="conflicting_args", exit_code=2)
        return

    fields: dict[str, Any] = {}
    if owner_id:
        fields["owner_id"] = owner_id
    if account_id:
        fields["account_id"] = account_id
    if amount is not None:
        fields["amount"] = amount
    if closed_date:
        fields["closed_date"] = closed_date

    async with ctx.client() as client:
        if stage_name:
            all_stages = await client.list_all_stages()
            stage_id = resolve_stage_id(stage_name, all_stages.items, kind="deal stage")
        if stage_id:
            fields["opportunity_stage_id"] = stage_id
        deal = await client.create_deal(name, **fields)

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
    """Flatten a deal's current opportunity_contact_roles into update_roles entries.

    ``opportunity_contact_role_type_id`` is only included when the existing role
    actually has one — we never send an explicit ``null`` (see ``_clean_roles``).
    """
    roles: list[dict] = []
    for r in getattr(deal, "opportunity_contact_roles", []) or []:
        entry: dict = {"contact_id": r.contact_id, "is_primary": bool(r.is_primary)}
        if r.role and r.role[0].opportunity_contact_role_type_id:
            entry["opportunity_contact_role_type_id"] = r.role[0].opportunity_contact_role_type_id
        roles.append(entry)
    return roles


def _clean_roles(roles: list[dict]) -> list[dict]:
    """Drop any ``opportunity_contact_role_type_id`` that is ``None`` so we never POST an
    explicit null (Apollo may reject roles without a role type — omit the key instead)."""
    for r in roles:
        if r.get("opportunity_contact_role_type_id") is None:
            r.pop("opportunity_contact_role_type_id", None)
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
            entry = {"contact_id": contact_id, "is_primary": False}
            roles.append(entry)
        if role_type_id is not None:
            entry["opportunity_contact_role_type_id"] = role_type_id
        if primary:
            for r in roles:
                r["is_primary"] = r["contact_id"] == contact_id

        # Entries are built dynamically (conditional keys, pop), so they're plain dicts;
        # cast to the client's RoleAssignment TypedDict at the boundary.
        updated = await client.update_opportunity_roles(id, cast("list[RoleAssignment]", _clean_roles(roles)))

    output(updated, ctx=ctx, format_fn=format_deal_detail)
