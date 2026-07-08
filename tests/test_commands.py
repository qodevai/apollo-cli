"""Tests for CLI commands."""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from qodev_apollo_api.models import Contact

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
    async def test_upsert_returns_existing_contact(self, capsys) -> None:
        """upsert-by-linkedin returns the existing contact (created=False) via canonical search, no write."""
        mock_client = MagicMock()
        contact = Contact.model_validate(
            {"id": "c1", "name": "Jane Smith", "linkedin_url": "http://www.linkedin.com/in/janesmith"}
        )
        mock_client.search_contacts = AsyncMock(return_value=MockSearchResult(items=[contact], total=1, page=1))
        mock_client.create_contact = AsyncMock()

        _ctx.ctx.configure(json_mode=True, api_key="test-key", limit=25, page=1)

        with patch.object(_ctx.ctx, "client", return_value=MockAsyncContextManager(mock_client)):
            from apollo_cli.commands.contacts import upsert_by_linkedin

            await upsert_by_linkedin("https://www.linkedin.com/in/janesmith/")

        assert mock_client.search_contacts.call_args.kwargs["linkedin_url"] == "http://www.linkedin.com/in/janesmith"
        mock_client.create_contact.assert_not_called()
        data = json.loads(capsys.readouterr().out)
        assert data["created"] is False
        assert data["contact"]["id"] == "c1"

    @pytest.mark.asyncio
    async def test_upsert_creates_when_missing(self, capsys) -> None:
        """upsert-by-linkedin creates (created=True) when none exists and --name is given."""
        mock_client = MagicMock()
        mock_client.search_contacts = AsyncMock(return_value=MockSearchResult(items=[], total=0, page=1))
        mock_client.create_contact = AsyncMock(
            return_value=Contact.model_validate(
                {"id": "new1", "name": "Jane Smith", "linkedin_url": "http://www.linkedin.com/in/janesmith"}
            )
        )

        _ctx.ctx.configure(json_mode=True, api_key="test-key", limit=25, page=1)

        with patch.object(_ctx.ctx, "client", return_value=MockAsyncContextManager(mock_client)):
            from apollo_cli.commands.contacts import upsert_by_linkedin

            await upsert_by_linkedin("https://www.linkedin.com/in/janesmith/", name="Jane Smith", title="VP")

        args, kwargs = mock_client.create_contact.call_args
        assert args == ("Jane", "Smith")
        assert kwargs["linkedin_url"] == "http://www.linkedin.com/in/janesmith"
        assert kwargs["title"] == "VP"
        data = json.loads(capsys.readouterr().out)
        assert data["created"] is True
        assert data["contact"]["id"] == "new1"

    @pytest.mark.asyncio
    async def test_upsert_requires_name_to_create(self, capsys) -> None:
        """upsert-by-linkedin errors (exit 2, code name_required) when missing and no --name given."""
        mock_client = MagicMock()
        mock_client.search_contacts = AsyncMock(return_value=MockSearchResult(items=[], total=0, page=1))
        mock_client.create_contact = AsyncMock()

        _ctx.ctx.configure(json_mode=True, api_key="test-key", limit=25, page=1)

        with patch.object(_ctx.ctx, "client", return_value=MockAsyncContextManager(mock_client)):
            from apollo_cli.commands.contacts import upsert_by_linkedin

            with pytest.raises(SystemExit) as exc:
                await upsert_by_linkedin("https://www.linkedin.com/in/janesmith/")

        assert exc.value.code == 2
        mock_client.create_contact.assert_not_called()
        assert json.loads(capsys.readouterr().out)["code"] == "name_required"

    @pytest.mark.asyncio
    async def test_upsert_rejects_single_word_name(self, capsys) -> None:
        """A single-word --name can't create (Apollo needs first + last) — errors, no write."""
        mock_client = MagicMock()
        mock_client.search_contacts = AsyncMock(return_value=MockSearchResult(items=[], total=0, page=1))
        mock_client.create_contact = AsyncMock()

        _ctx.ctx.configure(json_mode=True, api_key="test-key", limit=25, page=1)

        with patch.object(_ctx.ctx, "client", return_value=MockAsyncContextManager(mock_client)):
            from apollo_cli.commands.contacts import upsert_by_linkedin

            with pytest.raises(SystemExit) as exc:
                await upsert_by_linkedin("https://www.linkedin.com/in/janesmith/", name="Cher")

        assert exc.value.code == 2
        mock_client.create_contact.assert_not_called()
        assert json.loads(capsys.readouterr().out)["code"] == "name_required"

    @pytest.mark.asyncio
    async def test_upsert_name_fallback_prevents_duplicate(self, capsys) -> None:
        """A URL miss but a name-search hit with the same canonical URL returns existing, not a new create."""
        mock_client = MagicMock()
        existing = Contact.model_validate({"id": "c9", "linkedin_url": "https://www.linkedin.com/in/janesmith/"})
        mock_client.search_contacts = AsyncMock(
            side_effect=[
                MockSearchResult(items=[], total=0, page=1),  # URL lookup misses
                MockSearchResult(items=[existing], total=1, page=1),  # name search hits
            ]
        )
        mock_client.create_contact = AsyncMock()

        _ctx.ctx.configure(json_mode=True, api_key="test-key", limit=25, page=1)

        with patch.object(_ctx.ctx, "client", return_value=MockAsyncContextManager(mock_client)):
            from apollo_cli.commands.contacts import upsert_by_linkedin

            await upsert_by_linkedin("https://www.linkedin.com/in/janesmith/", name="Jane Smith")

        mock_client.create_contact.assert_not_called()  # deduped — no duplicate created
        assert json.loads(capsys.readouterr().out)["created"] is False

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


