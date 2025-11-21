#!/bin/bash
# 0RB_AETHER ISO Build Script
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BUILD_DIR="$SCRIPT_DIR/output"
ISO_NAME="0rb-aether.iso"
WORK_DIR="$BUILD_DIR/work"
SQUASH_DIR="$BUILD_DIR/squashfs-root"
ISO_DIR="$BUILD_DIR/iso"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[+]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
error() { echo -e "${RED}[-]${NC} $1"; exit 1; }

check_deps() {
    log "Checking dependencies..."
    local deps="squashfs-tools xorriso grub-pc-bin mtools cryptsetup"
    for dep in $deps; do
        dpkg -l "$dep" &>/dev/null || warn "Missing: $dep (install with apt)"
    done
}

prepare_dirs() {
    log "Preparing build directories..."
    rm -rf "$BUILD_DIR"
    mkdir -p "$WORK_DIR" "$SQUASH_DIR" "$ISO_DIR"/{boot/grub,live}
}

build_initramfs() {
    log "Building initramfs..."
    local initramfs_dir="$WORK_DIR/initramfs"
    mkdir -p "$initramfs_dir"/{bin,sbin,etc,proc,sys,dev,run,mnt/{root,newroot},lib,lib64}

    # Copy busybox
    if command -v busybox &>/dev/null; then
        cp "$(which busybox)" "$initramfs_dir/bin/"
        for cmd in sh mount umount mkdir cat echo sleep cp rm rmdir cd; do
            ln -sf busybox "$initramfs_dir/bin/$cmd"
        done
    fi

    # Copy cryptsetup and deps
    if command -v cryptsetup &>/dev/null; then
        cp "$(which cryptsetup)" "$initramfs_dir/sbin/"
        # Copy required libraries
        ldd "$(which cryptsetup)" | grep -o '/lib[^ ]*' | while read lib; do
            mkdir -p "$initramfs_dir$(dirname $lib)"
            cp "$lib" "$initramfs_dir$lib" 2>/dev/null || true
        done
    fi

    # Copy init script
    cp "$SCRIPT_DIR/initramfs/init" "$initramfs_dir/init"
    chmod +x "$initramfs_dir/init"

    # Create initramfs cpio
    (cd "$initramfs_dir" && find . | cpio -H newc -o | gzip > "$ISO_DIR/boot/initramfs.img")
    log "Initramfs created: $ISO_DIR/boot/initramfs.img"
}

build_squashfs() {
    log "Building squashfs root filesystem..."

    # Create minimal rootfs structure
    mkdir -p "$SQUASH_DIR"/{bin,sbin,usr/{bin,sbin,lib},lib,lib64,etc,var,tmp,run,home,root}
    mkdir -p "$SQUASH_DIR"/etc/{systemd/system,0rb}
    mkdir -p "$SQUASH_DIR"/opt/0rb/{brain,ui,tools}

    # Copy Brain binary if built
    if [ -f "$SCRIPT_DIR/../core/brain/target/release/orb-brain" ]; then
        cp "$SCRIPT_DIR/../core/brain/target/release/orb-brain" "$SQUASH_DIR/opt/0rb/brain/"
    fi

    # Create systemd service for brain
    cat > "$SQUASH_DIR/etc/systemd/system/orb-brain.service" << 'EOF'
[Unit]
Description=0RB Brain Orchestrator
After=network.target

[Service]
Type=simple
ExecStart=/opt/0rb/brain/orb-brain
Restart=always
RestartSec=5
Environment=ORB_SOCKET=/run/0rb/brain.sock
RuntimeDirectory=0rb

[Install]
WantedBy=multi-user.target
EOF

    # Create squashfs
    mksquashfs "$SQUASH_DIR" "$ISO_DIR/live/filesystem.squashfs" -comp xz -Xbcj x86
    log "Squashfs created: $ISO_DIR/live/filesystem.squashfs"
}

create_grub_config() {
    log "Creating GRUB configuration..."
    cat > "$ISO_DIR/boot/grub/grub.cfg" << 'EOF'
set timeout=5
set default=0

menuentry "0RB_AETHER - RAM Mode (Secure)" {
    linux /boot/vmlinuz toram quiet splash
    initrd /boot/initramfs.img
}

menuentry "0RB_AETHER - RAM Mode (Debug)" {
    linux /boot/vmlinuz toram debug
    initrd /boot/initramfs.img
}

menuentry "0RB_AETHER - Persistent Mode" {
    linux /boot/vmlinuz quiet splash
    initrd /boot/initramfs.img
}
EOF
}

create_iso() {
    log "Creating bootable ISO..."

    # Copy kernel (use current system kernel as placeholder)
    if [ -f /boot/vmlinuz-$(uname -r) ]; then
        cp /boot/vmlinuz-$(uname -r) "$ISO_DIR/boot/vmlinuz"
    else
        warn "No kernel found - ISO will need manual kernel addition"
        touch "$ISO_DIR/boot/vmlinuz"
    fi

    grub-mkrescue -o "$BUILD_DIR/$ISO_NAME" "$ISO_DIR" 2>/dev/null || \
        xorriso -as mkisofs -r -V "0RB_AETHER" \
            -b boot/grub/i386-pc/eltorito.img \
            -no-emul-boot -boot-load-size 4 -boot-info-table \
            -o "$BUILD_DIR/$ISO_NAME" "$ISO_DIR"

    log "ISO created: $BUILD_DIR/$ISO_NAME"
}

sign_iso() {
    log "Signing ISO..."
    if command -v gpg &>/dev/null; then
        sha256sum "$BUILD_DIR/$ISO_NAME" > "$BUILD_DIR/$ISO_NAME.sha256"
        # gpg --detach-sign "$BUILD_DIR/$ISO_NAME"  # Uncomment if GPG key available
        log "Checksum created: $BUILD_DIR/$ISO_NAME.sha256"
    else
        warn "GPG not available - skipping signature"
    fi
}

main() {
    echo "============================================"
    echo "       0RB_AETHER ISO Builder"
    echo "============================================"
    echo ""

    check_deps
    prepare_dirs
    build_initramfs
    build_squashfs
    create_grub_config
    create_iso
    sign_iso

    echo ""
    log "Build complete!"
    log "ISO: $BUILD_DIR/$ISO_NAME"
    log "To write to USB: sudo dd if=$BUILD_DIR/$ISO_NAME of=/dev/sdX bs=4M status=progress"
}

main "$@"
