"""Pipelines and stages command groups."""

from __future__ import annotations

from typing import Annotated

from cyclopts import App, Parameter

from apollo_cli.context import ctx
from apollo_cli.formatters.generic import detail_table, list_table
from apollo_cli.output import output, output_list

pipelines_app = App(name="pipelines", help="Pipeline management.")
stages_app = App(name="stages", help="Stage management.")

PIPELINE_LIST_COLUMNS = [
    ("ID", "id"),
    ("Title", "title"),
    ("Default", "default_pipeline"),
    ("Order", "display_order"),
]

PIPELINE_DETAIL_FIELDS = [
    ("ID", "id"),
    ("Title", "title"),
    ("Default", "default_pipeline"),
    ("Display Order", "display_order"),
    ("Source", "source"),
]

STAGE_LIST_COLUMNS = [
    ("ID", "id"),
    ("Name", "name"),
    ("Pipeline ID", "opportunity_pipeline_id"),
    ("Order", "display_order"),
    ("Probability", "probability"),
    ("Type", "type"),
]


@pipelines_app.command(name="list")
async def list_pipelines() -> None:
    """List all pipelines."""
    async with ctx.client() as client:
        result = await client.list_pipelines(page=ctx.page, limit=ctx.limit)

    output_list(
        items=result.items,
        total=result.total,
        page=result.page,
        limit=ctx.limit,
        ctx=ctx,
        format_fn=lambda items, **kw: list_table(items, PIPELINE_LIST_COLUMNS, title="Pipelines", **kw),
        resource_name="Pipelines",
    )


@pipelines_app.command
async def get(
    id: Annotated[str, Parameter(help="Pipeline ID")],
) -> None:
    """Get pipeline details by ID."""
    async with ctx.client() as client:
        pipeline = await client.get_pipeline(id)

    output(
        pipeline,
        ctx=ctx,
        format_fn=lambda d: detail_table(d, PIPELINE_DETAIL_FIELDS, title=f"Pipeline: {d.title or d.id}"),
    )


@pipelines_app.command(name="stages")
async def pipeline_stages(
    pipeline_id: Annotated[str, Parameter(help="Pipeline ID")],
) -> None:
    """List stages for a specific pipeline."""
    async with ctx.client() as client:
        result = await client.list_pipeline_stages(pipeline_id, page=ctx.page, limit=ctx.limit)

    output_list(
        items=result.items,
        total=result.total,
        page=result.page,
        limit=ctx.limit,
        ctx=ctx,
        format_fn=lambda items, **kw: list_table(items, STAGE_LIST_COLUMNS, title="Pipeline Stages", **kw),
        resource_name="Stages",
    )


@stages_app.command(name="list")
async def list_all_stages() -> None:
    """List all stages across all pipelines."""
    async with ctx.client() as client:
        result = await client.list_all_stages()

    output_list(
        items=result.items,
        total=result.total,
        page=result.page,
        limit=ctx.limit,
        ctx=ctx,
        format_fn=lambda items, **kw: list_table(items, STAGE_LIST_COLUMNS, title="All Stages", **kw),
        resource_name="Stages",
    )
