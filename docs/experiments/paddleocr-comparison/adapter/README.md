# Archived trial code

These files were used only during the PaddleOCR comparison. They are **not** imported by `src/`, `backend/`, or `run_analyze.py`.

| File | Role during the trial |
|------|------------------------|
| `engine.py` | PaddleOCR → EasyOCR `readtext()` adapter |
| `compare_ocr_engines.py` | Side-by-side runner (required a pipeline `ocr_engine` switch that has been removed) |
| `requirements-paddleocr.txt` | Extra packages that must **not** be merged into product `requirements.txt` |
| `setup-paddleocr.ps1` | One-off Windows install helper from the trial |

Do not `pip install` this folder as part of normal setup. Reproduction is out of scope; conclusions live in [Report 26](../../../reports/26-ocr-engine-comparison.md).
