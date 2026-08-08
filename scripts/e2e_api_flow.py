"""
Canli backend E2E + performans olcumu.

Akis:
  health → medicines → explain/info → (optional explain)
  → (optional analyze) → scans create/list/delete

Ornek:
  python scripts/e2e_api_flow.py
  python scripts/e2e_api_flow.py --image data/samples/parol_plus.jpg
  python scripts/e2e_api_flow.py --skip-analyze --json-out artifacts/e2e.json
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

import httpx

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.config import get_api_settings


def _step(
    name: str,
    fn,
    results: list[dict[str, Any]],
) -> Any:
    started = time.perf_counter()
    try:
        value = fn()
        elapsed_ms = (time.perf_counter() - started) * 1000
        results.append(
            {
                "step": name,
                "ok": True,
                "elapsed_ms": round(elapsed_ms, 1),
            }
        )
        print(f"[OK] {name}: {elapsed_ms:.0f} ms")
        return value
    except Exception as exc:
        elapsed_ms = (time.perf_counter() - started) * 1000
        results.append(
            {
                "step": name,
                "ok": False,
                "elapsed_ms": round(elapsed_ms, 1),
                "error": str(exc),
            }
        )
        print(f"[FAIL] {name}: {exc}")
        raise


def _sample_scan_payload() -> dict[str, Any]:
    return {
        "success": True,
        "filename": "e2e-synthetic.jpg",
        "detection_count": 1,
        "medicines": [
            {
                "box_index": 0,
                "bounding_box": {"x1": 0, "y1": 0, "x2": 10, "y2": 10},
                "yolo_confidence": 0.9,
                "ocr_text": "PAROL",
                "medicine_name": "Parol",
                "matching_score": 90.0,
                "status": "matched",
                "display_message": "Parol",
                "medicine": {
                    "medicine_id": "MED001",
                    "medicine_name": "Parol",
                },
            }
        ],
        "summary": {
            "matched_count": 1,
            "not_found_count": 0,
            "not_medicine_box_count": 0,
            "error_count": 0,
        },
        "ocr_mode": "fast",
        "processing_time_ms": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Mobile/backend API E2E + timing smoke test",
    )
    parser.add_argument(
        "--base-url",
        default=None,
        help="API base URL (default: from ApiSettings host/port)",
    )
    parser.add_argument(
        "--image",
        type=Path,
        default=PROJECT_ROOT / "data" / "samples" / "parol_plus.jpg",
        help="Analyze icin ornek goruntu",
    )
    parser.add_argument(
        "--skip-analyze",
        action="store_true",
        help="Gerçek OCR analyze adimini atla (hizli smoke)",
    )
    parser.add_argument(
        "--skip-explain",
        action="store_true",
        help="Explain POST adimini atla",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=None,
        help="Sonuclari JSON dosyasina yaz",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=300.0,
        help="HTTP timeout (analyze icin yuksek tutun)",
    )
    args = parser.parse_args()

    settings = get_api_settings()
    base_url = args.base_url or f"http://{settings.host}:{settings.port}"
    results: list[dict[str, Any]] = []
    report: dict[str, Any] = {
        "base_url": base_url,
        "steps": results,
    }

    print(f"E2E base URL: {base_url}")
    print(f"Skip analyze: {args.skip_analyze}")
    print(f"Skip explain: {args.skip_explain}")

    try:
        with httpx.Client(base_url=base_url, timeout=args.timeout) as client:
            health = _step(
                "GET /health",
                lambda: client.get("/health"),
                results,
            )
            if health.status_code != 200:
                raise RuntimeError(f"health status={health.status_code}")
            health_payload = health.json()
            report["health"] = {
                "status": health_payload.get("status"),
                "models_loaded": health_payload.get("models_loaded"),
                "medicine_count": health_payload.get("medicine_count"),
            }
            if health_payload.get("status") != "ok":
                raise RuntimeError("health status is not ok")

            meds = _step(
                "GET /api/v1/medicines?limit=5",
                lambda: client.get("/api/v1/medicines", params={"limit": 5}),
                results,
            )
            if meds.status_code != 200:
                raise RuntimeError(f"medicines status={meds.status_code}")
            report["medicines_total"] = meds.json().get("total")

            explain_info = _step(
                "GET /api/v1/explain/info",
                lambda: client.get("/api/v1/explain/info"),
                results,
            )
            explain_info_payload = explain_info.json()
            report["explain"] = {
                "ready": explain_info_payload.get("ready"),
                "status_message": explain_info_payload.get("status_message"),
            }

            if not args.skip_explain and explain_info_payload.get("ready"):
                explained = _step(
                    "POST /api/v1/explain (MED001)",
                    lambda: client.post(
                        "/api/v1/explain",
                        json={"medicine_id": "MED001", "locale": "tr"},
                    ),
                    results,
                )
                if explained.status_code != 200:
                    raise RuntimeError(
                        f"explain status={explained.status_code}: "
                        f"{explained.text}"
                    )
                report["explain"]["cached_first"] = explained.json().get(
                    "cached"
                )

                explained_2 = _step(
                    "POST /api/v1/explain cached (MED001)",
                    lambda: client.post(
                        "/api/v1/explain",
                        json={"medicine_id": "MED001", "locale": "tr"},
                    ),
                    results,
                )
                report["explain"]["cached_second"] = explained_2.json().get(
                    "cached"
                )

            analyze_payload: dict[str, Any]
            if args.skip_analyze:
                analyze_payload = _sample_scan_payload()
                results.append(
                    {
                        "step": "POST /api/v1/analyze",
                        "ok": True,
                        "elapsed_ms": 0.0,
                        "skipped": True,
                    }
                )
                print("[SKIP] POST /api/v1/analyze")
            else:
                if not args.image.exists():
                    raise FileNotFoundError(f"Image not found: {args.image}")
                if not health_payload.get("models_loaded"):
                    raise RuntimeError(
                        "models_loaded=false; analyze icin modeli yukleyin "
                        "veya --skip-analyze kullanin"
                    )

                def _analyze():
                    with args.image.open("rb") as handle:
                        return client.post(
                            "/api/v1/analyze",
                            params={"mode": "fast"},
                            files={
                                "file": (
                                    args.image.name,
                                    handle,
                                    "image/jpeg",
                                )
                            },
                        )

                analyzed = _step("POST /api/v1/analyze", _analyze, results)
                if analyzed.status_code != 200:
                    raise RuntimeError(
                        f"analyze status={analyzed.status_code}: "
                        f"{analyzed.text[:500]}"
                    )
                analyze_payload = analyzed.json()
                report["analyze"] = {
                    "success": analyze_payload.get("success"),
                    "detection_count": analyze_payload.get("detection_count"),
                    "matched_count": (
                        (analyze_payload.get("summary") or {}).get(
                            "matched_count"
                        )
                    ),
                    "processing_time_ms": analyze_payload.get(
                        "processing_time_ms"
                    ),
                    "timing": analyze_payload.get("timing"),
                }

            created = _step(
                "POST /api/v1/scans",
                lambda: client.post(
                    "/api/v1/scans",
                    json={
                        "response": analyze_payload,
                        "client_device_id": "e2e-script",
                    },
                ),
                results,
            )
            if created.status_code != 201:
                raise RuntimeError(
                    f"scans create status={created.status_code}: "
                    f"{created.text}"
                )
            scan_id = created.json()["scan"]["id"]
            report["scan_id"] = scan_id

            listed = _step(
                "GET /api/v1/scans",
                lambda: client.get("/api/v1/scans", params={"limit": 5}),
                results,
            )
            if listed.status_code != 200:
                raise RuntimeError(f"scans list status={listed.status_code}")

            _step(
                f"DELETE /api/v1/scans/{scan_id}",
                lambda: client.delete(f"/api/v1/scans/{scan_id}"),
                results,
            )

    except Exception as exc:
        report["ok"] = False
        report["error"] = str(exc)
        _write_report(args.json_out, report)
        print("\nE2E FAILED")
        return 1

    report["ok"] = True
    total_ms = sum(
        step.get("elapsed_ms", 0) for step in results if not step.get("skipped")
    )
    report["total_elapsed_ms"] = round(total_ms, 1)
    _write_report(args.json_out, report)

    print("\n=== Timing summary ===")
    for step in results:
        flag = "skip" if step.get("skipped") else ("ok" if step["ok"] else "fail")
        print(f"  {step['step']}: {step['elapsed_ms']} ms [{flag}]")
    print(f"Total (non-skip): {report['total_elapsed_ms']} ms")
    print("\nE2E PASSED")
    return 0


def _write_report(path: Path | None, report: dict[str, Any]) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Report written: {path}")


if __name__ == "__main__":
    sys.exit(main())
