from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Protocol

from backend.app.config import ApiSettings
from backend.app.exceptions import LlmNotConfiguredError, LlmUnavailableError
from backend.app.llm_models import DEFAULT_GEMINI_MODEL, GEMINI_FREE_TIER_MODELS
from backend.app.services.explanation_cache import ExplanationCache

logger = logging.getLogger(__name__)

VERIFY_PLACEHOLDER = "VERIFY_FROM_OFFICIAL_LEAFLET"

SYSTEM_PROMPT = """Sen bir ilaç bilgilendirme asistanısın.
Görevin, verilen resmi veritabanı alanlarına dayanarak kısa bir Türkçe açıklama yazmaktır.

Kurallar:
- En fazla 2-4 cümle kullan.
- Sadece verilen bilgilere dayan; uydurma yapma.
- Doz, kullanım süresi veya tedavi önerme.
- Eksik veya "doğrulanmalı" alan varsa eczacıya/prospektüse danışılmasını söyle.
- Sakin, bilgilendirici ve anlaşılır bir dil kullan.
"""


class MedicineExplainer(Protocol):
    def explain(
        self,
        medicine: dict[str, str],
        *,
        locale: str = "tr",
    ) -> str: ...


@dataclass(frozen=True)
class GeminiExplainResult:
    text: str
    model: str


def _format_field(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    if not cleaned or cleaned == VERIFY_PLACEHOLDER:
        return None
    return cleaned


def _build_user_prompt(medicine: dict[str, str]) -> str:
    fields = [
        ("İlaç adı", _format_field(medicine.get("medicine_name"))),
        ("Marka", _format_field(medicine.get("brand_name"))),
        ("Etken madde", _format_field(medicine.get("active_ingredient"))),
        ("Doz", _format_field(medicine.get("dosage"))),
        ("Form", _format_field(medicine.get("form"))),
        ("Kategori", _format_field(medicine.get("category"))),
    ]

    lines = [f"- {label}: {value}" for label, value in fields if value]
    if not lines:
        lines.append("- Veritabanında sınırlı bilgi mevcut.")

    return "Aşağıdaki ilaç kaydı için kısa Türkçe açıklama yaz:\n" + "\n".join(
        lines
    )


def _normalize_explanation(text: str) -> str:
    cleaned = text.strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


def _model_chain(primary: str) -> tuple[str, ...]:
    ordered: list[str] = []
    for candidate in (primary, *GEMINI_FREE_TIER_MODELS):
        if candidate and candidate not in ordered:
            ordered.append(candidate)
    return tuple(ordered)


def _is_retryable_gemini_error(exc: Exception) -> bool:
    message = str(exc)
    return (
        "404" in message
        or "429" in message
        or "NOT_FOUND" in message
        or "RESOURCE_EXHAUSTED" in message
    )


class MockMedicineExplainer:
    """API anahtarı olmadan geliştirme ve test için deterministik açıklama."""

    def explain(
        self,
        medicine: dict[str, str],
        *,
        locale: str = "tr",
    ) -> str:
        name = _format_field(medicine.get("medicine_name")) or "Bu ilaç"
        category = _format_field(medicine.get("category"))
        ingredient = _format_field(medicine.get("active_ingredient"))

        parts = [f"{name} hakkında kısa bilgi:"]
        if category:
            parts.append(f"Kategori: {category}.")
        if ingredient:
            parts.append(f"Etken madde: {ingredient}.")
        parts.append(
            "Detaylı kullanım bilgisi için prospektüsü okuyun ve eczacınıza danışın."
        )
        return _normalize_explanation(" ".join(parts))


class GeminiMedicineExplainer:
    """Google Gemini API ile ilaç açıklaması üretir; model fallback destekler."""

    def __init__(
        self,
        *,
        api_key: str,
        primary_model: str,
    ) -> None:
        self.api_key = api_key
        self.primary_model = primary_model
        self.models = _model_chain(primary_model)
        self.last_model_used: str | None = None
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                from google import genai
            except ImportError as exc:
                raise LlmUnavailableError(
                    "google-genai paketi yüklü değil."
                ) from exc

            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def explain(
        self,
        medicine: dict[str, str],
        *,
        locale: str = "tr",
    ) -> str:
        result = self.explain_with_model(medicine, locale=locale)
        return result.text

    def explain_with_model(
        self,
        medicine: dict[str, str],
        *,
        locale: str = "tr",
    ) -> GeminiExplainResult:
        prompt = _build_user_prompt(medicine)
        if locale != "tr":
            prompt += f"\n\nYanıt dili: {locale}"

        client = self._get_client()
        contents = f"{SYSTEM_PROMPT}\n\n{prompt}"
        errors: list[str] = []

        for model in self.models:
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=contents,
                )
            except Exception as exc:
                logger.warning(
                    "Gemini model failed (%s): %s",
                    model,
                    exc,
                )
                errors.append(f"{model}: {exc}")
                if _is_retryable_gemini_error(exc):
                    continue
                raise LlmUnavailableError(
                    "LLM servisi şu anda kullanılamıyor."
                ) from exc
            else:
                text = getattr(response, "text", None)
                if not text or not text.strip():
                    errors.append(f"{model}: empty response")
                    continue

                self.last_model_used = model
                return GeminiExplainResult(
                    text=_normalize_explanation(text),
                    model=model,
                )

        if any("429" in item or "RESOURCE_EXHAUSTED" in item for item in errors):
            raise LlmUnavailableError(
                "LLM kotası aşıldı. Lütfen biraz sonra tekrar deneyin."
            )

        logger.error("All Gemini models failed: %s", errors)
        raise LlmUnavailableError(
            "LLM servisi şu anda kullanılamıyor."
        )


class LlmExplanationService:
    """İlaç açıklaması servisi; cache ve sağlayıcı seçimi."""

    def __init__(
        self,
        *,
        settings: ApiSettings,
        explainer: MedicineExplainer,
        cache: ExplanationCache | None = None,
        provider: str = "mock",
        model: str = "mock",
    ) -> None:
        self.settings = settings
        self.explainer = explainer
        self.cache = cache or ExplanationCache()
        self.provider = provider
        self.model = model

    @classmethod
    def from_settings(cls, settings: ApiSettings) -> LlmExplanationService:
        if not settings.llm_is_configured:
            raise LlmNotConfiguredError()

        if settings.llm_mock_mode or settings.llm_provider == "mock":
            explainer: MedicineExplainer = MockMedicineExplainer()
            provider = "mock"
            model = "mock"
        else:
            explainer = GeminiMedicineExplainer(
                api_key=settings.gemini_api_key or "",
                primary_model=settings.llm_model,
            )
            provider = settings.llm_provider
            model = settings.llm_model

        return cls(
            settings=settings,
            explainer=explainer,
            provider=provider,
            model=model,
        )

    def explain_medicine(
        self,
        medicine: dict[str, str],
        *,
        locale: str = "tr",
    ) -> tuple[str, bool]:
        medicine_id = medicine.get("medicine_id", "").strip()
        if not medicine_id:
            raise LlmUnavailableError("İlaç kimliği eksik.")

        if self.settings.llm_cache_enabled:
            cached = self.cache.get(medicine_id, locale)
            if cached:
                return cached, True

        if isinstance(self.explainer, GeminiMedicineExplainer):
            result = self.explainer.explain_with_model(medicine, locale=locale)
            explanation = result.text
            self.model = result.model
        else:
            explanation = self.explainer.explain(medicine, locale=locale)

        if self.settings.llm_cache_enabled:
            self.cache.set(medicine_id, locale, explanation)

        return explanation, False
