import logging

from fastapi import APIRouter, Depends, File, Query, Request, UploadFile

from backend.app.config import ApiSettings, get_api_settings
from backend.app.dependencies import get_pipeline_manager
from backend.app.exceptions import PayloadTooLargeError
from backend.app.schemas.analyze import (
    AnalyzeInfoSchema,
    AnalyzeResponseSchema,
)
from backend.app.services.analyze_service import AnalyzeService
from src.services.config import OCRMode
from src.services.pipeline_manager import PipelineManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analyze", tags=["analyze"])


def get_analyze_service(
    settings: ApiSettings = Depends(get_api_settings),
    manager: PipelineManager = Depends(get_pipeline_manager),
) -> AnalyzeService:
    return AnalyzeService(manager=manager, settings=settings)


def _reject_oversized_content_length(
    request: Request,
    settings: ApiSettings,
) -> None:
    """Fail fast when Content-Length exceeds the upload cap (before body read)."""
    raw = request.headers.get("content-length")
    if raw is None:
        return
    try:
        content_length = int(raw)
    except ValueError:
        return
    if content_length > settings.max_upload_size_bytes:
        raise PayloadTooLargeError(
            f"Dosya boyutu limiti asildi "
            f"({settings.max_upload_size_mb:.1f} MB)."
        )


@router.get("/info", response_model=AnalyzeInfoSchema)
async def analyze_info(
    settings: ApiSettings = Depends(get_api_settings),
) -> AnalyzeInfoSchema:
    """Analyze endpoint limitleri ve mobil istemci bilgileri."""
    return AnalyzeInfoSchema(
        endpoint=f"{settings.api_prefix}/analyze",
        max_upload_size_mb=settings.max_upload_size_mb,
        allowed_extensions=list(settings.allowed_extensions),
        ocr_modes=["fast", "accurate"],
        response_statuses=[
            "matched",
            "not_found",
            "not_medicine_box",
            "error",
        ],
        rate_limit_analyze_per_minute=(
            settings.rate_limit_analyze_per_minute
            if settings.rate_limit_enabled
            else None
        ),
    )


@router.post("", response_model=AnalyzeResponseSchema)
async def analyze_medicine_image(
    request: Request,
    file: UploadFile = File(..., description="Medicine box photo"),
    mode: OCRMode | None = Query(
        default=None,
        description="OCR modu: fast (varsayilan) veya accurate",
    ),
    settings: ApiSettings = Depends(get_api_settings),
    service: AnalyzeService = Depends(get_analyze_service),
) -> AnalyzeResponseSchema:
    """
    Ilac kutusu fotografini yukler ve tum kutulari analiz eder.

    Flutter/mobil istemci `multipart/form-data` ile `file` alanini gonderir.
    """
    _reject_oversized_content_length(request, settings)
    file_bytes = await file.read()

    return await service.analyze_upload(
        file_bytes=file_bytes,
        filename=file.filename,
        content_type=file.content_type,
        ocr_mode=mode,
    )
