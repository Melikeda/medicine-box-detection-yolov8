from functools import lru_cache

from fastapi import APIRouter, Depends, File, Query, Request, UploadFile

from backend.app.config import ApiSettings, get_api_settings
from backend.app.dependencies import get_medicine_service
from backend.app.exceptions import RateLimitExceededError
from backend.app.middleware.rate_limit import AnalyzeRateLimiter
from backend.app.schemas.barcode import (
    BarcodeInfoSchema,
    BarcodeLookupResponseSchema,
    BarcodeScanResponseSchema,
)
from backend.app.services.barcode_scan_service import BarcodeScanService
from backend.app.services.medicine_service import MedicineQueryService

router = APIRouter(prefix="/barcode", tags=["barcode"])


@lru_cache
def _get_barcode_rate_limiter(max_requests: int) -> AnalyzeRateLimiter:
    return AnalyzeRateLimiter(max_requests=max_requests)


def enforce_barcode_rate_limit(
    request: Request,
    settings: ApiSettings = Depends(get_api_settings),
) -> None:
    if not settings.rate_limit_enabled:
        return

    limiter = _get_barcode_rate_limiter(
        settings.rate_limit_barcode_per_minute
    )
    client_host = request.client.host if request.client else "unknown"
    if not limiter.is_allowed(client_host):
        raise RateLimitExceededError(
            "Too many barcode requests. "
            "Please try again in a minute."
        )


def get_barcode_scan_service(
    settings: ApiSettings = Depends(get_api_settings),
    medicine_service: MedicineQueryService = Depends(get_medicine_service),
) -> BarcodeScanService:
    return BarcodeScanService(
        medicine_service=medicine_service,
        settings=settings,
    )


@router.get("/info", response_model=BarcodeInfoSchema)
async def barcode_info(
    settings: ApiSettings = Depends(get_api_settings),
) -> BarcodeInfoSchema:
    """Barcode endpoint information."""
    prefix = settings.api_prefix
    return BarcodeInfoSchema(
        endpoint=f"{prefix}/barcode",
        lookup_endpoint=f"{prefix}/barcode/lookup",
        scan_endpoint=f"{prefix}/barcode/scan",
        rate_limit_barcode_per_minute=(
            settings.rate_limit_barcode_per_minute
            if settings.rate_limit_enabled
            else None
        ),
    )


@router.get("/lookup", response_model=BarcodeLookupResponseSchema)
async def lookup_barcode(
    code: str = Query(..., min_length=8, max_length=160, description="EAN/GTIN"),
    _rate_limit: None = Depends(enforce_barcode_rate_limit),
    service: BarcodeScanService = Depends(get_barcode_scan_service),
) -> BarcodeLookupResponseSchema:
    """Find a medicine by decoded barcode text. Use /explain for explanations."""
    return service.lookup_code(code)


@router.post("/scan", response_model=BarcodeScanResponseSchema)
async def scan_barcode_image(
    file: UploadFile = File(..., description="Barkod veya kutu fotoğrafı"),
    _rate_limit: None = Depends(enforce_barcode_rate_limit),
    service: BarcodeScanService = Depends(get_barcode_scan_service),
) -> BarcodeScanResponseSchema:
    """Read a barcode from an image and search the medicine catalog."""
    file_bytes = await file.read()
    return service.scan_image(
        file_bytes=file_bytes,
        filename=file.filename,
        content_type=file.content_type,
    )
