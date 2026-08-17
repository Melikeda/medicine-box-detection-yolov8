"""Gemini model fallback chain tests."""

from backend.app.llm_models import GEMINI_FREE_TIER_MODELS
from backend.app.services.llm_service import _is_retryable_gemini_error, _model_chain


def test_model_chain_prefers_primary_then_free_tier_defaults() -> None:
    chain = _model_chain("gemini-flash-latest")
    assert chain[0] == "gemini-flash-latest"
    assert "gemini-flash-lite-latest" in chain


def test_model_chain_deduplicates_entries() -> None:
    chain = _model_chain("gemini-flash-lite-latest")
    assert chain.count("gemini-flash-lite-latest") == 1
    assert chain[0] == "gemini-flash-lite-latest"
    assert set(GEMINI_FREE_TIER_MODELS).issubset(set(chain))


def test_gemini_high_demand_is_retryable() -> None:
    error = RuntimeError(
        "503 UNAVAILABLE. This model is currently experiencing high demand."
    )
    assert _is_retryable_gemini_error(error) is True
