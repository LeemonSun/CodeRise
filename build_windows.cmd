@echo off
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\build_windows.ps1"
if errorlevel 1 (
    echo.
    echo Build failed. See error above.
    pause
    exit /b 1
)
echo.
echo Build completed. Check release folder.
pause
