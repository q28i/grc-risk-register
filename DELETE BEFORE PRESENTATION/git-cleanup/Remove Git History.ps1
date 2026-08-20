<#
.SYNOPSIS
    GRC Risk Register — Safe Presentation Git Removal Tool
.DESCRIPTION
    Safely removes .git directory from a specified target directory.
.PARAMETER TargetPath
    Path to the presentation copy folder.
.PARAMETER Force
    Skip interactive confirmation.
#>
param (
    [string]$TargetPath = "",
    [switch]$Force
)

Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "  GRC Risk Register — Safe Git History Removal Tool" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ""

if ([string]::IsNullOrWhiteSpace($TargetPath)) {
    Write-Host "Enter the full path to the presentation copy folder you want to clean." -ForegroundColor White
    Write-Host "(Example: C:\Users\YourName\Desktop\Presentation Copy)" -ForegroundColor Gray
    Write-Host ""
    $TargetPath = Read-Host "Target Folder Path"
}

if ([string]::IsNullOrWhiteSpace($TargetPath)) {
    Write-Host "`n[ERROR] No target folder specified. Refusing to operate on unknown folder." -ForegroundColor Red
    exit 1
}

$TargetPath = [System.IO.Path]::GetFullPath($TargetPath)

if (-not (Test-Path $TargetPath)) {
    Write-Host "`n[ERROR] Target folder does not exist: $TargetPath" -ForegroundColor Red
    exit 1
}

$gitDir = Join-Path $TargetPath ".git"

if (-not (Test-Path $gitDir)) {
    Write-Host "`n[INFO] No .git directory found at: $gitDir" -ForegroundColor Gray
    Write-Host "[INFO] Nothing to remove." -ForegroundColor Green
    exit 0
}

Write-Host "`nTarget Folder:" -ForegroundColor White
Write-Host "  $TargetPath" -ForegroundColor Yellow
Write-Host "Found Git Metadata:" -ForegroundColor White
Write-Host "  $gitDir" -ForegroundColor Yellow
Write-Host ""
Write-Host "WARNING: This will permanently delete the Git history from THIS COPY." -ForegroundColor Yellow
Write-Host "Source code, database, and project files will remain untouched." -ForegroundColor White
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ""

$confirmed = $Force
if (-not $confirmed) {
    $confirmText = Read-Host "Are you sure you want to permanently remove Git history from THIS COPY? (Y/N)"
    if ($confirmText -eq "Y" -or $confirmText -eq "YES") {
        $confirmed = $true
    }
}

if ($confirmed) {
    Write-Host "`n[REMOVING] Deleting .git directory..." -ForegroundColor Yellow
    try {
        Get-ChildItem -Path $gitDir -Recurse -Force -ErrorAction SilentlyContinue | ForEach-Object { $_.Attributes = 'Normal' }
        Remove-Item -Path $gitDir -Recurse -Force
        Write-Host "`n[SUCCESS] Git history removed successfully from:`n  $TargetPath" -ForegroundColor Green
    } catch {
        Write-Host "`n[ERROR] Failed to remove .git directory: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "`n[CANCELLED] Operation cancelled by user. No changes made." -ForegroundColor Gray
}

Write-Host ""
