from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from backend.app.config import get_api_settings


class ApiError(Exception):
    """Base API exception with HTTP status code and message."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: dict | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class UnsupportedMediaTypeError(ApiError):
    def __init__(self, message: str) -> None:
        super().__init__(
            message,
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        )


class PayloadTooLargeError(ApiError):
    def __init__(self, message: str) -> None:
        super().__init__(
            message,
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
        )


class PipelineNotReadyError(ApiError):
    def __init__(self, message: str = "AI pipeline is not ready.") -> None:
        super().__init__(
            message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApiError)
    async def handle_api_error(
        _request: Request,
        exc: ApiError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": exc.message,
                "details": exc.details,
            },
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(
        _request: Request,
        exc: Exception,
    ) -> JSONResponse:
        settings = get_api_settings()
        details: dict = {}
        if settings.expose_error_details:
            details["reason"] = str(exc)

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "Internal server error.",
                "details": details,
            },
        )
