from __future__ import annotations

import json
import logging
import re
from dataclasses import asdict, dataclass, field
from typing import Any, Protocol

from backend.app.config import ApiSettings
from backend.app.constants import LLM_EXPLANATION_DISCLAIMER
from backend.app.exceptions import LlmNotConfiguredError, LlmUnavailableError
from backend.app.llm_models import GEMINI_FREE_TIER_MODELS
from backend.app.services.explanation_cache import (
    ExplanationCache,
    get_shared_explanation_cache,
)

logger = logging.getLogger(__name__)

VERIFY_PLACEHOLDER = "VERIFY_FROM_OFFICIAL_LEAFLET"

FALLBACK_SUMMARY = "Bu ilaç hakkında yeterli açıklayıcı bilgi bulunamadı."

# General usage areas based on catalog categories.
# The DB does not store official per-medicine indications, so only safe
# statements derived from the category taxonomy are sent to the LLM context.
CATEGORY_USAGE_HINTS: dict[str, list[str]] = {
    "ağrı kesici": [
        "Hafif veya orta şiddette bazı ağrı durumları",
        "Ateşin eşlik ettiği bazı rahatsızlıklar",
        "Doktor tarafından uygun görülen diğer ağrı durumları",
    ],
    "kas ve eklem": [
        "Kas-iskelet sistemi kaynaklı bazı ağrı durumları",
        "Eklem kaynaklı bazı ağrı ve iltihap durumları",
        "Resmi kullanım bilgilerinde yer alan diğer uygun durumlar",
    ],
    "kas-iskelet": [
        "Kas-iskelet sistemi kaynaklı bazı ağrı durumları",
        "Eklem ve yumuşak doku kaynaklı bazı rahatsızlıklar",
        "Resmi kullanım bilgilerinde yer alan diğer uygun durumlar",
    ],
    "kas gevşetici": [
        "Kas gerginliğiyle ilişkili bazı durumlar",
        "Kas-iskelet sistemi kaynaklı bazı rahatsızlıklar",
        "Doktor tarafından uygun görülen diğer durumlar",
    ],
    "antibiyotik": [
        "Bakteriyel enfeksiyonların tedavisinde doktor tarafından reçete edilen durumlar",
        "Resmi kullanım bilgilerinde tanımlanan enfeksiyon türleri",
    ],
    "soğuk algınlığı": [
        "Soğuk algınlığına bağlı bazı şikayetlerin geçici rahatlatılması",
        "Burun tıkanıklığı, ateş veya ağrı gibi semptomların yönetiminde",
    ],
    "öksürük ilacı": [
        "Öksürükle ilişkili bazı solunum yolu şikayetleri",
        "Doktor veya eczacı önerisiyle uygun görülen öksürük durumları",
    ],
    "mide": [
        "Mide yanması, hazımsızlık veya asitle ilişkili bazı rahatsızlıklar",
        "Resmi kullanım bilgilerinde yer alan diğer mide-bağırsak durumları",
    ],
    "mide ilacı": [
        "Mide yanması, hazımsızlık veya asitle ilişkili bazı rahatsızlıklar",
        "Resmi kullanım bilgilerinde yer alan diğer mide-bağırsak durumları",
    ],
    "vitamin ve mineral": [
        "Vitamin veya mineral takviyesi gerektiren durumlar",
        "Beslenme desteği olarak doktor/eczacı önerisiyle kullanım",
    ],
    "food supplement": [
        "Besin takviyesi olarak destekleyici kullanım",
        "Doktor veya eczacı önerisiyle uygun görülen takviye durumları",
    ],
    "solunum": [
        "Solunum yolu ile ilişkili bazı rahatsızlıklar",
        "Resmi kullanım bilgilerinde yer alan diğer uygun durumlar",
    ],
    "nöroloji": [
        "Nöroloji alanında doktor tarafından reçete edilen bazı durumlar",
        "Resmi kullanım bilgilerinde yer alan diğer uygun durumlar",
    ],
    "kardiyoloji": [
        "Kardiyoloji alanında doktor tarafından reçete edilen bazı durumlar",
        "Resmi kullanım bilgilerinde yer alan diğer uygun durumlar",
    ],
    "endokrin": [
        "Endokrin alanda doktor tarafından reçete edilen bazı durumlar",
        "Resmi kullanım bilgilerinde yer alan diğer uygun durumlar",
    ],
    "genel": [
        "Resmi kullanım bilgilerinde tanımlanan durumlar",
    ],
}

