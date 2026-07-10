"""Jobs command group."""

from __future__ import annotations

from typing import Annotated

from cyclopts import App, Parameter

from apollo_cli.context import ctx
from apollo_cli.formatters.generic import list_table
from apollo_cli.output import output_json, output_markdown

jobs_app = App(name="jobs", help="Job postings.")

JOBS_LIST_COLUMNS = [
    ("Title", "title"),
    ("City", "city"),
    ("State", "state"),
    ("URL", "url"),
    ("Posted", "posted_at"),
]


@jobs_app.command(name="list")
async def list_jobs(
    account_id: Annotated[str, Parameter(help="Account ID")],
) -> None:
    """List job postings for an account."""
    async with ctx.client() as client:
        result = await client.list_account_jobs(account_id)

    if ctx.json_mode:
        output_json(result)
    else:
        md = list_table(result, JOBS_LIST_COLUMNS, title="Job Postings", total=len(result), page=1)
        output_markdown(md)
