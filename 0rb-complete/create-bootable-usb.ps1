# 0RB LIMITLESS OS - USB Installer Creator (Windows)
# ====================================================
# PowerShell script to create bootable USB on Windows
#
# Usage: Run as Administrator
#        .\create-bootable-usb.ps1
#

# Requires elevation
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Warning "Please run as Administrator!"
    pause
    exit
}

Write-Host @"
╔═══════════════════════════════════════════════════════════════╗
║         0RB LIMITLESS OS - USB INSTALLER CREATOR              ║
║                     (Windows Version)                         ║
║                                                               ║
║  Creates bootable USB with 0RB system                        ║
║  Love • Loyalty • Honor • Everybody Eats                     ║
╚═══════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan

# =============================================================================
# STEP 1: List Available USB Drives
# =============================================================================

Write-Host "`n[Step 1] Detecting USB drives..." -ForegroundColor Green

$drives = Get-Disk | Where-Object {$_.BusType -eq 'USB'}

if ($drives.Count -eq 0) {
    Write-Host "ERROR: No USB drives detected!" -ForegroundColor Red
    Write-Host "Please insert a USB drive and try again." -ForegroundColor Yellow
    pause
    exit
}

Write-Host "`nAvailable USB drives:" -ForegroundColor Cyan
$drives | Format-Table Number, FriendlyName, @{Name="Size"; Expression={"{0:N2} GB" -f ($_.Size / 1GB)}}

$diskNumber = Read-Host "`nEnter disk number to use"

$selectedDisk = Get-Disk -Number $diskNumber

if (-not $selectedDisk) {
    Write-Host "ERROR: Invalid disk number!" -ForegroundColor Red
    pause
    exit
}

Write-Host "`nSelected: $($selectedDisk.FriendlyName)" -ForegroundColor Cyan
Write-Host "Size: $([math]::Round($selectedDisk.Size / 1GB, 2)) GB" -ForegroundColor Cyan

$confirm = Read-Host "`nWARNING: This will ERASE ALL DATA on this drive!`nType 'YES' to continue"

if ($confirm -ne "YES") {
    Write-Host "Cancelled." -ForegroundColor Yellow
    exit
}

# =============================================================================
# STEP 2: Download Base ISO
# =============================================================================

Write-Host "`n[Step 2] Downloading Ubuntu ISO..." -ForegroundColor Green

$isoUrl = "https://releases.ubuntu.com/22.04/ubuntu-22.04.3-live-server-amd64.iso"
$isoFile = "$PSScriptRoot\ubuntu-22.04-server.iso"

if (-not (Test-Path $isoFile)) {
    Write-Host "  Downloading... (this may take a while)" -ForegroundColor Yellow

    $ProgressPreference = 'SilentlyContinue'
    Invoke-WebRequest -Uri $isoUrl -OutFile $isoFile
    $ProgressPreference = 'Continue'

    Write-Host "  ✓ Downloaded" -ForegroundColor Green
} else {
    Write-Host "  ✓ Using existing ISO" -ForegroundColor Green
}

# =============================================================================
# STEP 3: Format USB Drive
# =============================================================================

Write-Host "`n[Step 3] Formatting USB drive..." -ForegroundColor Green

# Clear disk
Clear-Disk -Number $diskNumber -RemoveData -Confirm:$false

# Create partition
$partition = New-Partition -DiskNumber $diskNumber -UseMaximumSize -IsActive
$volume = Format-Volume -Partition $partition -FileSystem FAT32 -NewFileSystemLabel "0RB_USB" -Confirm:$false

Write-Host "  ✓ Formatted" -ForegroundColor Green

# =============================================================================
# STEP 4: Mount ISO and Copy Files
# =============================================================================

Write-Host "`n[Step 4] Copying ISO contents..." -ForegroundColor Green

# Mount ISO
$mountResult = Mount-DiskImage -ImagePath $isoFile -PassThru
$isoLetter = ($mountResult | Get-Volume).DriveLetter

Write-Host "  ISO mounted at $isoLetter`:\" -ForegroundColor Yellow

# Get USB drive letter
$usbLetter = $volume.DriveLetter

# Copy ISO contents
Write-Host "  Copying files (this may take several minutes)..." -ForegroundColor Yellow
Copy-Item -Path "$isoLetter`:\*" -Destination "$usbLetter`:\" -Recurse -Force

# Unmount ISO
Dismount-DiskImage -ImagePath $isoFile

Write-Host "  ✓ ISO copied" -ForegroundColor Green

# =============================================================================
# STEP 5: Copy 0RB System Files
# =============================================================================

Write-Host "`n[Step 5] Copying 0RB system files..." -ForegroundColor Green

