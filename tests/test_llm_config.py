"""LLM configuration validation tests."""

import pytest

from backend.app.config import ApiSettings
from backend.app.main import create_app


def test_llm_placeholder_key_is_not_configured() -> None:
    settings = ApiSettings(
        llm_enabled=True,
        gemini_api_key="your_key_from_aistudio.google.com",
    )
    assert settings.llm_is_configured is False
    assert "gecersiz" in settings.llm_status_message.lower() or "ornek" in (
        settings.llm_status_message.lower()
    )


def test_llm_short_key_is_not_configured() -> None:
    settings = ApiSettings(
        llm_enabled=True,
        gemini_api_key="short-key",
    )
    assert settings.llm_is_configured is False


def test_llm_valid_key_is_configured() -> None:
    settings = ApiSettings(
        llm_enabled=True,
        gemini_api_key="AIzaSyAbcdefghijklmnopqrstuvwxyz123456",
    )
    assert settings.llm_is_configured is True
    assert "hazir" in settings.llm_status_message.lower()


def test_llm_mock_mode_configured_without_key() -> None:
    settings = ApiSettings(
        llm_enabled=True,
        llm_mock_mode=True,
        gemini_api_key=None,
    )
    assert settings.llm_is_configured is True


def test_production_rejects_enabled_llm_without_key() -> None:
    settings = ApiSettings(
        environment="production",
        cors_origins="https://app.example.com",
        llm_enabled=True,
        llm_mock_mode=False,
        gemini_api_key=None,
    )
    with pytest.raises(RuntimeError, match="GEMINI_API_KEY"):
        create_app(settings)


def test_production_allows_enabled_llm_with_mock_mode() -> None:
    settings = ApiSettings(
        environment="production",
        cors_origins="https://app.example.com",
        llm_enabled=True,
        llm_mock_mode=True,
        rate_limit_enabled=False,
    )
    app = create_app(settings)
    assert app.docs_url is None
