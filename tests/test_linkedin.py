"""Tests for LinkedIn URL canonicalization."""

from __future__ import annotations

import pytest

from apollo_cli.linkedin import apollo_canonical_linkedin_url

CANON = "http://www.linkedin.com/in/daniel-wessel-575597b8"


@pytest.mark.parametrize(
    "raw",
    [
        "http://www.linkedin.com/in/daniel-wessel-575597b8",  # already canonical
        "https://www.linkedin.com/in/daniel-wessel-575597b8/",  # https + trailing slash
        "https://linkedin.com/in/daniel-wessel-575597b8",  # missing www
        "www.linkedin.com/in/daniel-wessel-575597b8",  # no scheme
        "https://www.linkedin.com/in/daniel-wessel-575597b8?utm_source=share",  # query params
        "  https://www.linkedin.com/in/daniel-wessel-575597b8/  ",  # surrounding whitespace
        "https://www.linkedin.com/in/Daniel-Wessel-575597b8",  # mixed-case slug (Apollo stores lowercase)
    ],
)
def test_canonicalizes_common_variants_to_apollo_form(raw: str) -> None:
    assert apollo_canonical_linkedin_url(raw) == CANON


def test_lowercases_percent_encoding() -> None:
    # Apollo stores %hex lowercase; harvested LinkedIn URLs often arrive uppercase.
    raw = "https://www.linkedin.com/in/j%C3%BCrgen-baier/"
    assert apollo_canonical_linkedin_url(raw) == "http://www.linkedin.com/in/j%c3%bcrgen-baier"


@pytest.mark.parametrize(
    "raw",
    [
        "",
        "https://example.com/x",
        "https://www.linkedin.com/company/acme",  # not a person profile
        "https://www.linkedin.com/pub/foo/1/a2/3b4",  # legacy /pub/ — must not truncate
    ],
)
def test_non_in_profile_urls_pass_through_unchanged(raw: str) -> None:
    assert apollo_canonical_linkedin_url(raw) == raw
