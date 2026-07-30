from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.services.config import OCRMode, PipelineConfig


class ApiSettings(BaseSettings):
    """API runtime settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Medicine Box Detection API"
    app_version: str = "0.1.0"
    api_prefix: str = "/api/v1"
    host: str = "127.0.0.1"
    port: int = 8000
    reload: bool = False
    log_level: str = "INFO"

    ocr_mode: OCRMode = "fast"
    use_gpu: bool = False

    max_upload_size_mb: float = Field(default=10.0, ge=0.1, le=50.0)
    allowed_extensions: tuple[str, ...] = (
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".bmp",
    )

    cors_origins: tuple[str, ...] = ("*",)

    use_sqlite: bool = True
    sqlite_path: str = "data/database/medicines.db"
    yolo_model_path: str | None = None

    @property
    def max_upload_size_bytes(self) -> int:
        return int(self.max_upload_size_mb * 1024 * 1024)

    def create_pipeline_config(self) -> PipelineConfig:
        from pathlib import Path

        from src.services.config import PROJECT_ROOT

        sqlite_path = Path(self.sqlite_path)
        if not sqlite_path.is_absolute():
            sqlite_path = PROJECT_ROOT / sqlite_path

        model_path = None
        if self.yolo_model_path:
            model_path = Path(self.yolo_model_path)
            if not model_path.is_absolute():
                model_path = PROJECT_ROOT / model_path

        pipeline_kwargs: dict = {
            "ocr_mode": self.ocr_mode,
            "use_gpu": self.use_gpu,
            "use_sqlite": self.use_sqlite,
            "sqlite_path": sqlite_path,
        }
        if model_path is not None:
            pipeline_kwargs["model_path"] = model_path

        return PipelineConfig(**pipeline_kwargs)


@lru_cache
def get_api_settings() -> ApiSettings:
    return ApiSettings()
