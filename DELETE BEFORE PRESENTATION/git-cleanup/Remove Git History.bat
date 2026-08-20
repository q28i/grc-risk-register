@echo off
setlocal enabledelayedexpansion

title GRC Risk Register — Remove Git History

echo =======================================================
echo   GRC Risk Register — Git History Removal Tool
echo =======================================================
echo.

set "SCRIPT_DIR=%~dp0"
set "PY_SCRIPT=%SCRIPT_DIR%remove_git_history.py"

:: Automatically resolve PROJECT_ROOT (navigate up to find Grc Risk Management Code)
set "PROJECT_ROOT="
set "CHECK_DIR=%SCRIPT_DIR%"

:: Check up to 4 parent levels
for /L %%i in (1,1,4) do (
    if exist "!CHECK_DIR!\Grc Risk Management Code" (
        if exist "!CHECK_DIR!\Start GRC Risk Register.exe" set "PROJECT_ROOT=!CHECK_DIR!"
        if exist "!CHECK_DIR!\README.md" set "PROJECT_ROOT=!CHECK_DIR!"
    )
    if not "!PROJECT_ROOT!"=="" goto :found_root
    for %%p in ("!CHECK_DIR!\..") do set "CHECK_DIR=%%~fp"
)

:found_root
if "%PROJECT_ROOT%"=="" (
    echo [ERROR] Could not automatically locate the GRC project root.
    echo Safety check failed: Expected "Grc Risk Management Code" marker was not found.
    echo Refusing to operate on unknown directory.
    echo.
    exit /b 1
)

:: Normalize path
for %%R in ("%PROJECT_ROOT%") do set "PROJECT_ROOT=%%~fR"

echo [INFO] Discovered Project Root: "%PROJECT_ROOT%"
echo.

:: Try local embedded Python first
set "RUNTIME_PY=%PROJECT_ROOT%\runtime\python.exe"
if exist "%RUNTIME_PY%" (
    if exist "%PY_SCRIPT%" (
        "%RUNTIME_PY%" "%PY_SCRIPT%"
        exit /b !errorlevel!
    )
)

:: Try Python launcher (py -3)
py -3 --version >nul 2>&1
if %errorlevel% equ 0 (
    if exist "%PY_SCRIPT%" (
        py -3 "%PY_SCRIPT%"
        exit /b !errorlevel!
    )
)

:: Try system python
python --version >nul 2>&1
if %errorlevel% equ 0 (
    if exist "%PY_SCRIPT%" (
        python "%PY_SCRIPT%"
        exit /b !errorlevel!
    )
)

:: Native Batch Fallback (if Python is not installed)
echo [REMOVING] Performing native cleanup of Git metadata...

if exist "%PROJECT_ROOT%\.git" (
    echo [REMOVING] Deleting "%PROJECT_ROOT%\.git"...
    attrib -r -h -s "%PROJECT_ROOT%\.git\*.*" /s /d >nul 2>&1
    rd /s /q "%PROJECT_ROOT%\.git" >nul 2>&1
)

if exist "%PROJECT_ROOT%\.gitignore" (
    attrib -r -h -s "%PROJECT_ROOT%\.gitignore" >nul 2>&1
    del /f /q "%PROJECT_ROOT%\.gitignore" >nul 2>&1
)

if exist "%PROJECT_ROOT%\.gitattributes" (
    attrib -r -h -s "%PROJECT_ROOT%\.gitattributes" >nul 2>&1
    del /f /q "%PROJECT_ROOT%\.gitattributes" >nul 2>&1
)

if exist "%PROJECT_ROOT%\.gitmodules" (
    attrib -r -h -s "%PROJECT_ROOT%\.gitmodules" >nul 2>&1
    del /f /q "%PROJECT_ROOT%\.gitmodules" >nul 2>&1
)

echo.
if exist "%PROJECT_ROOT%\.git" (
    echo [ERROR] Failed to completely remove .git directory.
    exit /b 1
) else (
    echo =======================================================
    echo [SUCCESS] Project is 100% clean of all Git metadata.
    echo =======================================================
    echo.
    exit /b 0
)
