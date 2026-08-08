"""
Deprecated stub — kept so old docs/imports do not point at an empty file.

Use the real entry points instead:

- API server: ``python run_api.py``
- CLI analyze: ``python run_analyze.py --image ...``
"""

from __future__ import annotations

__all__: list[str] = []


def main() -> None:
    raise SystemExit(
        "src/app.py is deprecated.\n"
        "  Start API:     python run_api.py\n"
        "  CLI analyze:   python run_analyze.py --image data/samples/parol_plus.jpg"
    )


if __name__ == "__main__":
    main()
