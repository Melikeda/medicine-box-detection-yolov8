# Gemini API key kurulumu — anahtari chat'e yapistirmayin.
# Kullanim: powershell -ExecutionPolicy Bypass -File scripts/setup-gemini-key.ps1

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$envFile = Join-Path $projectRoot ".env"

if (-not (Test-Path $envFile)) {
    Write-Error ".env dosyasi bulunamadi: $envFile"
}

$key = Read-Host "Gemini API key'inizi girin (AIza... ile baslar)"
$key = $key.Trim()

if ($key.Length -lt 20 -or -not $key.StartsWith("AIza")) {
    Write-Error "Gecersiz anahtar formati. Google AI Studio'dan alinan key AIza ile baslar."
}

$content = Get-Content $envFile -Raw -Encoding UTF8
if ($content -match "(?m)^GEMINI_API_KEY=.*$") {
    $content = [regex]::Replace(
        $content,
        "(?m)^GEMINI_API_KEY=.*$",
        "GEMINI_API_KEY=$key"
    )
} else {
    $content += "`nGEMINI_API_KEY=$key`n"
}

Set-Content -Path $envFile -Value $content.TrimEnd() -Encoding UTF8 -NoNewline
Add-Content -Path $envFile -Value "`n" -Encoding UTF8

Write-Host "GEMINI_API_KEY .env dosyasina kaydedildi." -ForegroundColor Green
Write-Host "Backend'i baslatmak icin:"
Write-Host "  python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload"
