"""LinkedIn URL canonicalization for Apollo lookups.

Apollo stores and *exact-matches* LinkedIn profile URLs in the canonical form
``http://www.linkedin.com/in/<slug>`` — http scheme, ``www`` host, no trailing slash,
lowercased slug (Apollo lowercases the whole URL on its side). Apollo's ``linkedin_url``
search filter is a literal string match, so any other shape a user pastes (``https://``,
missing ``www``, a trailing slash, a mixed-case slug or ``%HEX``, tracking query params)
silently returns zero results. Canonicalizing
before searching is what makes ``contacts search --linkedin-url`` and ``upsert-by-linkedin``
match reliably.
"""

from __future__ import annotations

import re

# Modern LinkedIn profile URLs are /in/<slug>. Legacy /pub/ URLs carry a multi-segment
# id we must not truncate, so we leave anything that isn't /in/ untouched.
_PROFILE_RE = re.compile(r"linkedin\.com/in/([^/?#]+)", re.IGNORECASE)


def apollo_canonical_linkedin_url(url: str) -> str:
    """Return *url* in the exact form Apollo stores and matches on.

    Returns *url* unchanged if it is not a recognizable ``/in/`` LinkedIn profile URL,
    so passing a company page, a legacy ``/pub/`` URL, or an empty string is a no-op.
    """
    if not url:
        return url
    match = _PROFILE_RE.search(url.strip())
    if not match:
        return url
    slug = match.group(1).rstrip("/").lower()
    return f"http://www.linkedin.com/in/{slug}"
