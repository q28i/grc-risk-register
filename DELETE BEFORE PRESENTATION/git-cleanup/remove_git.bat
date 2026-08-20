@echo off
setlocal

echo =======================================================
echo   GRC Risk Register - Git Directory Removal Tool
echo =======================================================
echo.
echo WARNING: This utility is for preparing a presentation copy.
echo It will permanently delete the .git directory from THIS folder.
echo.
echo Current Directory: %CD%
echo.
echo If this is your main development repository, DO NOT proceed!
echo.
set /p CONFIRM="Type 'YES' to remove .git from this copy: "

if /i "%CONFIRM%"=="YES" (
    if exist ".git" (
        echo.
        echo Removing .git directory...
        rmdir /s /q ".git"
        echo .git directory successfully removed.
    ) else (
        echo.
        echo No .git directory found in current folder.
    )
) else (
    echo.
    echo Operation cancelled. No changes made.
)

echo.
pause
