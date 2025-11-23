# 🖥️ INSTALL 0RB OS ON YOUR PC

Complete guide to creating a bootable USB and installing 0RB OS on your machine.

---

## What You Get

A complete operating system with:
- ✅ Linux base (Ubuntu 22.04)
- ✅ 0RB Brain + Voice + Dashboard (auto-start on boot)
- ✅ All your systems pre-installed
- ✅ Docker + services configured
- ✅ Web dashboard at http://localhost

**Boot it up → System ready → Start creating**

---

## Quick Start (Choose Your OS)

### On Linux/Mac

```bash
cd 0rb-complete

# Make script executable
chmod +x create-bootable-usb.sh

# Run (replace /dev/sdX with your USB drive)
sudo ./create-bootable-usb.sh /dev/sdb

# Follow prompts
```

### On Windows

```powershell
# Open PowerShell as Administrator
cd 0rb-complete

# Run script
.\create-bootable-usb.ps1

# Follow prompts
```

**Time: ~15-30 minutes (depending on USB speed)**

---

## Detailed Steps

### Step 1: Find Your USB Drive

**Linux/Mac:**
```bash
# List all drives
lsblk

# Find your USB (usually /dev/sdb or /dev/sdc)
# Look for the one that matches your USB size
```

**Windows:**
```powershell
# Open Disk Management
diskmgmt.msc

# Find your USB drive number
# Note the disk number (e.g., "Disk 1")
```

**⚠️ IMPORTANT:** Make sure you select the correct drive! Everything on it will be erased!

---

### Step 2: Create Bootable USB

**Linux/Mac:**
```bash
sudo ./create-bootable-usb.sh /dev/sdX
# Replace X with your USB drive letter (b, c, d, etc.)
```

**Windows:**
```powershell
.\create-bootable-usb.ps1
# Script will show available drives
# Choose the correct one
```

**What the script does:**
1. Downloads Ubuntu 22.04 ISO (~1.4GB)
2. Creates partitions on USB
3. Installs bootloader (GRUB)
4. Copies Ubuntu ISO
5. Copies all 0RB system files
6. Creates auto-install script
7. Makes USB bootable

**Progress:**
```
[1/10] Downloading ISO...        (5-10 min)
[2/10] Creating partitions...    (1 min)
[3/10] Mounting...               (instant)
[4/10] Extracting ISO...         (3-5 min)
[5/10] Installing bootloader...  (1 min)
[6/10] Copying 0RB files...      (2 min)
[7/10] Creating install script...  (instant)
[8/10] Configuring persistence...  (1 min)
[9/10] Setting auto-run...       (instant)
[10/10] Finalizing...            (1 min)

✓ USB CREATED!
```

---

### Step 3: Boot from USB

1. **Insert USB** into target PC
2. **Restart** computer
3. **Access Boot Menu:**
   - During startup, press:
     - **F12** (most common)
     - **F8** (Dell)
     - **F10** (HP)
     - **DEL** or **F2** (BIOS/UEFI setup)
     - **ESC** (some laptops)
4. **Select USB drive** from boot menu
5. **Press Enter**

**Tip:** If boot menu doesn't appear, check your PC manual for the correct key.

---

### Step 4: Install Ubuntu

When USB boots, you'll see:

```
╔═══════════════════════════════════════╗
║     0RB LIMITLESS OS - INSTALLER      ║
╚═══════════════════════════════════════╝

1. Install 0RB LIMITLESS OS
2. Boot from hard disk

Select option:
```

**Choose option 1** and follow prompts:

1. **Language:** English
2. **Keyboard:** Default (or your preference)
3. **Network:** Connect if available (not required)
4. **Disk Setup:**
   - Choose "Use entire disk"
   - Or "Manual" if you want dual-boot
5. **User Setup:**
   - Username: your-name
   - Password: (choose secure password)
6. **Install:**
   - Wait 10-20 minutes
   - System will copy files and configure

