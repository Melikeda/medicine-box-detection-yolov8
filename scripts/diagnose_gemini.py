"""Gemini baglanti teshisi — API key'i yazdirmaz."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


def main() -> int:
    if load_dotenv:
        load_dotenv(ROOT / ".env")

    key = os.environ.get("GEMINI_API_KEY", "").strip()
    model = os.environ.get("LLM_MODEL", "gemini-2.0-flash").strip()

    print("=== Gemini Teshis ===")
    print(f"Key format: {'AIza...' if key.startswith('AIza') else 'AQ...' if key.startswith('AQ.') else 'diger'}")
    print(f"Key length: {len(key)}")
    print(f"Model: {model}")

    if not key:
        print("HATA: GEMINI_API_KEY bos")
        return 1

    from google import genai

    client = genai.Client(api_key=key)

    print("\n--- Mevcut flash modeller (ilk 8) ---")
    count = 0
    for m in client.models.list():
        name = getattr(m, "name", "") or ""
        if "flash" in name.lower() and "preview" not in name.lower():
            print(name.replace("models/", ""))
            count += 1
            if count >= 8:
                break

    prompt = "Parol ilaci hakkinda en fazla 2 cumle Turkce bilgi ver."
    for candidate in [model, "gemini-2.0-flash", "gemini-2.5-flash-lite", "gemini-flash-lite-latest"]:
        print(f"\n--- Deneme: {candidate} ---")
        try:
            response = client.models.generate_content(
                model=candidate,
                contents=prompt,
            )
            text = (getattr(response, "text", None) or "").strip()
            print(f"SONUC: BASARILI ({len(text)} karakter)")
            print(text[:300])
            return 0
        except Exception as exc:
            err = str(exc)
            if len(err) > 400:
                err = err[:400] + "..."
            print(f"SONUC: HATA — {type(exc).__name__}")
            print(err)

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
