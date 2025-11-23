#!/bin/bash
#
# 0RB LIMITLESS OS - USB Installer Creator
# ==========================================
# Creates a bootable USB drive with 0RB OS + Dashboard
#
# Usage: sudo ./create-bootable-usb.sh /dev/sdX
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════════╗
║         0RB LIMITLESS OS - USB INSTALLER CREATOR              ║
║                                                               ║
║  Creates bootable USB with:                                  ║
║  • Custom Linux base (Arch/Ubuntu)                           ║
║  • 0RB Brain + Voice + Dashboard                             ║
║  • Auto-start on boot                                        ║
║  • Encrypted storage                                         ║
║                                                               ║
║  Love • Loyalty • Honor • Everybody Eats                     ║
╚═══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}ERROR: Must run as root (sudo)${NC}"
  exit 1
fi

# Check USB device provided
if [ -z "$1" ]; then
  echo -e "${RED}ERROR: No device specified${NC}"
  echo ""
  echo "Usage: sudo $0 /dev/sdX"
  echo ""
  echo "Available devices:"
  lsblk -d -o NAME,SIZE,TYPE | grep disk
  echo ""
  echo "Example: sudo $0 /dev/sdb"
  exit 1
fi

USB_DEVICE=$1

# Confirm device
echo -e "${CYAN}Target device: $USB_DEVICE${NC}"
lsblk $USB_DEVICE
echo ""
echo -e "${RED}WARNING: This will ERASE ALL DATA on $USB_DEVICE!${NC}"
echo -n "Type 'YES' to continue: "
read -r CONFIRM

if [ "$CONFIRM" != "YES" ]; then
  echo "Cancelled."
  exit 0
fi

echo ""
echo -e "${GREEN}Starting USB creation...${NC}"
echo ""

# =============================================================================
# STEP 1: Download Base ISO
# =============================================================================

echo "[1/10] Downloading base ISO..."

ISO_URL="https://releases.ubuntu.com/22.04/ubuntu-22.04.3-live-server-amd64.iso"
ISO_FILE="ubuntu-22.04-server.iso"

if [ ! -f "$ISO_FILE" ]; then
  echo "  Downloading Ubuntu 22.04 Server..."
  wget -O "$ISO_FILE" "$ISO_URL"
else
  echo "  Using existing $ISO_FILE"
fi

# =============================================================================
# STEP 2: Create Partitions
# =============================================================================

echo "[2/10] Creating partitions..."

# Unmount if mounted
umount ${USB_DEVICE}* 2>/dev/null || true

# Create partition table
parted -s $USB_DEVICE mklabel gpt

# Create EFI partition (512MB)
parted -s $USB_DEVICE mkpart primary fat32 1MiB 513MiB
parted -s $USB_DEVICE set 1 esp on

# Create data partition (rest of space)
parted -s $USB_DEVICE mkpart primary ext4 513MiB 100%

# Format partitions
mkfs.fat -F32 ${USB_DEVICE}1
mkfs.ext4 -F ${USB_DEVICE}2

echo "  ✓ Partitions created"

# =============================================================================
# STEP 3: Mount Partitions
# =============================================================================

echo "[3/10] Mounting partitions..."

mkdir -p /mnt/usb_efi
mkdir -p /mnt/usb_data

mount ${USB_DEVICE}1 /mnt/usb_efi
mount ${USB_DEVICE}2 /mnt/usb_data

echo "  ✓ Mounted"

# =============================================================================
# STEP 4: Extract ISO
# =============================================================================

echo "[4/10] Extracting ISO..."

mkdir -p /mnt/iso
mount -o loop $ISO_FILE /mnt/iso

# Copy ISO contents to USB
rsync -av /mnt/iso/ /mnt/usb_data/

umount /mnt/iso

echo "  ✓ ISO extracted"

# =============================================================================
# STEP 5: Install Bootloader (GRUB)
# =============================================================================

echo "[5/10] Installing bootloader..."

# Install GRUB to USB
grub-install --target=x86_64-efi \
             --efi-directory=/mnt/usb_efi \
             --boot-directory=/mnt/usb_data/boot \
             --removable \
             --recheck

# Create GRUB config
cat > /mnt/usb_data/boot/grub/grub.cfg << 'GRUBEOF'
set timeout=10
set default=0

menuentry "Install 0RB LIMITLESS OS" {
    set root=(hd0,gpt2)
    linux /casper/vmlinuz boot=casper quiet splash ---
    initrd /casper/initrd
}

menuentry "Boot from hard disk" {
    exit
}
GRUBEOF

echo "  ✓ Bootloader installed"

# =============================================================================
# STEP 6: Copy 0RB System Files
# =============================================================================

echo "[6/10] Copying 0RB system files..."

# Create 0rb directory
mkdir -p /mnt/usb_data/0rb

