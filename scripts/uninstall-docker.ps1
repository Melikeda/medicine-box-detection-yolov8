#Requires -RunAsAdministrator
<#
  Completely remove Docker Desktop and leftover data from this machine.
  Usage:
    Set-ExecutionPolicy -Scope Process Bypass -Force
    .\scripts\uninstall-docker.ps1
#>

$ErrorActionPreference = "Continue"
$LogFile = Join-Path $PSScriptRoot "uninstall-docker.log"
"" | Set-Content $LogFile

function Log([string]$Message) {
    $line = "[$(Get-Date -Format 'HH:mm:ss')] $Message"
    Add-Content -Path $LogFile -Value $line
    Write-Host $Message
}

Log "=== Docker complete uninstall ==="

# 1. Stop Docker processes
Log "Stopping Docker processes ..."
$names = @(
    "Docker Desktop",
    "com.docker.backend",
    "com.docker.build",
    "com.docker.service",
    "docker",
    "docker-compose"
)
foreach ($name in $names) {
    Get-Process -Name $name -ErrorAction SilentlyContinue | ForEach-Object {
        Log "  Stopping $($_.Name) (PID $($_.Id))"
        Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
    }
}
Start-Sleep -Seconds 3

# 2. Stop Docker Windows service if present
$svc = Get-Service -Name "com.docker.service" -ErrorAction SilentlyContinue
if ($svc) {
    Log "Stopping com.docker.service ..."
    Stop-Service -Name "com.docker.service" -Force -ErrorAction SilentlyContinue
}

# 3. Remove Docker WSL distros (if any)
Log "Removing Docker WSL distros ..."
foreach ($distro in @("docker-desktop", "docker-desktop-data")) {
    $list = wsl -l -v 2>&1 | Out-String
    if ($list -match $distro) {
        Log "  wsl --unregister $distro"
        wsl --unregister $distro 2>&1 | ForEach-Object { Log "  $_" }
    } else {
        Log "  $distro not found (OK)"
    }
}

# 4. Uninstall via winget
Log "Uninstalling Docker Desktop (winget) ..."
$wingetOut = winget uninstall --id Docker.DockerDesktop `
    --accept-source-agreements `
    --disable-interactivity `
    --force 2>&1 | Out-String
Log $wingetOut

# 5. Fallback: Docker Desktop Installer uninstall
$installer = "$env:LOCALAPPDATA\Programs\DockerDesktop\Docker Desktop Installer.exe"
if (Test-Path $installer) {
    Log "Running Docker Desktop Installer uninstall ..."
    $p = Start-Process -FilePath $installer -ArgumentList "uninstall", "--quiet" -Wait -PassThru
    Log "  Installer exit code: $($p.ExitCode)"
}

# 6. Delete leftover folders
$paths = @(
    "$env:LOCALAPPDATA\Docker",
    "$env:LOCALAPPDATA\Programs\DockerDesktop",
    "$env:APPDATA\Docker",
    "$env:USERPROFILE\.docker",
    "$env:PROGRAMDATA\Docker",
    "$env:PROGRAMDATA\DockerDesktop"
)

Log "Removing leftover folders ..."
foreach ($path in $paths) {
    if (Test-Path $path) {
        Log "  Removing $path"
        Remove-Item -Path $path -Recurse -Force -ErrorAction SilentlyContinue
        if (Test-Path $path) {
            Log "  WARN: could not fully remove $path (may need reboot)"
        } else {
            Log "  OK removed"
        }
    } else {
        Log "  Skip (not found): $path"
    }
}

# 7. Verify
Log "Verification:"
$dockerCmd = Get-Command docker -ErrorAction SilentlyContinue
if ($dockerCmd) {
    Log "  WARN: docker still in PATH: $($dockerCmd.Source)"
} else {
    Log "  OK: docker command not found"
}

if (Test-Path "$env:LOCALAPPDATA\Programs\DockerDesktop") {
    Log "  WARN: DockerDesktop folder still exists"
} else {
    Log "  OK: DockerDesktop folder removed"
}

Log "=== Uninstall complete ==="
Log "Next: reboot, then reinstall Docker Desktop from https://www.docker.com/products/docker-desktop/"
