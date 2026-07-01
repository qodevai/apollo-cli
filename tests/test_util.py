"""Tests for shared utility helpers."""

from __future__ import annotations

import pytest

from apollo_cli.util import parse_csv


class TestParseCsv:
    def test_basic(self) -> None:
        assert parse_csv("a,b,c") == ["a", "b", "c"]

    def test_strips_whitespace(self) -> None:
        assert parse_csv("a, b ,  c") == ["a", "b", "c"]

    def test_drops_embedded_empty_tokens(self) -> None:
        assert parse_csv("a,,b") == ["a", "b"]

    def test_drops_whitespace_only_tokens(self) -> None:
        assert parse_csv("a, ,b") == ["a", "b"]

    def test_drops_leading_and_trailing_commas(self) -> None:
        assert parse_csv(",a,b,") == ["a", "b"]

    def test_all_empty_returns_empty_list(self) -> None:
        assert parse_csv(",,,") == []
        assert parse_csv("   ") == []

    def test_single_token(self) -> None:
        assert parse_csv("solo") == ["solo"]

    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("a,,b", ["a", "b"]),
            ("a, ,b", ["a", "b"]),
            (" a , b ", ["a", "b"]),
            (",a,", ["a"]),
        ],
    )
    def test_edge_cases(self, raw: str, expected: list[str]) -> None:
        assert parse_csv(raw) == expected
