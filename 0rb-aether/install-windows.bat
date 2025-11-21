@echo off
REM 0RB_AETHER Windows One-Click Installer
REM Downloads pre-built ISO and writes to USB

setlocal EnableDelayedExpansion

echo ============================================
echo        0RB_AETHER WINDOWS INSTALLER
echo ============================================
echo.

REM Check admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Run as Administrator
    echo Right-click this file and select "Run as administrator"
    pause
    exit /b 1
)

REM Download Rufus portable
echo [+] Downloading Rufus...
powershell -Command "& {Invoke-WebRequest -Uri 'https://github.com/pbatard/rufus/releases/download/v4.3/rufus-4.3p.exe' -OutFile '%TEMP%\rufus.exe'}"

REM Download ISO from GitHub
echo [+] Downloading 0RB_AETHER ISO...
set ISO_URL=https://github.com/miKeDroP-JB/Capstone/raw/claude/usb-bootable-meta-os-01TzhMb5gNhJ7FHLLvEY1q7H/0rb-aether/build/output/0rb-aether.iso
powershell -Command "& {Invoke-WebRequest -Uri '%ISO_URL%' -OutFile '%TEMP%\0rb-aether.iso'}"

if not exist "%TEMP%\0rb-aether.iso" (
    echo ERROR: Failed to download ISO
    pause
    exit /b 1
)

echo.
echo [+] ISO downloaded to: %TEMP%\0rb-aether.iso
echo [+] Opening Rufus...
echo.
echo INSTRUCTIONS:
echo 1. In Rufus, select your USB drive
echo 2. Click SELECT and choose: %TEMP%\0rb-aether.iso
echo 3. Set Partition scheme to: MBR
echo 4. Set Target system to: BIOS or UEFI
echo 5. Click START
echo.

start "" "%TEMP%\rufus.exe"

echo.
echo After Rufus completes:
echo 1. Restart your computer
echo 2. Press F12/F2/DEL during boot (depends on your PC)
echo 3. Select USB drive from boot menu
echo 4. In BIOS, disable Secure Boot if needed
echo.
pause
