"""Tests for shared utility helpers."""

from __future__ import annotations

import pytest

from apollo_cli.util import parse_comma_list, resolve_stage_id


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


class TestResolveStageId:
    def test_matches_case_insensitively(self) -> None:
        stages = [{"id": "s1", "name": "Negotiation"}, {"id": "s2", "name": "Won"}]
        assert resolve_stage_id("negotiation", stages) == "s1"

    def test_works_with_model_like_objects(self) -> None:
        class S:
            def __init__(self, id, name):
                self.id, self.name = id, name

        assert resolve_stage_id("Won", [S("s1", "Neg"), S("s2", "Won")]) == "s2"

    def test_unknown_name_lists_available(self) -> None:
        stages = [{"id": "s1", "name": "Won"}, {"id": "s2", "name": "Lost"}]
        with pytest.raises(ValueError, match=r"No stage named 'Nope'\. Available: Lost, Won"):
            resolve_stage_id("Nope", stages)

    def test_available_list_is_capped(self) -> None:
        stages = [{"id": str(i), "name": f"Stage{i:02d}"} for i in range(30)]
        with pytest.raises(ValueError, match=r"\(\+15 more\)"):
            resolve_stage_id("missing", stages)
