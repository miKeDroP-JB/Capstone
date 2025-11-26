@echo off
title 0RB_AETHER Installer
color 0B

echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║                     0RB_AETHER INSTALLER                      ║
echo ║          Love  -  Loyalty  -  Honor  -  Everybody Eats        ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

echo [1/3] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo   X Python not found!
    echo   Download from: https://www.python.org/downloads/
    echo   Make sure to check "Add Python to PATH"
    pause
    exit /b 1
)
echo   √ Python found

echo [2/3] Installing dependencies...
python -m pip install -q fastapi uvicorn pydantic httpx aiofiles tomli
echo   √ Dependencies installed

echo [3/3] Creating launcher...
(
echo @echo off
echo title 0RB_AETHER
echo cd /d "%%~dp0"
echo python launch.py
echo pause
) > START_0RB.bat
echo   √ Created START_0RB.bat

echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║                   INSTALLATION COMPLETE!                      ║
echo ║                                                               ║
echo ║  Run START_0RB.bat to launch, then open:                     ║
echo ║  http://localhost:8080                                       ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

set /p launch="Launch now? (Y/n): "
if /i "%launch%"=="n" goto end
python launch.py

:end
pause
