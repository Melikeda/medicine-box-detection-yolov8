import logging

from fastapi import APIRouter, Depends, Request

from backend.app.config import ApiSettings, get_api_settings
from backend.app.schemas.analyze import HealthResponseSchema

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponseSchema)
async def health_check(
    request: Request,
    settings: ApiSettings = Depends(get_api_settings),
) -> HealthResponseSchema:
    """Return API and pipeline readiness information."""
    manager = getattr(request.app.state, "pipeline_manager", None)
    models_loaded = manager is not None and manager.is_loaded
    medicine_count = manager.medicine_count if manager else None

    logger.debug(
        "Health check: models_loaded=%s medicine_count=%s",
        models_loaded,
        medicine_count,
    )

    return HealthResponseSchema(
        status="ok" if models_loaded else "degraded",
        app_name=settings.app_name,
        version=settings.app_version,
        models_loaded=models_loaded,
        ocr_mode=settings.ocr_mode,
        medicine_count=medicine_count,
    )
