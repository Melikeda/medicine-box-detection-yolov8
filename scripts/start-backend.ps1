# Backend baslatma (Windows)
# Kullanim: powershell -ExecutionPolicy Bypass -File scripts/start-backend.ps1

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

& "$PSScriptRoot/stop-backend.ps1"
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

Write-Host "Backend baslatiliyor: http://127.0.0.1:8000"
Write-Host "LLM modeli .env dosyasindan okunur (gemini-flash-latest)"
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