BASE_WARNINGS = [
    "Bu bilgiler kişisel tıbbi tavsiye yerine geçmez; doktorunuza veya eczacınıza danışın.",
    "Kullanmadan önce ürün prospektüsünü okuyun.",
    "Doz ve kullanım süresi için sağlık uzmanınızın önerisini takip edin.",
]

CATEGORY_EXTRA_WARNINGS: dict[str, list[str]] = {
    "antibiyotik": [
        "Antibiyotikler doktor önerisi olmadan kullanılmamalıdır.",
        "Tedavi süresi ve doz, hekim talimatına göre tamamlanmalıdır.",
    ],
}


SYSTEM_PROMPT = """
# Role
Sen bir ilaç bilgilendirme asistanısın. Kullanıcıya eşleşen ilaç hakkında
kısa, anlaşılır ve güvenli genel bilgi sunarsın.

# Objective
Asıl amacın "Bu ilaç nedir?" sorusuna teknik tanım yapmak değil;
"Bu ilaç hangi durumlarda kullanılabilir ve kullanıcı temel olarak ne bilmeli?"
sorusuna cevap vermektir.

# Input context
Sana yapılandırılmış ilaç kaydı verilir. Bu kayıtta ilaç adı, etken madde,
doz, form, kategori ve (varsa) kategoriye dayalı izinli kullanım alanları bulunur.
Resmi endikasyon / kontrendikasyon listesi veritabanında olmayabilir.

# Output schema
Yalnızca geçerli JSON döndür. Markdown, kod bloğu veya ek metin yazma.
Şema:
{
  "summary": "string",
  "usage": "string",
  "commonUses": ["string"],
  "activeIngredient": "string",
  "dose": "string",
  "form": "string",
  "category": "string",
  "warnings": ["string"],
  "disclaimer": "string"
}

# Medical safety rules
- Kişiye özel teşhis koyma.
- Kişinin semptomuna göre ilaç seçme.
- "Bu ilacı kullanmalısınız", "sizin için uygundur", "tavsiye edilir" deme.
- "Şu ağrınız varsa bunu kullanın" gibi ifadeler kullanma.
- Doz değiştirme veya reçete yerine geçecek öneri verme.
- Tercih edilen dil:
  - "Bu ilaç, resmi/kategori kullanım alanları arasında bulunan bazı durumlarda kullanılabilir."
  - "Bu tür durumlarda doktor tarafından reçete edilebilir."
  - "Kullanım için doktorunuzun veya eczacınızın önerisini takip edin."

# Hallucination prevention
- Verilmeyen ilaç bilgisini uydurma.
- İzinli kullanım listesi (allowed_common_uses) dışına çıkma.
- Kendi genel tıbbi bilginle ek hastalık/endikasyon ekleme.
- Spesifik hastalık adı (ör. migren, menisküs yırtığı) uydurma.
- allowed_common_uses boşsa commonUses = [] bırak ve usage içinde
  "Bu bilgi mevcut değil" de.
- warnings için yalnızca verilen allowed_warnings maddelerini kullan veya
  bunları anlamı bozmadan sadeleştir.

# Language / style rules
- Dil: Türkçe (aksi belirtilmedikçe), sade ve bilgilendirici.
- Teknik alanları (ad, doz, form, etken madde) summary içinde tekrar tekrar yazma.
- summary: 2-3 cümle; kullanım odaklı olsun.
- usage: 1-2 cümle; "hangi durumlarda kullanılabilir" odaklı olsun.
- commonUses: 3-5 madde (izinli listeden).
- warnings: 2-5 madde.

# Length limits
- Çok uzun tıbbi makale yazma.
- Mobil ekranda rahat okunacak kadar kısa tut.
""".strip()


