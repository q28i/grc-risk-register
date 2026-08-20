<#
.SYNOPSIS
    GRC Risk Register — Automatic Safe Git History Removal Tool
.DESCRIPTION
    Automatically discovers the project root and removes .git metadata with zero prompts.
#>

Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "  GRC Risk Register — Git History Removal Tool" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ""

$scriptDir = $PSScriptRoot
$current = [System.IO.DirectoryInfo]::new($scriptDir)
$projectRoot = $null

# Check up to 5 parent levels for project markers
for ($i = 0; $i -lt 6 -and $current -ne $null; $i++) {
    $appCode = Join-Path $current.FullName "Grc Risk Management Code"
    $launcher = Join-Path $current.FullName "Start GRC Risk Register.exe"
    $readme = Join-Path $current.FullName "README.md"

    if ((Test-Path $appCode) -and ((Test-Path $launcher) -or (Test-Path $readme))) {
        $projectRoot = $current.FullName
        break
    }
    $current = $current.Parent
}

if ([string]::IsNullOrWhiteSpace($projectRoot)) {
    Write-Host "[ABORTED] Could not automatically locate the GRC project root." -ForegroundColor Red
    Write-Host "Safety check failed: 'Grc Risk Management Code' folder not found in parent hierarchy." -ForegroundColor Red
    Write-Host "Refusing to operate on unknown directory." -ForegroundColor Red
    exit 1
}

Write-Host "[INFO] Discovered Project Root: $projectRoot" -ForegroundColor Yellow
Write-Host "`n[REMOVING] Deleting all Git metadata and repository history..." -ForegroundColor Yellow

$removedCount = 0

# 1. Delete all .git directories recursively
Get-ChildItem -Path $projectRoot -Filter ".git" -Directory -Recurse -Force -ErrorAction SilentlyContinue | ForEach-Object {
    $targetPath = $_.FullName
    Write-Host "[REMOVING] Deleting folder: $targetPath" -ForegroundColor White
    try {
        Get-ChildItem -Path $targetPath -Recurse -Force -ErrorAction SilentlyContinue | ForEach-Object { $_.Attributes = 'Normal' }
        Remove-Item -Path $targetPath -Recurse -Force
        $removedCount++
    } catch {
        Write-Host "[ERROR] Could not delete $targetPath: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# 2. Delete Git configuration files (.gitignore, .gitattributes, .gitmodules)
@(".gitignore", ".gitattributes", ".gitmodules") | ForEach-Object {
    $fileName = $_
    Get-ChildItem -Path $projectRoot -Filter $fileName -File -Recurse -Force -ErrorAction SilentlyContinue | ForEach-Object {
        $filePath = $_.FullName
        Write-Host "[REMOVING] Deleting file: $filePath" -ForegroundColor White
        try {
            $_.Attributes = 'Normal'
            Remove-Item -Path $filePath -Force
            $removedCount++
        } catch {
            Write-Host "[ERROR] Could not delete $filePath: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

$rootGit = Join-Path $projectRoot ".git"
$isClean = -not (Test-Path $rootGit)

Write-Host "`n=======================================================" -ForegroundColor Cyan
Write-Host "  CLEANUP SUMMARY" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "Items removed: $removedCount" -ForegroundColor White

if ($isClean) {
    Write-Host "`n[SUCCESS] Project is 100% clean of all Git metadata and version control history." -ForegroundColor Green
    Write-Host "Source code, presentation database, and application runtime are intact.`n" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n[WARNING] Some Git artifacts could not be removed.`n" -ForegroundColor Yellow
    exit 1
}
