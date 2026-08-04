# Port 8000 uzerindeki tum backend sureclerini durdurur.
# Kullanim: powershell -ExecutionPolicy Bypass -File scripts/stop-backend.ps1

$ErrorActionPreference = "SilentlyContinue"

for ($attempt = 1; $attempt -le 8; $attempt++) {
    $pids = @()

    $netstatLines = netstat -ano | Select-String ":8000\s+.*LISTENING"
    foreach ($line in $netstatLines) {
        $parts = ($line.ToString().Trim() -split "\s+")
        if ($parts.Length -ge 1) {
            $pids += [int]$parts[-1]
        }
    }

    $connectionPids = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue |
        Select-Object -ExpandProperty OwningProcess -Unique
    if ($connectionPids) {
        $pids += $connectionPids
    }

    $pids = $pids | Sort-Object -Unique
    if (-not $pids) {
        Write-Host "Port 8000 bos."
        break
    }

    foreach ($procId in $pids) {
        Write-Host "Durduruluyor: PID $procId"
        Stop-Process -Id $procId -Force
    }

    Start-Sleep -Seconds 2
}

$remaining = netstat -ano | Select-String ":8000\s+.*LISTENING"
if ($remaining) {
    Write-Warning "Port 8000 hala dolu. Gorev Yoneticisi'nden python.exe sureclerini kapatin."
    exit 1
}

Write-Host "Backend surecleri temizlendi."
