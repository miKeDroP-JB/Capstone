# 0RB_AETHER PowerShell One-Click Installer
# Run as Administrator: Right-click -> Run with PowerShell

#Requires -RunAsAdministrator

$ErrorActionPreference = "Stop"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "     0RB_AETHER WINDOWS INSTALLER" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Download ISO
$ISOUrl = "https://github.com/miKeDroP-JB/Capstone/raw/claude/usb-bootable-meta-os-01TzhMb5gNhJ7FHLLvEY1q7H/0rb-aether/build/output/0rb-aether.iso"
$ISOPath = "$env:TEMP\0rb-aether.iso"

Write-Host "[+] Downloading 0RB_AETHER ISO..." -ForegroundColor Green
try {
    Invoke-WebRequest -Uri $ISOUrl -OutFile $ISOPath -UseBasicParsing
    Write-Host "[+] Downloaded to: $ISOPath" -ForegroundColor Green
} catch {
    Write-Host "[-] Download failed: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Manual download: $ISOUrl" -ForegroundColor Yellow
    pause
    exit 1
}

# List USB drives
Write-Host ""
Write-Host "[*] Available USB drives:" -ForegroundColor Yellow
Get-Disk | Where-Object { $_.BusType -eq 'USB' } | Format-Table -Property Number, FriendlyName, Size

Write-Host ""
$DiskNumber = Read-Host "Enter USB disk number to write to (or 'q' to quit)"

if ($DiskNumber -eq 'q') {
    Write-Host "Cancelled by user" -ForegroundColor Yellow
    exit 0
}

# Confirm
$Disk = Get-Disk -Number $DiskNumber
Write-Host ""
Write-Host "WARNING: This will ERASE all data on:" -ForegroundColor Red
Write-Host "  Disk $DiskNumber - $($Disk.FriendlyName) ($([math]::Round($Disk.Size/1GB, 2)) GB)" -ForegroundColor Red
Write-Host ""
$Confirm = Read-Host "Type 'YES' to continue"

if ($Confirm -ne 'YES') {
    Write-Host "Cancelled" -ForegroundColor Yellow
    exit 0
}

# Write ISO to USB
Write-Host ""
Write-Host "[+] Writing ISO to USB..." -ForegroundColor Green

try {
    # Clean disk
    Clear-Disk -Number $DiskNumber -RemoveData -Confirm:$false

    # Write ISO using dd-like method
    $ISOBytes = [System.IO.File]::ReadAllBytes($ISOPath)
    $Stream = [System.IO.File]::OpenWrite("\\.\PhysicalDrive$DiskNumber")
    $Stream.Write($ISOBytes, 0, $ISOBytes.Length)
    $Stream.Close()

    Write-Host "[+] Write complete!" -ForegroundColor Green
} catch {
    Write-Host "[-] Write failed: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Alternative: Use Rufus" -ForegroundColor Yellow
    Write-Host "1. Download Rufus: https://rufus.ie" -ForegroundColor Yellow
    Write-Host "2. Select ISO: $ISOPath" -ForegroundColor Yellow
    Write-Host "3. Select USB and click START" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "         INSTALLATION COMPLETE!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Restart your computer" -ForegroundColor White
Write-Host "2. Press F12/F2/DEL during boot to open boot menu" -ForegroundColor White
Write-Host "3. Select your USB drive" -ForegroundColor White
Write-Host "4. In BIOS: Disable Secure Boot if boot fails" -ForegroundColor White
Write-Host ""
pause
