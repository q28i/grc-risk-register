<#
.SYNOPSIS
    Removes the .git directory from a presentation copy with explicit confirmation.
#>

Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "  GRC Risk Register - Git Directory Removal Tool" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "WARNING: This utility is for preparing a presentation copy." -ForegroundColor Yellow
Write-Host "It will permanently delete the .git directory from THIS folder." -ForegroundColor Yellow
Write-Host ""
Write-Host "Current Directory: $PWD" -ForegroundColor White
Write-Host ""

$confirm = Read-Host "Type 'YES' to remove .git from this copy"

if ($confirm -eq "YES") {
    if (Test-Path ".git") {
        Write-Host "`nRemoving .git directory..." -ForegroundColor Yellow
        Remove-Item -Path ".git" -Recurse -Force
        Write-Host ".git directory successfully removed." -ForegroundColor Green
    } else {
        Write-Host "`nNo .git directory found in current folder." -ForegroundColor Gray
    }
} else {
    Write-Host "`nOperation cancelled. No changes made." -ForegroundColor Gray
}

Write-Host ""