**After installation:** System will restart automatically

---

### Step 5: First Boot

After restart:

1. **Login** with your username/password
2. **System auto-configures:**
   ```
   ╔═══════════════════════════════════════╗
   ║     0RB LIMITLESS OS - SETUP          ║
   ╚═══════════════════════════════════════╝

   [1/8] Updating system...
   [2/8] Installing dependencies...
   [3/8] Installing Python packages...
   [4/8] Configuring Docker...
   [5/8] Installing 0RB system...
   [6/8] Creating services...
   [7/8] Configuring web server...
   [8/8] Creating shortcuts...

   ✓ INSTALLATION COMPLETE!

   Dashboard: http://localhost
   API: http://localhost:8080

   Restarting...
   ```

3. **System restarts again** (final setup)
4. **Login** → Desktop ready!

---

### Step 6: Use Your System

**Desktop shortcuts created:**
- 🖥️ **0RB Dashboard** → Opens http://localhost in browser
- 💻 **Terminal** → Access command line
- 📁 **Files** → Browse /opt/0rb

**System services running:**
- ✅ 0RB Bridge (port 8080)
- ✅ Voice Agency (auto-start)
- ✅ PostgreSQL database
- ✅ Redis cache
- ✅ Nginx web server

**Start creating:**
```bash
# Open terminal
cd /opt/0rb

# Talk to AI guide
python3 ai_guide.py

# Create something
python3 CREATE.py "Build HVAC dashboard with love"

# Check what's running
docker ps
```

---

## System Requirements

### Minimum
- **CPU:** 64-bit processor (Intel/AMD)
- **RAM:** 8GB
- **Storage:** 50GB
- **USB:** 16GB (for installer)

### Recommended
- **CPU:** Quad-core 2.0GHz+
- **RAM:** 16GB+
- **Storage:** 100GB+ SSD
- **USB:** 32GB (faster is better)
- **Network:** Ethernet or WiFi

### Tested On
- ✅ Desktop PC (Intel/AMD)
- ✅ Laptop (most brands)
- ✅ Mini PC (Intel NUC, etc.)
- ✅ Virtual Machine (VMware, VirtualBox)
- ⚠️ Mac (Intel Macs work, M1/M2 need special setup)
- ❌ Chromebook (not compatible)

---

## Troubleshooting

### USB won't boot

**Problem:** PC doesn't boot from USB

**Solutions:**
1. Check BIOS/UEFI settings:
   - Disable Secure Boot
   - Enable Legacy Boot (if needed)
   - Set USB as first boot device
2. Try different USB port (USB 2.0 sometimes more compatible)
3. Recreate USB (might be corrupted)

---

### "No operating system found"

**Problem:** After install, PC can't find OS

**Solutions:**
1. Check boot order in BIOS
2. Set hard drive as first boot device
3. Repair bootloader:
   ```bash
   sudo grub-install /dev/sda
   sudo update-grub
   ```

---

### Services not starting

**Problem:** Dashboard not accessible after boot

**Solutions:**
```bash
# Check service status
sudo systemctl status orb-bridge

# Restart service
sudo systemctl restart orb-bridge

# View logs
sudo journalctl -u orb-bridge -f

# Manual start
cd /opt/0rb/0rb-complete
sudo docker-compose up -d
```

---

### System is slow

**Problem:** System feels sluggish

**Solutions:**
1. Check available RAM: `free -h`
2. Check disk space: `df -h`
3. Stop unused services:
   ```bash
   sudo docker ps
   sudo docker stop [container-name]
   ```
4. Add more RAM/SSD if possible

---

## Dual Boot Setup

Want to keep Windows/Mac AND run 0RB OS?

### During Installation

1. **At disk setup:**
   - Choose "Manual partitioning"
   - Shrink existing partition
   - Create new partition for 0RB
   - Keep existing OS partition

