#!/bin/bash
# 0RB_AETHER Secure RAM Wipe Script
# Anti-forensic memory clearing on shutdown
#
# WARNING: No PM-perfect wipe guarantees on all hardware.
# This is a best-effort approach. Document threat model.

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

log() { echo -e "${GREEN}[WIPE]${NC} $1"; }
warn() { echo -e "${RED}[WARN]${NC} $1"; }

# Ensure running as root
if [ "$EUID" -ne 0 ]; then
    echo "Must run as root"
    exit 1
fi

PASSES=${1:-3}  # Number of overwrite passes
FORCE=${2:-0}   # Skip confirmation

log "0RB_AETHER Emergency RAM Wipe Initiated"
log "Passes: $PASSES"

# Confirmation unless forced
if [ "$FORCE" != "1" ]; then
    echo -n "Confirm wipe? [y/N]: "
    read -r confirm
    [ "$confirm" != "y" ] && exit 0
fi

# 1. Sync filesystems
log "Syncing filesystems..."
sync

# 2. Kill non-essential processes
log "Terminating user processes..."
pkill -9 -u "$(id -u)" 2>/dev/null || true

# 3. Clear tmpfs and shared memory
log "Clearing tmpfs and shared memory..."
for mount in /dev/shm /tmp /run; do
    if mountpoint -q "$mount" 2>/dev/null; then
        log "  Wiping $mount..."
        find "$mount" -type f -exec shred -n $PASSES -z {} \; 2>/dev/null || true
        rm -rf "${mount:?}"/* 2>/dev/null || true
    fi
done

# 4. Overwrite free memory
log "Overwriting free memory (this may take a while)..."
for pass in $(seq 1 $PASSES); do
    log "  Pass $pass/$PASSES..."

    # Create large files to consume free RAM
    dd if=/dev/urandom of=/dev/shm/.wipe_$pass bs=1M count=1024 2>/dev/null || true
    sync

    # Remove immediately
    rm -f /dev/shm/.wipe_$pass
done

# 5. Drop caches
log "Dropping kernel caches..."
echo 3 > /proc/sys/vm/drop_caches 2>/dev/null || true

# 6. Clear swap (if any - should be disabled in RAM-only mode)
if [ -f /proc/swaps ]; then
    while read -r line; do
        swap_dev=$(echo "$line" | awk 'NR>1 {print $1}')
        if [ -n "$swap_dev" ]; then
            log "Disabling and clearing swap: $swap_dev"
            swapoff "$swap_dev" 2>/dev/null || true
        fi
    done < /proc/swaps
fi

# 7. Clear kernel ring buffer
log "Clearing kernel logs..."
dmesg -C 2>/dev/null || true

# 8. Clear bash history
log "Clearing shell histories..."
for user_home in /home/* /root; do
    [ -d "$user_home" ] || continue
    rm -f "$user_home/.bash_history" 2>/dev/null || true
    rm -f "$user_home/.zsh_history" 2>/dev/null || true
    rm -f "$user_home/.python_history" 2>/dev/null || true
done

# 9. Wipe Brain database if exists
if [ -f /run/0rb/brain.db ]; then
    log "Wiping Brain database..."
    shred -n $PASSES -z /run/0rb/brain.db
    rm -f /run/0rb/brain.db
fi

# 10. Final sync
sync

log "RAM wipe complete"

# 11. Power off or reboot
if [ "${POWEROFF:-1}" = "1" ]; then
    log "Powering off..."
    poweroff -f
else
    log "Rebooting..."
    reboot -f
fi
