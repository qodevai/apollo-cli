"""Conversation-specific formatters."""

from __future__ import annotations

from typing import Any

from apollo_cli.formatters.generic import detail_table, list_table


def _get(item: Any, key: str) -> Any:
    """Read ``key`` from a Pydantic model (attr) or a dict — so the rich detail view
    renders whether ``get_conversation()`` returns models or raw dicts."""
    return item.get(key) if isinstance(item, dict) else getattr(item, key, None)


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
    topic = _get(data, "topic") or "Conversation"
    md = detail_table(data, CONVERSATION_DETAIL_FIELDS, title=f"Conversation: {topic}")

    # Participants (richer than the participant_names list in the metadata table)
    participants = _get(data, "participants_info") or []
    if participants:
        md += "\n\n## Participants\n"
        for p in participants:
            name = _get(p, "name") or "Unknown"
            title = _get(p, "title")
            account = _get(p, "account_name")
            internal = _get(p, "is_internal_participant")
            suffix = ", ".join(x for x in [title, account] if x)
            tag = " (internal)" if internal else ""
            md += f"\n- **{name}**{tag}" + (f" — {suffix}" if suffix else "")

    # Associated deals
    deals = _get(data, "deals") or []
    if deals:
        md += "\n\n## Deals\n"
        for d in deals:
            name = _get(d, "name") or _get(d, "id") or "Unknown"
            account = _get(d, "account_name")
            md += f"\n- {name}" + (f" ({account})" if account else "")

    # AI-generated call summary (detail endpoint only)
    summary = _get(data, "call_summary")
    if summary:
        md += _format_summary(summary)

    # Transcript (detail endpoint only)
    if _get(data, "transcript"):
        md += "\n\n" + format_transcript(data)

    return md


def format_transcript(data: Any) -> str:
    """Render just the transcript of a conversation as `**Speaker:** sentence` lines."""
    segments = _get(data, "transcript") or []
    if not segments:
        return "## Transcript\n\n_No transcript available._"
    lines = ["## Transcript", ""]
    for seg in segments:
        speaker = _get(seg, "participant_name") or "Unknown"
        sentence = _get(seg, "spoken_sentence") or ""
        lines.append(f"- **{speaker}:** {sentence}")
    return "\n".join(lines)


def _format_summary(summary: Any) -> str:
    """Render the AI call summary (outcome, pain points, objections, next steps)."""
    md = "\n\n## Call Summary\n"
    outcome = _get(summary, "outcome")
    if outcome:
        md += f"\n**Outcome:** {outcome}\n"
    pricing = _get(summary, "pricing_discussion")
    if pricing:
        md += f"\n**Pricing discussion:** {pricing}\n"

    for label, attr, field in (
        ("Pain Points", "pain_points", "text"),
        ("Objections", "objections", "text"),
        ("Next Steps", "next_steps", "step"),
    ):
        items = _get(summary, attr) or []
        if items:
            md += f"\n### {label}\n"
            for item in items:
                text = _get(item, field) or ""
                who = _get(item, "participant_name")
                md += f"\n- {text}" + (f" — _{who}_" if who else "")
    return md
