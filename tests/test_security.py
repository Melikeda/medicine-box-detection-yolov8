"""Production hardening: rate limit, headers, CORS, error masking."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.config import ApiSettings, get_api_settings
from backend.app.exceptions import register_exception_handlers
from backend.app.middleware.rate_limit import (
    AnalyzeRateLimitMiddleware,
    AnalyzeRateLimiter,
)
from backend.app.middleware.security_headers import SecurityHeadersMiddleware


def test_parse_cors_origins_from_comma_separated_string() -> None:
    settings = ApiSettings(cors_origins="http://localhost:3000, https://app.example.com")
    assert settings.cors_origins == (
        "http://localhost:3000",
        "https://app.example.com",
    )


def test_production_hides_internal_error_details() -> None:
    get_api_settings.cache_clear()
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/boom")
    def boom() -> None:
        raise RuntimeError("secret-db-password")

    app.state.api_settings = ApiSettings(environment="production")

    original_get = get_api_settings

    def production_settings() -> ApiSettings:
        return ApiSettings(environment="production")

    import backend.app.exceptions as exceptions_module

    exceptions_module.get_api_settings = production_settings
    try:
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/boom")
    finally:
        exceptions_module.get_api_settings = original_get
        get_api_settings.cache_clear()

    assert response.status_code == 500
    payload = response.json()
    assert payload["details"] == {}


def test_security_headers_middleware() -> None:
    app = FastAPI()
    app.add_middleware(SecurityHeadersMiddleware)

    @app.get("/ping")
    def ping() -> dict[str, str]:
        return {"ok": "true"}

    client = TestClient(app)
    response = client.get("/ping")

    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"


def test_analyze_rate_limit_returns_429() -> None:
    limiter = AnalyzeRateLimiter(max_requests=2, window_seconds=60)
    app = FastAPI()
    app.add_middleware(AnalyzeRateLimitMiddleware, limiter=limiter)

    @app.post("/api/v1/analyze")
    def analyze_stub() -> dict[str, bool]:
        return {"success": True}

    client = TestClient(app)
    assert client.post("/api/v1/analyze").status_code == 200
    assert client.post("/api/v1/analyze").status_code == 200
    blocked = client.post("/api/v1/analyze")
    assert blocked.status_code == 429
    assert blocked.json()["success"] is False


def test_analyze_rate_limiter_allows_other_paths() -> None:
    limiter = AnalyzeRateLimiter(max_requests=1, window_seconds=60)
    app = FastAPI()
    app.add_middleware(AnalyzeRateLimitMiddleware, limiter=limiter)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    client = TestClient(app)
    assert client.get("/health").status_code == 200
    assert client.get("/health").status_code == 200
