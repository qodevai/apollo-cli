"""News command group."""

from __future__ import annotations

from typing import Annotated

from cyclopts import App, Parameter

from apollo_cli.context import ctx
from apollo_cli.formatters.generic import list_table
from apollo_cli.output import output_json, output_markdown

news_app = App(name="news", help="Account news.")

NEWS_LIST_COLUMNS = [
    ("Title", "title"),
    ("Category", "category"),
    ("Published", "published_at"),
    ("URL", "url"),
]


@news_app.command(name="list")
async def list_news(
    account_id: Annotated[str, Parameter(help="Account ID")],
) -> None:
    """List news articles for an account."""
    async with ctx.client() as client:
        result = await client.list_account_news(account_id)

    if ctx.json_mode:
        output_json(result)
    else:
        md = list_table(result, NEWS_LIST_COLUMNS, title="Account News", total=len(result), page=1)
        output_markdown(md)
