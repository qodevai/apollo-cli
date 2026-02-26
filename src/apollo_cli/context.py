"""Global context shared across all commands."""

from __future__ import annotations

from dataclasses import dataclass

from qodev_apollo_api import ApolloClient


@dataclass
class Context:
    """Shared state passed from the meta launcher to every command."""

    json_mode: bool = False
    api_key: str | None = None
    limit: int = 25
    page: int = 1

    def client(self) -> ApolloClient:
        """Create a new ApolloClient with the configured API key."""
        kwargs: dict = {}
        if self.api_key:
            kwargs["api_key"] = self.api_key
        return ApolloClient(**kwargs)

    def configure(self, *, json_mode: bool, api_key: str | None, limit: int, page: int) -> None:
        """Update context fields in place (preserves references held by command modules)."""
        self.json_mode = json_mode
        self.api_key = api_key
        self.limit = limit
        self.page = page


# Module-level singleton — updated in place by the meta launcher.
ctx = Context()
