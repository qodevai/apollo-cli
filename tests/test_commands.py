"""Tests for CLI commands."""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import apollo_cli.context as _ctx


class MockAsyncContextManager:
    """Mock async context manager for client()."""

    def __init__(self, mock_client: MagicMock):
        self.mock_client = mock_client

    async def __aenter__(self):
        return self.mock_client

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class MockSearchResult:
    """Mock search result with pagination."""

    def __init__(self, items: list[Any], total: int, page: int):
        self.items = items
        self.total = total
        self.page = page


class TestContactsCommands:
    @pytest.mark.asyncio
    async def test_contacts_search_json(self, sample_contact: dict, capsys) -> None:
        """Test contacts search in JSON mode."""
        mock_client = MagicMock()
        mock_client.search_contacts = AsyncMock(return_value=MockSearchResult(items=[sample_contact], total=1, page=1))

        _ctx.ctx.configure(json_mode=True, api_key="test-key", limit=25, page=1)

        with patch.object(_ctx.ctx, "client", return_value=MockAsyncContextManager(mock_client)):
            from apollo_cli.commands.contacts import search

            await search()

        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["items"][0]["name"] == "Jane Smith"
        assert data["total"] == 1

    @pytest.mark.asyncio
    async def test_contacts_search_with_query(self, sample_contact: dict, capsys) -> None:
        """Test contacts search with query parameter."""
        mock_client = MagicMock()
        mock_client.search_contacts = AsyncMock(return_value=MockSearchResult(items=[sample_contact], total=1, page=1))

        _ctx.ctx.configure(json_mode=True, api_key="test-key", limit=25, page=1)

        with patch.object(_ctx.ctx, "client", return_value=MockAsyncContextManager(mock_client)):
            from apollo_cli.commands.contacts import search

            await search(query="engineer")

        mock_client.search_contacts.assert_called_once()
        call_kwargs = mock_client.search_contacts.call_args.kwargs
        assert call_kwargs["q_keywords"] == "engineer"

    @pytest.mark.asyncio
    async def test_contacts_search_canonicalizes_linkedin_url(self, sample_contact: dict, capsys) -> None:
        """--linkedin-url is canonicalized to Apollo's exact stored form before searching."""
        mock_client = MagicMock()
        mock_client.search_contacts = AsyncMock(return_value=MockSearchResult(items=[sample_contact], total=1, page=1))

        _ctx.ctx.configure(json_mode=True, api_key="test-key", limit=25, page=1)

        with patch.object(_ctx.ctx, "client", return_value=MockAsyncContextManager(mock_client)):
            from apollo_cli.commands.contacts import search

            await search(linkedin_url="https://www.linkedin.com/in/janesmith/")

        call_kwargs = mock_client.search_contacts.call_args.kwargs
        assert call_kwargs["linkedin_url"] == "http://www.linkedin.com/in/janesmith"

    @pytest.mark.asyncio
    async def test_find_by_linkedin_uses_canonical_search(self, capsys) -> None:
        """find-by-linkedin resolves via an exact canonical search (not the client's https path)."""
        mock_client = MagicMock()
        match = MagicMock(id="abc-123", linkedin_url="http://www.linkedin.com/in/janesmith")
        mock_client.search_contacts = AsyncMock(return_value=MockSearchResult(items=[match], total=1, page=1))
        mock_client.find_contact_by_linkedin_url = AsyncMock(return_value=None)

        _ctx.ctx.configure(json_mode=True, api_key="test-key", limit=25, page=1)

        with patch.object(_ctx.ctx, "client", return_value=MockAsyncContextManager(mock_client)):
            from apollo_cli.commands.contacts import find_by_linkedin

            await find_by_linkedin("https://www.linkedin.com/in/janesmith/")

        assert mock_client.search_contacts.call_args.kwargs["linkedin_url"] == "http://www.linkedin.com/in/janesmith"
        mock_client.find_contact_by_linkedin_url.assert_not_called()  # found via search; no fallback
        data = json.loads(capsys.readouterr().out)
        assert data["contact_id"] == "abc-123"

    @pytest.mark.asyncio
    async def test_contacts_get(self, sample_contact: dict, capsys) -> None:
        """Test contacts get command."""
        mock_client = MagicMock()
        mock_client.get_contact = AsyncMock(return_value=sample_contact)

        _ctx.ctx.configure(json_mode=True, api_key="test-key", limit=25, page=1)

        with patch.object(_ctx.ctx, "client", return_value=MockAsyncContextManager(mock_client)):
            from apollo_cli.commands.contacts import get

            await get(id="test-contact-123")

        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["name"] == "Jane Smith"
        assert data["title"] == "VP Engineering"


