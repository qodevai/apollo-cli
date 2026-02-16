"""Usage stats command."""

from __future__ import annotations

from cyclopts import App

from apollo_cli.context import ctx
from apollo_cli.output import output_json, output_markdown

usage_app = App(name="usage", help="API usage statistics.")


@usage_app.default
async def usage() -> None:
    """Show API usage statistics and rate limits."""
    async with ctx.client() as client:
        data = await client.get_api_usage()
        rate = client.rate_limit_status

    if ctx.json_mode:
        output_json({"usage": data, "rate_limits": rate})
    else:
        md = _format_usage(data, rate)
        output_markdown(md)


def _format_usage(data: dict, rate: dict) -> str:
    lines = ["# API Usage"]

    if rate:
        lines.append("")
        lines.append("## Rate Limits")
        lines.append("")
        lines.append("| Window | Limit | Remaining |")
        lines.append("|--------|-------|-----------|")
        if "hourly_limit" in rate:
            lines.append(f"| Hourly | {rate.get('hourly_limit', '?')} | {rate.get('hourly_left', '?')} |")
        if "minute_limit" in rate:
            lines.append(f"| Minute | {rate.get('minute_limit', '?')} | {rate.get('minute_left', '?')} |")
        if "daily_limit" in rate:
            lines.append(f"| Daily | {rate.get('daily_limit', '?')} | {rate.get('daily_left', '?')} |")

    if data:
        lines.append("")
        lines.append("## Endpoint Usage")
        lines.append("")
        lines.append("| Endpoint | Day Consumed | Day Left | Hour Consumed | Hour Left |")
        lines.append("|----------|-------------|----------|--------------|-----------|")
        for endpoint, stats in data.items():
            day_consumed = stats.get("day", {}).get("consumed", "?")
            day_left = stats.get("day", {}).get("left_over", "?")
            hour_consumed = stats.get("hour", {}).get("consumed", "?")
            hour_left = stats.get("hour", {}).get("left_over", "?")
            lines.append(f"| {endpoint} | {day_consumed} | {day_left} | {hour_consumed} | {hour_left} |")

    return "\n".join(lines)
