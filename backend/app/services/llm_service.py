from __future__ import annotations

import json
import logging
import re
from dataclasses import asdict, dataclass, field
from typing import Any, Protocol

from backend.app.config import ApiSettings
from backend.app.constants import (
    LLM_EXPLANATION_DISCLAIMER,
    disclaimer_for_locale,
)
from backend.app.exceptions import LlmNotConfiguredError, LlmUnavailableError
from backend.app.llm_models import GEMINI_FREE_TIER_MODELS
from backend.app.services.explanation_cache import (
    ExplanationCache,
    get_shared_explanation_cache,
)

logger = logging.getLogger(__name__)

VERIFY_PLACEHOLDER = "VERIFY_FROM_OFFICIAL_LEAFLET"

FALLBACK_SUMMARY = "Bu ilaç hakkında yeterli açıklayıcı bilgi bulunamadı."
FALLBACK_SUMMARY_EN = (
    "Not enough explanatory information was found for this medicine."
)

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

CATEGORY_USAGE_HINTS_EN: dict[str, list[str]] = {
    "ağrı kesici": [
        "Some mild to moderate pain situations",
        "Some illnesses that include fever",
        "Other pain situations a doctor considers appropriate",
    ],
    "kas ve eklem": [
        "Some musculoskeletal pain situations",
        "Some joint pain and inflammation situations",
        "Other appropriate situations listed in official use information",
    ],
    "kas-iskelet": [
        "Some musculoskeletal pain situations",
        "Some joint and soft-tissue complaints",
        "Other appropriate situations listed in official use information",
    ],
    "kas gevşetici": [
        "Some situations related to muscle tightness",
        "Some musculoskeletal complaints",
        "Other situations a doctor considers appropriate",
    ],
    "antibiyotik": [
        "Bacterial infections prescribed by a doctor",
        "Infection types described in official use information",
    ],
    "soğuk algınlığı": [
        "Temporary relief of some cold-related complaints",
        "Managing symptoms such as nasal congestion, fever, or pain",
    ],
    "öksürük ilacı": [
        "Some respiratory complaints related to cough",
        "Cough situations a doctor or pharmacist considers appropriate",
    ],
    "mide": [
        "Some complaints related to heartburn, indigestion, or acid",
        "Other gastrointestinal situations listed in official use information",
    ],
    "mide ilacı": [
        "Some complaints related to heartburn, indigestion, or acid",
        "Other gastrointestinal situations listed in official use information",
    ],
    "vitamin ve mineral": [
        "Situations that need vitamin or mineral supplementation",
        "Supportive use with doctor or pharmacist advice",
    ],
    "food supplement": [
        "Supportive use as a food supplement",
        "Supplement situations a doctor or pharmacist considers appropriate",
    ],
    "solunum": [
        "Some respiratory complaints",
        "Other appropriate situations listed in official use information",
    ],
    "nöroloji": [
        "Some neurology situations prescribed by a doctor",
        "Other appropriate situations listed in official use information",
    ],
    "kardiyoloji": [
        "Some cardiology situations prescribed by a doctor",
        "Other appropriate situations listed in official use information",
    ],
    "endokrin": [
        "Some endocrine situations prescribed by a doctor",
        "Other appropriate situations listed in official use information",
    ],
    "genel": [
        "Situations described in official use information",
    ],
}

BASE_WARNINGS_EN = [
    "This information does not replace personal medical advice; consult a doctor or pharmacist.",
    "Read the product leaflet before use.",
    "Follow a healthcare professional for dose and duration.",
]

CATEGORY_EXTRA_WARNINGS_EN: dict[str, list[str]] = {
    "antibiyotik": [
        "Antibiotics must not be used without a doctor's advice.",
        "Complete the dose and duration as instructed by a physician.",
    ],
}


