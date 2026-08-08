from functools import lru_cache

from fastapi import APIRouter, Depends, HTTPException, Request, status

from backend.app.config import ApiSettings, get_api_settings
from backend.app.constants import LLM_EXPLANATION_DISCLAIMER
from backend.app.dependencies import get_llm_service, get_medicine_service
from backend.app.exceptions import RateLimitExceededError
from backend.app.middleware.rate_limit import AnalyzeRateLimiter
from backend.app.schemas.explain import (
    ExplainInfoSchema,
    ExplainRequestSchema,
    ExplainResponseSchema,
)
from backend.app.services.llm_service import LlmExplanationService
from backend.app.services.medicine_service import MedicineQueryService

router = APIRouter(prefix="/explain", tags=["explain"])


@lru_cache
def _get_explain_rate_limiter(max_requests: int) -> AnalyzeRateLimiter:
    return AnalyzeRateLimiter(max_requests=max_requests)


def enforce_explain_rate_limit(
    request: Request,
    settings: ApiSettings = Depends(get_api_settings),
) -> None:
    if not settings.rate_limit_enabled:
        return

    limiter = _get_explain_rate_limiter(settings.rate_limit_explain_per_minute)
    client_host = request.client.host if request.client else "unknown"
    if not limiter.is_allowed(client_host):
        raise RateLimitExceededError(
            "Cok fazla aciklama istegi. "
            "Lutfen bir dakika sonra tekrar deneyin."
        )


@router.get("/info", response_model=ExplainInfoSchema)
async def explain_info(
    settings: ApiSettings = Depends(get_api_settings),
) -> ExplainInfoSchema:
    """Explain endpoint yapılandırma bilgisi."""
    return ExplainInfoSchema(
        endpoint=f"{settings.api_prefix}/explain",
        llm_enabled=settings.llm_enabled,
        llm_configured=settings.llm_is_configured,
        ready=settings.llm_is_configured,
        status_message=settings.llm_status_message,
        provider=settings.llm_provider,
        model=settings.llm_model,
        rate_limit_enabled=settings.rate_limit_enabled,
        rate_limit_explain_per_minute=(
            settings.rate_limit_explain_per_minute
            if settings.rate_limit_enabled
            else None
        ),
        cache_enabled=settings.llm_cache_enabled,
    )


@router.post("", response_model=ExplainResponseSchema)
async def explain_medicine(
    payload: ExplainRequestSchema,
    _rate_limit: None = Depends(enforce_explain_rate_limit),
    medicine_service: MedicineQueryService = Depends(get_medicine_service),
    llm_service: LlmExplanationService = Depends(get_llm_service),
) -> ExplainResponseSchema:
    """Eşleşen ilaç için kısa Türkçe LLM açıklaması üretir."""
    medicine = medicine_service.get_medicine(payload.medicine_id)
    if medicine is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ilac bulunamadi: {payload.medicine_id}",
        )

    explanation, cached = llm_service.explain_medicine(
        medicine,
        locale=payload.locale,
    )

    return ExplainResponseSchema(
        medicine_id=medicine["medicine_id"],
        medicine_name=medicine.get("medicine_name", ""),
        explanation=explanation,
        disclaimer=LLM_EXPLANATION_DISCLAIMER,
        cached=cached,
        provider=llm_service.provider,
        model=llm_service.model,
    )
