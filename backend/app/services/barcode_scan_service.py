"""Barkod görüntüsü yükleme ve katalog eşlemesi."""

from __future__ import annotations

import logging
import time

import cv2
import numpy as np

from backend.app.config import ApiSettings
from backend.app.constants import MEDICAL_DISCLAIMER
from backend.app.exceptions import PayloadTooLargeError
from backend.app.schemas.barcode import (
    BarcodeLookupResponseSchema,
    BarcodeScanResponseSchema,
    DecodedBarcodeSchema,
)
from backend.app.schemas.medicines import MedicineSchema
from backend.app.services.medicine_service import MedicineQueryService
from backend.app.services.upload_validator import (
    validate_image_bytes,
    validate_upload_metadata,
)
from src.barcode.decoder import decode_barcodes
from src.barcode.normalize import normalize_barcode

logger = logging.getLogger(__name__)

BARCODE_MATCHED = "İlaç barkod ile eşleştirildi."
BARCODE_NOT_FOUND = "Barkod katalogda bulunamadı."
NO_BARCODE = "Görüntüde barkod okunamadı."


class BarcodeScanService:
    """POST /barcode/scan ve GET /barcode/lookup iş mantığı."""

    def __init__(
        self,
        *,
        medicine_service: MedicineQueryService,
        settings: ApiSettings,
    ) -> None:
        self.medicine_service = medicine_service
        self.settings = settings

    def lookup_code(self, raw_code: str) -> BarcodeLookupResponseSchema:
        medicine = self.medicine_service.get_medicine_by_barcode(raw_code)
        code = normalize_barcode(raw_code) or raw_code.strip()
        if medicine is None:
            logger.info("Barcode not in catalog: %s", code)
            return BarcodeLookupResponseSchema(
                success=False,
                barcode=code,
                status="not_found",
                display_message=BARCODE_NOT_FOUND,
            )
        return BarcodeLookupResponseSchema(
            success=True,
            barcode=code,
            status="matched",
            display_message=BARCODE_MATCHED,
            medicine=MedicineSchema(**medicine),
        )

    def scan_image(
        self,
        *,
        file_bytes: bytes,
        filename: str | None,
        content_type: str | None,
    ) -> BarcodeScanResponseSchema:
        started = time.perf_counter()
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

        image = _decode_image_bytes(file_bytes)
        decoded = decode_barcodes(image) if image is not None else []
        decoded_schemas = [
            DecodedBarcodeSchema(
                text=item.text,
                normalized=item.normalized,
                format=item.format,
            )
            for item in decoded
        ]
        elapsed_ms = (time.perf_counter() - started) * 1000

        if not decoded:
            return BarcodeScanResponseSchema(
                success=False,
                status="no_barcode",
                display_message=NO_BARCODE,
                decoded_count=0,
                processing_time_ms=elapsed_ms,
                disclaimer=MEDICAL_DISCLAIMER,
            )

        for item in decoded:
            medicine = self.medicine_service.get_medicine_by_barcode(
                item.text
            ) or self.medicine_service.get_medicine_by_barcode(
                item.normalized
            )
            if medicine is None:
                continue
            return BarcodeScanResponseSchema(
                success=True,
                status="matched",
                display_message=BARCODE_MATCHED,
                barcode=item.normalized,
                barcode_format=item.format,
                decoded_count=len(decoded),
                decoded=decoded_schemas,
                medicine=MedicineSchema(**medicine),
                processing_time_ms=elapsed_ms,
                disclaimer=MEDICAL_DISCLAIMER,
            )

        first = decoded[0]
        return BarcodeScanResponseSchema(
            success=False,
            status="not_found",
            display_message=BARCODE_NOT_FOUND,
            barcode=first.normalized,
            barcode_format=first.format,
            decoded_count=len(decoded),
            decoded=decoded_schemas,
            processing_time_ms=elapsed_ms,
            disclaimer=MEDICAL_DISCLAIMER,
        )


def _decode_image_bytes(file_bytes: bytes) -> np.ndarray | None:
    array = np.frombuffer(file_bytes, dtype=np.uint8)
    image = cv2.imdecode(array, cv2.IMREAD_COLOR)
    return image
