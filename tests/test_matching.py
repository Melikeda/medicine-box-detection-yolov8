from src.matching.medicine_matcher import (
    find_best_medicine_match,
    is_dosage_or_form_only_text,
    is_generic_active_ingredient,
    normalize_text,
)
from src.matching.text_normalizer import is_garbage_ocr_text
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


def test_ibuprofen_only_ocr_does_not_false_match_brufen(
    seeded_pipeline_config: PipelineConfig,
) -> None:
    """Etken madde tek basina okunursa marka secilmemeli (Nurofen -> Brufen hatasi)."""
    service = MatchingService.from_sqlite(
        seeded_pipeline_config,
        seed_from_csv=False,
    )
    result = service.match_text(["ibuprofen"])

    assert result.status == "not_found"
    assert result.medicine_name is None


def test_nurofen_brand_still_matches_cold_and_flu(
    seeded_pipeline_config: PipelineConfig,
) -> None:
    service = MatchingService.from_sqlite(
        seeded_pipeline_config,
        seed_from_csv=False,
    )
    result = service.match_text(["nurofen cold flu"])

    assert result.status == "matched"
    assert result.medicine_name == "Nurofen Cold & Flu"


def test_find_best_medicine_match_rejects_generic_active_ingredient() -> None:
    from pathlib import Path

    from src.database.csv_reader import load_medicines

    medicines = load_medicines(
        csv_path=Path("data/database/medicines.csv"),
    )
    medicine, score, _ = find_best_medicine_match(
        query_text="ibuprofen",
        medicines=medicines,
    )

    assert medicine is None
    assert score == 0.0
    assert is_generic_active_ingredient("ibuprofen")


def test_garbage_ocr_text_is_detected() -> None:
    assert is_garbage_ocr_text("1778v1 7dv~ ww 6w oc / bw od7")
    assert not is_garbage_ocr_text("omesek")
    assert not is_garbage_ocr_text("ibucold")


def test_garbage_ocr_does_not_false_match_iburamin(
    seeded_pipeline_config: PipelineConfig,
) -> None:
    service = MatchingService.from_sqlite(
        seeded_pipeline_config,
        seed_from_csv=False,
    )
    result = service.match_text(
        ["1778v1 7dv~ ww 6w oc / bw od7"]
    )

    assert result.status != "matched"
    assert result.medicine_name != "Iburamin Cold"


def test_levopront_and_biteral_match_when_ocr_reads_brand(
    seeded_pipeline_config: PipelineConfig,
) -> None:
    service = MatchingService.from_sqlite(
        seeded_pipeline_config,
        seed_from_csv=False,
    )

    levopront = service.match_text(["levopront"])
    biteral = service.match_text(["biteral"])
    nurofen = service.match_text(["nurofen cold flu"])

    assert levopront.status == "matched"
    assert levopront.medicine_name == "Levopront"
    assert biteral.status == "matched"
    assert biteral.medicine_name == "Biteral"
    assert nurofen.status == "matched"
    assert nurofen.medicine_name == "Nurofen Cold & Flu"


def test_ornldarol_garbage_does_not_false_match_parol(
    seeded_pipeline_config: PipelineConfig,
) -> None:
    """Ters Biteral OCR (ornldarol) Parol Plus ile eslesmemeli."""
    service = MatchingService.from_sqlite(
        seeded_pipeline_config,
        seed_from_csv=False,
    )
    result = service.match_text(["ornldarol"])

    assert result.status != "matched"
    assert result.medicine_name != "Parol Plus"
    assert result.medicine_name != "Parol"
