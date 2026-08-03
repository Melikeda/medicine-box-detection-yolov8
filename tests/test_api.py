import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.exceptions import register_exception_handlers
from backend.app.routers import analyze as analyze_router
from backend.app.routers import health, medicines
from backend.app.services.medicine_service import MedicineQueryService
from backend.app.services.upload_validator import (
    validate_image_bytes,
    validate_upload_metadata,
)
from src.services.config import PipelineConfig


@pytest.fixture()
def medicine_app(
    seeded_pipeline_config: PipelineConfig,
) -> TestClient:
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(medicines.router, prefix="/api/v1")

    def override_medicine_service() -> MedicineQueryService:
        return MedicineQueryService.from_pipeline_config(
            seeded_pipeline_config
        )

    app.dependency_overrides[
        medicines.get_medicine_service
    ] = override_medicine_service

    return TestClient(app)


def test_list_medicines_endpoint(medicine_app: TestClient) -> None:
    response = medicine_app.get("/api/v1/medicines")
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["total"] == 6
    assert payload["source"] == "sqlite"


def test_search_medicines_endpoint(medicine_app: TestClient) -> None:
    response = medicine_app.get(
        "/api/v1/medicines",
        params={"search": "parafon"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["medicines"][0]["medicine_id"] == "MED038"


def test_get_medicine_detail_and_404(
    medicine_app: TestClient,
) -> None:
    ok = medicine_app.get("/api/v1/medicines/MED033")
    assert ok.status_code == 200
    assert ok.json()["medicine"]["medicine_name"] == "Ibucold C"

    missing = medicine_app.get("/api/v1/medicines/MED999")
    assert missing.status_code == 404


def test_categories_endpoint(medicine_app: TestClient) -> None:
    response = medicine_app.get("/api/v1/medicines/categories")
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] >= 3
    assert "Ağrı Kesici" in payload["categories"]


def test_health_endpoint_with_loaded_manager() -> None:
    class FakeManager:
        is_loaded = True
        medicine_count = 6
        database_source = "sqlite"

    app = FastAPI()
    app.include_router(health.router)
    app.state.pipeline_manager = FakeManager()

    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["medicine_count"] == 6
    assert payload["database_source"] == "sqlite"


def test_analyze_info_endpoint() -> None:
    app = FastAPI()
    app.include_router(analyze_router.router, prefix="/api/v1")
    client = TestClient(app)

    response = client.get("/api/v1/analyze/info")
    assert response.status_code == 200
    payload = response.json()
    assert payload["file_field"] == "file"
    assert "fast" in payload["ocr_modes"]
    assert "matched" in payload["response_statuses"]


def test_upload_validator_rejects_bad_extension() -> None:
    with pytest.raises(Exception) as exc_info:
        validate_upload_metadata(
            filename="notes.txt",
            content_type="text/plain",
            allowed_extensions=(".jpg", ".png"),
        )
    assert "Desteklenmeyen" in str(exc_info.value)


def test_upload_validator_accepts_octet_stream_with_jpg_suffix() -> None:
    suffix = validate_upload_metadata(
        filename="photo.jpg",
        content_type="application/octet-stream",
        allowed_extensions=(".jpg", ".jpeg", ".png"),
    )
    assert suffix == ".jpg"


def test_upload_validator_accepts_png_bytes() -> None:
    # Minimal valid 1x1 PNG
    png_bytes = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde"
        b"\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05"
        b"\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    validate_image_bytes(png_bytes, suffix=".png")
