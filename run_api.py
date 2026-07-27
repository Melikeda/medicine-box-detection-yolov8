"""Run the FastAPI backend with Uvicorn."""

import uvicorn

from backend.app.config import get_api_settings


def main() -> None:
    settings = get_api_settings()

    uvicorn.run(
        "backend.app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
