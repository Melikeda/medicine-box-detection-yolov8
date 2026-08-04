import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.config import ApiSettings, get_api_settings
from backend.app.exceptions import register_exception_handlers
from backend.app.routers import explain as explain_router
from backend.app.services.llm_service import (
    LlmExplanationService,
    MockMedicineExplainer,
)
from backend.app.services.medicine_service import MedicineQueryService
from src.services.config import PipelineConfig


@pytest.fixture()
def llm_settings() -> ApiSettings:
    return ApiSettings(
        llm_enabled=True,
        llm_mock_mode=True,
        llm_provider="mock",
    )


@pytest.fixture()
def explain_app(
    seeded_pipeline_config: PipelineConfig,
    llm_settings: ApiSettings,
) -> TestClient:
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(explain_router.router, prefix="/api/v1")

    def override_medicine_service() -> MedicineQueryService:
        return MedicineQueryService.from_pipeline_config(
            seeded_pipeline_config
        )

    def override_settings() -> ApiSettings:
        return llm_settings

    llm_service = LlmExplanationService(
        settings=llm_settings,
        explainer=MockMedicineExplainer(),
        provider="mock",
        model="mock",
    )

    def override_llm_service() -> LlmExplanationService:
        return llm_service

    app.dependency_overrides[
        explain_router.get_medicine_service
    ] = override_medicine_service
    app.dependency_overrides[get_api_settings] = override_settings
    app.dependency_overrides[
        explain_router.get_llm_service
    ] = override_llm_service

    return TestClient(app)


def test_explain_info_endpoint(explain_app: TestClient) -> None:
    response = explain_app.get("/api/v1/explain/info")
    assert response.status_code == 200
    payload = response.json()
    assert payload["endpoint"] == "/api/v1/explain"
    assert payload["llm_enabled"] is True
    assert payload["llm_configured"] is True
    assert payload["provider"] == "mock"
    assert payload["model"] == "gemini-flash-latest"


def test_explain_medicine_not_found(explain_app: TestClient) -> None:
    response = explain_app.post(
        "/api/v1/explain",
        json={"medicine_id": "MED999"},
    )
    assert response.status_code == 404


def test_explain_medicine_success(explain_app: TestClient) -> None:
    response = explain_app.post(
        "/api/v1/explain",
        json={"medicine_id": "MED001", "locale": "tr"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["medicine_id"] == "MED001"
    assert payload["medicine_name"] == "Parol"
    assert "Parol" in payload["explanation"]
    assert "tavsiye" in payload["disclaimer"].lower()
    assert payload["provider"] == "mock"
    assert payload["cached"] is False

    cached = explain_app.post(
        "/api/v1/explain",
        json={"medicine_id": "MED001", "locale": "tr"},
    )
    assert cached.status_code == 200
    assert cached.json()["cached"] is True


def test_explain_disabled_returns_503(
    seeded_pipeline_config: PipelineConfig,
) -> None:
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(explain_router.router, prefix="/api/v1")

    disabled_settings = ApiSettings(llm_enabled=False)

    def override_medicine_service() -> MedicineQueryService:
        return MedicineQueryService.from_pipeline_config(
            seeded_pipeline_config
        )

    app.dependency_overrides[
        explain_router.get_medicine_service
    ] = override_medicine_service
    app.dependency_overrides[get_api_settings] = lambda: disabled_settings

    client = TestClient(app)
    response = client.post(
        "/api/v1/explain",
        json={"medicine_id": "MED001"},
    )
    assert response.status_code == 503
