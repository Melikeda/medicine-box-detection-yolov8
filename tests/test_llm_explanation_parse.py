"""
LLM explanation parsing and fallback unit tests.
"""

from backend.app.services.llm_service import (
    MedicineExplanation,
    build_medicine_context,
    build_mock_explanation,
    get_category_usage_hints,
    normalize_explanation_payload,
    parse_llm_explanation,
)


def _etol() -> dict[str, str]:
    return {
        "medicine_id": "MED020",
        "medicine_name": "Etol Fort",
        "brand_name": "Etol",
        "active_ingredient": "Etodolac",
        "dosage": "400 MG",
        "form": "Film Coated Tablet",
        "category": "Kas ve Eklem",
    }


def test_category_usage_hints_for_muscle_joint() -> None:
    hints = get_category_usage_hints("Kas ve Eklem")
    assert hints
    assert any("eklem" in item.casefold() for item in hints)


def test_build_medicine_context_includes_allowed_uses() -> None:
    context = build_medicine_context(_etol())
    assert context["name"] == "Etol Fort"
    assert context["activeIngredient"] == "Etodolac"
    assert context["allowed_common_uses"]
    assert context["indications"] == []
    assert "not in the database" in context["data_notes"].lower()


def test_parse_valid_json_explanation() -> None:
    raw = """
    {
      "summary": "Etol Fort, etodolak içeren bir ilaçtır.",
      "usage": "Kas-iskelet kaynaklı bazı durumlarda kullanılabilir.",
      "commonUses": ["Eklem kaynaklı bazı ağrı durumları"],
      "activeIngredient": "Etodolac",
      "dose": "400 MG",
      "form": "Film Coated Tablet",
      "category": "Kas ve Eklem",
      "warnings": ["Doktorunuza danışın."],
      "disclaimer": "Tıbbi tavsiye değildir."
    }
    """
    result = parse_llm_explanation(raw, medicine=_etol())
    assert "Etol Fort" in result.summary
    assert result.common_uses == ["Eklem kaynaklı bazı ağrı durumları"]
    assert result.warnings == ["Doktorunuza danışın."]
    assert result.dose == "400 MG"


def test_parse_fenced_json_explanation() -> None:
    raw = """```json
    {"summary": "Kısa özet", "usage": "", "commonUses": [], "warnings": []}
    ```"""
    result = parse_llm_explanation(raw, medicine=_etol())
    assert result.summary == "Kısa özet"
    # Fall back to the category when commonUses is empty.
    assert result.common_uses


def test_parse_invalid_json_falls_back_to_plain_text() -> None:
    raw = "Bu ilaç hakkında genel bir düz metin açıklama."
    result = parse_llm_explanation(raw, medicine=_etol())
    assert result.summary.startswith("Bu ilaç hakkında")
    assert result.common_uses  # category fallback
    assert result.warnings


def test_normalize_missing_summary_uses_fallback() -> None:
    result = normalize_explanation_payload({}, medicine=_etol())
    assert "yeterli açıklayıcı bilgi" in result.summary.casefold()


def test_mock_explanation_is_usage_focused() -> None:
    result = build_mock_explanation(_etol())
    assert "Etol Fort" in result.summary
    assert result.common_uses
    assert "tavsiye edilir" not in result.summary.casefold()
    assert "kullanmalısınız" not in result.usage.casefold()
    text = result.explanation_text.casefold()
    assert "etodolac" in text or "kas" in text


def test_mock_explanation_english_locale() -> None:
    result = build_mock_explanation(_etol(), locale="en")
    assert "Etol Fort" in result.summary
    assert "contains" in result.summary.lower() or "medicine" in result.summary.lower()
    assert any("joint" in item.lower() or "muscle" in item.lower() for item in result.common_uses)
    assert "medical advice" in result.disclaimer.lower()


def test_antibiotic_mock_has_extra_warning() -> None:
    medicine = {
        "medicine_id": "MED027",
        "medicine_name": "Augmentin",
        "active_ingredient": "Amoxicillin And Enzyme Inhibitor",
        "dosage": "500 MG/125 MG",
        "form": "Film Coated Tablet",
        "category": "Antibiyotik",
    }
    result = build_mock_explanation(medicine)
    assert any("antibiyotik" in item.casefold() for item in result.warnings)


def test_vitamin_mock_has_category_uses() -> None:
    medicine = {
        "medicine_id": "MED030",
        "medicine_name": "Supradyn",
        "active_ingredient": "Multivitamin / Mineral",
        "dosage": "Combined tablet",
        "form": "Film Coated Tablet",
        "category": "Vitamin ve Mineral",
    }
    result = build_mock_explanation(medicine)
    assert result.common_uses
    assert any("vitamin" in item.casefold() for item in result.common_uses)


def test_missing_category_does_not_invent_uses() -> None:
    medicine = {
        "medicine_id": "MED999",
        "medicine_name": "Bilinmeyen",
        "active_ingredient": "X",
        "dosage": "10 mg",
        "form": "Tablet",
        "category": "",
    }
    result = build_mock_explanation(medicine)
    assert result.common_uses == []
    assert "mevcut değil" in result.usage.casefold()


def test_cache_roundtrip_structured() -> None:
    original = build_mock_explanation(_etol())
    restored = MedicineExplanation.from_cache_payload(original.to_cache_payload())
    assert restored is not None
    assert restored.summary == original.summary
    assert restored.common_uses == original.common_uses
    assert restored.warnings == original.warnings


def test_legacy_plain_cache_payload_still_works() -> None:
    restored = MedicineExplanation.from_cache_payload("Eski düz metin açıklama")
    assert restored is not None
    assert restored.summary == "Eski düz metin açıklama"
