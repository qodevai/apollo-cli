"""Tests for shared utility helpers."""

from __future__ import annotations

import pytest

from apollo_cli.util import parse_comma_list


class TestParseCommaList:
    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("a,b,c", ["a", "b", "c"]),
            ("a, b ,  c", ["a", "b", "c"]),
            ("a,,b", ["a", "b"]),
            ("a, ,b", ["a", "b"]),
            (",a,b,", ["a", "b"]),
            ("solo", ["solo"]),
            ("", []),
            ("   ", []),
        ],
    )
    def test_returns_stripped_non_empty_tokens(self, raw: str, expected: list[str]) -> None:
        assert parse_comma_list(raw) == expected

    @pytest.mark.parametrize("raw", [",,,", ",", " , , "])
    def test_raises_when_input_has_content_but_no_usable_tokens(self, raw: str) -> None:
        """`",,,"` means the user typed *something* — silently returning [] would
        omit the flag, which "fail early and loud" forbids. Empty/whitespace-only
        input (tested above) is fine because it maps cleanly to "flag not provided"."""
        with pytest.raises(ValueError, match="only separators"):
            parse_comma_list(raw)