# Create 0rb directory on USB
$orbPath = "$usbLetter`:\0rb"
New-Item -ItemType Directory -Path $orbPath -Force | Out-Null

# Copy system files
$sourceFiles = @(
    "$PSScriptRoot\..\the_instant_creator.py",
    "$PSScriptRoot\..\ai_connectors.py",
    "$PSScriptRoot\..\brain_os.py",
    "$PSScriptRoot\..\ekosystem.py",
    "$PSScriptRoot\..\CREATE.py",
    "$PSScriptRoot\..\ai_guide.py"
)

foreach ($file in $sourceFiles) {
    if (Test-Path $file) {
        Copy-Item -Path $file -Destination $orbPath -Force
    }
}

# Copy entire 0rb-complete directory
if (Test-Path "$PSScriptRoot\*") {
    Copy-Item -Path $PSScriptRoot -Destination "$orbPath\0rb-complete" -Recurse -Force
}

# Copy documentation
$docs = Get-ChildItem "$PSScriptRoot\..\*.md"
foreach ($doc in $docs) {
    Copy-Item -Path $doc -Destination $orbPath -Force
}

Write-Host "  ✓ System files copied" -ForegroundColor Green

# =============================================================================
# STEP 6: Create Auto-Install Script
# =============================================================================

Write-Host "`n[Step 6] Creating install script..." -ForegroundColor Green

$installScript = @'
#!/bin/bash
# 0RB LIMITLESS OS - Auto Installer

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║         0RB LIMITLESS OS - INSTALLATION                       ║"
echo "╚═══════════════════════════════════════════════════════════════╝"

# Install to /opt/0rb
sudo mkdir -p /opt/0rb
sudo cp -r /media/usb/0rb/* /opt/0rb/
sudo chmod +x /opt/0rb/*.py

# Install dependencies
sudo apt update
sudo apt install -y python3 python3-pip docker.io docker-compose nginx

# Install Python packages
sudo pip3 install fastapi uvicorn httpx pydantic

# Start 0RB Bridge
cd /opt/0rb/0rb-complete
sudo docker-compose up -d

echo ""
echo "✅ Installation complete!"
echo "Dashboard: http://localhost:8080"
echo ""
'@

Set-Content -Path "$orbPath\install.sh" -Value $installScript -Encoding UTF8

Write-Host "  ✓ Install script created" -ForegroundColor Green

# =============================================================================
# STEP 7: Create README
# =============================================================================

Write-Host "`n[Step 7] Creating README..." -ForegroundColor Green

$readme = @"
# 0RB LIMITLESS OS - USB Installer

## What's on this USB

- Ubuntu 22.04 Server ISO
- Complete 0RB Empire system
- Auto-install script

## Installation Instructions

1. **Boot from this USB**
   - Insert USB into target PC
   - Restart computer
   - Press F12/F8/DEL to access boot menu
   - Select USB drive

2. **Install Ubuntu**
   - Choose "Install Ubuntu Server"
   - Follow prompts (defaults are fine)
   - Create username and password

3. **Install 0RB System**
   ```bash
   cd /media/usb/0rb
   sudo bash install.sh
   ```

4. **Access Dashboard**
   - Open browser
   - Go to http://localhost:8080
   - Start creating!

## System Requirements

- 8GB+ RAM
- 50GB+ storage
- 64-bit processor
- Internet connection

## Support

See WELCOME.md for complete guide
Run: python ai_guide.py for interactive help

## Philosophy

Love • Loyalty • Honor • Everybody Eats

💝 Built with love
"@

Set-Content -Path "$usbLetter`:\README.txt" -Value $readme -Encoding UTF8

Write-Host "  ✓ README created" -ForegroundColor Green

# =============================================================================
# FINALIZE
# =============================================================================

Write-Host "`n[Finalize] Syncing and ejecting..." -ForegroundColor Green

# Flush buffers
Write-VolumeCache -DriveLetter $usbLetter

Write-Host @"

╔═══════════════════════════════════════════════════════════════╗
║         USB INSTALLER CREATED SUCCESSFULLY! ✓                 ║
╚═══════════════════════════════════════════════════════════════╝

USB Drive: $usbLetter`:\ ($($selectedDisk.FriendlyName))
Size: $([math]::Round($selectedDisk.Size / 1GB, 2)) GB

Next Steps:
  1. Safely eject USB drive (right-click → Eject)
  2. Insert into target PC
  3. Boot from USB (F12/F8/DEL for boot menu)
  4. Follow installation prompts
  5. Run install.sh after Ubuntu boots
  6. Access dashboard at http://localhost:8080

💝 Your 0RB OS is ready to deploy!

"@ -ForegroundColor Green

pause
