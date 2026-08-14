# ARCHIVED — do not run as part of Yolocilin setup.
# One-off Windows helper from the PaddleOCR comparison trial (Report 26).

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

$python = Join-Path $projectRoot "venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    $python = "python"
}

Write-Host "Installing optional PaddleOCR deps (EasyOCR stays default)..."
& $python -m pip install -r (Join-Path $projectRoot "requirements-paddleocr.txt")
if ($LASTEXITCODE -ne 0) {
    Write-Host "Install failed. See docs/guides/ocr-engines.md" -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "Verifying import..."
& $python -c "from paddleocr import PaddleOCR; from src.ocr.engine import paddleocr_is_available; print('paddleocr_ok', paddleocr_is_available())"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Import failed. The default EasyOCR pipeline is unchanged." -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host ""
Write-Host "PaddleOCR ready. Default engine is still EasyOCR."
Write-Host "Compare:"
Write-Host "  python scripts/compare_ocr_engines.py --image data/samples/parol_plus.jpg --mode fast"
Write-Host "Use Paddle for one API session:"
Write-Host "  `$env:OCR_ENGINE='paddleocr'"
Write-Host "  python run_api.py"