class TestConversationsCommands:
    @pytest.mark.asyncio
    async def test_conversations_search_json(self, sample_conversation: dict, capsys) -> None:
        """Test conversations search in JSON mode."""
        mock_client = MagicMock()
        mock_client.search_conversations = AsyncMock(
            return_value=MockSearchResult(items=[sample_conversation], total=1, page=1)
        )

        _ctx.ctx.configure(json_mode=True, api_key="test-key", limit=25, page=1)

        with patch.object(_ctx.ctx, "client", return_value=MockAsyncContextManager(mock_client)):
            from apollo_cli.commands.conversations import search

            await search()

        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["items"][0]["id"] == "test-conversation-321"
        assert data["items"][0]["conversation_type"] == "zoom"
        assert data["total"] == 1

    @pytest.mark.asyncio
    async def test_conversations_search_with_query(self, sample_conversation: dict, capsys) -> None:
        """Test conversations search forwards the keyword as q_keywords."""
        mock_client = MagicMock()
        mock_client.search_conversations = AsyncMock(
            return_value=MockSearchResult(items=[sample_conversation], total=1, page=1)
        )

        _ctx.ctx.configure(json_mode=True, api_key="test-key", limit=25, page=1)

        with patch.object(_ctx.ctx, "client", return_value=MockAsyncContextManager(mock_client)):
            from apollo_cli.commands.conversations import search

            await search(query="discovery")

        mock_client.search_conversations.assert_called_once()
        assert mock_client.search_conversations.call_args.kwargs["q_keywords"] == "discovery"

    @pytest.mark.asyncio
    async def test_conversations_get(self, sample_conversation: dict, capsys) -> None:
        """Test conversations get command."""
        mock_client = MagicMock()
        mock_client.get_conversation = AsyncMock(return_value=sample_conversation)

        _ctx.ctx.configure(json_mode=True, api_key="test-key", limit=25, page=1)

        with patch.object(_ctx.ctx, "client", return_value=MockAsyncContextManager(mock_client)):
            from apollo_cli.commands.conversations import get

            await get(id="test-conversation-321")

        mock_client.get_conversation.assert_called_once_with("test-conversation-321")
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["topic"] == "Acme <> QoDev discovery call"


class TestPeopleCommands:
    @pytest.mark.asyncio
    async def test_people_search_domain_and_pagination(self, capsys) -> None:
        """people search forwards --organization-domains and the global --limit/--page."""
        mock_client = MagicMock()
        mock_client.search_people = AsyncMock(
            return_value={"people": [{"id": "p1", "name": "Jane"}], "pagination": {"total_entries": 1}}
        )

        _ctx.ctx.configure(json_mode=True, api_key="test-key", limit=50, page=2)

        with patch.object(_ctx.ctx, "client", return_value=MockAsyncContextManager(mock_client)):
            from apollo_cli.commands.people import search

            await search(organization_domains="acme.com, globex.com", seniorities="vp,director")

        kwargs = mock_client.search_people.call_args.kwargs
        assert kwargs["q_organization_domains_list"] == ["acme.com", "globex.com"]
        assert kwargs["person_seniorities"] == ["vp", "director"]
        assert kwargs["per_page"] == 50
        assert kwargs["page"] == 2
        data = json.loads(capsys.readouterr().out)
        assert data["items"][0]["name"] == "Jane"
        assert data["total"] == 1