@dataclass
class MedicineExplanation:
    """Structured medicine explanation."""

    summary: str
    usage: str = ""
    common_uses: list[str] = field(default_factory=list)
    active_ingredient: str | None = None
    dose: str | None = None
    form: str | None = None
    category: str | None = None
    warnings: list[str] = field(default_factory=list)
    disclaimer: str = LLM_EXPLANATION_DISCLAIMER

    @property
    def explanation_text(self) -> str:
        """Backward-compatible plain text (summary + usage)."""
        parts = [part.strip() for part in (self.summary, self.usage) if part.strip()]
        return " ".join(parts) if parts else FALLBACK_SUMMARY

    def to_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "usage": self.usage,
            "commonUses": list(self.common_uses),
            "activeIngredient": self.active_ingredient,
            "dose": self.dose,
            "form": self.form,
            "category": self.category,
            "warnings": list(self.warnings),
            "disclaimer": self.disclaimer,
        }

    def to_cache_payload(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)

    @classmethod
    def from_cache_payload(cls, payload: str) -> MedicineExplanation | None:
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            # Legacy cache: plain-text explanation.
            text = payload.strip()
            if not text:
                return None
            return cls(summary=text, disclaimer=LLM_EXPLANATION_DISCLAIMER)

        if not isinstance(data, dict):
            return None
        return normalize_explanation_payload(data)


class MedicineExplainer(Protocol):
    def explain(
        self,
        medicine: dict[str, str],
        *,
        locale: str = "tr",
    ) -> MedicineExplanation: ...


@dataclass(frozen=True)
class GeminiExplainResult:
    explanation: MedicineExplanation
    model: str


def _format_field(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    if not cleaned or cleaned == VERIFY_PLACEHOLDER:
        return None
    return cleaned


def _normalize_category_key(category: str | None) -> str:
    if not category:
        return ""
    return " ".join(category.strip().casefold().split())


def get_category_usage_hints(category: str | None) -> list[str]:
    key = _normalize_category_key(category)
    if not key:
        return []
    if key in CATEGORY_USAGE_HINTS:
        return list(CATEGORY_USAGE_HINTS[key])
    for hint_key, hints in CATEGORY_USAGE_HINTS.items():
        if hint_key in key or key in hint_key:
            return list(hints)
    return []


def get_allowed_warnings(category: str | None) -> list[str]:
    warnings = list(BASE_WARNINGS)
    key = _normalize_category_key(category)
    for cat_key, extra in CATEGORY_EXTRA_WARNINGS.items():
        if cat_key == key or cat_key in key:
            warnings.extend(extra)
    return warnings


def build_medicine_context(medicine: dict[str, str]) -> dict[str, Any]:
    """Structured medicine context sent to the LLM."""
    category = _format_field(medicine.get("category"))
    return {
        "name": _format_field(medicine.get("medicine_name")),
        "brand": _format_field(medicine.get("brand_name")),
        "activeIngredient": _format_field(medicine.get("active_ingredient")),
        "dose": _format_field(medicine.get("dosage")),
        "form": _format_field(medicine.get("form")),
        "category": category,
        "indications": [],
        "officialWarnings": [],
        "contraindications": [],
        "allowed_common_uses": get_category_usage_hints(category),
        "allowed_warnings": get_allowed_warnings(category),
        "data_notes": (
            "Resmi endikasyon, kontrendikasyon ve ilaç bazlı uyarı alanları "
            "veritabanında mevcut değil. Yalnızca kategoriye dayalı izinli "
            "kullanım maddeleri ile verilen alanları kullan."
        ),
    }


def _build_user_prompt(medicine: dict[str, str]) -> str:
    context = build_medicine_context(medicine)
    return (
        "Aşağıdaki ilaç kaydı için kullanıcı odaklı JSON açıklama üret.\n"
        "Yalnızca bu context'teki bilgilere dayan.\n\n"
        f"{json.dumps(context, ensure_ascii=False, indent=2)}"
    )


def _as_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        cleaned = value.strip()
        return [cleaned] if cleaned else []
    if isinstance(value, list):
        items: list[str] = []
        for item in value:
            if item is None:
                continue
            text = str(item).strip()
            if text:
                items.append(text)
        return items
    return []


def _extract_json_object(text: str) -> dict[str, Any] | None:
    cleaned = text.strip()
    if not cleaned:
        return None

    fence = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned, re.IGNORECASE)
    if fence:
        cleaned = fence.group(1).strip()

    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start >= 0 and end > start:
        try:
            parsed = json.loads(cleaned[start : end + 1])
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            return None
    return None


