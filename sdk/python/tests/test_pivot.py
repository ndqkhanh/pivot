"""Tests for Pivot Python SDK."""

import pytest
from unittest.mock import Mock, patch
from pivot import initialize, PivotConfig


def test_initialize_default_config():
    """Test initialization with default config."""
    config = initialize()

    assert config.endpoint == "http://localhost:4317"
    assert config.run_id is not None
    assert config.policy_version == "default"
    assert config.stakeholder_principal == "unknown"
    assert config.enable_replay is True


def test_initialize_custom_config():
    """Test initialization with custom config."""
    custom_config = PivotConfig(
        endpoint="http://custom:4317",
        run_id="test-run-123",
        policy_version="v1.0",
        stakeholder_principal="user_alice",
        enable_replay=False
    )

    config = initialize(custom_config)

    assert config.endpoint == "http://custom:4317"
    assert config.run_id == "test-run-123"
    assert config.policy_version == "v1.0"
    assert config.stakeholder_principal == "user_alice"
    assert config.enable_replay is False


def test_set_harness_attributes():
    """Test setting harness attributes on span."""
    from pivot import set_harness_attributes

    mock_span = Mock()

    set_harness_attributes(
        mock_span,
        run_id="test-run-123",
        policy_version="v1.0",
        stakeholder_principal="user_alice"
    )

    # Verify attributes were set
    calls = mock_span.set_attribute.call_args_list
    assert any("harness.run_id" in str(call) for call in calls)
    assert any("harness.policy_version" in str(call) for call in calls)
    assert any("harness.stakeholder.principal" in str(call) for call in calls)


@patch('pivot.openai_instrumentation.openai')
def test_openai_instrumentation(mock_openai):
    """Test OpenAI instrumentation."""
    from pivot.openai_instrumentation import instrument_openai, uninstrument_openai

    # Instrument
    instrument_openai(stakeholder_principal="user_test")

    # Verify instrumentation
    assert mock_openai.ChatCompletion.create != mock_openai.ChatCompletion.create

    # Uninstrument
    uninstrument_openai()


@patch('pivot.anthropic_instrumentation.anthropic')
def test_anthropic_instrumentation(mock_anthropic):
    """Test Anthropic instrumentation."""
    from pivot.anthropic_instrumentation import instrument_anthropic, uninstrument_anthropic

    # Instrument
    instrument_anthropic(stakeholder_principal="user_test")

    # Uninstrument
    uninstrument_anthropic()


def test_get_current_run_id():
    """Test getting current run ID."""
    from pivot import get_current_run_id

    run_id = get_current_run_id()
    assert run_id is not None
    assert isinstance(run_id, str)
    assert len(run_id) > 0
