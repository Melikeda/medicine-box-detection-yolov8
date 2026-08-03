"""Analyze endpoint için basit IP rate limit."""

from __future__ import annotations

import time
from collections import defaultdict
from threading import Lock

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class AnalyzeRateLimiter:
    def __init__(
        self,
        *,
        max_requests: int,
        window_seconds: int = 60,
    ) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def is_allowed(self, client_id: str) -> bool:
        now = time.monotonic()
        with self._lock:
            window_start = now - self.window_seconds
            hits = [
                timestamp
                for timestamp in self._hits[client_id]
                if timestamp > window_start
            ]
            if len(hits) >= self.max_requests:
                self._hits[client_id] = hits
                return False
            hits.append(now)
            self._hits[client_id] = hits
            return True


class AnalyzeRateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        *,
        limiter: AnalyzeRateLimiter,
        analyze_path_suffix: str = "/analyze",
    ) -> None:
        super().__init__(app)
        self.limiter = limiter
        self.analyze_path_suffix = analyze_path_suffix

    async def dispatch(self, request: Request, call_next):
        if (
            request.method == "POST"
            and request.url.path.endswith(self.analyze_path_suffix)
        ):
            client_host = request.client.host if request.client else "unknown"
            if not self.limiter.is_allowed(client_host):
                return JSONResponse(
                    status_code=429,
                    content={
                        "success": False,
                        "error": (
                            "Cok fazla analiz istegi. "
                            "Lutfen bir dakika sonra tekrar deneyin."
                        ),
                        "details": {},
                    },
                )

        return await call_next(request)