def normalize_explanation_payload(
    data: dict[str, Any],
    *,
    medicine: dict[str, str] | None = None,
) -> MedicineExplanation:
    """Validate LLM/cache JSON and apply fallbacks for missing fields."""
    summary = str(data.get("summary") or "").strip()
    usage = str(data.get("usage") or "").strip()
    common_uses = _as_string_list(
        data.get("commonUses", data.get("common_uses"))
    )
    warnings = _as_string_list(data.get("warnings"))
    disclaimer = str(data.get("disclaimer") or "").strip() or LLM_EXPLANATION_DISCLAIMER

    active = _format_field(
        str(data.get("activeIngredient") or data.get("active_ingredient") or "")
        or None
    )
    dose = _format_field(str(data.get("dose") or data.get("dosage") or "") or None)
    form = _format_field(str(data.get("form") or "") or None)
    category = _format_field(str(data.get("category") or "") or None)

    if medicine:
        active = active or _format_field(medicine.get("active_ingredient"))
        dose = dose or _format_field(medicine.get("dosage"))
        form = form or _format_field(medicine.get("form"))
        category = category or _format_field(medicine.get("category"))

    if not summary:
        summary = FALLBACK_SUMMARY

    if not common_uses and medicine:
        common_uses = get_category_usage_hints(medicine.get("category"))

    if not warnings:
        warnings = get_allowed_warnings(category or (medicine or {}).get("category"))

    # Length limits.
    common_uses = common_uses[:5]
    warnings = warnings[:5]

    return MedicineExplanation(
        summary=summary,
        usage=usage,
        common_uses=common_uses,
        active_ingredient=active,
        dose=dose,
        form=form,
        category=category,
        warnings=warnings,
        disclaimer=disclaimer,
    )


def parse_llm_explanation(
    raw_text: str,
    *,
    medicine: dict[str, str],
) -> MedicineExplanation:
    """Safely convert LLM text into a MedicineExplanation."""
    data = _extract_json_object(raw_text)
    if data is not None:
        return normalize_explanation_payload(data, medicine=medicine)

    # Plain-text fallback keeps the app from crashing.
    plain = re.sub(r"\s+", " ", raw_text).strip()
    return MedicineExplanation(
        summary=plain or FALLBACK_SUMMARY,
        usage="",
        common_uses=get_category_usage_hints(medicine.get("category")),
        active_ingredient=_format_field(medicine.get("active_ingredient")),
        dose=_format_field(medicine.get("dosage")),
        form=_format_field(medicine.get("form")),
        category=_format_field(medicine.get("category")),
        warnings=get_allowed_warnings(medicine.get("category")),
        disclaimer=LLM_EXPLANATION_DISCLAIMER,
    )


def build_mock_explanation(medicine: dict[str, str]) -> MedicineExplanation:
    name = _format_field(medicine.get("medicine_name")) or "Bu ilaç"
    ingredient = _format_field(medicine.get("active_ingredient"))
    category = _format_field(medicine.get("category"))
    common_uses = get_category_usage_hints(category)

    if ingredient and category:
        summary = (
            f"{name}, {ingredient} içeren ve {category} kategorisinde yer alan "
            f"bir ilaçtır."
        )
    elif ingredient:
        summary = f"{name}, {ingredient} içeren bir ilaçtır."
    elif category:
        summary = f"{name}, {category} kategorisinde yer alan bir ilaçtır."
    else:
        summary = f"{name} hakkında sınırlı katalog bilgisi bulunmaktadır."

    if common_uses:
        usage = (
            "Bu ilaç, kategoriye göre tanımlanan genel kullanım alanlarında "
            "doktor tarafından reçete edilebilir. Kullanım için doktorunuzun "
            "veya eczacınızın önerisini takip edin."
        )
    else:
        usage = (
            "Resmi kullanım alanı bu veri kaynağında mevcut değil. "
            "Detaylı bilgi için prospektüse ve eczacınıza danışın."
        )

    return MedicineExplanation(
        summary=summary,
        usage=usage,
        common_uses=common_uses,
        active_ingredient=ingredient,
        dose=_format_field(medicine.get("dosage")),
        form=_format_field(medicine.get("form")),
        category=category,
        warnings=get_allowed_warnings(category),
        disclaimer=LLM_EXPLANATION_DISCLAIMER,
    )


def _model_chain(primary: str) -> tuple[str, ...]:
    ordered: list[str] = []
    for candidate in (primary, *GEMINI_FREE_TIER_MODELS):
        if candidate and candidate not in ordered:
            ordered.append(candidate)
    return tuple(ordered)


