@echo off
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\publish_release.ps1"
if errorlevel 1 (
    echo.
    echo Release was not published. See error above.
    pause
    exit /b 1
)
echo.
echo Release created successfully.
pause
