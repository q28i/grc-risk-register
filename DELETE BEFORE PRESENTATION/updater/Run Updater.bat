@echo off
setlocal

:: ============================================================================
:: GRC Risk Register — Application Updater Launcher
:: ============================================================================

set "SCRIPT_DIR=%~dp0"
set "UPDATER_PY=%SCRIPT_DIR%updater.py"
set "RUNTIME_PY=%SCRIPT_DIR%..\..\runtime\python.exe"

title GRC Risk Register — Updater

if not exist "%UPDATER_PY%" (
    echo [ERROR] updater.py not found in "%SCRIPT_DIR%".
    echo Please ensure the updater folder is intact.
    echo.
    pause
    exit /b 1
)

:: Try local embedded Python first
if exist "%RUNTIME_PY%" (
    "%RUNTIME_PY%" "%UPDATER_PY%" %*
    exit /b %errorlevel%
)

:: Try Python launcher (py -3)
py -3 --version >nul 2>&1
if %errorlevel% equ 0 (
    py -3 "%UPDATER_PY%" %*
    exit /b %errorlevel%
)

:: Try system python
python --version >nul 2>&1
if %errorlevel% equ 0 (
    python "%UPDATER_PY%" %*
    exit /b %errorlevel%
)

echo ============================================================================
echo [ERROR] Python was not found on this system.
echo ============================================================================
echo.
echo The updater requires Python to run.
echo If this is a fresh machine, run "Start GRC Risk Register.exe" first to
echo automatically provision the local runtime environment.
echo.
pause
exit /b 1
