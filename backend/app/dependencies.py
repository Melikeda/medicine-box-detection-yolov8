from fastapi import Request

from backend.app.exceptions import PipelineNotReadyError
from src.services.pipeline_manager import PipelineManager


def get_pipeline_manager(request: Request) -> PipelineManager:
    """Return the singleton pipeline manager loaded during app startup."""
    manager = getattr(request.app.state, "pipeline_manager", None)

    if manager is None or not manager.is_loaded:
        raise PipelineNotReadyError()

    return manager