class TestStageNameFilter:
    @pytest.mark.asyncio
    async def test_deals_search_stage_name_resolves(self, sample_deal: dict, capsys) -> None:
        """deals search --stage-name resolves the name to an opportunity_stage_ids filter."""
        mock_client = MagicMock()
        mock_client.list_all_stages = AsyncMock(
            return_value=MockSearchResult(
                items=[{"id": "st-neg", "name": "Negotiation"}, {"id": "st-won", "name": "Won"}], total=2, page=1
            )
        )
        mock_client.search_deals = AsyncMock(return_value=MockSearchResult(items=[sample_deal], total=1, page=1))

        _ctx.ctx.configure(json_mode=True, api_key="test-key", limit=25, page=1)

        with patch.object(_ctx.ctx, "client", return_value=MockAsyncContextManager(mock_client)):
            from apollo_cli.commands.deals import search

            await search(stage_name="negotiation")  # case-insensitive

        assert mock_client.search_deals.call_args.kwargs["opportunity_stage_ids"] == ["st-neg"]

    @pytest.mark.asyncio
    async def test_deals_search_unknown_stage_name_errors(self, capsys) -> None:
        """An unknown --stage-name is a validation error listing the available names."""
        mock_client = MagicMock()
        mock_client.list_all_stages = AsyncMock(
            return_value=MockSearchResult(items=[{"id": "st-won", "name": "Won"}], total=1, page=1)
        )
        mock_client.search_deals = AsyncMock()

        _ctx.ctx.configure(json_mode=True, api_key="test-key", limit=25, page=1)

        with patch.object(_ctx.ctx, "client", return_value=MockAsyncContextManager(mock_client)):
            from apollo_cli.commands.deals import search

            with pytest.raises(ValueError, match="No deal stage named 'Nope'"):
                await search(stage_name="Nope")

        mock_client.search_deals.assert_not_called()


class TestDealRoleCommands:
    @pytest.mark.asyncio
    async def test_set_role_read_modify_write_primary(self, sample_deal: dict, capsys) -> None:
        """set-role reads existing roles, adds the contact, and makes it the sole primary."""
        from qodev_apollo_api.models import Deal

        deal = Deal.model_validate(
            {
                "id": "d1",
                "name": "Enterprise Deal",
                "opportunity_contact_roles": [
                    {
                        "id": "r1",
                        "contact_id": "c-old",
                        "is_primary": True,
                        "role": [{"opportunity_contact_role_type_id": "rt-x"}],
                    },
                ],
            }
        )
        mock_client = MagicMock()
        mock_client.get_deal = AsyncMock(return_value=deal)
        mock_client.update_opportunity_roles = AsyncMock(return_value=deal)

        _ctx.ctx.configure(json_mode=True, api_key="test-key", limit=25, page=1)

        with patch.object(_ctx.ctx, "client", return_value=MockAsyncContextManager(mock_client)):
            from apollo_cli.commands.deals import set_role

            await set_role("d1", contact_id="c-new", primary=True)

        opp_id, roles = mock_client.update_opportunity_roles.call_args.args
        assert opp_id == "d1"
        by_contact = {r["contact_id"]: r for r in roles}
        assert by_contact["c-new"]["is_primary"] is True
        assert by_contact["c-old"]["is_primary"] is False  # demoted
        assert by_contact["c-old"]["opportunity_contact_role_type_id"] == "rt-x"  # preserved


class TestCustomFieldsCommand:
    @pytest.mark.asyncio
    async def test_custom_fields_list_filters_by_modality(self, capsys) -> None:
        """custom-fields list --modality filters the returned definitions client-side."""
        from qodev_apollo_api.models import CustomField

        fields = [
            CustomField.model_validate({"id": "f1", "modality": "contact", "name": "First Message", "type": "date"}),
            CustomField.model_validate({"id": "f2", "modality": "opportunity", "name": "Region", "type": "text"}),
        ]
        mock_client = MagicMock()
        mock_client.list_custom_fields = AsyncMock(return_value=fields)

        _ctx.ctx.configure(json_mode=True, api_key="test-key", limit=25, page=1)

        with patch.object(_ctx.ctx, "client", return_value=MockAsyncContextManager(mock_client)):
            from apollo_cli.commands.custom_fields import list_fields

            await list_fields(modality="opportunity")

        data = json.loads(capsys.readouterr().out)
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == "Region"


class TestConversationTranscript:
    @pytest.mark.asyncio
    async def test_conversations_transcript_json(self, capsys) -> None:
        """conversations transcript emits just the transcript segments in JSON mode."""
        from qodev_apollo_api.models import ConversationDetail

        detail = ConversationDetail.model_validate(
            {
                "id": "c1",
                "topic": "Sync",
                "transcript": [
                    {"id": "t1", "participant_name": "Jane", "spoken_sentence": "Hi."},
                    {"id": "t2", "participant_name": "John", "spoken_sentence": "Hello."},
                ],
            }
        )
        mock_client = MagicMock()
        mock_client.get_conversation = AsyncMock(return_value=detail)

        _ctx.ctx.configure(json_mode=True, api_key="test-key", limit=25, page=1)

        with patch.object(_ctx.ctx, "client", return_value=MockAsyncContextManager(mock_client)):
            from apollo_cli.commands.conversations import transcript

            await transcript(id="c1")

        data = json.loads(capsys.readouterr().out)
        assert [seg["spoken_sentence"] for seg in data] == ["Hi.", "Hello."]


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
