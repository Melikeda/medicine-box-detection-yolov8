import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import get_api_settings
from backend.app.exceptions import register_exception_handlers
from backend.app.logging_config import configure_logging
from backend.app.routers import analyze, health, medicines
from src.services.pipeline_manager import PipelineManager

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load AI models once at startup; release them on shutdown."""
    settings = get_api_settings()
    configure_logging(settings.log_level)

    logger.info("Starting %s v%s", settings.app_name, settings.app_version)
    logger.info("OCR mode: %s", settings.ocr_mode)

    pipeline_config = settings.create_pipeline_config()
    manager = PipelineManager.get_instance(pipeline_config)

    try:
        manager.load()
    except Exception:
        logger.exception("Pipeline models failed to load.")
        raise

    app.state.pipeline_manager = manager
    app.state.api_settings = settings

    logger.info("API startup complete.")

    yield

    logger.info("Shutting down API.")
    manager.unload()
    PipelineManager.reset_instance()


def create_app() -> FastAPI:
    settings = get_api_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
    )

    register_exception_handlers(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=True,
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

    return app


app = create_app()
