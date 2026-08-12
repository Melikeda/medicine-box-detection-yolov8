#Requires -Version 5.1
<#
.SYNOPSIS
  Restrict ACL on %USERPROFILE%\.kaggle\kaggle.json to the current user only.

.DESCRIPTION
  Kaggle CLI credentials must never be world-readable or committed to Git.
  This script:
  - Verifies kaggle.json exists under ~/.kaggle
  - Removes inherited ACLs
  - Grants FullControl only to the current Windows user
  - Reminds you to expire unused Kaggle Access Tokens in the web UI

  Does NOT print or upload the key.
#>

$ErrorActionPreference = "Stop"

$kaggleDir = Join-Path $env:USERPROFILE ".kaggle"
$kaggleJson = Join-Path $kaggleDir "kaggle.json"

if (-not (Test-Path -LiteralPath $kaggleJson)) {
    Write-Error "Missing $kaggleJson. Place your Legacy API kaggle.json there first (never commit it)."
}

# Basic shape check without dumping secrets
try {
    $obj = Get-Content -LiteralPath $kaggleJson -Raw -Encoding UTF8 | ConvertFrom-Json
} catch {
    Write-Error "kaggle.json is not valid JSON."
}

if ([string]::IsNullOrWhiteSpace($obj.username) -or [string]::IsNullOrWhiteSpace($obj.key)) {
    Write-Error "kaggle.json must contain non-empty 'username' and 'key' fields."
}

New-Item -ItemType Directory -Force -Path $kaggleDir | Out-Null

# Directory: current user only
$dirAcl = Get-Acl -LiteralPath $kaggleDir
$dirAcl.SetAccessRuleProtection($true, $false)
$dirAcl.Access | ForEach-Object { [void]$dirAcl.RemoveAccessRule($_) }
$dirRule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    $env:USERNAME,
    "FullControl",
    "ContainerInherit,ObjectInherit",
    "None",
    "Allow"
)
$dirAcl.AddAccessRule($dirRule)
Set-Acl -LiteralPath $kaggleDir -AclObject $dirAcl

# File: current user only
$fileAcl = Get-Acl -LiteralPath $kaggleJson
$fileAcl.SetAccessRuleProtection($true, $false)
$fileAcl.Access | ForEach-Object { [void]$fileAcl.RemoveAccessRule($_) }
$fileRule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    $env:USERNAME,
    "FullControl",
    "Allow"
)
$fileAcl.AddAccessRule($fileRule)
Set-Acl -LiteralPath $kaggleJson -AclObject $fileAcl

# Remove common accidental copies
$downloadsCopy = Join-Path $env:USERPROFILE "Downloads\kaggle.json"
if (Test-Path -LiteralPath $downloadsCopy) {
    Remove-Item -LiteralPath $downloadsCopy -Force
    Write-Host "Removed Downloads\kaggle.json copy."
}

Write-Host "Hardened ACL on:"
Write-Host "  $kaggleDir"
Write-Host "  $kaggleJson"
Write-Host "Username present: $($obj.username)"
Write-Host ""
Write-Host "Next (Kaggle web UI):"
Write-Host "  1) https://www.kaggle.com/settings/account -> API"
Write-Host "  2) Expire unused Access Tokens (keep only what you need)"
Write-Host "  3) If this key may have leaked: Expire Legacy API Key, create a new one, replace ~/.kaggle/kaggle.json, re-run this script"
