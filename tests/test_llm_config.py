"""LLM configuration validation tests."""

from backend.app.config import ApiSettings


def test_llm_placeholder_key_is_not_configured() -> None:
    settings = ApiSettings(
        llm_enabled=True,
        gemini_api_key="your_key_from_aistudio.google.com",
    )
    assert settings.llm_is_configured is False


def test_llm_valid_key_is_configured() -> None:
    settings = ApiSettings(
        llm_enabled=True,
        gemini_api_key="AIzaSyAbcdefghijklmnopqrstuvwxyz123456",
    )
    assert settings.llm_is_configured is True


def test_llm_mock_mode_configured_without_key() -> None:
    settings = ApiSettings(
        llm_enabled=True,
        llm_mock_mode=True,
        gemini_api_key=None,
    )
    assert settings.llm_is_configured is True
