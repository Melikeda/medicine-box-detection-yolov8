"""
Barcode normalization, decoding, and catalog matching tests.
"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

import cv2
import numpy as np
import pytest
from barcode import EAN13
from barcode.writer import ImageWriter
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.config import ApiSettings, get_api_settings
from backend.app.exceptions import register_exception_handlers
from backend.app.routers import barcode as barcode_router
from backend.app.services.medicine_service import MedicineQueryService
from src.barcode.decoder import decode_barcodes
from src.barcode.normalize import is_plausible_barcode, normalize_barcode
from src.database.repository import (
    get_medicine_by_barcode,
    seed_medicines_from_csv,
)
from src.database.session import session_scope
from src.services.config import PipelineConfig
from src.services.matching_service import MatchingService


def _ean13_png(digits12: str) -> tuple[str, bytes]:
    buffer = BytesIO()
    ean = EAN13(digits12, writer=ImageWriter())
    ean.write(buffer, options={"write_text": False, "quiet_zone": 6.5})
    return str(ean.get_fullcode()), buffer.getvalue()


def _png_to_bgr(png_bytes: bytes) -> np.ndarray:
    array = np.frombuffer(png_bytes, dtype=np.uint8)
    image = cv2.imdecode(array, cv2.IMREAD_COLOR)
    assert image is not None
    return image


def test_normalize_ean13_and_gs1_datamatrix() -> None:
    assert normalize_barcode("869 9522 09047 3") == "8699522090473"
    assert normalize_barcode("0108699522090473") == "8699522090473"
    assert normalize_barcode("(01)08699522090473") == "8699522090473"
    assert is_plausible_barcode("8699522090473")
    from src.barcode.normalize import barcode_lookup_keys

    keys = barcode_lookup_keys("010869952209047317250101")
    assert "8699522090473" in keys
    assert normalize_barcode("]C18699832090055") == "8699832090055"
    assert normalize_barcode("]E08699522090473") == "8699522090473"
    aim_keys = barcode_lookup_keys("]C18699832090055")
    assert "8699832090055" in aim_keys
    assert "18699832090055" not in aim_keys


def test_decode_generated_ean13() -> None:
    full_code, png_bytes = _ean13_png("869952209047")
    decoded = decode_barcodes(_png_to_bgr(png_bytes))
    assert decoded
    assert decoded[0].normalized == full_code


def test_decode_without_zxing_returns_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    import src.barcode.decoder as decoder

    monkeypatch.setattr(decoder, "_zxingcpp", None)
    monkeypatch.setattr(decoder, "_zxing_checked", True)
    image = np.zeros((40, 40, 3), dtype=np.uint8)
    assert decoder.decode_barcodes(image) == []


def test_seed_and_lookup_barcode(
    sample_csv_path: Path,
    sqlite_path: Path,
) -> None:
    full_code, _png = _ean13_png("869952209047")
    barcodes_csv = sample_csv_path.with_name("medicine_barcodes.csv")
    barcodes_csv.write_text(
        f"barcode,medicine_id\n{full_code},MED001\n",
        encoding="utf-8",
    )
    seed_medicines_from_csv(
        csv_path=sample_csv_path,
        database_path=sqlite_path,
        replace_existing=True,
        barcodes_csv_path=barcodes_csv,
    )
    with session_scope() as session:
        medicine = get_medicine_by_barcode(session, full_code)
        assert medicine is not None
        assert medicine.medicine_id == "MED001"
        assert get_medicine_by_barcode(session, "0000000000000") is None
        gtin14 = f"0{full_code}"
        assert get_medicine_by_barcode(session, gtin14) is not None


def test_matching_service_barcode_hit(
    seeded_pipeline_config: PipelineConfig,
    sample_csv_path: Path,
) -> None:
    full_code, _png = _ean13_png("869952209047")
    barcodes_csv = sample_csv_path.with_name("medicine_barcodes.csv")
    barcodes_csv.write_text(
        f"barcode,medicine_id\n{full_code},MED001\n",
        encoding="utf-8",
    )
    service = MatchingService.from_sqlite(
        seeded_pipeline_config,
        seed_from_csv=True,
    )
    matched = service.match_barcode(full_code)
    assert matched.status == "matched"
    assert matched.match_source == "barcode"
    assert matched.medicine is not None
    assert matched.medicine["medicine_id"] == "MED001"
    assert matched.matching_score == 100.0

    missing = service.match_barcode("8690000000000")
    assert missing.status == "not_found"
    assert missing.match_source == "barcode"


@pytest.fixture()
def barcode_app(
    seeded_pipeline_config: PipelineConfig,
    sample_csv_path: Path,
) -> tuple[TestClient, str]:
    full_code, png_bytes = _ean13_png("869952209047")
    barcodes_csv = sample_csv_path.with_name("medicine_barcodes.csv")
    barcodes_csv.write_text(
        f"barcode,medicine_id\n{full_code},MED001\n",
        encoding="utf-8",
    )
    seed_medicines_from_csv(
        csv_path=sample_csv_path,
        database_path=seeded_pipeline_config.sqlite_path,
        replace_existing=True,
        barcodes_csv_path=barcodes_csv,
    )
    MedicineQueryService.reset_instance()

    settings = ApiSettings(rate_limit_enabled=False)
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(barcode_router.router, prefix="/api/v1")
    app.dependency_overrides[get_api_settings] = lambda: settings

    def override_medicine_service() -> MedicineQueryService:
        return MedicineQueryService.from_pipeline_config(
            seeded_pipeline_config
        )

    from backend.app.dependencies import get_medicine_service

    app.dependency_overrides[get_medicine_service] = override_medicine_service
    return TestClient(app), full_code, png_bytes


def test_barcode_lookup_endpoint(barcode_app: tuple) -> None:
    client, full_code, _png = barcode_app
    ok = client.get("/api/v1/barcode/lookup", params={"code": full_code})
    assert ok.status_code == 200
    payload = ok.json()
    assert payload["success"] is True
    assert payload["status"] == "matched"
    assert payload["medicine"]["medicine_id"] == "MED001"

    missing = client.get(
        "/api/v1/barcode/lookup",
        params={"code": "8690000000004"},
    )
    assert missing.status_code == 200
    assert missing.json()["status"] == "not_found"


def test_barcode_scan_endpoint(barcode_app: tuple) -> None:
    client, full_code, png_bytes = barcode_app
    response = client.post(
        "/api/v1/barcode/scan",
        files={"file": ("ean.png", png_bytes, "image/png")},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["status"] == "matched"
    assert payload["barcode"] == full_code
    assert payload["medicine"]["medicine_name"] == "Parol"


def test_barcode_info_endpoint() -> None:
    app = FastAPI()
    app.include_router(barcode_router.router, prefix="/api/v1")
    client = TestClient(app)
    response = client.get("/api/v1/barcode/info")
    assert response.status_code == 200
    payload = response.json()
    assert payload["scan_endpoint"].endswith("/barcode/scan")
    assert "EAN-13" in payload["supported_formats"]


def test_skrs_index_fallback_without_catalog(tmp_path: Path) -> None:
    from src.barcode.skrs_resolver import (
        medicine_from_skrs_hit,
        resolve_skrs_barcode,
    )

    index_csv = tmp_path / "skrs_barcode_index.csv"
    index_csv.write_text(
        "barcode,ilac_adi,atc_kodu,atc_adi,durumu\n"
        "8691111111114,CORASPIN 100 MG TABLET,B01AC06,ACETYLSALICYLIC ACID,AKTIF\n",
        encoding="utf-8",
    )
    hit = resolve_skrs_barcode(
        "08691111111114",
        index_csv=index_csv,
    )
    assert hit is not None
    assert hit.ilac_adi.startswith("CORASPIN")
    medicine = medicine_from_skrs_hit(hit)
    assert medicine["medicine_id"].startswith("SKRS-")
    assert "Coraspin" in medicine["medicine_name"] or "CORASPIN" in medicine[
        "medicine_name"
    ].upper()