2. **Bootloader:**
   - GRUB will detect both OS
   - Choose at startup

**Recommended partition sizes:**
- 0RB OS: 50GB minimum
- Swap: 8GB (equal to RAM)

---

## Uninstall

To remove 0RB OS and go back:

### If Dual Boot
1. Boot into other OS (Windows/Mac)
2. Use disk management to delete 0RB partition
3. Expand original partition
4. Remove bootloader (Windows: `bootrec /fixmbr`)

### If Solo Install
1. Create new bootable USB (Windows/Linux)
2. Boot from it
3. Install new OS (overwrites 0RB)

---

## What Gets Installed

### System Software
- Ubuntu 22.04 LTS (base OS)
- Python 3.11
- Docker + Docker Compose
- PostgreSQL 15
- Redis 7
- Nginx
- Node.js (for dashboard)

### 0RB Systems
- THE INSTANT CREATOR
- AI Connectors (Claude/Gemini/GPT)
- Brain OS (security fortress)
- Ekosystem (build orchestrator)
- Voice Agency
- 0RB Bridge (integration API)
- Dashboard (web UI)

### Auto-Start Services
```
orb-bridge.service   → Port 8080
orb-voice.service    → Voice system
postgresql.service   → Database
redis.service        → Cache
nginx.service        → Web server
docker.service       → Container runtime
```

---

## Post-Install Configuration

### Set API Keys

```bash
cd /opt/0rb

# Edit environment
sudo nano .env

# Add your keys
ANTHROPIC_API_KEY=your-claude-key
OPENAI_API_KEY=your-gpt-key
GOOGLE_API_KEY=your-gemini-key

# Restart services
sudo systemctl restart orb-bridge
```

### Configure Voice

```bash
# Add Twilio credentials
TWILIO_ACCOUNT_SID=your-sid
TWILIO_AUTH_TOKEN=your-token
TWILIO_PHONE_NUMBER=+1234567890
ELEVENLABS_API_KEY=your-key
```

### Remote Access

```bash
# Find your local IP
ip addr show

# Access from other devices
http://192.168.1.X:8080

# For internet access, set up port forwarding
# Router settings → Forward port 8080 to your PC
```

---

## Updates

### Update 0RB System

```bash
cd /opt/0rb

# Pull latest changes (if Git repo)
git pull origin main

# Restart services
sudo docker-compose restart
```

### Update Ubuntu

```bash
sudo apt update
sudo apt upgrade

# Reboot if kernel updated
sudo reboot
```

---

## Backup

### Create Backup

```bash
# Backup 0RB data
sudo tar -czf orb-backup-$(date +%Y%m%d).tar.gz /opt/0rb

# Backup database
sudo -u postgres pg_dump orb_empire > orb-db-$(date +%Y%m%d).sql
```

### Restore Backup

```bash
# Restore files
sudo tar -xzf orb-backup-20251123.tar.gz -C /

# Restore database
sudo -u postgres psql orb_empire < orb-db-20251123.sql

# Restart services
sudo systemctl restart orb-bridge
```

---

## Support

**Problems?**
```bash
# Use AI guide
python3 /opt/0rb/ai_guide.py

# Ask:
# "System won't boot"
# "Services not starting"
# "Dashboard not loading"
```

**Documentation:**
- [WELCOME.md](../WELCOME.md) - Complete guide
- [DEPLOY.md](DEPLOY.md) - Deployment guide
- [START_HERE.md](../START_HERE.md) - Quick start

---

## Philosophy

**Love • Loyalty • Honor • Everybody Eats**

This OS embodies these values:
- ✅ Built with love
- ✅ Free and open
- ✅ Community-first
- ✅ Helps people

**Install it. Use it. Build with love.** 💝

---

**Your 0RB OS is ready.** 🚀

```bash
sudo ./create-bootable-usb.sh /dev/sdX
```

**GO INSTALL.** 🔥
