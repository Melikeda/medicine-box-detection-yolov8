from functools import lru_cache

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from backend.app.config import ApiSettings, get_api_settings
from backend.app.dependencies import get_scan_service
from backend.app.exceptions import RateLimitExceededError
from backend.app.middleware.rate_limit import AnalyzeRateLimiter
from backend.app.schemas.scans import (
    ScanCreateRequestSchema,
    ScanCreateResponseSchema,
    ScanDeleteResponseSchema,
    ScanDetailResponseSchema,
    ScanDetailSchema,
    ScanInfoSchema,
    ScanListItemSchema,
    ScanListResponseSchema,
)
from backend.app.services.scan_service import ScanQueryService

router = APIRouter(prefix="/scans", tags=["scans"])


@lru_cache
def _get_scans_rate_limiter(max_requests: int) -> AnalyzeRateLimiter:
    return AnalyzeRateLimiter(max_requests=max_requests)


def enforce_scans_rate_limit(
    request: Request,
    settings: ApiSettings = Depends(get_api_settings),
) -> None:
    if not settings.rate_limit_enabled:
        return

    limiter = _get_scans_rate_limiter(settings.rate_limit_scans_per_minute)
    client_host = request.client.host if request.client else "unknown"
    if not limiter.is_allowed(client_host):
        raise RateLimitExceededError(
            "Cok fazla tarama gecmisi istegi. "
            "Lutfen bir dakika sonra tekrar deneyin."
        )


@router.get("/info", response_model=ScanInfoSchema)
async def scans_info(
    settings: ApiSettings = Depends(get_api_settings),
) -> ScanInfoSchema:
    return ScanInfoSchema(
        endpoint=f"{settings.api_prefix}/scans",
        max_entries=settings.scan_history_max_entries,
    )


@router.get("", response_model=ScanListResponseSchema)
async def list_scans(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    service: ScanQueryService = Depends(get_scan_service),
) -> ScanListResponseSchema:
    scans, total = service.list_scans(limit=limit, offset=offset)
    return ScanListResponseSchema(
        total=total,
        count=len(scans),
        offset=offset,
        limit=limit,
        source=service.source,
        scans=[ScanListItemSchema(**item) for item in scans],
    )


@router.post(
    "",
    response_model=ScanCreateResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_scan(
    payload: ScanCreateRequestSchema,
    _rate_limit: None = Depends(enforce_scans_rate_limit),
    service: ScanQueryService = Depends(get_scan_service),
) -> ScanCreateResponseSchema:
    if not payload.response.success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sadece basarili analiz sonuclari kaydedilir.",
        )

    scan = service.create_scan(
        response=payload.response.model_dump(mode="json"),
        preview_label=payload.preview_label,
        client_device_id=payload.client_device_id,
    )
    return ScanCreateResponseSchema(scan=ScanDetailSchema(**scan))


@router.get("/{scan_id}", response_model=ScanDetailResponseSchema)
async def get_scan(
    scan_id: int,
    service: ScanQueryService = Depends(get_scan_service),
) -> ScanDetailResponseSchema:
    scan = service.get_scan(scan_id)
    if scan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tarama bulunamadi: {scan_id}",
        )
    return ScanDetailResponseSchema(
        source=service.source,
        scan=ScanDetailSchema(**scan),
    )


@router.delete("/{scan_id}", response_model=ScanDeleteResponseSchema)
async def remove_scan(
    scan_id: int,
    service: ScanQueryService = Depends(get_scan_service),
) -> ScanDeleteResponseSchema:
    deleted = service.delete_scan(scan_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tarama bulunamadi: {scan_id}",
        )
    return ScanDeleteResponseSchema(deleted_id=scan_id)