class TestAccountsCommands:
    @pytest.mark.asyncio
    async def test_accounts_search_json(self, sample_account: dict, capsys) -> None:
        """Test accounts search in JSON mode."""
        mock_client = MagicMock()
        mock_client.search_accounts = AsyncMock(return_value=MockSearchResult(items=[sample_account], total=1, page=1))

        _ctx.ctx.configure(json_mode=True, api_key="test-key", limit=25, page=1)

        with patch.object(_ctx.ctx, "client", return_value=MockAsyncContextManager(mock_client)):
            from apollo_cli.commands.accounts import search

            await search()

        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["items"][0]["name"] == "Acme Corp"
        assert data["items"][0]["domain"] == "acme.com"

    @pytest.mark.asyncio
    async def test_accounts_get(self, sample_account: dict, capsys) -> None:
        """Test accounts get command."""
        mock_client = MagicMock()
        mock_client.get_account = AsyncMock(return_value=sample_account)

        _ctx.ctx.configure(json_mode=True, api_key="test-key", limit=25, page=1)

        with patch.object(_ctx.ctx, "client", return_value=MockAsyncContextManager(mock_client)):
            from apollo_cli.commands.accounts import get

            await get(id="test-account-456")

        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["name"] == "Acme Corp"
        assert data["industry"] == "Technology"


class TestDealsCommands:
    @pytest.mark.asyncio
    async def test_deals_search_json(self, sample_deal: dict, capsys) -> None:
        """Test deals search in JSON mode."""
        mock_client = MagicMock()
        mock_client.search_deals = AsyncMock(return_value=MockSearchResult(items=[sample_deal], total=1, page=1))

        _ctx.ctx.configure(json_mode=True, api_key="test-key", limit=25, page=1)

        with patch.object(_ctx.ctx, "client", return_value=MockAsyncContextManager(mock_client)):
            from apollo_cli.commands.deals import search

            await search()

        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["items"][0]["name"] == "Enterprise Deal"
        assert data["items"][0]["amount"] == 50000

    @pytest.mark.asyncio
    async def test_deals_get(self, sample_deal: dict, capsys) -> None:
        """Test deals get command."""
        mock_client = MagicMock()
        mock_client.get_deal = AsyncMock(return_value=sample_deal)

        _ctx.ctx.configure(json_mode=True, api_key="test-key", limit=25, page=1)

        with patch.object(_ctx.ctx, "client", return_value=MockAsyncContextManager(mock_client)):
            from apollo_cli.commands.deals import get

            await get(id="test-deal-789")

        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["name"] == "Enterprise Deal"
        assert data["stage_name"] == "Negotiation"


class TestUsageCommand:
    @pytest.mark.asyncio
    async def test_usage_json(self, sample_usage: dict, capsys) -> None:
        """Test usage command in JSON mode."""
        mock_client = MagicMock()
        mock_client.get_api_usage = AsyncMock(return_value=sample_usage)
        mock_client.rate_limit_status = {}

        _ctx.ctx.configure(json_mode=True, api_key="test-key", limit=25, page=1)

        with patch.object(_ctx.ctx, "client", return_value=MockAsyncContextManager(mock_client)):
            from apollo_cli.commands.usage import usage

            await usage()

        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["usage"]["credits_used"] == 1000
        assert data["usage"]["credits_available"] == 9000
        assert data["usage"]["credit_limit"] == 10000


