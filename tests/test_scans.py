"""Server-side scan history API tests."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.dependencies import get_scan_service
from backend.app.exceptions import register_exception_handlers
from backend.app.routers import scans as scans_router
from backend.app.services.scan_service import ScanQueryService
from src.database.repository import build_scan_preview_label
from src.services.config import PipelineConfig


def _sample_analyze_payload(*, success: bool = True) -> dict:
    return {
        "success": success,
        "filename": "box.jpg",
        "detection_count": 1,
        "medicines": [
            {
                "box_index": 0,
                "bounding_box": {"x1": 0, "y1": 0, "x2": 10, "y2": 10},
                "yolo_confidence": 0.9,
                "ocr_text": "PAROL",
                "medicine_name": "Parol",
                "matching_score": 0.95,
                "status": "matched",
                "display_message": "Parol",
            }
        ],
        "medicines_compared": 8,
        "summary": {
            "matched_count": 1,
            "not_found_count": 0,
            "not_medicine_box_count": 0,
            "error_count": 0,
        },
        "ocr_mode": "fast",
        "processing_time_ms": 1200.0,
    }


def _scans_client(config: PipelineConfig) -> TestClient:
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(scans_router.router, prefix="/api/v1")

    def override_scan_service() -> ScanQueryService:
        return ScanQueryService.from_pipeline_config(
            config,
            max_entries=5,
        )

    app.dependency_overrides[get_scan_service] = override_scan_service
    return TestClient(app)


def test_build_scan_preview_label_uses_matched_names() -> None:
    label = build_scan_preview_label(_sample_analyze_payload())
    assert label == "Parol"


def test_scans_info_endpoint(seeded_pipeline_config: PipelineConfig) -> None:
    client = _scans_client(seeded_pipeline_config)
    response = client.get("/api/v1/scans/info")
    assert response.status_code == 200
    payload = response.json()
    assert payload["endpoint"] == "/api/v1/scans"
    assert payload["auth_required"] is False
    assert payload["max_entries"] == 200


def test_create_list_get_delete_scan(
    seeded_pipeline_config: PipelineConfig,
) -> None:
    client = _scans_client(seeded_pipeline_config)

    created = client.post(
        "/api/v1/scans",
        json={
            "response": _sample_analyze_payload(),
            "client_device_id": "emulator-1",
        },
    )
    assert created.status_code == 201
    body = created.json()
    assert body["success"] is True
    scan_id = body["scan"]["id"]
    assert body["scan"]["preview_label"] == "Parol"
    assert body["scan"]["matched_count"] == 1
    assert body["scan"]["client_device_id"] == "emulator-1"
    assert body["scan"]["response"]["filename"] == "box.jpg"

    listed = client.get("/api/v1/scans")
    assert listed.status_code == 200
    list_body = listed.json()
    assert list_body["total"] == 1
    assert list_body["count"] == 1
    assert list_body["scans"][0]["id"] == scan_id

    detail = client.get(f"/api/v1/scans/{scan_id}")
    assert detail.status_code == 200
    assert detail.json()["scan"]["id"] == scan_id

    deleted = client.delete(f"/api/v1/scans/{scan_id}")
    assert deleted.status_code == 200
    assert deleted.json()["deleted_id"] == scan_id

    missing = client.get(f"/api/v1/scans/{scan_id}")
    assert missing.status_code == 404


def test_create_scan_rejects_failed_analyze(
    seeded_pipeline_config: PipelineConfig,
) -> None:
    client = _scans_client(seeded_pipeline_config)
    response = client.post(
        "/api/v1/scans",
        json={"response": _sample_analyze_payload(success=False)},
    )
    assert response.status_code == 400


def test_scan_history_trims_old_entries(
    seeded_pipeline_config: PipelineConfig,
) -> None:
    client = _scans_client(seeded_pipeline_config)
    for index in range(7):
        payload = _sample_analyze_payload()
        payload["filename"] = f"box-{index}.jpg"
        response = client.post(
            "/api/v1/scans",
            json={"response": payload},
        )
        assert response.status_code == 201

    listed = client.get("/api/v1/scans")
    assert listed.status_code == 200
    assert listed.json()["total"] == 5
