from __future__ import annotations

from threading import Lock


class ExplanationCache:
    """medicine_id + locale bazlı bellek içi açıklama önbelleği."""

    def __init__(self) -> None:
        self._entries: dict[str, str] = {}
        self._lock = Lock()

    @staticmethod
    def _cache_key(medicine_id: str, locale: str) -> str:
        return f"{medicine_id.strip().lower()}:{locale.strip().lower()}"

    def get(self, medicine_id: str, locale: str) -> str | None:
        key = self._cache_key(medicine_id, locale)
        with self._lock:
            return self._entries.get(key)

    def set(self, medicine_id: str, locale: str, explanation: str) -> None:
        key = self._cache_key(medicine_id, locale)
        with self._lock:
            self._entries[key] = explanation

    def clear(self) -> None:
        with self._lock:
            self._entries.clear()


_shared_cache: ExplanationCache | None = None


def get_shared_explanation_cache() -> ExplanationCache:
    """Uygulama genelinde paylaşılan cache singleton'ı döndürür."""
    global _shared_cache
    if _shared_cache is None:
        _shared_cache = ExplanationCache()
    return _shared_cache


def reset_shared_explanation_cache() -> None:
    """Test veya yeniden yapılandırma için paylaşılan cache'i sıfırlar."""
    global _shared_cache
    if _shared_cache is not None:
        _shared_cache.clear()
    _shared_cache = None
