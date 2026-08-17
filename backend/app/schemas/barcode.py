from typing import Literal

from pydantic import BaseModel, Field

from backend.app.schemas.medicines import MedicineSchema


class BarcodeLookupResponseSchema(BaseModel):
    """Catalog lookup by barcode text."""

    success: bool
    barcode: str
    status: Literal["matched", "not_found"]
    display_message: str
    match_source: str = "barcode"
    medicine: MedicineSchema | None = None


class DecodedBarcodeSchema(BaseModel):
    text: str
    normalized: str
    format: str = "unknown"


class BarcodeScanResponseSchema(BaseModel):
    """Barcode decoding from an image plus catalog matching."""

    success: bool
    status: Literal["matched", "not_found", "no_barcode"]
    display_message: str
    match_source: str = "barcode"
    barcode: str | None = None
    barcode_format: str | None = None
    decoded_count: int = 0
    decoded: list[DecodedBarcodeSchema] = Field(default_factory=list)
    medicine: MedicineSchema | None = None
    processing_time_ms: float = 0.0
    disclaimer: str | None = None


class BarcodeInfoSchema(BaseModel):
    endpoint: str
    lookup_endpoint: str
    scan_endpoint: str
    supported_formats: list[str] = Field(
        default_factory=lambda: [
            "EAN-13",
            "EAN-8",
            "UPC-A",
            "Code128",
            "QR",
            "DataMatrix",
        ]
    )
    rate_limit_barcode_per_minute: int | None = None
