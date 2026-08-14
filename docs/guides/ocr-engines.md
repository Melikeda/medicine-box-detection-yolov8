# OCR engine

Yolocilin reads box text with **EasyOCR** (Turkish + English). That is the only engine in the product: `requirements.txt`, Docker, CI, CLI, and the API.

A one-off comparison with PaddleOCR was run on `feature/paddleocr-engine`. PaddleOCR was **not** adopted (similar identity accuracy, slower CPU, extra install, Windows runtime issues). It is not installed or loaded.

- Decision: [Report 26](../reports/26-ocr-engine-comparison.md)
- Trial record (photos, JSON, archived adapter): [experiments/paddleocr-comparison](../experiments/paddleocr-comparison/)
