"""Tests for context management."""

from __future__ import annotations

from unittest.mock import patch

import apollo_cli.context as _ctx
from apollo_cli.context import Context


class TestContext:
    def test_context_initialization(self) -> None:
        """Test default context initialization."""
        ctx = Context()
        assert ctx.json_mode is False
        assert ctx.api_key is None
        assert ctx.limit == 25
        assert ctx.page == 1

    def test_context_initialization_with_values(self) -> None:
        """Test context initialization with values."""
        ctx = Context(json_mode=True, api_key="test-key", limit=50, page=2)
        assert ctx.json_mode is True
        assert ctx.api_key == "test-key"
        assert ctx.limit == 50
        assert ctx.page == 2

    def test_context_configure_in_place(self) -> None:
        """Test that configure updates context in place."""
        ctx = Context()
        original_id = id(ctx)

        ctx.configure(json_mode=True, api_key="new-key", limit=10, page=3)

        assert id(ctx) == original_id  # Same object
        assert ctx.json_mode is True
        assert ctx.api_key == "new-key"
        assert ctx.limit == 10
        assert ctx.page == 3

    def test_context_client_with_api_key(self) -> None:
        """Test client creation with explicit API key."""
        ctx = Context(api_key="test-key-123")
        with patch("apollo_cli.context.ApolloClient") as mock_client_class:
            ctx.client()
            mock_client_class.assert_called_once_with(api_key="test-key-123")

    def test_context_client_without_api_key(self) -> None:
        """Test client creation without explicit API key (uses env var)."""
        ctx = Context()
        with patch("apollo_cli.context.ApolloClient") as mock_client_class:
            ctx.client()
            mock_client_class.assert_called_once_with()

    def test_global_context_singleton(self) -> None:
        """Test that module-level ctx is a singleton."""
        assert isinstance(_ctx.ctx, Context)

        original_id = id(_ctx.ctx)
        _ctx.ctx.configure(json_mode=True, api_key="test", limit=10, page=1)

        # Still same object after configure
        assert id(_ctx.ctx) == original_id

    def test_context_client_with_env_var(self, monkeypatch) -> None:
        """Test that client respects APOLLO_API_KEY env var."""
        monkeypatch.setenv("APOLLO_API_KEY", "env-key-123")

        ctx = Context()  # No explicit api_key
        with patch("apollo_cli.context.ApolloClient") as mock_client_class:
            ctx.client()
            # When no api_key is provided, ApolloClient will read from env
            mock_client_class.assert_called_once_with()
