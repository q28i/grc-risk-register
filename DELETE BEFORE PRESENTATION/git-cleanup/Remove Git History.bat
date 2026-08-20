@echo off
setlocal

:: ============================================================================
:: GRC Risk Register — Safe Git History Removal Tool
:: ============================================================================

set "SCRIPT_DIR=%~dp0"
set "PY_SCRIPT=%SCRIPT_DIR%remove_git_history.py"
set "RUNTIME_PY=%SCRIPT_DIR%..\..\runtime\python.exe"

title GRC Risk Register — Git History Removal

:: Try local embedded Python first
if exist "%RUNTIME_PY%" (
    "%RUNTIME_PY%" "%PY_SCRIPT%" %*
    exit /b %errorlevel%
)

:: Try Python launcher (py -3)
py -3 --version >nul 2>&1
if %errorlevel% equ 0 (
    py -3 "%PY_SCRIPT%" %*
    exit /b %errorlevel%
)

:: Try system python
python --version >nul 2>&1
if %errorlevel% equ 0 (
    python "%PY_SCRIPT%" %*
    exit /b %errorlevel%
)

:: Native Batch Fallback (if Python is unavailable)
echo =======================================================
echo   GRC Risk Register — Safe Git History Removal Tool
echo =======================================================
echo.

set "TARGET_DIR=%~1"

if "%TARGET_DIR%"=="" (
    echo Enter the full path to the presentation copy folder you want to clean.
    echo (Example: C:\Users\YourName\Desktop\Presentation Copy)
    echo.
    set /p "TARGET_DIR=Enter target folder path: "
)

if "%TARGET_DIR%"=="" (
    echo.
    echo [ERROR] No target folder specified.
    echo Refusing to operate on current directory without explicit confirmation.
    echo.
    pause
    exit /b 1
)

:: Trim quotes
set "TARGET_DIR=%TARGET_DIR:"=%"

if not exist "%TARGET_DIR%" (
    echo.
    echo [ERROR] Target folder does not exist:
    echo   "%TARGET_DIR%"
    echo.
    pause
    exit /b 1
)

set "GIT_DIR=%TARGET_DIR%\.git"

if not exist "%GIT_DIR%" (
    echo.
    echo [INFO] No .git directory found at:
    echo   "%GIT_DIR%"
    echo [INFO] Nothing to remove.
    echo.
    pause
    exit /b 0
)

echo.
echo Target Folder:
echo   "%TARGET_DIR%"
echo.
echo Found Git Metadata:
echo   "%GIT_DIR%"
echo.
echo WARNING: This will permanently delete the Git history from THIS COPY.
echo Source code, database, and project files will remain untouched.
echo =======================================================
echo.

set "CONFIRM="
set /p "CONFIRM=Are you sure you want to permanently remove Git history from THIS COPY? (Y/N): "

if /i not "%CONFIRM%"=="Y" if /i not "%CONFIRM%"=="YES" (
    echo.
    echo [CANCELLED] Operation cancelled by user. No changes made.
    echo.
    pause
    exit /b 0
)

echo.
echo [REMOVING] Deleting .git directory...

attrib -r -h -s "%GIT_DIR%\*.*" /s /d >nul 2>&1
rd /s /q "%GIT_DIR%" >nul 2>&1

if exist "%GIT_DIR%" (
    echo.
    echo [ERROR] Failed to completely remove .git directory.
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo =======================================================
    echo [SUCCESS] Git history removed successfully from:
    echo   "%TARGET_DIR%"
    echo =======================================================
    echo.
    pause
    exit /b 0
)
