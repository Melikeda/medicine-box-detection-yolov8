from src.matching.medicine_matcher import (
    is_dosage_or_form_only_text,
    normalize_text,
)
from src.matching.text_normalizer import normalize_ocr_text
from src.services.config import PipelineConfig
from src.services.matching_service import (
    MatchingService,
    is_reliable_medicine_match,
)


def test_normalize_ocr_euro_to_c() -> None:
    assert normalize_ocr_text("ibucold €") == "ibucold c"


def test_normalize_text_uses_ocr_normalizer() -> None:
    assert normalize_text("  Ibucold  €  ") == "ibucold c"


def test_dosage_only_text_is_detected() -> None:
    assert is_dosage_or_form_only_text(
        "250 mo / j0o mo tablot"
    )


def test_brand_with_dosage_is_not_dosage_only() -> None:
    assert not is_dosage_or_form_only_text("Parol 500 mg")


def test_partial_brand_match_accepts_fen(
    seeded_pipeline_config: PipelineConfig,
) -> None:
    service = MatchingService.from_sqlite(
        seeded_pipeline_config,
        seed_from_csv=False,
    )
    result = service.match_text(["fen"])

    assert result.status == "matched"
    assert result.medicine_name == "Nurofen Cold & Flu"
    assert result.matching_score >= 85.0


def test_ibucold_euro_matches_ibucold_c(
    seeded_pipeline_config: PipelineConfig,
) -> None:
    service = MatchingService.from_sqlite(
        seeded_pipeline_config,
        seed_from_csv=False,
    )
    result = service.match_text(["ibucold €"])

    assert result.status == "matched"
    assert result.medicine_name == "Ibucold C"


def test_dosage_ocr_does_not_false_match_nurofen(
    seeded_pipeline_config: PipelineConfig,
) -> None:
    service = MatchingService.from_sqlite(
        seeded_pipeline_config,
        seed_from_csv=False,
    )
    result = service.match_text(["250 mo / j0o mo tablot"])

    assert result.status == "not_found"
    assert result.medicine_name is None


def test_single_letter_is_not_reliable_match() -> None:
    assert not is_reliable_medicine_match(
        query_text="s",
        medicine_name="Gaviscon",
        minimum_text_length=3,
        minimum_name_coverage_ratio=0.45,
    )


def test_parafon_exact_match(
    seeded_pipeline_config: PipelineConfig,
) -> None:
    service = MatchingService.from_sqlite(
        seeded_pipeline_config,
        seed_from_csv=False,
    )
    result = service.match_text(["parafon"])

    assert result.status == "matched"
    assert result.medicine_name == "Parafon"
    assert result.matching_score == 100.0
