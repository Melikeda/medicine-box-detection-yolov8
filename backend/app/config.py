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

    @property
    def max_upload_size_bytes(self) -> int:
        return int(self.max_upload_size_mb * 1024 * 1024)

    def create_pipeline_config(self) -> PipelineConfig:
        from pathlib import Path

        return PipelineConfig(
            ocr_mode=self.ocr_mode,
            use_gpu=self.use_gpu,
            use_sqlite=self.use_sqlite,
            sqlite_path=Path(self.sqlite_path),
        )


@lru_cache
def get_api_settings() -> ApiSettings:
    return ApiSettings()