SYSTEM_PROMPT = """
# Role
You are a medicine-information assistant. Give short, clear, and safe general
information about a matched medicine.

# Objective
Do not write a technical definition of "what is this drug?".
Answer: "In which situations can this medicine be used, and what should the
user know at a basic level?"

# Input context
You receive a structured medicine record: name, active ingredient, dose, form,
category, and (when present) category-based allowed use items.
Official indication / contraindication lists may be missing from the database.

# Output schema
Return valid JSON only. Do not write markdown, code fences, or extra text.
Schema:
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
- Do not diagnose a specific person.
- Do not choose a medicine based on the user's symptoms.
- Do not say "you should use this", "this is suitable for you", or "it is recommended".
- Do not say "if you have this pain, use this".
- Do not change the dose or replace a prescription.
- Prefer wording such as:
  - "This medicine may be used in some situations listed among official/category uses."
  - "A doctor may prescribe it in these kinds of situations."
  - "Follow your doctor or pharmacist for use."

# Hallucination prevention
- Do not invent medicine facts that were not provided.
- Stay inside the allowed_common_uses list.
- Do not add extra diseases/indications from general medical knowledge.
- Do not invent specific disease names (for example migraine, meniscus tear).
- If allowed_common_uses is empty, leave commonUses = [] and say
  "This information is not available" in usage.
- For warnings, use only allowed_warnings items, or simplify them without
  changing the meaning.

# Language / style rules
- Write all JSON string values in the language given at the end of the user prompt.
- Do not repeat technical fields (name, dose, form, active ingredient) over and over in summary.
- summary: 2-3 sentences, usage-focused.
- usage: 1-2 sentences, focused on "in which situations it may be used".
- commonUses: 3-5 items from the allowed list.
- warnings: 2-5 items.

# Length limits
- Do not write a long medical article.
- Keep it short enough to read comfortably on a mobile screen.
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


def _locale_is_english(locale: str) -> bool:
    return (locale or "tr").strip().lower().startswith("en")


def _fallback_summary(locale: str = "tr") -> str:
    return FALLBACK_SUMMARY_EN if _locale_is_english(locale) else FALLBACK_SUMMARY


def _lookup_category_hints(
    table: dict[str, list[str]],
    category: str | None,
) -> list[str]:
    key = _normalize_category_key(category)
    if not key:
        return []
    if key in table:
        return list(table[key])
    for hint_key, hints in table.items():
        if hint_key in key or key in hint_key:
            return list(hints)
    return []


def get_category_usage_hints(
    category: str | None,
    *,
    locale: str = "tr",
) -> list[str]:
    table = (
        CATEGORY_USAGE_HINTS_EN
        if _locale_is_english(locale)
        else CATEGORY_USAGE_HINTS
    )
    return _lookup_category_hints(table, category)


def get_allowed_warnings(
    category: str | None,
    *,
    locale: str = "tr",
) -> list[str]:
    extra_table = (
        CATEGORY_EXTRA_WARNINGS_EN
        if _locale_is_english(locale)
        else CATEGORY_EXTRA_WARNINGS
    )
    warnings = list(
        BASE_WARNINGS_EN if _locale_is_english(locale) else BASE_WARNINGS
    )
    key = _normalize_category_key(category)
    for cat_key, extra in extra_table.items():
        if cat_key == key or cat_key in key:
            warnings.extend(extra)
    return warnings


def build_medicine_context(
    medicine: dict[str, str],
    *,
    locale: str = "tr",
) -> dict[str, Any]:
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
        "allowed_common_uses": get_category_usage_hints(category, locale="en"),
        "allowed_warnings": get_allowed_warnings(category, locale="en"),
        "data_notes": (
            "Official indication, contraindication, and per-medicine warning "
            "fields are not in the database. Use only the allowed category-based "
            "use items and the fields provided."
        ),
    }


def _build_user_prompt(medicine: dict[str, str], *, locale: str = "tr") -> str:
    context = build_medicine_context(medicine, locale=locale)
    language = "English" if _locale_is_english(locale) else "Turkish"
    return (
        "Produce a user-focused JSON explanation for the medicine record below.\n"
        "Rely only on this context.\n\n"
        f"{json.dumps(context, ensure_ascii=False, indent=2)}\n\n"
        f"Write all JSON string values in {language}."
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
    locale: str = "tr",
) -> MedicineExplanation:
    """Validate LLM/cache JSON and apply fallbacks for missing fields."""
    summary = str(data.get("summary") or "").strip()
    usage = str(data.get("usage") or "").strip()
    common_uses = _as_string_list(
        data.get("commonUses", data.get("common_uses"))
    )
    warnings = _as_string_list(data.get("warnings"))
    disclaimer = (
        str(data.get("disclaimer") or "").strip()
        or disclaimer_for_locale(locale)
    )

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
        summary = _fallback_summary(locale)

    if not common_uses and medicine:
        common_uses = get_category_usage_hints(
            medicine.get("category"),
            locale=locale,
        )

    if not warnings:
        warnings = get_allowed_warnings(
            category or (medicine or {}).get("category"),
            locale=locale,
        )

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
    locale: str = "tr",
) -> MedicineExplanation:
    """Safely convert LLM text into a MedicineExplanation."""
    data = _extract_json_object(raw_text)
    if data is not None:
        return normalize_explanation_payload(
            data,
            medicine=medicine,
            locale=locale,
        )

    # Plain-text fallback keeps the app from crashing.
    plain = re.sub(r"\s+", " ", raw_text).strip()
    return MedicineExplanation(
        summary=plain or _fallback_summary(locale),
        usage="",
        common_uses=get_category_usage_hints(
            medicine.get("category"),
            locale=locale,
        ),
        active_ingredient=_format_field(medicine.get("active_ingredient")),
        dose=_format_field(medicine.get("dosage")),
        form=_format_field(medicine.get("form")),
        category=_format_field(medicine.get("category")),
        warnings=get_allowed_warnings(medicine.get("category"), locale=locale),
        disclaimer=disclaimer_for_locale(locale),
    )


def build_mock_explanation(
    medicine: dict[str, str],
    *,
    locale: str = "tr",
) -> MedicineExplanation:
    english = _locale_is_english(locale)
    name = _format_field(medicine.get("medicine_name")) or (
        "This medicine" if english else "Bu ilaç"
    )
    ingredient = _format_field(medicine.get("active_ingredient"))
    category = _format_field(medicine.get("category"))
    common_uses = get_category_usage_hints(category, locale=locale)

    if english:
        if ingredient and category:
            summary = (
                f"{name} is a {category} medicine that contains {ingredient}."
            )
        elif ingredient:
            summary = f"{name} contains {ingredient}."
        elif category:
            summary = f"{name} is listed in the {category} category."
        else:
            summary = f"Limited catalog information is available for {name}."
        if common_uses:
            usage = (
                "A doctor may prescribe this medicine in the general use areas "
                "defined for its category. Follow your doctor or pharmacist "
                "for use."
            )
        else:
            usage = (
                "Official use information is not available in this data source. "
                "Ask a pharmacist and read the leaflet for details."
            )
    else:
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
        warnings=get_allowed_warnings(category, locale=locale),
        disclaimer=disclaimer_for_locale(locale),
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
        return build_mock_explanation(medicine, locale=locale)


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
                    "google-genai is not installed."
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
        prompt = _build_user_prompt(medicine, locale=locale)

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
                    "LLM service is currently unavailable."
                ) from exc
            else:
                text = getattr(response, "text", None)
                if not text or not text.strip():
                    errors.append(f"{model}: empty response")
                    continue

                self.last_model_used = model
                return GeminiExplainResult(
                    explanation=parse_llm_explanation(
                        text,
                        medicine=medicine,
                        locale=locale,
                    ),
                    model=model,
                )

        joined = " ".join(errors).upper()
        if "429" in joined or "RESOURCE_EXHAUSTED" in joined:
            raise LlmUnavailableError(
                "LLM quota exceeded. Please try again in a moment."
            )
        if "503" in joined or "UNAVAILABLE" in joined or "HIGH DEMAND" in joined:
            raise LlmUnavailableError(
                "Google Gemini is currently busy. "
                "Please try again in a few seconds."
            )

        logger.error("All Gemini models failed: %s", errors)
        raise LlmUnavailableError(
            "LLM service is currently unavailable."
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
            raise LlmUnavailableError("Medicine id is missing.")

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
            explanation = build_mock_explanation(medicine, locale=locale)
            self.model = "catalog-fallback"
            return explanation, False

        if self.settings.llm_cache_enabled:
            self.cache.set(medicine_id, locale, explanation.to_cache_payload())

        return explanation, False
