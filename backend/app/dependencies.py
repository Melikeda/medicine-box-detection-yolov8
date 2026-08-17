import logging

from fastapi import Depends, Request

from backend.app.config import ApiSettings, get_api_settings
from backend.app.exceptions import PipelineNotReadyError
from backend.app.services.llm_service import (
    LlmExplanationService,
    MockMedicineExplainer,
)
from backend.app.services.medicine_service import MedicineQueryService
from backend.app.services.scan_service import ScanQueryService
from src.services.pipeline_manager import PipelineManager

logger = logging.getLogger(__name__)


def get_pipeline_manager(request: Request) -> PipelineManager:
    """Return the singleton pipeline manager loaded during app startup."""
    manager = getattr(request.app.state, "pipeline_manager", None)

    if manager is None or not manager.is_loaded:
        raise PipelineNotReadyError()

    return manager


def get_medicine_service(
    settings: ApiSettings = Depends(get_api_settings),
) -> MedicineQueryService:
    """Return the shared medicine query service with one DB engine init."""
    return MedicineQueryService.from_pipeline_config(
        settings.create_pipeline_config()
    )


def get_scan_service(
    settings: ApiSettings = Depends(get_api_settings),
) -> ScanQueryService:
    """Return the shared server-side scan history service."""
    return ScanQueryService.from_pipeline_config(
        settings.create_pipeline_config(),
        max_entries=settings.scan_history_max_entries,
    )


def get_llm_service(
    settings: ApiSettings = Depends(get_api_settings),
) -> LlmExplanationService:
    """Return the shared LLM service with a single cache singleton.

    When Gemini is not configured, generate catalog text instead of a 503 so
    the mobile "About medicine" card does not show a red error state.
    """
    if settings.llm_is_configured:
        return LlmExplanationService.get_instance(settings)

    logger.warning(
        "Explain using catalog fallback: %s",
        settings.llm_status_message,
    )
    return LlmExplanationService(
        settings=settings,
        explainer=MockMedicineExplainer(),
        provider="catalog-fallback",
        model="catalog-fallback",
    )
