"""Root App definition, global options, and error handling."""

from __future__ import annotations

import sys
from typing import Annotated

from cyclopts import App, Group, Parameter
from qodev_apollo_api import APIError, AuthenticationError, RateLimitError

import apollo_cli.context as _ctx

app = App(
    name="apollo",
    help="Agent-friendly CLI for the Apollo API.",
    help_format="rich",
    version_flags=[],
)

app.meta.group_parameters = Group("Global Options", sort_key=0)


# ---------------------------------------------------------------------------
# Import and register command groups
# ---------------------------------------------------------------------------
from apollo_cli.commands.accounts import accounts_app  # noqa: E402
from apollo_cli.commands.calls import calls_app  # noqa: E402
from apollo_cli.commands.contacts import contacts_app  # noqa: E402
from apollo_cli.commands.deals import deals_app  # noqa: E402
from apollo_cli.commands.emails import emails_app  # noqa: E402
from apollo_cli.commands.enrich import enrich_app  # noqa: E402
from apollo_cli.commands.install import install_app  # noqa: E402
from apollo_cli.commands.jobs import jobs_app  # noqa: E402
from apollo_cli.commands.news import news_app  # noqa: E402
from apollo_cli.commands.notes import notes_app  # noqa: E402
from apollo_cli.commands.people import people_app  # noqa: E402
from apollo_cli.commands.pipelines import pipelines_app, stages_app  # noqa: E402
from apollo_cli.commands.tasks import tasks_app  # noqa: E402
from apollo_cli.commands.usage import usage_app  # noqa: E402

# Register all sub-apps
_sub_apps = [
    contacts_app,
    accounts_app,
    deals_app,
    pipelines_app,
    stages_app,
    enrich_app,
    people_app,
    notes_app,
    tasks_app,
    calls_app,
    emails_app,
    news_app,
    jobs_app,
    usage_app,
    install_app,
]

for sub in _sub_apps:
    app.command(sub)
    sub.help_epilogue = ""  # Prevent epilogue propagation

# Build dynamic help epilogue
from apollo_cli.help_reference import build_command_reference  # noqa: E402

app.help_epilogue = build_command_reference(_sub_apps)


# ---------------------------------------------------------------------------
# Meta launcher — global options & error handling
# ---------------------------------------------------------------------------

EXIT_AUTH = 80
EXIT_RATE_LIMIT = 81
EXIT_API = 82
EXIT_VALIDATION = 83


@app.meta.default
def launcher(
    *tokens: Annotated[str, Parameter(show=False, allow_leading_hyphen=True)],
    json: Annotated[bool, Parameter(name="--json", help="Output as JSON", negative="")] = False,
    api_key: Annotated[
        str | None, Parameter(name="--api-key", help="Apollo API key (overrides APOLLO_API_KEY)", show=False)
    ] = None,
    limit: Annotated[int, Parameter(name="--limit", help="Results per page")] = 25,
    page: Annotated[int, Parameter(name="--page", help="Page number")] = 1,
) -> None:
    """Apollo CLI — search contacts, accounts, deals, and more."""
    # Configure the global context singleton before dispatching to subcommands.
    _ctx.ctx.configure(json_mode=json, api_key=api_key, limit=limit, page=page)

    try:
        app(tokens)
    except AuthenticationError as exc:
        _handle_error(str(exc), code="authentication", exit_code=EXIT_AUTH)
    except RateLimitError as exc:
        msg = str(exc)
        if exc.retry_after:
            msg += f" (retry after {exc.retry_after}s)"
        _handle_error(msg, code="rate_limit", exit_code=EXIT_RATE_LIMIT)
    except APIError as exc:
        _handle_error(str(exc), code="api_error", exit_code=EXIT_API)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:
        _handle_error(f"Unexpected error: {exc}", code="unknown", exit_code=1)


def _handle_error(message: str, *, code: str, exit_code: int) -> None:
    from apollo_cli.output import error

    error(message, ctx=_ctx.ctx, code=code, exit_code=exit_code)


def main() -> None:
    app.meta()
