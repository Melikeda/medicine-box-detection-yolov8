from typing import Any, Literal

from pydantic import BaseModel, Field


class BoundingBoxSchema(BaseModel):
    x1: int
    y1: int
    x2: int
    y2: int


class MedicineBoxResultSchema(BaseModel):
    box_index: int
    bounding_box: BoundingBoxSchema
    yolo_confidence: float
    ocr_text: str | None = None
    medicine_name: str | None = None
    matching_score: float = 0.0
    status: Literal["matched", "not_found", "not_medicine_box", "error"]
    display_message: str
    best_candidate: str | None = None
    error: str | None = None
    medicine: dict[str, str] | None = None


class AnalyzeSummarySchema(BaseModel):
    """Mobil uygulama icin ozet sayaclar."""

    matched_count: int = 0
    not_found_count: int = 0
    not_medicine_box_count: int = 0
    error_count: int = 0


class AnalyzeTimingSchema(BaseModel):
    """Pipeline aşama süreleri (ms)."""

    yolo_ms: float = 0.0
    ocr_ms: float = 0.0
    matching_ms: float = 0.0
    total_ms: float = 0.0


class AnalyzeResponseSchema(BaseModel):
    success: bool
    filename: str | None = None
    detection_count: int
    medicines: list[MedicineBoxResultSchema] = Field(default_factory=list)
    medicines_compared: int = 0
    error: str | None = None
    summary: AnalyzeSummarySchema = Field(
        default_factory=AnalyzeSummarySchema
    )
    ocr_mode: str = "fast"
    processing_time_ms: float = 0.0
    timing: AnalyzeTimingSchema | None = None
    image_resized: bool = False


class AnalyzeInfoSchema(BaseModel):
    """Analyze endpoint limitleri ve desteklenen formatlar."""

    endpoint: str
    method: str = "POST"
    content_type: str = "multipart/form-data"
    file_field: str = "file"
    max_upload_size_mb: float
    allowed_extensions: list[str]
    ocr_modes: list[str]
    response_statuses: list[str]


class HealthResponseSchema(BaseModel):
    status: Literal["ok", "degraded"]
    app_name: str
    version: str
    models_loaded: bool
    ocr_mode: str
    medicine_count: int | None = None
    database_source: str | None = None


class ErrorResponseSchema(BaseModel):
    success: bool = False
    error: str
    details: dict[str, Any] = Field(default_factory=dict)
