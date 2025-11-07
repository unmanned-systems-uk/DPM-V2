# DPM-V2 Air-Side Deployment Tools
## NVMe SSD Migration Scripts

This directory contains scripts and documentation for migrating the Air-Side Raspberry Pi 5 from SD card to NVMe SSD.

---

## Files

| File | Purpose |
|------|---------|
| `backup-air-side.sh` | **Backup script** - Creates comprehensive backup of current SD card system |
| `deploy-air-side.sh` | **Deployment script** - Sets up fresh OS on NVMe with all dependencies |
| `NVME_MIGRATION_CHECKLIST.md` | **Migration guide** - Step-by-step checklist for migration process |
| `README.md` | This file |

---

## Quick Start

### 1. Before Migration: Create Backup

```bash
# Run backup script (creates backup directory with timestamp)
sudo ~/DPM-V2/tools/deployment/backup-air-side.sh

# Backup will be created at:
# /home/dpm/air-side-backup-YYYYMMDD-HHMMSS/

# Copy backup to external storage for safety!
rsync -av --progress /home/dpm/air-side-backup-* /media/external-drive/
```

### 2. Migration Options

#### Option A: SD Card Clone (Fastest)
- Use Raspberry Pi Imager or `dd` to clone SD to NVMe
- Boot from NVMe
- Verify network and Docker configuration
- **Risk:** Clone may fail or have issues

#### Option B: Fresh Install (Recommended)
- Flash fresh Raspberry Pi OS to NVMe
- Boot from NVMe
- Run deployment script
- Restore files from backup
- **Risk:** Takes longer but more reliable

### 3. Fresh Install Deployment

```bash
# After booting fresh OS on NVMe, run deployment script:
sudo ~/DPM-V2/tools/deployment/deploy-air-side.sh

# Reboot after deployment
sudo reboot

# After reboot, restore project files:
cd /home/dpm
rsync -av /path/to/backup/project/DPM-V2/ ~/DPM-V2/

# Restore Sony SDK:
tar -xzf /path/to/backup/sdk/CrSDK*.tar.gz

# Build and run Docker container:
cd ~/DPM-V2/sbc
docker build -t payload-manager:latest .
docker run -d \
    --name payload-manager \
    --restart unless-stopped \
    --network host \
    --device /dev/bus/usb:/dev/bus/usb \
    -v $(pwd)/logs:/app/logs:rw \
    payload-manager:latest
```

---

## Critical Network Configuration

**Air-Side MUST have static IP for VXLAN bridge to H16:**

```
Interface: eth0
IP Address: 192.168.144.10/24
Gateway: None (point-to-point to H16)
```

The deployment script configures this automatically by adding to `/etc/dhcpcd.conf`:

```bash
interface eth0
static ip_address=192.168.144.10/24
noipv6
```

**Verification:**
```bash
ip addr show eth0
# Should show: inet 192.168.144.10/24

ping 192.168.144.11
# Should reach H16 (if powered on)
```

---

## Backup Contents

The backup script creates a comprehensive backup including:

### Project Files
- `/home/dpm/DPM-V2/` - Complete project source
- `/home/dpm/CrSDK_v2.00.00_20250805a_Linux64ARMv8/` - Sony SDK (compressed)

### Configuration
- Network configuration (`/etc/dhcpcd.conf`, IP state)
- Docker configuration and container setup
- User configs (`.bashrc`, `.ssh`, `.gitconfig`)
- System package list (`dpkg --get-selections`)

### Documentation
- Restoration guide (auto-generated)
- Network configuration details
- Docker container recreation script
- Backup manifest

---

## Deployment Script Features

The `deploy-air-side.sh` script performs:

1. ✅ System update and upgrade
2. ✅ Install development tools (gcc, g++, cmake, git)
3. ✅ Install Docker CE
4. ✅ Install Python 3 and pip
5. ✅ Configure network (static IP for eth0)
6. ✅ Configure USB permissions for Sony camera
7. ✅ Create project directories
8. ✅ Enable SSH
9. ✅ Set hostname to 'air-side-pi5'
10. ✅ Configure system limits
11. ✅ Install utilities (htop, ncdu, etc.)
12. ✅ Create deployment summary

**IMPORTANT:** System reboot required after deployment for network configuration to take effect.

