@echo off
setlocal
echo =======================================================
echo   GRC Risk Register - Presentation Git Removal Tool
echo =======================================================
echo.

set "TARGET_DIR=%~1"
if "%TARGET_DIR%"=="" (
    set /p "TARGET_DIR=Enter path to presentation copy (press Enter for current folder): "
)
if "%TARGET_DIR%"=="" (
    set "TARGET_DIR=%cd%"
)

if not exist "%TARGET_DIR%\.git" (
    echo No .git directory found at: %TARGET_DIR%\.git
    echo Nothing to remove.
    goto :end
)

echo.
echo WARNING: This will remove version history from:
echo   %TARGET_DIR%\.git
echo.
set /p "CONFIRM=Type YES to confirm deletion: "
if /i not "%CONFIRM%"=="YES" (
    echo.
    echo Operation cancelled. No files modified.
    goto :end
)

echo.
echo Removing .git directory...
attrib -r -h -s "%TARGET_DIR%\.git\*.*" /s /d >nul 2>&1
rd /s /q "%TARGET_DIR%\.git"
if exist "%TARGET_DIR%\.git" (
    echo [ERROR] Failed to completely remove .git directory.
) else (
    echo [SUCCESS] .git directory removed successfully.
)

:end
echo.
endlocal
