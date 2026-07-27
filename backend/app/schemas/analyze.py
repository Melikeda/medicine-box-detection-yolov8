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


class AnalyzeResponseSchema(BaseModel):
    success: bool
    image_path: str
    detection_count: int
    medicines: list[MedicineBoxResultSchema] = Field(default_factory=list)
    medicines_compared: int = 0
    error: str | None = None


class HealthResponseSchema(BaseModel):
    status: Literal["ok", "degraded"]
    app_name: str
    version: str
    models_loaded: bool
    ocr_mode: str
    medicine_count: int | None = None


class ErrorResponseSchema(BaseModel):
    success: bool = False
    error: str
    details: dict[str, Any] = Field(default_factory=dict)
