# 0RB_AETHER - Windows Installation Guide

## One-Click Install (PowerShell)

1. **Download** this folder to your PC
2. **Right-click** `install-windows.ps1`
3. **Select** "Run with PowerShell"
4. Follow prompts to write ISO to USB
5. **Reboot** and boot from USB

## Alternative: Manual Method

1. **Download ISO**:
   - Right-click and "Save As": [0rb-aether.iso](https://github.com/miKeDroP-JB/Capstone/raw/claude/usb-bootable-meta-os-01TzhMb5gNhJ7FHLLvEY1q7H/0rb-aether/build/output/0rb-aether.iso)

2. **Download Rufus**: https://rufus.ie

3. **In Rufus**:
   - Device: Select your USB drive
   - Boot selection: Click SELECT → choose `0rb-aether.iso`
   - Partition scheme: **MBR**
   - Target system: **BIOS or UEFI**
   - Click **START**

4. **Boot from USB**:
   - Restart PC
   - Press F12/F2/DEL (varies by manufacturer) during boot
   - Select USB drive
   - **Important**: Disable Secure Boot in BIOS if boot fails

## Troubleshooting

**"Access Denied" when running PowerShell script:**
- Right-click PowerShell script → Properties
- Check "Unblock" at bottom → OK
- Or run: `Set-ExecutionPolicy Bypass -Scope Process`

**USB doesn't show in boot menu:**
- Enter BIOS/UEFI settings
- Enable "Legacy Boot" or "CSM Support"
- Disable "Secure Boot"
- Move USB to top of boot order

**"No bootable device" error:**
- Re-write USB with Rufus using **DD Image mode**
- Try USB 2.0 port instead of USB 3.0

**Need help?**
Open an issue: https://github.com/miKeDroP-JB/Capstone/issues
