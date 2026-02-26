"""Tests for output formatting."""

from __future__ import annotations

import json
from datetime import datetime
from decimal import Decimal

import pytest

from apollo_cli.context import Context
from apollo_cli.output import error, output, output_list


class TestJsonOutput:
    def test_output_dict_json_mode(self, capsys) -> None:
        """Test JSON output for dict data."""
        ctx = Context(json_mode=True)
        data = {"name": "Test", "value": 123}

        output(data, ctx=ctx)

        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert result["name"] == "Test"
        assert result["value"] == 123

    def test_output_list_json_mode(self, capsys) -> None:
        """Test JSON output for list data."""
        ctx = Context(json_mode=True)
        items = [{"id": 1}, {"id": 2}]

        def format_fn(item):
            return str(item["id"])

        output_list(
            items=items,
            total=2,
            page=1,
            limit=25,
            ctx=ctx,
            format_fn=format_fn,
            resource_name="Test",
        )

        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert len(result["items"]) == 2
        assert result["total"] == 2
        assert result["page"] == 1
        assert result["limit"] == 25

    def test_output_with_datetime(self, capsys) -> None:
        """Test JSON output handles datetime serialization."""
        ctx = Context(json_mode=True)
        data = {"created_at": datetime(2024, 1, 15, 10, 30, 0)}

        output(data, ctx=ctx)

        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert "2024-01-15" in result["created_at"]

    def test_output_with_decimal(self, capsys) -> None:
        """Test JSON output handles Decimal serialization."""
        ctx = Context(json_mode=True)
        data = {"amount": Decimal("99.99")}

        output(data, ctx=ctx)

        captured = capsys.readouterr()
        result = json.loads(captured.out)
        # Decimals are serialized as floats in JSON
        assert result["amount"] == 99.99


class TestMarkdownOutput:
    def test_output_markdown_mode(self, capsys) -> None:
        """Test markdown output for dict data."""
        ctx = Context(json_mode=False)
        data = {"name": "Test", "value": 123}

        output(data, ctx=ctx)

        captured = capsys.readouterr()
        # Just verify something was printed (exact format depends on rich)
        assert len(captured.out) > 0

    def test_output_list_markdown_mode(self, capsys) -> None:
        """Test markdown output for list data."""
        ctx = Context(json_mode=False)
        items = [{"id": 1, "name": "One"}, {"id": 2, "name": "Two"}]

        def format_fn(items, **kwargs):
            return "\n".join([f"{item['id']}: {item['name']}" for item in items])

        output_list(
            items=items,
            total=2,
            page=1,
            limit=25,
            ctx=ctx,
            format_fn=format_fn,
            resource_name="Test",
        )

        captured = capsys.readouterr()
        assert "1: One" in captured.out or "2: Two" in captured.out


class TestErrorOutput:
    def test_error_json_mode(self, capsys) -> None:
        """Test error output in JSON mode."""
        ctx = Context(json_mode=True)

        with pytest.raises(SystemExit) as exc_info:
            error("Test error", ctx=ctx, code="test_error", exit_code=99)

        assert exc_info.value.code == 99

        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert result["error"] == "Test error"
        assert result["code"] == "test_error"

    def test_error_markdown_mode(self, capsys) -> None:
        """Test error output in markdown mode."""
        ctx = Context(json_mode=False)

        with pytest.raises(SystemExit) as exc_info:
            error("Test error", ctx=ctx, code="test_error", exit_code=99)

        assert exc_info.value.code == 99

        captured = capsys.readouterr()
        # Error output goes to stderr in markdown mode
        assert "Error" in captured.err or "error" in captured.err.lower()
