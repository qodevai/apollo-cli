"""Test fixtures for Apollo CLI tests."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

import apollo_cli.context as _ctx
from apollo_cli.context import Context


@pytest.fixture
def ctx():
    """Fresh Context instance for each test."""
    return Context()


@pytest.fixture
def json_ctx():
    """Context with JSON mode enabled."""
    return Context(json_mode=True)


@pytest.fixture
def mock_client():
    """Pre-configured mock Apollo client."""
    client = MagicMock()
    return client


@pytest.fixture
def sample_contact():
    """Sample contact dict for testing."""
    return {
        "id": "test-contact-123",
        "name": "Jane Smith",
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane@example.com",
        "title": "VP Engineering",
        "organization_name": "Acme Corp",
        "linkedin_url": "https://linkedin.com/in/janesmith",
        "created_at": "2024-01-15T10:30:00Z",
        "phone_numbers": [
            {"number": "+1-555-0100", "type": "mobile"},
        ],
    }


@pytest.fixture
def sample_account():
    """Sample account dict for testing."""
    return {
        "id": "test-account-456",
        "name": "Acme Corp",
        "domain": "acme.com",
        "industry": "Technology",
        "estimated_num_employees": 500,
        "website_url": "https://acme.com",
    }


@pytest.fixture
def sample_deal():
    """Sample deal dict for testing."""
    return {
        "id": "test-deal-789",
        "name": "Enterprise Deal",
        "amount": 50000,
        "stage_name": "Negotiation",
        "is_won": False,
        "owner_id": "owner-123",
    }


@pytest.fixture
def sample_pipeline():
    """Sample pipeline dict for testing."""
    return {
        "id": "pipeline-123",
        "name": "Sales Pipeline",
        "created_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def sample_stage():
    """Sample stage dict for testing."""
    return {
        "id": "stage-123",
        "name": "Qualified Lead",
        "display_name": "Qualified Lead",
    }


@pytest.fixture
def sample_usage():
    """Sample usage stats dict for testing."""
    return {
        "credits_used": 1000,
        "credits_available": 9000,
        "credit_limit": 10000,
        "email_credits_used": 500,
        "export_credits_used": 200,
        "request_limit": 1000,
        "requests_used": 250,
    }


@pytest.fixture
def mock_env(monkeypatch):
    """Set standard environment variables."""
    monkeypatch.setenv("APOLLO_API_KEY", "test-key-123")


@pytest.fixture
def mock_global_ctx():
    """Reset global context to known state for testing."""
    # Store original state
    original_json_mode = _ctx.ctx.json_mode
    original_api_key = _ctx.ctx.api_key
    original_limit = _ctx.ctx.limit
    original_page = _ctx.ctx.page

    # Configure for test
    _ctx.ctx.configure(json_mode=False, api_key="test-key", limit=25, page=1)

    yield _ctx.ctx

    # Restore original state
    _ctx.ctx.configure(
        json_mode=original_json_mode,
        api_key=original_api_key,
        limit=original_limit,
        page=original_page,
    )
