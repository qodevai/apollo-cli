"""Tests for the root App's global error-code mapping (app.py's launcher)."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from qodev_apollo_api import RoleAssignmentError
from qodev_apollo_api.models import Deal

import apollo_cli.context as _ctx
from apollo_cli.app import launcher


class MockAsyncContextManager:
    """Mock async context manager for client()."""

    def __init__(self, mock_client: MagicMock):
        self.mock_client = mock_client

    async def __aenter__(self):
        return self.mock_client

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class TestRoleAssignmentErrorExitCode:
    def test_deals_set_role_fail_loud_exits_82(self, capsys) -> None:
        """When Apollo drops a set-role write, RoleAssignmentError propagates from
        update_opportunity_roles through `deals set-role` and the launcher maps it
        to exit code 82 (API error), not a bare crash or a swallowed success."""
        deal = Deal.model_validate({"id": "d1", "opportunity_contact_roles": []})
        mock_client = MagicMock()
        mock_client.get_deal = AsyncMock(return_value=deal)
        mock_client.update_opportunity_roles = AsyncMock(
            side_effect=RoleAssignmentError(
                "update_opportunity_roles: contact(s) ['c1'] missing from read-back",
                opportunity_id="d1",
                missing_contact_ids=["c1"],
            )
        )

        with (
            patch.object(_ctx.ctx, "client", return_value=MockAsyncContextManager(mock_client)),
            pytest.raises(SystemExit) as exc_info,
        ):
            launcher(
                "deals",
                "set-role",
                "d1",
                "--contact-id",
                "c1",
                json=True,
                api_key="test-key",
                limit=25,
                page=1,
            )

        assert exc_info.value.code == 82
        payload = json.loads(capsys.readouterr().out)
        assert payload["code"] == "role_assignment_failed"
        assert "c1" in payload["error"]
