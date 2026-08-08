from pathlib import Path
from typing import Annotated, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

from backend.app.llm_models import DEFAULT_GEMINI_MODEL
from src.services.config import OCRMode, PipelineConfig

EnvironmentMode = Literal["development", "production"]
LlmProvider = Literal["gemini", "mock"]

_BACKEND_DIR = Path(__file__).resolve().parents[1]
_PROJECT_ROOT = _BACKEND_DIR.parent
_ENV_FILE = _PROJECT_ROOT / ".env"


class ApiSettings(BaseSettings):
    """API runtime settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
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
    environment: EnvironmentMode = "development"

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

    cors_origins: Annotated[tuple[str, ...], NoDecode] = ("*",)
    rate_limit_enabled: bool = True
    rate_limit_analyze_per_minute: int = Field(default=20, ge=1, le=1000)

    use_sqlite: bool = True
    sqlite_path: str = "data/database/medicines.db"
    yolo_model_path: str | None = None

    llm_enabled: bool = False
    llm_provider: LlmProvider = "gemini"
    gemini_api_key: str | None = None
    llm_model: str = DEFAULT_GEMINI_MODEL
    llm_cache_enabled: bool = True
    llm_mock_mode: bool = False
    # Keep aligned with Gemini free-tier RPM guidance (see Report 21).
    rate_limit_explain_per_minute: int = Field(default=5, ge=1, le=1000)
    rate_limit_scans_per_minute: int = Field(default=30, ge=1, le=1000)
    scan_history_max_entries: int = Field(default=200, ge=10, le=5000)

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> tuple[str, ...]:
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped or stripped == "*":
                return ("*",)
            parts = tuple(
                part.strip()
                for part in stripped.split(",")
                if part.strip()
            )
            return parts or ("*",)
        if isinstance(value, (list, tuple)):
            return tuple(str(item).strip() for item in value if str(item).strip())
        return ("*",)

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def expose_error_details(self) -> bool:
        return not self.is_production

    @property
    def docs_enabled(self) -> bool:
        """Swagger/ReDoc/OpenAPI only outside production."""
        return not self.is_production

    @property
    def cors_allow_credentials(self) -> bool:
        """Browsers reject credentials with wildcard CORS origins."""
        return "*" not in self.cors_origins

    @property
    def max_upload_size_bytes(self) -> int:
        return int(self.max_upload_size_mb * 1024 * 1024)

    def validate_production_security(self) -> None:
        """Fail fast when production is misconfigured."""
        if not self.is_production:
            return

        if not self.cors_origins or "*" in self.cors_origins:
            raise RuntimeError(
                "ENVIRONMENT=production requires explicit CORS_ORIGINS "
                "(comma-separated origins; '*' is not allowed)."
            )

        self.validate_llm_configuration()

    def validate_llm_configuration(self) -> None:
        """
        Fail fast when explain is enabled but not usable.

        In production, LLM_ENABLED=true requires a valid key or mock mode.
        """
        if not self.llm_enabled or self.llm_is_configured:
            return

        message = (
            "LLM_ENABLED=true but explain is not configured. "
            "Set a valid GEMINI_API_KEY, or LLM_MOCK_MODE=true for local/dev."
        )
        if self.is_production:
            raise RuntimeError(message)

    @property
    def llm_is_configured(self) -> bool:
        if not self.llm_enabled:
            return False
        if self.llm_mock_mode or self.llm_provider == "mock":
            return True

        key = (self.gemini_api_key or "").strip()
        if len(key) < 20:
            return False

        lowered = key.lower()
        placeholder_markers = (
            "__buraya",
            "your_key",
            "paste",
            "example",
            "changeme",
            "replace_me",
            "xxx",
        )
        if any(marker in lowered for marker in placeholder_markers):
            return False

        return True

    @property
    def llm_status_message(self) -> str:
        """Human-readable explain readiness for /explain/info and logs."""
        if not self.llm_enabled:
            return "LLM kapali. Acmak icin LLM_ENABLED=true yapin."
        if self.llm_mock_mode or self.llm_provider == "mock":
            return "LLM hazir (mock mode)."
        if self.llm_is_configured:
            return "LLM hazir (Gemini)."
        key = (self.gemini_api_key or "").strip()
        if not key:
            return "LLM acik ama GEMINI_API_KEY eksik."
        return "LLM acik ama GEMINI_API_KEY gecersiz veya ornek deger."

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


def get_api_settings() -> ApiSettings:
    return ApiSettings()
