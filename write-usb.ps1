# 0RB LIMITLESS OS - Windows USB Writer
# Run this script as Administrator

param(
    [string]$IsoPath,
    [string]$UsbDrive
)

# Check for admin privileges
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

Write-Host @"
╔═══════════════════════════════════════════╗
║   0RB LIMITLESS OS - USB Writer          ║
║   Windows Edition                         ║
╚═══════════════════════════════════════════╝
"@ -ForegroundColor Cyan

# Find ISO if not provided
if (-not $IsoPath) {
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    $IsoPath = Join-Path $scriptDir "0rb-aether\build\output\0rb-aether.iso"

    if (-not (Test-Path $IsoPath)) {
        Write-Host "`nERROR: ISO not found at: $IsoPath" -ForegroundColor Red
        Write-Host "`nPlease build the ISO first or specify the path:" -ForegroundColor Yellow
        Write-Host "  .\write-usb.ps1 -IsoPath 'C:\path\to\0rb-aether.iso'" -ForegroundColor Gray
        exit 1
    }
}

Write-Host "`n✅ Found ISO: $IsoPath" -ForegroundColor Green
$isoSize = [math]::Round((Get-Item $IsoPath).Length / 1MB, 2)
Write-Host "   Size: $isoSize MB`n" -ForegroundColor Gray

# Show available USB drives
Write-Host "📋 Available USB drives:" -ForegroundColor Yellow
Get-Disk | Where-Object { $_.BusType -eq 'USB' } | Format-Table Number, FriendlyName, Size, PartitionStyle

# Get USB drive if not provided
if (-not $UsbDrive) {
    $diskNumber = Read-Host "`nEnter USB disk number (from 'Number' column above)"
} else {
    $diskNumber = $UsbDrive
}

# Validate disk
$disk = Get-Disk -Number $diskNumber -ErrorAction SilentlyContinue
if (-not $disk) {
    Write-Host "ERROR: Invalid disk number: $diskNumber" -ForegroundColor Red
    exit 1
}

if ($disk.BusType -ne 'USB') {
    Write-Host "WARNING: Disk $diskNumber is NOT a USB drive!" -ForegroundColor Red
    Write-Host "Bus Type: $($disk.BusType)" -ForegroundColor Red
    $confirm = Read-Host "Are you ABSOLUTELY SURE? (type 'YES I AM SURE')"
    if ($confirm -ne 'YES I AM SURE') {
        Write-Host "Aborted." -ForegroundColor Yellow
        exit 1
    }
}

# Show disk info
Write-Host "`n📊 Disk information:" -ForegroundColor Blue
$disk | Format-List Number, FriendlyName, Size, BusType, PartitionStyle

# Final confirmation
Write-Host "⚠️  WARNING: This will COMPLETELY ERASE disk $diskNumber!" -ForegroundColor Red
$finalConfirm = Read-Host "Continue? (yes/no)"
if ($finalConfirm -ne 'yes') {
    Write-Host "Aborted." -ForegroundColor Yellow
    exit 1
}

Write-Host "`n🚀 Starting write process...`n" -ForegroundColor Green

try {
    # Step 1: Clean disk
    Write-Host "1️⃣  Cleaning disk..." -ForegroundColor Cyan
    Clear-Disk -Number $diskNumber -RemoveData -Confirm:$false -ErrorAction Stop
    Write-Host "   ✅ Cleaned`n" -ForegroundColor Green

    # Step 2: Initialize disk
    Write-Host "2️⃣  Initializing disk as GPT..." -ForegroundColor Cyan
    Initialize-Disk -Number $diskNumber -PartitionStyle GPT -ErrorAction Stop
    Write-Host "   ✅ Initialized`n" -ForegroundColor Green

    # Step 3: Mount ISO and copy
    Write-Host "3️⃣  Mounting ISO..." -ForegroundColor Cyan
    $mountResult = Mount-DiskImage -ImagePath $IsoPath -PassThru -ErrorAction Stop
    $isoVolume = Get-Volume -DiskImage $mountResult
    $isoDriveLetter = $isoVolume.DriveLetter
    Write-Host "   ✅ Mounted as $isoDriveLetter`:`n" -ForegroundColor Green

    # Step 4: Create partition
    Write-Host "4️⃣  Creating partition..." -ForegroundColor Cyan
    $partition = New-Partition -DiskNumber $diskNumber -UseMaximumSize -IsActive -ErrorAction Stop
    $driveLetter = $partition | Add-PartitionAccessPath -AssignDriveLetter -PassThru | Get-Partition | Select-Object -ExpandProperty DriveLetter
    Write-Host "   ✅ Created as $driveLetter`:`n" -ForegroundColor Green

    # Step 5: Format
    Write-Host "5️⃣  Formatting as FAT32..." -ForegroundColor Cyan
    Format-Volume -DriveLetter $driveLetter -FileSystem FAT32 -NewFileSystemLabel "0RB_OS" -Confirm:$false -ErrorAction Stop
    Write-Host "   ✅ Formatted`n" -ForegroundColor Green

    # Step 6: Copy files
    Write-Host "6️⃣  Copying ISO contents to USB..." -ForegroundColor Cyan
    Write-Host "   This may take 5-15 minutes..." -ForegroundColor Gray

    $source = "$isoDriveLetter`:\*"
    $destination = "$driveLetter`:\"

    Copy-Item -Path $source -Destination $destination -Recurse -Force -Verbose

    Write-Host "`n   ✅ Files copied`n" -ForegroundColor Green

    # Step 7: Unmount ISO
    Write-Host "7️⃣  Cleaning up..." -ForegroundColor Cyan
    Dismount-DiskImage -ImagePath $IsoPath -ErrorAction Stop
    Write-Host "   ✅ ISO unmounted`n" -ForegroundColor Green

    Write-Host @"
╔═══════════════════════════════════════════╗
║   ✅ USB CREATION SUCCESSFUL!             ║
╚═══════════════════════════════════════════╝
"@ -ForegroundColor Green

    Write-Host "`nNext steps:" -ForegroundColor Cyan
    Write-Host "  1. Safely eject USB drive" -ForegroundColor Gray
    Write-Host "  2. Insert USB into target computer" -ForegroundColor Gray
    Write-Host "  3. Reboot and select USB in BIOS boot menu" -ForegroundColor Gray
    Write-Host "  4. Experience the 0RB boot sequence! 🌌`n" -ForegroundColor Gray

    Write-Host '"The pleasure is all mine." - 0RB' -ForegroundColor Blue

} catch {
    Write-Host "`nERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "`nTry using Rufus instead: https://rufus.ie/" -ForegroundColor Yellow
    exit 1
}
