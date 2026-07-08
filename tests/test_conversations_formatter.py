"""Tests for the conversation detail/list formatters."""

from __future__ import annotations

from qodev_apollo_api.models import Conversation, ConversationDetail

from apollo_cli.formatters.conversations import format_conversation_detail, format_conversation_list


def test_list_formatter_renders_columns() -> None:
    conv = Conversation.model_validate(
        {"id": "c1", "topic": "Discovery", "conversation_type": "zoom", "duration": 1800}
    )
    md = format_conversation_list([conv], total=1, page=1)
    assert "Conversations" in md
    assert "Discovery" in md
    assert "c1" in md


def test_detail_formatter_renders_transcript_and_summary() -> None:
    detail = ConversationDetail.model_validate(
        {
            "id": "c1",
            "topic": "Acme discovery",
            "conversation_type": "zoom",
            "duration": 1800,
            "participants_info": [
                {"id": "p1", "name": "Jane Smith", "title": "VP", "is_internal_participant": True},
                {"id": "p2", "name": "John Doe", "account_name": "Acme"},
            ],
            "deals": [{"id": "d1", "name": "Enterprise Deal", "account_name": "Acme"}],
            "call_summary": {
                "outcome": "Positive — moving to POC",
                "pain_points": [{"id": "pp1", "text": "Manual data entry", "participant_name": "John Doe"}],
                "next_steps": [{"id": "ns1", "step": "Send proposal"}],
            },
            "transcript": [
                {"id": "t1", "participant_name": "Jane Smith", "spoken_sentence": "Thanks for joining."},
                {"id": "t2", "participant_name": "John Doe", "spoken_sentence": "Happy to be here."},
            ],
            "video_recording": {"url": "https://example.com/rec"},
        }
    )
    md = format_conversation_detail(detail)

    # Metadata
    assert "Conversation: Acme discovery" in md
    assert "https://example.com/rec" in md
    # Participants section
    assert "## Participants" in md
    assert "Jane Smith" in md and "(internal)" in md
    # Deals section
    assert "## Deals" in md and "Enterprise Deal" in md
    # Summary section
    assert "## Call Summary" in md
    assert "Positive — moving to POC" in md
    assert "Manual data entry" in md
    assert "Send proposal" in md
    # Transcript section
    assert "## Transcript" in md
    assert "**Jane Smith:** Thanks for joining." in md


def test_detail_formatter_minimal_conversation() -> None:
    """A search-level Conversation (no transcript/summary) still renders cleanly."""
    conv = Conversation.model_validate({"id": "c1", "topic": "Quick sync"})
    md = format_conversation_detail(conv)
    assert "Conversation: Quick sync" in md
    assert "## Transcript" not in md
    assert "## Call Summary" not in md


def test_detail_formatter_handles_raw_dict() -> None:
    """The rich detail view renders from a raw dict too, not only Pydantic models."""
    data = {
        "id": "c1",
        "topic": "Dict sync",
        "participants_info": [{"name": "Jane", "title": "VP", "is_internal_participant": True}],
        "deals": [{"id": "d1", "name": "Enterprise Deal", "account_name": "Acme"}],
        "call_summary": {"outcome": "Good", "next_steps": [{"step": "Follow up"}]},
        "transcript": [{"participant_name": "Jane", "spoken_sentence": "Hello."}],
    }
    md = format_conversation_detail(data)
    assert "Conversation: Dict sync" in md
    assert "## Participants" in md and "Jane" in md and "(internal)" in md
    assert "## Deals" in md and "Enterprise Deal" in md
    assert "## Call Summary" in md and "Good" in md and "Follow up" in md
    assert "## Transcript" in md and "**Jane:** Hello." in md