def _is_retryable_gemini_error(exc: Exception) -> bool:
    message = str(exc).upper()
    return any(
        token in message
        for token in (
            "404",
            "429",
            "503",
            "NOT_FOUND",
            "RESOURCE_EXHAUSTED",
            "UNAVAILABLE",
            "HIGH DEMAND",
            "UNAUTHENTICATED",
            "PERMISSION_DENIED",
            "API_KEY_INVALID",
            "INVALID_API_KEY",
        )
    )


class MockMedicineExplainer:
    """Deterministic explanation for development and tests without an API key."""

    def explain(
        self,
        medicine: dict[str, str],
        *,
        locale: str = "tr",
    ) -> MedicineExplanation:
        _ = locale
        return build_mock_explanation(medicine)


class GeminiMedicineExplainer:
    """Generate medicine explanations with Google Gemini and model fallback."""

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
    ) -> MedicineExplanation:
        result = self.explain_with_model(medicine, locale=locale)
        return result.explanation

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
                response = self._generate(client, model=model, contents=contents)
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
                    explanation=parse_llm_explanation(text, medicine=medicine),
                    model=model,
                )

        joined = " ".join(errors).upper()
        if "429" in joined or "RESOURCE_EXHAUSTED" in joined:
            raise LlmUnavailableError(
                "LLM kotası aşıldı. Lütfen biraz sonra tekrar deneyin."
            )
        if "503" in joined or "UNAVAILABLE" in joined or "HIGH DEMAND" in joined:
            raise LlmUnavailableError(
                "Google Gemini şu anda yoğun. "
                "Birkaç saniye sonra tekrar deneyin."
            )

        logger.error("All Gemini models failed: %s", errors)
        raise LlmUnavailableError(
            "LLM servisi şu anda kullanılamıyor."
        )

    def _generate(self, client: Any, *, model: str, contents: str) -> Any:
        """Prefer JSON output and fall back to a plain request if unsupported."""
        try:
            from google.genai import types
        except ImportError:
            return client.models.generate_content(model=model, contents=contents)

        try:
            return client.models.generate_content(
                model=model,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
            )
        except Exception as exc:
            # Some models may not support the JSON MIME type.
            if "response_mime_type" in str(exc) or "INVALID_ARGUMENT" in str(exc):
                logger.info(
                    "JSON mime type unsupported for %s; retrying plain text",
                    model,
                )
                return client.models.generate_content(
                    model=model,
                    contents=contents,
                )
            raise


class LlmExplanationService:
    """Medicine explanation service with cache and provider selection."""

    _instance: LlmExplanationService | None = None

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
        self.cache = cache or get_shared_explanation_cache()
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
            cache=get_shared_explanation_cache(),
            provider=provider,
            model=model,
        )

    @classmethod
    def get_instance(cls, settings: ApiSettings) -> LlmExplanationService:
        """Return a single LLM service instance within the same process."""
        if cls._instance is None:
            cls._instance = cls.from_settings(settings)
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reset the service singleton for tests or reconfiguration."""
        cls._instance = None

    def explain_medicine(
        self,
        medicine: dict[str, str],
        *,
        locale: str = "tr",
    ) -> tuple[MedicineExplanation, bool]:
        medicine_id = medicine.get("medicine_id", "").strip()
        if not medicine_id:
            raise LlmUnavailableError("İlaç kimliği eksik.")

        if self.settings.llm_cache_enabled:
            cached = self.cache.get(medicine_id, locale)
            if cached:
                parsed = MedicineExplanation.from_cache_payload(cached)
                if parsed is not None:
                    return parsed, True

        try:
            if isinstance(self.explainer, GeminiMedicineExplainer):
                result = self.explainer.explain_with_model(medicine, locale=locale)
                explanation = result.explanation
                self.model = result.model
            else:
                explanation = self.explainer.explain(medicine, locale=locale)
        except LlmUnavailableError:
            logger.warning(
                "Gemini unavailable for %s; using catalog fallback.",
                medicine_id,
            )
            explanation = build_mock_explanation(medicine)
            self.model = "catalog-fallback"
            return explanation, False

        if self.settings.llm_cache_enabled:
            self.cache.set(medicine_id, locale, explanation.to_cache_payload())

        return explanation, False
