#!/bin/bash
# 0RB_AETHER One-Click Installer
# Usage: sudo ./install.sh [USB_DEVICE]
# Example: sudo ./install.sh /dev/sdb

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
USB_DEVICE="${1:-}"

log() { echo -e "${GREEN}[+]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
error() { echo -e "${RED}[-]${NC} $1"; exit 1; }
header() { echo -e "\n${CYAN}=== $1 ===${NC}\n"; }

# Check root
[[ $EUID -ne 0 ]] && error "Run as root: sudo $0 [USB_DEVICE]"

header "0RB_AETHER INSTALLER"

# Detect OS
if [ -f /etc/debian_version ]; then
    PKG_MGR="apt-get"
    PKG_INSTALL="apt-get install -y"
elif [ -f /etc/fedora-release ]; then
    PKG_MGR="dnf"
    PKG_INSTALL="dnf install -y"
elif [ -f /etc/arch-release ]; then
    PKG_MGR="pacman"
    PKG_INSTALL="pacman -S --noconfirm"
else
    warn "Unknown distro - install dependencies manually"
    PKG_INSTALL="echo SKIP:"
fi

# Step 1: Install dependencies
header "Installing Dependencies"
$PKG_INSTALL \
    curl git build-essential pkg-config \
    squashfs-tools xorriso grub-pc-bin grub-efi-amd64-bin mtools \
    cryptsetup libssl-dev \
    python3 python3-pip \
    libwayland-dev libxkbcommon-dev 2>/dev/null || true

# Install Rust if needed
if ! command -v cargo &>/dev/null; then
    log "Installing Rust..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source "$HOME/.cargo/env"
fi

# Step 2: Build Brain
header "Building Brain Orchestrator"
cd "$SCRIPT_DIR/core/brain"
cargo build --release 2>&1 | tail -5
log "Brain built: target/release/orb-brain"

# Step 3: Build Compositor (optional - may fail without full GPU deps)
header "Building Compositor"
cd "$SCRIPT_DIR/ui/compositor"
cargo build --release 2>&1 | tail -5 || warn "Compositor build skipped (missing GPU deps)"

# Step 4: Create ISO
header "Creating Bootable Image"
cd "$SCRIPT_DIR"
chmod +x build/make_iso.sh build/initramfs/init core/security/ram_wipe.sh

# Create output directory
mkdir -p build/output

# Simplified ISO creation
ISO_DIR="build/output/iso"
mkdir -p "$ISO_DIR"/{boot/grub,live,EFI/BOOT}

# Copy kernel
if [ -f /boot/vmlinuz-$(uname -r) ]; then
    cp /boot/vmlinuz-$(uname -r) "$ISO_DIR/boot/vmlinuz"
    cp /boot/initrd.img-$(uname -r) "$ISO_DIR/boot/initrd.img" 2>/dev/null || true
fi

# Create minimal squashfs with our tools
SQUASH_ROOT="build/output/squashfs-root"
mkdir -p "$SQUASH_ROOT"/{opt/0rb/{brain,ui},etc/systemd/system,usr/local/bin}

# Copy binaries
cp core/brain/target/release/orb-brain "$SQUASH_ROOT/opt/0rb/brain/" 2>/dev/null || true
cp ui/compositor/target/release/orb-compositor "$SQUASH_ROOT/opt/0rb/ui/" 2>/dev/null || true
cp core/security/ram_wipe.sh "$SQUASH_ROOT/usr/local/bin/"
cp tools/asr/voice_auth.py "$SQUASH_ROOT/usr/local/bin/"

# Create systemd service
cat > "$SQUASH_ROOT/etc/systemd/system/orb-brain.service" << 'SVCEOF'
[Unit]
Description=0RB Brain Orchestrator
After=network.target
[Service]
Type=simple
ExecStart=/opt/0rb/brain/orb-brain
Restart=always
Environment=ORB_SOCKET=/run/0rb/brain.sock
RuntimeDirectory=0rb
[Install]
WantedBy=multi-user.target
SVCEOF

# Create squashfs
mksquashfs "$SQUASH_ROOT" "$ISO_DIR/live/filesystem.squashfs" -comp xz -quiet

# GRUB config
cat > "$ISO_DIR/boot/grub/grub.cfg" << 'GRUBEOF'
set timeout=5
set default=0
menuentry "0RB_AETHER - Secure Boot (RAM)" {
    linux /boot/vmlinuz toram quiet
    initrd /boot/initrd.img
}
menuentry "0RB_AETHER - Debug Mode" {
    linux /boot/vmlinuz toram debug
    initrd /boot/initrd.img
}
GRUBEOF

# Create ISO
ISO_PATH="build/output/0rb-aether.iso"
grub-mkrescue -o "$ISO_PATH" "$ISO_DIR" 2>/dev/null || \
    xorriso -as mkisofs -R -J -V "0RB_AETHER" -o "$ISO_PATH" "$ISO_DIR" 2>/dev/null

log "ISO created: $ISO_PATH"

# Step 5: Write to USB (if device specified)
if [ -n "$USB_DEVICE" ]; then
    header "Writing to USB: $USB_DEVICE"

    # Safety check
    if [ ! -b "$USB_DEVICE" ]; then
        error "Device $USB_DEVICE not found"
    fi

    # Confirm
    echo -e "${RED}WARNING: This will ERASE $USB_DEVICE${NC}"
    lsblk "$USB_DEVICE"
    read -p "Continue? [y/N]: " confirm
    [[ "$confirm" != "y" ]] && exit 0

    # Unmount
    umount "${USB_DEVICE}"* 2>/dev/null || true

    # Write
    log "Writing image (this may take a while)..."
    dd if="$ISO_PATH" of="$USB_DEVICE" bs=4M status=progress conv=fsync
    sync

    log "USB ready! Boot from $USB_DEVICE"
else
    warn "No USB device specified"
    echo "To write to USB later:"
    echo "  sudo dd if=$ISO_PATH of=/dev/sdX bs=4M status=progress"
fi

header "INSTALLATION COMPLETE"
echo "
Files created:
  - $ISO_PATH (bootable image)
  - core/brain/target/release/orb-brain

Next steps:
  1. Write ISO to USB: sudo dd if=$ISO_PATH of=/dev/sdX bs=4M
  2. Boot from USB
  3. Enter LUKS passphrase when prompted
"
