<#
.SYNOPSIS
    Safely removes .git directory from a target copy for presentation/submission.
.PARAMETER TargetPath
    Path to the copy to clean up. If omitted, prompts the user.
.PARAMETER Force
    Skips interactive confirmation.
#>
param (
    [string]$TargetPath = "",
    [switch]$Force
)

Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "  GRC Risk Register — Presentation Git Removal Tool" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ""

if ([string]::IsNullOrWhiteSpace($TargetPath)) {
    Write-Host "Enter the path to the presentation copy directory you wish to clean:" -ForegroundColor White
    Write-Host "Leave blank to target current directory: $($PWD.Path)" -ForegroundColor Gray
    $inputPath = Read-Host "Target Directory"
    if ([string]::IsNullOrWhiteSpace($inputPath)) {
        $TargetPath = $PWD.Path
    } else {
        $TargetPath = $inputPath
    }
}

$TargetPath = [System.IO.Path]::GetFullPath($TargetPath)
Write-Host "Target directory: $TargetPath" -ForegroundColor Yellow

$gitDir = Join-Path $TargetPath ".git"

if (-not (Test-Path $gitDir)) {
    Write-Host "No .git directory found at: $gitDir" -ForegroundColor Gray
    Write-Host "Nothing to remove." -ForegroundColor Green
    exit 0
}

Write-Host "Found Git metadata at: $gitDir" -ForegroundColor Yellow
Write-Host "This will remove the Git version history from this target directory." -ForegroundColor Yellow
Write-Host "Source files, database, and templates will remain untouched." -ForegroundColor White
Write-Host ""

$confirmed = $Force
if (-not $confirmed) {
    $confirmText = Read-Host "Type 'YES' to proceed with removing .git from $TargetPath"
    if ($confirmText -eq "YES") {
        $confirmed = $true
    }
}

if ($confirmed) {
    try {
        # Clear read-only attributes on git objects before removal
        Get-ChildItem -Path $gitDir -Recurse -Force -ErrorAction SilentlyContinue | ForEach-Object { $_.Attributes = 'Normal' }
        Remove-Item -Path $gitDir -Recurse -Force
        Write-Host "[SUCCESS] .git directory successfully removed from $TargetPath." -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] Failed to remove .git directory: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "Operation cancelled. No changes made." -ForegroundColor Gray
}

Write-Host ""