class TestPipelinesCommands:
    @pytest.mark.asyncio
    async def test_pipelines_list_json(self, sample_pipeline: dict, capsys) -> None:
        """Test pipelines list in JSON mode."""
        mock_client = MagicMock()
        mock_client.list_pipelines = AsyncMock(return_value=MockSearchResult(items=[sample_pipeline], total=1, page=1))

        _ctx.ctx.configure(json_mode=True, api_key="test-key", limit=25, page=1)

        with patch.object(_ctx.ctx, "client", return_value=MockAsyncContextManager(mock_client)):
            from apollo_cli.commands.pipelines import list_pipelines

            await list_pipelines()

        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == "Sales Pipeline"

    @pytest.mark.asyncio
    async def test_pipelines_get(self, sample_pipeline: dict, capsys) -> None:
        """Test pipelines get command."""
        mock_client = MagicMock()
        mock_client.get_pipeline = AsyncMock(return_value=sample_pipeline)

        _ctx.ctx.configure(json_mode=True, api_key="test-key", limit=25, page=1)

        with patch.object(_ctx.ctx, "client", return_value=MockAsyncContextManager(mock_client)):
            from apollo_cli.commands.pipelines import get

            await get(id="pipeline-123")

        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["name"] == "Sales Pipeline"


class TestNotesCommands:
    @pytest.mark.asyncio
    async def test_notes_create_with_opportunity_ids(self, capsys) -> None:
        """`notes create --opportunity-ids X,Y` forwards a list to the client."""
        mock_client = MagicMock()
        mock_client.create_note = AsyncMock(return_value={"id": "note-1", "content": "hi"})

        _ctx.ctx.configure(json_mode=True, api_key="test-key", limit=25, page=1)

        with patch.object(_ctx.ctx, "client", return_value=MockAsyncContextManager(mock_client)):
            from apollo_cli.commands.notes import create

            await create(content="hi", opportunity_ids="deal-1, deal-2")

        mock_client.create_note.assert_called_once()
        assert mock_client.create_note.call_args.args == ("hi",)
        assert mock_client.create_note.call_args.kwargs["opportunity_ids"] == ["deal-1", "deal-2"]

    @pytest.mark.asyncio
    async def test_notes_search_with_opportunity_id(self, capsys) -> None:
        """`notes search --opportunity-id X` filters by opportunity_ids=[X]."""
        mock_client = MagicMock()
        mock_client.search_notes = AsyncMock(return_value=MockSearchResult(items=[], total=0, page=1))

        _ctx.ctx.configure(json_mode=True, api_key="test-key", limit=25, page=1)

        with patch.object(_ctx.ctx, "client", return_value=MockAsyncContextManager(mock_client)):
            from apollo_cli.commands.notes import search

            await search(opportunity_id="deal-1")

        mock_client.search_notes.assert_called_once()
        assert mock_client.search_notes.call_args.kwargs["opportunity_ids"] == ["deal-1"]

    @pytest.mark.asyncio
    async def test_notes_create_attaches_to_all_three_at_once(self, capsys) -> None:
        """A single note can attach to contacts, accounts, and opportunities together."""
        mock_client = MagicMock()
        mock_client.create_note = AsyncMock(return_value={"id": "note-1", "content": "combined"})

        _ctx.ctx.configure(json_mode=True, api_key="test-key", limit=25, page=1)

        with patch.object(_ctx.ctx, "client", return_value=MockAsyncContextManager(mock_client)):
            from apollo_cli.commands.notes import create

            await create(
                content="combined",
                contact_ids="c1",
                account_ids="a1",
                opportunity_ids="d1",
            )

        call_kwargs = mock_client.create_note.call_args.kwargs
        assert call_kwargs["contact_ids"] == ["c1"]
        assert call_kwargs["account_ids"] == ["a1"]
        assert call_kwargs["opportunity_ids"] == ["d1"]