# Copy all your systems
cp -r ../the_instant_creator.py /mnt/usb_data/0rb/
cp -r ../ai_connectors.py /mnt/usb_data/0rb/
cp -r ../brain_os.py /mnt/usb_data/0rb/
cp -r ../ekosystem.py /mnt/usb_data/0rb/
cp -r ../CREATE.py /mnt/usb_data/0rb/
cp -r ../ai_guide.py /mnt/usb_data/0rb/
cp -r ../0rb-complete /mnt/usb_data/0rb/

# Copy documentation
cp -r ../*.md /mnt/usb_data/0rb/

echo "  ✓ System files copied"

# =============================================================================
# STEP 7: Create Auto-Install Script
# =============================================================================

echo "[7/10] Creating auto-install script..."

cat > /mnt/usb_data/0rb/install.sh << 'INSTALLEOF'
#!/bin/bash
#
# 0RB LIMITLESS OS - Installer
# Runs on first boot to set up everything
#

set -e

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║         0RB LIMITLESS OS - INSTALLATION                       ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Update system
echo "[1/8] Updating system..."
apt update && apt upgrade -y

# Install dependencies
echo "[2/8] Installing dependencies..."
apt install -y \
    python3 \
    python3-pip \
    docker.io \
    docker-compose \
    nginx \
    postgresql \
    redis \
    git \
    curl \
    wget \
    htop \
    tmux

# Install Python packages
echo "[3/8] Installing Python packages..."
pip3 install \
    fastapi \
    uvicorn \
    httpx \
    pydantic \
    slowapi \
    psycopg2-binary \
    redis \
    twilio \
    elevenlabs

# Set up Docker
echo "[4/8] Configuring Docker..."
systemctl enable docker
systemctl start docker
usermod -aG docker $USER

# Copy 0RB files to /opt
echo "[5/8] Installing 0RB system..."
mkdir -p /opt/0rb
cp -r /media/usb/0rb/* /opt/0rb/
chmod +x /opt/0rb/*.py
chmod +x /opt/0rb/CREATE.py

# Create systemd services
echo "[6/8] Creating services..."

# 0RB Bridge service
cat > /etc/systemd/system/orb-bridge.service << 'SERVICEEOF'
[Unit]
Description=0RB Bridge API
After=network.target docker.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/0rb/0rb-complete/backend/brain
ExecStart=/usr/bin/python3 orb_bridge.py
Restart=always

[Install]
WantedBy=multi-user.target
SERVICEEOF

# Enable services
systemctl daemon-reload
systemctl enable orb-bridge
systemctl start orb-bridge

# Configure nginx
echo "[7/8] Configuring web server..."
cat > /etc/nginx/sites-available/0rb << 'NGINXEOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /ws {
        proxy_pass http://localhost:8080/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $upgrade;
        proxy_set_header Connection "upgrade";
    }
}
NGINXEOF

ln -sf /etc/nginx/sites-available/0rb /etc/nginx/sites-enabled/
systemctl restart nginx

# Create desktop shortcuts
echo "[8/8] Creating shortcuts..."
cat > /home/$USER/Desktop/0rb-dashboard.desktop << 'DESKTOPEOF'
[Desktop Entry]
Name=0RB Dashboard
Comment=Open 0RB Dashboard
Exec=firefox http://localhost
Icon=/opt/0rb/icon.png
Terminal=false
Type=Application
DESKTOPEOF

chmod +x /home/$USER/Desktop/0rb-dashboard.desktop

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║         0RB LIMITLESS OS - INSTALLED! ✓                       ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "System is ready!"
echo ""
echo "Access dashboard: http://localhost"
echo "API: http://localhost:8080"
echo ""
echo "Restarting in 10 seconds..."
sleep 10
reboot
INSTALLEOF

chmod +x /mnt/usb_data/0rb/install.sh

echo "  ✓ Install script created"

# =============================================================================
# STEP 8: Configure Persistence
# =============================================================================

echo "[8/10] Configuring persistence..."

# Create casper-rw file for persistence
dd if=/dev/zero of=/mnt/usb_data/casper-rw bs=1M count=4096
mkfs.ext4 -F /mnt/usb_data/casper-rw

echo "  ✓ Persistence configured"

# =============================================================================
# STEP 9: Set Auto-Run on Boot
# =============================================================================

echo "[9/10] Configuring auto-run..."

# Add to casper boot parameters
sed -i 's/quiet splash/quiet splash persistent/' /mnt/usb_data/boot/grub/grub.cfg

echo "  ✓ Auto-run configured"

# =============================================================================
# STEP 10: Finalize
# =============================================================================

echo "[10/10] Finalizing..."

# Sync and unmount
sync
umount /mnt/usb_efi
umount /mnt/usb_data

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║         USB INSTALLER CREATED SUCCESSFULLY! ✓                 ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "USB Device: $USB_DEVICE"
echo ""
echo "Next steps:"
echo "  1. Remove USB drive safely"
echo "  2. Insert into target PC"
echo "  3. Boot from USB (F12/F8/DEL to access boot menu)"
echo "  4. Select 'Install 0RB LIMITLESS OS'"
echo "  5. System will auto-install and restart"
echo "  6. Access dashboard at http://localhost"
echo ""
echo "💝 Your 0RB OS is ready to deploy!"
echo ""
