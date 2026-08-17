from src.matching.medicine_matcher import (
    find_best_medicine_match,
    is_dosage_or_form_only_text,
    is_generic_active_ingredient,
    normalize_text,
)
from src.matching.text_normalizer import is_garbage_ocr_text
from src.matching.text_normalizer import normalize_ocr_text
from src.services.candidate_processor import (
    has_weak_ocr_candidates,
    max_candidate_alpha_length,
)
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


def test_normalize_ocr_strips_registered_mark() -> None:
    assert normalize_ocr_text("Levopront® 60 mg") == "levopront 60 mg"


def test_brand_plus_dose_line_matches_levopront(
    seeded_pipeline_config: PipelineConfig,
) -> None:
    service = MatchingService.from_sqlite(
        seeded_pipeline_config,
        seed_from_csv=False,
    )
    result = service.match_text(
        ["Levopront® 60 mg", "Tablet", "Dompé", "ABDİİBRAHİM"]
    )
    assert result.status == "matched"
    assert result.medicine_name == "Levopront"


def test_short_suffix_fragment_does_not_match_nurofen(
    seeded_pipeline_config: PipelineConfig,
) -> None:
    service = MatchingService.from_sqlite(
        seeded_pipeline_config,
        seed_from_csv=False,
    )
    result = service.match_text(["fen"])

    assert result.status != "matched"
    assert result.medicine_name != "Nurofen"


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
        minimum_text_length=5,
        minimum_name_coverage_ratio=0.55,
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
    """A brand should not be selected when OCR reads only the active ingredient (Nurofen -> Brufen bug)."""
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
    """Reversed Biteral OCR (ornldarol) must not match Parol Plus."""
    service = MatchingService.from_sqlite(
        seeded_pipeline_config,
        seed_from_csv=False,
    )
    result = service.match_text(["ornldarol"])

    assert result.status != "matched"
    assert result.medicine_name != "Parol Plus"
    assert result.medicine_name != "Parol"


def test_ferrum_matches_and_not_pharmaton() -> None:
    """Ferrum OCR should hit Ferrum catalog rows, never Pharmaton."""
    from pathlib import Path

    config = PipelineConfig(
        medicines_csv_path=Path("data/database/medicines.csv"),
        use_sqlite=False,
    )
    service = MatchingService.from_config(config)
    result = service.match_text(["FERRUM", "Ferrum Hausmann"])

    assert result.status == "matched"
    assert result.medicine_name is not None
    assert "ferrum" in result.medicine_name.lower()
    assert "pharmaton" not in result.medicine_name.lower()


def test_unknown_brand_returns_not_found_not_wrong_drug() -> None:
    """A clear brand token outside the catalog must not match another medicine."""
    from pathlib import Path

    config = PipelineConfig(
        medicines_csv_path=Path("data/database/medicines.csv"),
        use_sqlite=False,
    )
    service = MatchingService.from_config(config)
    result = service.match_text(["ZYXNOTREALBRAND", "ENDOXYZFAKE"])

    assert result.status != "matched"
    assert result.medicine_name is None


def test_has_weak_ocr_candidates_detects_short_reads() -> None:
    assert has_weak_ocr_candidates(["lie"])
    assert has_weak_ocr_candidates(["lie", "mg"])
    assert not has_weak_ocr_candidates(["levopront"])
    assert max_candidate_alpha_length(["lie", "levopront"]) == 9


def test_suffix_ocr_fragments_do_not_pick_wrong_brand() -> None:
    """Phone-photo failures: 3-letter suffixes must not become a drug card."""
    from pathlib import Path

    config = PipelineConfig(
        medicines_csv_path=Path("data/database/medicines.csv"),
        use_sqlite=False,
    )
    service = MatchingService.from_config(config)

    cases = (
        ("alm", "Mydocalm"),
        ("pal", "Gripal"),
        ("dex", "Dodex"),
        ("uno", "Imunol Defence"),
        ("ocalm", "Mydocalm"),
    )
    for ocr_text, forbidden_name in cases:
        result = service.match_text([ocr_text])
        assert result.status != "matched", ocr_text
        assert result.medicine_name != forbidden_name, ocr_text


def test_exact_short_brand_etol_still_matches(
    seeded_pipeline_config: PipelineConfig,
) -> None:
    service = MatchingService.from_sqlite(
        seeded_pipeline_config,
        seed_from_csv=False,
    )
    result = service.match_text(["etol"])

    assert result.status == "matched"
    assert result.medicine_name is not None
    assert "etol" in result.medicine_name.lower()


def test_full_brand_reads_still_match(
    seeded_pipeline_config: PipelineConfig,
) -> None:
    service = MatchingService.from_sqlite(
        seeded_pipeline_config,
        seed_from_csv=False,
    )

    parol = service.match_text(["parol"])
    nurofen = service.match_text(["nurofen"])

    assert parol.status == "matched"
    assert parol.medicine_name == "Parol"
    assert parol.matching_score == 100.0
    assert nurofen.status == "matched"
    assert nurofen.medicine_name == "Nurofen"
