# Flutter + Android development environment for medicine-box-detection-yolov8
# Source this file in PowerShell: . .\scripts\env-flutter.ps1

$FlutterHome = "C:\src\flutter"
$JavaHome = "C:\Program Files\Microsoft\jdk-17.0.20.8-hotspot"
$AndroidHome = Join-Path $env:LOCALAPPDATA "Android\Sdk"

$env:FLUTTER_HOME = $FlutterHome
$env:JAVA_HOME = $JavaHome
$env:ANDROID_HOME = $AndroidHome
$env:ANDROID_SDK_ROOT = $AndroidHome

$pathEntries = @(
    (Join-Path $FlutterHome "bin"),
    (Join-Path $JavaHome "bin"),
    (Join-Path $AndroidHome "platform-tools"),
    (Join-Path $AndroidHome "cmdline-tools\latest\bin"),
    (Join-Path $AndroidHome "emulator")
)

foreach ($entry in $pathEntries) {
    if (Test-Path $entry) {
        if ($env:Path -notlike "*$entry*") {
            $env:Path = "$entry;$env:Path"
        }
    }
}

Write-Host "Flutter env loaded:" -ForegroundColor Green
Write-Host "  FLUTTER_HOME=$env:FLUTTER_HOME"
Write-Host "  JAVA_HOME=$env:JAVA_HOME"
Write-Host "  ANDROID_HOME=$env:ANDROID_HOME"
