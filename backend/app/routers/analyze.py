import logging
import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, UploadFile

from backend.app.config import ApiSettings, get_api_settings
from backend.app.dependencies import get_pipeline_manager
from backend.app.exceptions import (
    PayloadTooLargeError,
    UnsupportedMediaTypeError,
)
from backend.app.schemas.analyze import AnalyzeResponseSchema
from src.services.pipeline_manager import PipelineManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analyze", tags=["analyze"])

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/bmp",
}


def _resolve_upload_suffix(
    filename: str | None,
    content_type: str | None,
) -> str:
    if filename:
        suffix = Path(filename).suffix.lower()
        if suffix:
            return suffix

    if content_type == "image/png":
        return ".png"
    if content_type == "image/webp":
        return ".webp"
    if content_type == "image/bmp":
        return ".bmp"

    return ".jpg"


def _validate_upload(
    upload: UploadFile,
    settings: ApiSettings,
) -> None:
    suffix = _resolve_upload_suffix(
        upload.filename,
        upload.content_type,
    )

    if suffix not in settings.allowed_extensions:
        raise UnsupportedMediaTypeError(
            f"Desteklenmeyen dosya uzantisi: {suffix}"
        )

    if (
        upload.content_type is not None
        and upload.content_type not in ALLOWED_CONTENT_TYPES
    ):
        raise UnsupportedMediaTypeError(
            f"Desteklenmeyen content-type: {upload.content_type}"
        )


@router.post("", response_model=AnalyzeResponseSchema)
async def analyze_medicine_image(
    file: UploadFile = File(..., description="Medicine box photo"),
    settings: ApiSettings = Depends(get_api_settings),
    manager: PipelineManager = Depends(get_pipeline_manager),
) -> AnalyzeResponseSchema:
    """
    Upload a medicine box photo and analyze all detected boxes.

    YOLO detects boxes, OCR reads text, RapidFuzz matches CSV drugs.
    """
    _validate_upload(file, settings)

    file_bytes = await file.read()

    if not file_bytes:
        raise UnsupportedMediaTypeError("Bos dosya yuklenemez.")

    if len(file_bytes) > settings.max_upload_size_bytes:
        raise PayloadTooLargeError(
            f"Dosya boyutu limiti asildi "
            f"({settings.max_upload_size_mb:.1f} MB)."
        )

    suffix = _resolve_upload_suffix(
        file.filename,
        file.content_type,
    )

    temp_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
        ) as temp_file:
            temp_file.write(file_bytes)
            temp_path = Path(temp_file.name)

        logger.info(
            "Analyze request received: filename=%s size=%s bytes",
            file.filename,
            len(file_bytes),
        )

        result = manager.analyze_all(temp_path)
        return AnalyzeResponseSchema(**result.to_dict())

    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
