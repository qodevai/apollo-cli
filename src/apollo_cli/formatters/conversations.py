"""Conversation-specific formatters."""

from __future__ import annotations

from typing import Any

from apollo_cli.formatters.generic import detail_table, list_table

CONVERSATION_LIST_COLUMNS = [
    ("ID", "id"),
    ("Topic", "topic"),
    ("Type", "conversation_type"),
    ("Start", "start_time"),
    ("Duration", "duration"),
    ("Host", "host"),
    ("State", "state"),
]

CONVERSATION_DETAIL_FIELDS = [
    ("ID", "id"),
    ("Topic", "topic"),
    ("Type", "conversation_type"),
    ("Start", "start_time"),
    ("Duration (s)", "duration"),
    ("Host", "host"),
    ("Host ID", "host_id"),
    ("State", "state"),
    ("Internal", "is_internal"),
    ("Private", "is_private"),
    ("Comments", "comment_count"),
    ("Participants", "participant_names"),
    ("Accounts", "account_names"),
    ("Recording", "video_recording.url"),
    ("Pushed to CRM", "pushed_to_crm"),
]


def format_conversation_list(items: list[Any], *, total: int = 0, page: int = 1) -> str:
    """Format a list of conversations as a markdown table."""
    return list_table(items, CONVERSATION_LIST_COLUMNS, title="Conversations", total=total, page=page)


def format_conversation_detail(data: Any) -> str:
    """Format a single conversation (with transcript & summary) as a markdown detail view."""
    topic = getattr(data, "topic", None) or "Conversation"
    md = detail_table(data, CONVERSATION_DETAIL_FIELDS, title=f"Conversation: {topic}")

    # Participants (richer than the participant_names list in the metadata table)
    participants = getattr(data, "participants_info", None) or []
    if participants:
        md += "\n\n## Participants\n"
        for p in participants:
            name = getattr(p, "name", None) or "Unknown"
            title = getattr(p, "title", None)
            account = getattr(p, "account_name", None)
            internal = getattr(p, "is_internal_participant", None)
            suffix = ", ".join(x for x in [title, account] if x)
            tag = " (internal)" if internal else ""
            md += f"\n- **{name}**{tag}" + (f" — {suffix}" if suffix else "")

    # Associated deals
    deals = getattr(data, "deals", None) or []
    if deals:
        md += "\n\n## Deals\n"
        for d in deals:
            name = getattr(d, "name", None) or getattr(d, "id", "Unknown")
            account = getattr(d, "account_name", None)
            md += f"\n- {name}" + (f" ({account})" if account else "")

    # AI-generated call summary (detail endpoint only)
    summary = getattr(data, "call_summary", None)
    if summary:
        md += _format_summary(summary)

    # Transcript (detail endpoint only)
    if getattr(data, "transcript", None):
        md += "\n\n" + format_transcript(data)

    return md


def format_transcript(data: Any) -> str:
    """Render just the transcript of a conversation as `**Speaker:** sentence` lines."""
    segments = getattr(data, "transcript", None) or []
    if not segments:
        return "## Transcript\n\n_No transcript available._"
    lines = ["## Transcript", ""]
    for seg in segments:
        speaker = getattr(seg, "participant_name", None) or "Unknown"
        sentence = getattr(seg, "spoken_sentence", None) or ""
        lines.append(f"- **{speaker}:** {sentence}")
    return "\n".join(lines)


def _format_summary(summary: Any) -> str:
    """Render the AI call summary (outcome, pain points, objections, next steps)."""
    md = "\n\n## Call Summary\n"
    outcome = getattr(summary, "outcome", None)
    if outcome:
        md += f"\n**Outcome:** {outcome}\n"
    pricing = getattr(summary, "pricing_discussion", None)
    if pricing:
        md += f"\n**Pricing discussion:** {pricing}\n"

    for label, attr, field in (
        ("Pain Points", "pain_points", "text"),
        ("Objections", "objections", "text"),
        ("Next Steps", "next_steps", "step"),
    ):
        items = getattr(summary, attr, None) or []
        if items:
            md += f"\n### {label}\n"
            for item in items:
                text = getattr(item, field, None) or ""
                who = getattr(item, "participant_name", None)
                md += f"\n- {text}" + (f" — _{who}_" if who else "")
    return md