---

## Verification After Migration

### Network
```bash
ip addr show eth0         # Should show 192.168.144.10/24
ping 192.168.144.11       # Should reach H16
```

### Docker
```bash
docker ps                 # Should show payload-manager running
docker logs payload-manager  # Should show camera connected
```

### Camera
```bash
lsusb | grep Sony         # Should show Sony camera
```

### Storage
```bash
lsblk                     # Should show nvme0n1
df -h                     # Should show NVMe mounted on /
```

---

## Troubleshooting

### Network Issues
**Problem:** eth0 doesn't have static IP

**Solution:**
```bash
sudo nano /etc/dhcpcd.conf
# Add:
# interface eth0
# static ip_address=192.168.144.10/24
# noipv6

sudo systemctl restart dhcpcd
```

### Docker Permission Denied
**Problem:** Cannot run docker commands

**Solution:**
```bash
# Log out and log back in (user needs to join docker group)
# Or run:
newgrp docker
```

### Camera Not Detected
**Problem:** lsusb shows camera but Docker can't access it

**Solution:**
```bash
# Check camera is in PC Remote mode (camera LCD)
# Reload udev rules:
sudo udevadm control --reload-rules
# Unplug and replug camera USB
```

### Container Won't Start
**Problem:** payload-manager container fails to start

**Solution:**
```bash
# Check logs:
docker logs payload-manager

# Rebuild container:
cd ~/DPM-V2/sbc
docker rm -f payload-manager
docker build -t payload-manager:latest .
# Run container (see above)
```

---

## Performance Expectations

### NVMe vs SD Card

| Metric | SD Card (UHS-I) | NVMe SSD | Improvement |
|--------|-----------------|----------|-------------|
| Boot Time | 40-60 seconds | 15-25 seconds | **~60% faster** |
| Sequential Read | 90 MB/s | 500+ MB/s | **~5x faster** |
| Sequential Write | 70 MB/s | 450+ MB/s | **~6x faster** |
| Random IOPS | ~1,000 | ~50,000 | **~50x faster** |
| Docker Build | 5-10 minutes | 1-2 minutes | **~5x faster** |

**Benefits for DPM-V2:**
- Faster camera file transfers
- Quicker Docker builds
- More responsive logging
- Faster image capture processing (future feature)

---

## Safety and Recovery

### Backup Safety
- **Always copy backup to external storage before migration**
- Keep original SD card as emergency recovery
- Test backup restoration before wiping SD card

### Rollback Options
1. **SD Card Clone Failed:** Boot from original SD card
2. **Fresh Install Failed:** Use backup to restore on new SD card
3. **NVMe Hardware Failed:** Replace NVMe, restore from backup

---

## Script Maintenance

### Updating Scripts
Scripts are version controlled in DPM-V2 git repository:

```bash
cd ~/DPM-V2
git status tools/deployment/
git commit -m "Update deployment scripts"
git push
```

### Testing Scripts
Test backup script (won't harm system):
```bash
sudo ~/DPM-V2/tools/deployment/backup-air-side.sh /tmp/test-backup
```

**DO NOT** test deployment script on production system!

---

## Additional Resources

### Related Documentation
- `NVME_MIGRATION_CHECKLIST.md` - Complete step-by-step guide
- `(backup)/docs/RESTORATION_GUIDE.md` - Generated during backup
- `~/DEPLOYMENT_SUMMARY.txt` - Generated after deployment
- DPM-V2 main docs: `~/DPM-V2/docs/`

### External Resources
- [Raspberry Pi 5 NVMe Boot](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html)
- [Docker on Raspberry Pi](https://docs.docker.com/engine/install/debian/)
- [Sony Camera Remote SDK](https://support.d-imaging.sony.co.jp/app/sdk/en/index.html)

---

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review backup restoration guide
3. Check Docker logs: `docker logs payload-manager`
4. Review deployment summary: `cat ~/DEPLOYMENT_SUMMARY.txt`
5. Create GitHub issue: https://github.com/unmanned-systems-uk/DPM-V2/issues

---

**Last Updated:** 2025-11-07
**DPM-V2 Version:** 1.0.0
**Tested On:** Raspberry Pi 5 Model B (8GB), Raspberry Pi OS Bookworm 64-bit
