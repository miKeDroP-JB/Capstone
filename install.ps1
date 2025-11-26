# 0RB_AETHER Windows Installer
# Love - Loyalty - Honor - Everybody Eats
#
# Run with: powershell -ExecutionPolicy Bypass -File install.ps1

$ErrorActionPreference = "Stop"

Write-Host @"

╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║     ██████╗ ██████╗ ██████╗      █████╗ ███████╗████████╗    ║
║    ██╔═████╗██╔══██╗██╔══██╗    ██╔══██╗██╔════╝╚══██╔══╝    ║
║    ██║██╔██║██████╔╝██████╔╝    ███████║█████╗     ██║       ║
║    ████╔╝██║██╔══██╗██╔══██╗    ██╔══██║██╔══╝     ██║       ║
║    ╚██████╔╝██║  ██║██████╔╝    ██║  ██║███████╗   ██║       ║
║     ╚═════╝ ╚═╝  ╚═╝╚═════╝     ╚═╝  ╚═╝╚══════╝   ╚═╝       ║
║                                                               ║
║                    WINDOWS INSTALLER                          ║
║                                                               ║
║          Love  -  Loyalty  -  Honor  -  Everybody Eats        ║
╚═══════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan

# Check Python
Write-Host "[1/4] Checking Python..." -ForegroundColor Yellow
$python = $null
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $version = & $cmd --version 2>&1
        if ($version -match "Python 3") {
            $python = $cmd
            Write-Host "  ✓ Found $version" -ForegroundColor Green
            break
        }
    } catch {}
}

if (-not $python) {
    Write-Host "  ✗ Python 3 not found!" -ForegroundColor Red
    Write-Host "  Install from: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "  Make sure to check 'Add Python to PATH'" -ForegroundColor Yellow
    exit 1
}

# Install dependencies
Write-Host "[2/4] Installing dependencies..." -ForegroundColor Yellow
$deps = @("fastapi", "uvicorn", "pydantic", "httpx", "aiofiles", "tomli")
foreach ($dep in $deps) {
    Write-Host "  Installing $dep..." -NoNewline
    & $python -m pip install -q $dep 2>&1 | Out-Null
    Write-Host " ✓" -ForegroundColor Green
}

# Create startup script
Write-Host "[3/4] Creating startup script..." -ForegroundColor Yellow
$startScript = @"
@echo off
title 0RB_AETHER
cd /d "%~dp0"
$python launch.py
pause
"@
$startScript | Out-File -FilePath "START_0RB.bat" -Encoding ASCII
Write-Host "  ✓ Created START_0RB.bat" -ForegroundColor Green

# Create desktop shortcut
Write-Host "[4/4] Creating desktop shortcut..." -ForegroundColor Yellow
$desktop = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktop "0RB_AETHER.lnk"
$WshShell = New-Object -ComObject WScript.Shell
$shortcut = $WshShell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = Join-Path $PWD "START_0RB.bat"
$shortcut.WorkingDirectory = $PWD
$shortcut.Description = "Launch 0RB_AETHER - Love Loyalty Honor Everybody Eats"
$shortcut.Save()
Write-Host "  ✓ Created desktop shortcut" -ForegroundColor Green

Write-Host @"

╔═══════════════════════════════════════════════════════════════╗
║                   INSTALLATION COMPLETE!                      ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  To start 0RB_AETHER:                                        ║
║                                                               ║
║    Option 1: Double-click '0RB_AETHER' on your desktop       ║
║    Option 2: Run 'START_0RB.bat' in this folder              ║
║    Option 3: Run '$python launch.py'                         ║
║                                                               ║
║  Then open: http://localhost:8080                            ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Green

# Ask to launch now
$launch = Read-Host "Launch 0RB_AETHER now? (Y/n)"
if ($launch -ne "n" -and $launch -ne "N") {
    Write-Host "`nStarting 0RB_AETHER...`n" -ForegroundColor Cyan
    & $python launch.py
}
