from fastapi import Depends, Request

from backend.app.config import ApiSettings, get_api_settings
from backend.app.exceptions import LlmNotConfiguredError, PipelineNotReadyError
from backend.app.services.llm_service import LlmExplanationService
from backend.app.services.medicine_service import MedicineQueryService
from backend.app.services.scan_service import ScanQueryService
from src.services.pipeline_manager import PipelineManager


def get_pipeline_manager(request: Request) -> PipelineManager:
    """Return the singleton pipeline manager loaded during app startup."""
    manager = getattr(request.app.state, "pipeline_manager", None)

    if manager is None or not manager.is_loaded:
        raise PipelineNotReadyError()

    return manager


def get_medicine_service(
    settings: ApiSettings = Depends(get_api_settings),
) -> MedicineQueryService:
    """Paylaşılan ilaç sorgu servisini döndürür (tek DB engine init)."""
    return MedicineQueryService.from_pipeline_config(
        settings.create_pipeline_config()
    )


def get_scan_service(
    settings: ApiSettings = Depends(get_api_settings),
) -> ScanQueryService:
    """Paylaşılan sunucu tarama geçmişi servisini döndürür."""
    return ScanQueryService.from_pipeline_config(
        settings.create_pipeline_config(),
        max_entries=settings.scan_history_max_entries,
    )


def get_llm_service(
    settings: ApiSettings = Depends(get_api_settings),
) -> LlmExplanationService:
    """Paylaşılan LLM servisini döndürür (tek cache singleton)."""
    if not settings.llm_enabled:
        raise LlmNotConfiguredError(
            "LLM ozelligi devre disi. LLM_ENABLED=true yapin."
        )
    if not settings.llm_is_configured:
        raise LlmNotConfiguredError(settings.llm_status_message)
    return LlmExplanationService.get_instance(settings)
