@echo off
title GRC Risk Register Launcher

:: 1. Navigate to script directory
cd /d "%~dp0"

:: If running from parent folder, enter project directory if present
if exist "Grc Risk Management Code\app.py" (
    cd "Grc Risk Management Code"
)

:: Verify app.py exists
if not exist "app.py" (
    echo.
    echo ========================================================
    echo   Error: app.py not found in the project directory.
    echo   Please ensure the launcher is located in the project
    echo   root folder.
    echo ========================================================
    echo.
    pause
    exit /b 1
)

:: 2. Locate Python executable
set "PYTHON_CMD="
set "PYTHONW_CMD="

python --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "PYTHON_CMD=python"
    set "PYTHONW_CMD=pythonw"
    goto PYTHON_READY
)

py -3 --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "PYTHON_CMD=py -3"
    set "PYTHONW_CMD=pyw -3"
    goto PYTHON_READY
)

py --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "PYTHON_CMD=py"
    set "PYTHONW_CMD=pyw"
    goto PYTHON_READY
)

echo.
echo ========================================================
echo   Python 3 is required to run GRC Risk Register.
echo   Please install Python 3 (https://www.python.org)
echo   and ensure it is added to your PATH, then try again.
echo ========================================================
echo.
pause
exit /b 1

:PYTHON_READY
echo ========================================================
echo   GRC Risk Register - Plug-and-Play Launcher
echo ========================================================
echo.

:: 3. Health check: is GRC Risk Register already running on port 8000?
echo Checking if server is already running...
%PYTHON_CMD% -c "import urllib.request; resp=urllib.request.urlopen('http://127.0.0.1:8000/', timeout=2); html=resp.read().decode('utf-8', errors='ignore'); exit(0 if 'GRC Risk Register' in html else 1)" >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo GRC Risk Register is already running.
    echo Opening default browser at http://127.0.0.1:8000...
    start "" "http://127.0.0.1:8000"
    ping 127.0.0.1 -n 2 >nul
    exit /b 0
)

:: 4. Start Python server as an independent detached background process
echo Starting local web server in the background...
start "" "%PYTHONW_CMD%" app.py

:: 5. Poll server until HTTP response is ready (up to 30 attempts, 1 sec each)
echo Waiting for server to become ready...
set ATTEMPTS=0

:POLL_LOOP
set /a ATTEMPTS+=1
%PYTHON_CMD% -c "import urllib.request; resp=urllib.request.urlopen('http://127.0.0.1:8000/', timeout=1); html=resp.read().decode('utf-8', errors='ignore'); exit(0 if 'GRC Risk Register' in html else 1)" >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo.
    echo Server is ready!
    echo Opening default browser at http://127.0.0.1:8000...
    start "" "http://127.0.0.1:8000"
    ping 127.0.0.1 -n 2 >nul
    exit /b 0
)

if %ATTEMPTS% geq 30 goto STARTUP_FAILED
ping 127.0.0.1 -n 2 >nul
goto POLL_LOOP

:STARTUP_FAILED
echo.
echo ========================================================
echo   GRC Risk Register could not be started.
echo   The server did not respond at http://127.0.0.1:8000
echo   within 30 seconds.
echo.
echo   Possible causes:
echo     1. Port 8000 is occupied by another application.
echo     2. Missing file permissions in the project folder.
echo ========================================================
echo.
pause
exit /b 1
