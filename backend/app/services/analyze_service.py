import asyncio
import logging
import tempfile
import time
from pathlib import Path

from backend.app.config import ApiSettings
from backend.app.exceptions import PayloadTooLargeError
from backend.app.schemas.analyze import (
    AnalyzeResponseSchema,
    AnalyzeSummarySchema,
)
from backend.app.services.upload_validator import (
    validate_image_bytes,
    validate_upload_metadata,
)
from src.services.config import OCRMode
from src.services.pipeline_manager import PipelineManager

logger = logging.getLogger(__name__)


def _build_summary(
    medicines: list,
) -> AnalyzeSummarySchema:
    matched_count = 0
    not_found_count = 0
    not_medicine_box_count = 0
    error_count = 0

    for box in medicines:
        if box.status == "matched":
            matched_count += 1
        elif box.status == "not_found":
            not_found_count += 1
        elif box.status == "not_medicine_box":
            not_medicine_box_count += 1
        elif box.status == "error":
            error_count += 1

    return AnalyzeSummarySchema(
        matched_count=matched_count,
        not_found_count=not_found_count,
        not_medicine_box_count=not_medicine_box_count,
        error_count=error_count,
    )


def _run_analysis(
    manager: PipelineManager,
    temp_path: Path,
    *,
    ocr_mode: OCRMode,
) -> AnalyzeResponseSchema:
    manager.config.ocr_mode = ocr_mode

    pipeline_result = manager.analyze_all(temp_path)
    response_data = pipeline_result.to_dict()

    return AnalyzeResponseSchema(
        success=pipeline_result.success,
        filename=None,
        detection_count=pipeline_result.detection_count,
        medicines=response_data["medicines"],
        medicines_compared=pipeline_result.medicines_compared,
        error=pipeline_result.error,
        summary=_build_summary(pipeline_result.medicines),
        ocr_mode=ocr_mode,
        processing_time_ms=0.0,
    )


class AnalyzeService:
    """Upload + pipeline orchestration for analyze endpoint."""

    def __init__(
        self,
        manager: PipelineManager,
        settings: ApiSettings,
    ) -> None:
        self.manager = manager
        self.settings = settings

    async def analyze_upload(
        self,
        *,
        file_bytes: bytes,
        filename: str | None,
        content_type: str | None,
        ocr_mode: OCRMode | None = None,
    ) -> AnalyzeResponseSchema:
        selected_mode = ocr_mode or self.settings.ocr_mode

        if len(file_bytes) > self.settings.max_upload_size_bytes:
            raise PayloadTooLargeError(
                f"Dosya boyutu limiti asildi "
                f"({self.settings.max_upload_size_mb:.1f} MB)."
            )

        suffix = validate_upload_metadata(
            filename=filename,
            content_type=content_type,
            allowed_extensions=self.settings.allowed_extensions,
        )
        validate_image_bytes(file_bytes, suffix=suffix)

        temp_path: Path | None = None
        started_at = time.perf_counter()

        try:
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=suffix,
            ) as temp_file:
                temp_file.write(file_bytes)
                temp_path = Path(temp_file.name)

            logger.info(
                "Analyze request: filename=%s size=%s mode=%s",
                filename,
                len(file_bytes),
                selected_mode,
            )

            result = await asyncio.to_thread(
                _run_analysis,
                self.manager,
                temp_path,
                ocr_mode=selected_mode,
            )

            result.filename = filename
            result.processing_time_ms = (
                time.perf_counter() - started_at
            ) * 1000

            return result

        finally:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)
