from typing import Any

from pydantic import BaseModel, Field

from backend.app.schemas.analyze import AnalyzeResponseSchema


class ScanCreateRequestSchema(BaseModel):
    """Başarılı analyze yanıtını sunucu geçmişine kaydet."""

    response: AnalyzeResponseSchema
    preview_label: str | None = Field(default=None, max_length=255)
    client_device_id: str | None = Field(default=None, max_length=128)


class ScanListItemSchema(BaseModel):
    id: int
    created_at: str
    detection_count: int
    matched_count: int
    preview_label: str
    filename: str | None = None
    ocr_mode: str = "fast"
    client_device_id: str | None = None


class ScanDetailSchema(ScanListItemSchema):
    response: dict[str, Any]


class ScanCreateResponseSchema(BaseModel):
    success: bool = True
    scan: ScanDetailSchema


class ScanListResponseSchema(BaseModel):
    success: bool = True
    total: int
    count: int
    offset: int = 0
    limit: int = 50
    source: str = "sqlite"
    scans: list[ScanListItemSchema] = Field(default_factory=list)


class ScanDetailResponseSchema(BaseModel):
    success: bool = True
    source: str = "sqlite"
    scan: ScanDetailSchema


class ScanDeleteResponseSchema(BaseModel):
    success: bool = True
    deleted_id: int


class ScanInfoSchema(BaseModel):
    endpoint: str
    method: str = "POST"
    list_method: str = "GET"
    auth_required: bool = False
    max_entries: int
    note: str = (
        "No auth yet — scans are stored globally. "
        "Images stay on the device; only analyze JSON is synced."
    )
