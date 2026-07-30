# Permanently add Flutter/Android/Java to the current user's PATH (Windows).
# Run once after initial setup: .\scripts\install-flutter-path.ps1

$ErrorActionPreference = "Stop"

$FlutterHome = "C:\src\flutter"
$JavaHome = "C:\Program Files\Microsoft\jdk-17.0.20.8-hotspot"
$AndroidHome = Join-Path $env:LOCALAPPDATA "Android\Sdk"

$userPath = [Environment]::GetEnvironmentVariable("Path", "User")

$entries = @(
    (Join-Path $FlutterHome "bin"),
    (Join-Path $JavaHome "bin"),
    (Join-Path $AndroidHome "platform-tools"),
    (Join-Path $AndroidHome "cmdline-tools\latest\bin"),
    (Join-Path $AndroidHome "emulator")
)

foreach ($entry in $entries) {
    if (-not (Test-Path $entry)) {
        Write-Warning "Path not found, skipping: $entry"
        continue
    }
    if ($userPath -notlike "*$entry*") {
        $userPath = if ([string]::IsNullOrWhiteSpace($userPath)) { $entry } else { "$userPath;$entry" }
        Write-Host "Added to PATH: $entry" -ForegroundColor Green
    } else {
        Write-Host "Already in PATH: $entry"
    }
}

[Environment]::SetEnvironmentVariable("Path", $userPath, "User")
[Environment]::SetEnvironmentVariable("FLUTTER_HOME", $FlutterHome, "User")
[Environment]::SetEnvironmentVariable("JAVA_HOME", $JavaHome, "User")
[Environment]::SetEnvironmentVariable("ANDROID_HOME", $AndroidHome, "User")
[Environment]::SetEnvironmentVariable("ANDROID_SDK_ROOT", $AndroidHome, "User")

Write-Host ""
Write-Host "User environment variables updated." -ForegroundColor Green
Write-Host "Open a new terminal for PATH changes to take effect globally."
