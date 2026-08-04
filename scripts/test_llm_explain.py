"""Gemini explain endpoint canli testi (API key .env icinde olmali)."""

from __future__ import annotations

import json
import sys

import httpx

from backend.app.config import get_api_settings


def main() -> int:
    settings = get_api_settings()
    base = f"http://{settings.host}:{settings.port}"

    print("=== LLM Yapilandirma ===")
    print(f"LLM enabled: {settings.llm_enabled}")
    print(f"LLM configured: {settings.llm_is_configured}")
    print(f"Model: {settings.llm_model}")
    print(f"Mock mode: {settings.llm_mock_mode}")
    key = settings.gemini_api_key or ""
    print(f"API key set: {bool(key) and len(key) > 10}")

    if not settings.llm_is_configured:
        print("\nHATA: LLM yapilandirilmamis.")
        print("Calistirin: powershell -ExecutionPolicy Bypass -File scripts/setup-gemini-key.ps1")
        return 1

    with httpx.Client(base_url=base, timeout=60.0) as client:
        info = client.get("/api/v1/explain/info")
        info_payload = info.json()
        print("\n=== GET /api/v1/explain/info ===")
        print(json.dumps(info_payload, ensure_ascii=False, indent=2))

        api_model = info_payload.get("model")
        if api_model and api_model != settings.llm_model:
            print("\nUYARI: .env modeli ile calisan backend modeli FARKLI!")
            print(f"  .env:     {settings.llm_model}")
            print(f"  backend:  {api_model}")
            print("  Eski backend sureci 8000 portunda takili olabilir.")
            print("  Cozum:")
            print("    powershell -ExecutionPolicy Bypass -File scripts/stop-backend.ps1")
            print("    powershell -ExecutionPolicy Bypass -File scripts/start-backend.ps1")

        response = client.post(
            "/api/v1/explain",
            json={"medicine_id": "MED001", "locale": "tr"},
        )
        print("\n=== POST /api/v1/explain (MED001 - Parol) ===")
        print(f"Status: {response.status_code}")
        payload = response.json()
        if response.status_code == 200:
            print(f"Ilac: {payload.get('medicine_name')}")
            print(f"Provider: {payload.get('provider')} / {payload.get('model')}")
            print(f"Cached: {payload.get('cached')}")
            print(f"Aciklama: {payload.get('explanation')}")
            print(f"Disclaimer: {payload.get('disclaimer')}")
            return 0

        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    sys.exit(main())
