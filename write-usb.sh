#!/bin/bash
# Safe USB Writer for 0RB LIMITLESS OS
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔═══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   0RB LIMITLESS OS - USB Writer          ║${NC}"
echo -e "${BLUE}╔═══════════════════════════════════════════╗${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}❌ This script must be run as root${NC}"
  echo "   Run: sudo $0"
  exit 1
fi

# Find ISO
ISO_PATH="$(dirname "$0")/0rb-aether/build/output/0rb-aether.iso"

if [ ! -f "$ISO_PATH" ]; then
  echo -e "${RED}❌ ISO not found at: $ISO_PATH${NC}"
  echo ""
  echo "Build the ISO first:"
  echo "  cd 0rb-aether/build"
  echo "  sudo ./make_iso.sh"
  exit 1
fi

echo -e "${GREEN}✅ Found ISO: $ISO_PATH${NC}"
ISO_SIZE=$(du -h "$ISO_PATH" | cut -f1)
echo "   Size: $ISO_SIZE"
echo ""

# Show connected drives
echo -e "${YELLOW}📋 Connected storage devices:${NC}"
lsblk -o NAME,SIZE,TYPE,MOUNTPOINT,MODEL | grep -E "disk|NAME"
echo ""

# Get target device
echo -e "${YELLOW}⚠️  WARNING: This will COMPLETELY ERASE the target drive!${NC}"
echo ""
read -p "Enter USB device (e.g., /dev/sdb): " DEVICE

# Validate device
if [ ! -b "$DEVICE" ]; then
  echo -e "${RED}❌ Invalid device: $DEVICE${NC}"
  exit 1
fi

# Safety check - don't allow /dev/sda (usually main system disk)
if [ "$DEVICE" = "/dev/sda" ] || [ "$DEVICE" = "/dev/nvme0n1" ]; then
  echo -e "${RED}❌ DANGER: $DEVICE is likely your system disk!${NC}"
  echo "   Are you ABSOLUTELY SURE this is your USB drive?"
  read -p "Type 'YES I AM SURE' to continue: " CONFIRM
  if [ "$CONFIRM" != "YES I AM SURE" ]; then
    echo "Aborted."
    exit 1
  fi
fi

# Show device info
echo ""
echo -e "${BLUE}📊 Device information:${NC}"
lsblk "$DEVICE" -o NAME,SIZE,TYPE,MOUNTPOINT,MODEL
echo ""
fdisk -l "$DEVICE" 2>/dev/null | head -5
echo ""

# Final confirmation
read -p "🔥 FINAL WARNING: Erase $DEVICE and write 0RB OS? (yes/no): " FINAL_CONFIRM
if [ "$FINAL_CONFIRM" != "yes" ]; then
  echo "Aborted."
  exit 1
fi

echo ""
echo -e "${GREEN}🚀 Starting write process...${NC}"
echo ""

# Unmount any mounted partitions
echo "1️⃣  Unmounting any mounted partitions..."
for partition in ${DEVICE}*; do
  if mountpoint -q "$partition" 2>/dev/null; then
    umount "$partition" 2>/dev/null || true
  fi
done
echo "   ✅ Unmounted"
echo ""

# Write ISO
echo "2️⃣  Writing ISO to $DEVICE..."
echo "   This will take 5-15 minutes depending on USB speed..."
echo ""

dd if="$ISO_PATH" of="$DEVICE" bs=4M status=progress oflag=sync

echo ""
echo -e "${GREEN}✅ Write complete!${NC}"
echo ""

# Sync
echo "3️⃣  Syncing data to disk..."
sync
echo "   ✅ Synced"
echo ""

# Verify (optional)
echo "4️⃣  Verifying write (optional)..."
read -p "Run verification? (yes/no): " VERIFY

if [ "$VERIFY" = "yes" ]; then
  echo "   Reading back from USB and comparing..."
  ISO_MD5=$(md5sum "$ISO_PATH" | cut -d' ' -f1)
  USB_MD5=$(dd if="$DEVICE" bs=4M count=$(stat -c%s "$ISO_PATH" | awk '{print int($1/4194304)+1}') 2>/dev/null | md5sum | cut -d' ' -f1)

  if [ "$ISO_MD5" = "$USB_MD5" ]; then
    echo -e "   ${GREEN}✅ Verification PASSED${NC}"
  else
    echo -e "   ${RED}❌ Verification FAILED${NC}"
    echo "   ISO MD5:  $ISO_MD5"
    echo "   USB MD5:  $USB_MD5"
    exit 1
  fi
fi

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   ✅ USB CREATION SUCCESSFUL!             ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════╝${NC}"
echo ""
echo "Next steps:"
echo "  1. Safely remove USB: sync && sudo eject $DEVICE"
echo "  2. Insert USB into target computer"
echo "  3. Reboot and select USB in BIOS boot menu"
echo "  4. Experience the 0RB boot sequence! 🌌"
echo ""
echo -e "${BLUE}\"The pleasure is all mine.\"${NC} - 0RB"
echo ""
