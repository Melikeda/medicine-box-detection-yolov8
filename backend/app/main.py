import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import ApiSettings, get_api_settings
from backend.app.exceptions import register_exception_handlers
from backend.app.logging_config import configure_logging
from backend.app.middleware.rate_limit import (
    AnalyzeRateLimitMiddleware,
    AnalyzeRateLimiter,
)
from backend.app.middleware.security_headers import SecurityHeadersMiddleware
from backend.app.routers import analyze, explain, health, medicines, scans
from backend.app.services.explanation_cache import reset_shared_explanation_cache
from backend.app.services.llm_service import LlmExplanationService
from backend.app.services.medicine_service import MedicineQueryService
from backend.app.services.scan_service import ScanQueryService
from src.database.session import reset_engine
from src.services.pipeline_manager import PipelineManager

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load AI models once at startup; release them on shutdown."""
    settings = get_api_settings()
    configure_logging(settings.log_level)

    logger.info("Starting %s v%s", settings.app_name, settings.app_version)
    logger.info("Environment: %s", settings.environment)
    logger.info("OCR mode: %s", settings.ocr_mode)
    logger.info("API docs enabled: %s", settings.docs_enabled)
    logger.info("Explain status: %s", settings.llm_status_message)
    if settings.llm_enabled and not settings.llm_is_configured:
        logger.warning(
            "Explain is enabled but not ready. "
            "POST /api/v1/explain will return 503 until configured."
        )
    elif settings.llm_is_configured:
        logger.info(
            "Explain ready (cache=%s, rate_limit=%s/min)",
            settings.llm_cache_enabled,
            (
                settings.rate_limit_explain_per_minute
                if settings.rate_limit_enabled
                else "off"
            ),
        )

    pipeline_config = settings.create_pipeline_config()
    manager = PipelineManager.get_instance(pipeline_config)

    try:
        manager.load()
    except Exception:
        logger.exception("Pipeline models failed to load.")
        raise

    medicine_service = MedicineQueryService.from_pipeline_config(pipeline_config)
    scan_service = ScanQueryService.from_pipeline_config(
        pipeline_config,
        max_entries=settings.scan_history_max_entries,
    )
    app.state.pipeline_manager = manager
    app.state.medicine_service = medicine_service
    app.state.scan_service = scan_service
    app.state.api_settings = settings

    if settings.llm_is_configured:
        app.state.llm_service = LlmExplanationService.get_instance(settings)

    logger.info(
        "Scan history ready (max_entries=%s)",
        settings.scan_history_max_entries,
    )
    logger.info("API startup complete.")

    yield

    logger.info("Shutting down API.")
    manager.unload()
    PipelineManager.reset_instance()
    LlmExplanationService.reset_instance()
    MedicineQueryService.reset_instance()
    ScanQueryService.reset_instance()
    reset_shared_explanation_cache()
    reset_engine()


def create_app(settings: ApiSettings | None = None) -> FastAPI:
    settings = settings or get_api_settings()
    settings.validate_production_security()
    settings.validate_llm_configuration()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
        docs_url="/docs" if settings.docs_enabled else None,
        redoc_url="/redoc" if settings.docs_enabled else None,
        openapi_url="/openapi.json" if settings.docs_enabled else None,
    )

    register_exception_handlers(app)

    app.add_middleware(SecurityHeadersMiddleware)

    if settings.rate_limit_enabled:
        limiter = AnalyzeRateLimiter(
            max_requests=settings.rate_limit_analyze_per_minute,
        )
        app.add_middleware(
            AnalyzeRateLimitMiddleware,
            limiter=limiter,
        )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(
        analyze.router,
        prefix=settings.api_prefix,
    )
    app.include_router(
        medicines.router,
        prefix=settings.api_prefix,
    )
    app.include_router(
        explain.router,
        prefix=settings.api_prefix,
    )
    app.include_router(
        scans.router,
        prefix=settings.api_prefix,
    )

    return app


app = create_app()
