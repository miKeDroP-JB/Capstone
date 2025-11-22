#!/bin/bash
# Find USB Drive Helper Script

echo "🔍 Scanning for USB drives..."
echo ""
echo "Connected storage devices:"
lsblk -o NAME,SIZE,TYPE,MOUNTPOINT,MODEL | grep -E "disk|part"

echo ""
echo "⚠️  CRITICAL: Identify your USB drive carefully!"
echo ""
echo "Typical USB device names:"
echo "  - /dev/sdb (if you have one internal disk)"
echo "  - /dev/sdc (if you have two internal disks)"
echo "  - /dev/nvme0n1 (NVMe drives - usually NOT USB)"
echo ""
echo "💡 Tips:"
echo "  1. Look at the SIZE column (USB should match your drive size)"
echo "  2. Check the MODEL column (should say 'USB' or manufacturer)"
echo "  3. Internal drives usually show up as /dev/sda or /dev/nvme0n1"
echo ""
echo "To see more details about a specific device:"
echo "  sudo fdisk -l /dev/sdX"
echo ""
