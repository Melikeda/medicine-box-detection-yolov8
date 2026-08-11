"""Marka varyanti disambiguation + failure_reason siniflandirmasi."""

from src.matching.brand_disambiguation import (
    disambiguate_brand_family_matches,
    evidence_alignment_boost,
    is_base_sku,
)
from src.matching.medicine_matcher import find_best_medicine_match
from src.services.config import PipelineConfig
from src.services.failure_reasons import (
    classify_box_failure,
    hint_for,
    is_bbox_partial,
)
from src.services.matching_service import MatchingService
from src.services.detection import BoundingBox


def _load_csv_service() -> MatchingService:
    from pathlib import Path

    config = PipelineConfig(
        medicines_csv_path=Path("data/database/medicines.csv"),
        use_sqlite=False,
    )
    return MatchingService.from_config(config)


def test_parol_alone_prefers_base_not_plus() -> None:
    service = _load_csv_service()
    result = service.match_text(["Parol", "500 mg", "Tablet"])

    assert result.status == "matched"
    assert result.medicine_name == "Parol"


def test_parol_plus_ocr_selects_plus() -> None:
    service = _load_csv_service()
    result = service.match_text(["Parol Plus", "Tablet"])

    assert result.status == "matched"
    assert result.medicine_name == "Parol Plus"


def test_majezik_tablet_not_gargara() -> None:
    service = _load_csv_service()
    result = service.match_text(
        ["Majezik", "100 mg", "Film Tablet", "Flurbiprofen"]
    )

    assert result.status == "matched"
    assert result.medicine_name == "Majezik"
    assert "Gargara" not in (result.medicine_name or "")


def test_majezik_gargara_when_token_present() -> None:
    service = _load_csv_service()
    result = service.match_text(["Majezik", "Gargara", "%0,25"])

    assert result.status == "matched"
    assert result.medicine_name is not None
    assert "Gargara" in result.medicine_name


def test_dolorex_tablet_not_jel() -> None:
    service = _load_csv_service()
    result = service.match_text(
        ["Dolorex", "50 mg", "Tablet", "Diclofenac"]
    )

    assert result.status == "matched"
    assert result.medicine_name == "Dolorex"
    assert "Jel" not in (result.medicine_name or "")


def test_dolorex_jel_when_token_present() -> None:
    service = _load_csv_service()
    result = service.match_text(["Dolorex", "%1", "Jel", "50 G"])

    assert result.status == "matched"
    assert result.medicine_name is not None
    assert "Jel" in result.medicine_name


def test_find_best_majezik_alone_is_base() -> None:
    from pathlib import Path

    from src.database.csv_reader import load_medicines

    medicines = load_medicines(Path("data/database/medicines.csv"))
    medicine, score, name = find_best_medicine_match(
        query_text="Majezik",
        medicines=medicines,
    )

    assert medicine is not None
    assert name == "Majezik"
    assert score >= 88.0
    assert is_base_sku(medicine)


def test_disambiguate_reorders_gargara_behind_base() -> None:
    from pathlib import Path

    from src.database.csv_reader import load_medicines

    medicines = load_medicines(Path("data/database/medicines.csv"))
    majezik = next(m for m in medicines if m["medicine_id"] == "MED006")
    gargara = next(m for m in medicines if m["medicine_id"] == "MED044")

    ranked = [
        (gargara, 100.0, "Majezik"),
        (majezik, 100.0, "Majezik"),
    ]
    evidence = ["Majezik", "100 mg", "Film Tablet"]
    result = disambiguate_brand_family_matches(
        ranked,
        evidence_texts=evidence,
        all_medicines=medicines,
    )

    assert result[0][0]["medicine_id"] == "MED006"
    assert evidence_alignment_boost(majezik, " ".join(evidence).lower()) > (
        evidence_alignment_boost(gargara, " ".join(evidence).lower())
    )


def test_failure_hint_partial_and_blurry() -> None:
    assert "yarim" in hint_for("partial_box").lower() or "tamam" in hint_for(
        "partial_box"
    ).lower()
    assert "bulanik" in hint_for("blurry").lower()


def test_is_bbox_partial_detects_edge() -> None:
    assert is_bbox_partial(
        x1=0,
        y1=10,
        x2=100,
        y2=200,
        image_width=1000,
        image_height=1000,
    )
    assert not is_bbox_partial(
        x1=100,
        y1=100,
        x2=400,
        y2=400,
        image_width=1000,
        image_height=1000,
    )


def test_classify_not_found_readable_as_not_in_catalog() -> None:
    info = classify_box_failure(
        status="not_found",
        matching_score=90.0,
        ocr_text="SomeKnownLookingBrandName",
        candidate_texts=["SomeKnownLookingBrandName"],
        bounding_box=BoundingBox(x1=50, y1=50, x2=200, y2=200),
        image_width=800,
        image_height=600,
    )

    assert info is not None
    assert info.reason == "not_in_catalog"
    assert info.hint


def test_classify_matched_returns_none() -> None:
    assert (
        classify_box_failure(
            status="matched",
            matching_score=100.0,
            ocr_text="Parol",
        )
        is None
    )


def test_match_text_sets_failure_reason_when_unmatched() -> None:
    service = _load_csv_service()
    result = service.match_text(["ZYXNOTREALBRANDXYZ"])

    assert result.status != "matched"
    assert result.failure_reason is not None
    assert result.hint is not None
