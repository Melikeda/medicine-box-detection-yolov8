"""
Mobile+backend API E2E smoke (YOLO/OCR olmadan).

Akış: health → medicines → explain → scans
Analyze upload, pipeline mock ile doğrulanır (CI-friendly).
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_IMAGE = PROJECT_ROOT / "data" / "samples" / "parol_plus.jpg"

from backend.app.config import ApiSettings, get_api_settings
from backend.app.dependencies import (
    get_llm_service,
    get_medicine_service,
    get_pipeline_manager,
    get_scan_service,
)
from backend.app.exceptions import register_exception_handlers
from backend.app.routers import analyze as analyze_router
from backend.app.routers import explain as explain_router
from backend.app.routers import health, medicines, scans
from backend.app.routers.analyze import get_analyze_service
from backend.app.schemas.analyze import (
    AnalyzeResponseSchema,
    AnalyzeSummarySchema,
    AnalyzeTimingSchema,
    BoundingBoxSchema,
    MedicineBoxResultSchema,
)
from backend.app.services.llm_service import (
    LlmExplanationService,
    MockMedicineExplainer,
)
from backend.app.services.medicine_service import MedicineQueryService
from backend.app.services.scan_service import ScanQueryService
from src.services.config import PipelineConfig


def _sample_analyze_response() -> AnalyzeResponseSchema:
    return AnalyzeResponseSchema(
        success=True,
        filename="e2e.jpg",
        detection_count=1,
        medicines=[
            MedicineBoxResultSchema(
                box_index=0,
                bounding_box=BoundingBoxSchema(x1=0, y1=0, x2=10, y2=10),
                yolo_confidence=0.91,
                ocr_text="PAROL",
                medicine_name="Parol",
                matching_score=92.0,
                status="matched",
                display_message="Parol",
                medicine={
                    "medicine_id": "MED001",
                    "medicine_name": "Parol",
                    "brand_name": "Parol",
                    "active_ingredient": "Paracetamol",
                    "dosage": "500 mg",
                    "form": "Tablet",
                    "category": "Ağrı Kesici",
                },
            )
        ],
        medicines_compared=8,
        summary=AnalyzeSummarySchema(matched_count=1),
        ocr_mode="fast",
        processing_time_ms=1500.0,
        timing=AnalyzeTimingSchema(
            yolo_ms=100.0,
            ocr_ms=1200.0,
            matching_ms=50.0,
            total_ms=1500.0,
        ),
        image_resized=True,
        disclaimer="Test disclaimer",
    )


class _FakeAnalyzeService:
    async def analyze_upload(self, **_kwargs: Any) -> AnalyzeResponseSchema:
        return _sample_analyze_response()


class _FakePipelineManager:
    is_loaded = True
    medicine_count = 8
    database_source = "sqlite"


def _build_e2e_client(config: PipelineConfig) -> TestClient:
    settings = ApiSettings(
        llm_enabled=True,
        llm_mock_mode=True,
        llm_provider="mock",
        rate_limit_enabled=False,
        scan_history_max_entries=50,
    )

    app = FastAPI()
    register_exception_handlers(app)
    app.state.pipeline_manager = _FakePipelineManager()
    app.include_router(health.router)
    app.include_router(analyze_router.router, prefix="/api/v1")
    app.include_router(medicines.router, prefix="/api/v1")
    app.include_router(explain_router.router, prefix="/api/v1")
    app.include_router(scans.router, prefix="/api/v1")

    medicine_service = MedicineQueryService.from_pipeline_config(config)
    scan_service = ScanQueryService.from_pipeline_config(
        config,
        max_entries=50,
    )
    llm_service = LlmExplanationService(
        settings=settings,
        explainer=MockMedicineExplainer(),
        provider="mock",
        model="mock",
    )

    app.dependency_overrides[get_api_settings] = lambda: settings
    app.dependency_overrides[get_pipeline_manager] = (
        lambda: app.state.pipeline_manager
    )
    app.dependency_overrides[get_medicine_service] = lambda: medicine_service
    app.dependency_overrides[get_scan_service] = lambda: scan_service
    app.dependency_overrides[get_llm_service] = lambda: llm_service
    app.dependency_overrides[get_analyze_service] = _FakeAnalyzeService

    return TestClient(app)


def _timed(client: TestClient, method: str, path: str, **kwargs: Any):
    started = time.perf_counter()
    response = getattr(client, method)(path, **kwargs)
    elapsed_ms = (time.perf_counter() - started) * 1000
    return response, elapsed_ms


def test_mobile_backend_api_e2e_flow(
    seeded_pipeline_config: PipelineConfig,
) -> None:
    client = _build_e2e_client(seeded_pipeline_config)
    timings: dict[str, float] = {}

    health_response, timings["health_ms"] = _timed(client, "get", "/health")
    assert health_response.status_code == 200
    assert health_response.json()["status"] == "ok"
    assert health_response.json()["models_loaded"] is True

    meds_response, timings["medicines_ms"] = _timed(
        client,
        "get",
        "/api/v1/medicines",
        params={"search": "parol"},
    )
    assert meds_response.status_code == 200
    assert meds_response.json()["total"] >= 1

    explain_info, timings["explain_info_ms"] = _timed(
        client,
        "get",
        "/api/v1/explain/info",
    )
    assert explain_info.status_code == 200
    assert explain_info.json()["ready"] is True

    explain_response, timings["explain_ms"] = _timed(
        client,
        "post",
        "/api/v1/explain",
        json={"medicine_id": "MED001", "locale": "tr"},
    )
    assert explain_response.status_code == 200
    assert explain_response.json()["cached"] is False

    explain_cached, timings["explain_cached_ms"] = _timed(
        client,
        "post",
        "/api/v1/explain",
        json={"medicine_id": "MED001", "locale": "tr"},
    )
    assert explain_cached.status_code == 200
    assert explain_cached.json()["cached"] is True

    assert SAMPLE_IMAGE.exists(), f"Missing sample image: {SAMPLE_IMAGE}"
    analyze_response, timings["analyze_mock_ms"] = _timed(
        client,
        "post",
        "/api/v1/analyze",
        files={
            "file": (
                SAMPLE_IMAGE.name,
                SAMPLE_IMAGE.read_bytes(),
                "image/jpeg",
            )
        },
    )
    assert analyze_response.status_code == 200
    analyze_payload = analyze_response.json()
    assert analyze_payload["success"] is True
    assert analyze_payload["summary"]["matched_count"] == 1

    scan_create, timings["scan_create_ms"] = _timed(
        client,
        "post",
        "/api/v1/scans",
        json={
            "response": analyze_payload,
            "client_device_id": "e2e-test",
        },
    )
    assert scan_create.status_code == 201
    scan_id = scan_create.json()["scan"]["id"]

    scan_list, timings["scan_list_ms"] = _timed(client, "get", "/api/v1/scans")
    assert scan_list.status_code == 200
    assert scan_list.json()["total"] >= 1

    scan_detail, timings["scan_detail_ms"] = _timed(
        client,
        "get",
        f"/api/v1/scans/{scan_id}",
    )
    assert scan_detail.status_code == 200
    assert scan_detail.json()["scan"]["client_device_id"] == "e2e-test"

    scan_delete, timings["scan_delete_ms"] = _timed(
        client,
        "delete",
        f"/api/v1/scans/{scan_id}",
    )
    assert scan_delete.status_code == 200

    # Non-OCR API steps should stay snappy in CI.
    for key, value in timings.items():
        assert value < 5000, f"{key} too slow: {value:.1f}ms"

    assert timings["explain_cached_ms"] <= timings["explain_ms"] + 50
    assert timings["medicines_ms"] < 2000
    assert timings["scan_create_ms"] < 2000
