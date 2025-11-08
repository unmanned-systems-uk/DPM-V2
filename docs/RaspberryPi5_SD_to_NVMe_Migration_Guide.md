# Raspberry Pi 5: Ubuntu Migration from SD Card to NVMe SSD

## Complete Step-by-Step Guide

**Author's Note:** This guide is based on a real migration experience with Ubuntu on Raspberry Pi 5. It includes all the critical steps and troubleshooting lessons learned during the process.

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Important Warnings](#important-warnings)
4. [Migration Process](#migration-process)
5. [Critical Lessons Learned](#critical-lessons-learned)
6. [Troubleshooting](#troubleshooting)
7. [Performance Expectations](#performance-expectations)

---

## Overview

This guide walks you through migrating a live Ubuntu installation from an SD card to an NVMe SSD on a Raspberry Pi 5. The process involves:

- Partitioning and formatting the NVMe drive
- Cloning your entire system using rsync
- Configuring boot parameters
- **Regenerating initramfs with NVMe support (CRITICAL)**
- Setting up the bootloader

**Estimated Time:** 1-2 hours (depending on SD card size and system complexity)

---

## Prerequisites

### Hardware Requirements

- Raspberry Pi 5
- NVMe SSD (M.2 form factor)
- NVMe HAT or adapter for Raspberry Pi 5
- Working SD card with Ubuntu currently running
- Keyboard and monitor (or SSH access)

### Software Requirements

- Ubuntu already installed and running on SD card
- Root/sudo access
- Basic familiarity with terminal commands

### Before You Begin

- **Backup your data** - While this process is non-destructive to the SD card, always have backups
- Ensure your Pi is connected to power (preferably use the official power supply)
- Have stable internet connection for any updates

---

## Important Warnings

⚠️ **CRITICAL WARNINGS:**

1. **The NVMe drive will be completely erased** - All data on the NVMe will be lost
2. **Keep the SD card inserted** during the initial setup and first boot attempts
3. **Do NOT skip Step 5** (initramfs regeneration) - This is the most critical step
4. **Partition table type matters** - Must use MBR/DOS partition table, NOT GPT
5. **Partition type matters** - Boot partition must be type 'c' (W95 FAT32 LBA)

📝 **Important Notes:**

- The process is done while the system is running from the SD card
- Your SD card remains bootable as a backup
- The entire process can be reversed if needed
- After successful migration, the SD card can be safely removed

---

## Migration Process

### Step 1: Identify Your NVMe Drive

Boot from your SD card as normal, then identify the NVMe device:

```bash
lsblk
```

**Look for your devices:**
- SD card will be `/dev/mmcblk0` (with partitions `/dev/mmcblk0p1`, `/dev/mmcblk0p2`)
- NVMe will be `/dev/nvme0n1` (no partitions yet if new)

⚠️ **IMPORTANT:** Double-check you have the correct device names before proceeding!

---

### Step 2: Partition the NVMe Drive

We need to create two partitions using **MBR/DOS partition table** (NOT GPT):

```bash
sudo fdisk /dev/nvme0n1
```

**In fdisk, follow these steps exactly:**

#### Create Partition 1 (Boot - 512MB)

1. Press `n` (new partition)
2. Press `1` (partition number 1)
3. Press `Enter` (accept default first sector)
4. Type `+512M` (last sector for 512MB partition)
5. Press `Enter`

#### Set Partition 1 Type to FAT32

6. Press `t` (change type)
7. Press `1` (partition 1)
8. Type `c` (W95 FAT32 LBA)
9. Press `Enter`

#### Create Partition 2 (Root - Remaining Space)

10. Press `n` (new partition)
11. Press `2` (partition number 2)
12. Press `Enter` (accept default first sector)
13. Press `Enter` (accept default last sector - uses all remaining space)

#### Write Changes

14. Press `w` (write changes and exit)

**Verify the partition table:**

```bash
sudo fdisk -l /dev/nvme0n1
```

You should see:
- Disklabel type: **dos** (NOT gpt)
- `/dev/nvme0n1p1`: 512M, Type: **c W95 FAT32 (LBA)**
- `/dev/nvme0n1p2`: Remaining space, Type: **83 Linux**

---

### Step 3: Format the Partitions

Format the boot partition as FAT32:

```bash
sudo mkfs.vfat -F 32 /dev/nvme0n1p1
```

Format the root partition as ext4:

```bash
sudo mkfs.ext4 /dev/nvme0n1p2
```

---

### Step 4: Set Partition Labels

Ubuntu expects specific labels for boot partitions:

```bash
sudo fatlabel /dev/nvme0n1p1 system-boot
sudo e2label /dev/nvme0n1p2 writable
```

**Verify the labels:**

```bash
sudo blkid | grep nvme
```

You should see:
- `/dev/nvme0n1p1`: LABEL="system-boot"
- `/dev/nvme0n1p2`: LABEL="writable"

---

### Step 5: Mount the NVMe Partitions

Create mount points:

```bash
sudo mkdir -p /mnt/root
sudo mkdir -p /mnt/boot
```

Mount the root partition first:

```bash
sudo mount /dev/nvme0n1p2 /mnt/root
```

Create the boot firmware directory and mount the boot partition:

```bash
sudo mkdir -p /mnt/root/boot/firmware
sudo mount /dev/nvme0n1p1 /mnt/root/boot/firmware
```

**Verify mounts:**

```bash
df -h | grep nvme
```

---

### Step 6: Clone Your System with rsync

This is where we copy everything from the SD card to the NVMe. This will take several minutes.

```bash
sudo rsync -aAXv --exclude={"/dev/*","/proc/*","/sys/*","/tmp/*","/run/*","/mnt/*","/media/*","/lost+found"} / /mnt/root/
```

**What this command does:**
- `-a`: Archive mode (preserves permissions, timestamps, symlinks)
- `-A`: Preserve ACLs
- `-X`: Preserve extended attributes
- `-v`: Verbose output
- `--exclude`: Skips virtual filesystems and temporary directories

⏱️ **Expected time:** 10-30 minutes depending on your SD card size and speed

---

### Step 7: Get UUIDs for Configuration

Get the UUIDs of both NVMe partitions:

```bash
sudo blkid /dev/nvme0n1p1
sudo blkid /dev/nvme0n1p2
```

**Write down or copy these UUIDs** - you'll need them in the next step.

Example output:
```
/dev/nvme0n1p1: LABEL="system-boot" UUID="9EA0-E34A" TYPE="vfat"
/dev/nvme0n1p2: LABEL="writable" UUID="d9e266de-b6b0-49b0-81fb-d2b5ca212b21" TYPE="ext4"
```

---

### Step 8: Configure fstab on NVMe

Edit the fstab file on the NVMe:

```bash
sudo nano /mnt/root/etc/fstab
```

**Replace the entire contents with** (using YOUR UUIDs from Step 7):

```
UUID=d9e266de-b6b0-49b0-81fb-d2b5ca212b21 / ext4 defaults 0 1
UUID=9EA0-E34A /boot/firmware vfat defaults 0 2
```

**Critical: Make sure you have the UUIDs in the correct order:**
- First line: Root partition (ext4) mounted at `/`
- Second line: Boot partition (vfat) mounted at `/boot/firmware`

Save and exit: `Ctrl+X`, then `Y`, then `Enter`

---

### Step 9: Configure Boot Command Line

Edit the cmdline.txt file:

```bash
sudo nano /mnt/root/boot/firmware/cmdline.txt
```

**Find the `root=` parameter and change it to:**

```
root=LABEL=writable
```

The complete line should look similar to:
```
zswap.enabled=1 zswap.zpool=z3fold zswap.compressor=zstd multipath=off dwc_otg.lpm_enable=0 console=tty1 root=LABEL=writable rootfstype=ext4 rootwait fixrtc quiet splash
```

⚠️ **IMPORTANT:** This is all ONE line - do not add line breaks!

Save and exit: `Ctrl+X`, then `Y`, then `Enter`

---

### Step 10: Regenerate Initramfs (MOST CRITICAL STEP)

🔴 **THIS IS THE MOST IMPORTANT STEP - DO NOT SKIP!**

The initramfs (initial RAM filesystem) needs to include NVMe drivers for early boot. Without this, the kernel will panic and fail to boot from NVMe.

**Unmount the NVMe partitions first:**

```bash
sudo umount /mnt/root/boot/firmware
sudo umount /mnt/root
```

**Mount them again to ensure we're working with the NVMe system:**

```bash
sudo mount /dev/nvme0n1p2 /mnt/root
sudo mount /dev/nvme0n1p1 /mnt/root/boot/firmware
```

**Now regenerate the initramfs:**

Since you're already running from a system that has access to the NVMe, the simplest approach is:

```bash
sudo update-initramfs -u -k all
```

**What this does:**
- Updates all kernel versions (`-k all`)
- Includes NVMe drivers in the early boot environment
- Ensures the kernel can find and mount the NVMe root filesystem

⏱️ **Expected time:** 1-2 minutes

---

### Step 11: Update Bootloader Configuration

First, check if your bootloader needs updating:

```bash
sudo rpi-eeprom-update
```

If an update is available, install it:

```bash
sudo rpi-eeprom-update -a
sudo reboot
```

After reboot (still from SD card), configure the boot order:

```bash
sudo rpi-eeprom-config --edit
```

**Find the `BOOT_ORDER=` line and change it to:**

```
BOOT_ORDER=0xf416
```

**What this means:**
- `6` = NVMe boot
- `4` = USB boot
- `1` = SD card boot
- `f` = Repeat/network boot

This tells the Pi to try NVMe first, then USB, then SD card.

Save and exit.

---

### Step 12: Unmount and Prepare for First Boot

Unmount the NVMe partitions:

```bash
sudo umount /mnt/root/boot/firmware
sudo umount /mnt/root
```

**Verify everything is unmounted:**

```bash
df -h | grep nvme
```

(Should show nothing)

---

### Step 13: First Boot from NVMe

**Now reboot:**

```bash
sudo reboot
```

🤞 **Keep the SD card inserted** for this first boot attempt.

**What should happen:**
- Pi boots from NVMe
- System loads normally
- You see the Ubuntu login screen/desktop

---

### Step 14: Verify You're Running from NVMe

After logging in, verify you're running from NVMe:

```bash
df -h /
```

**Expected output:**
```
Filesystem      Size  Used Avail Use% Mounted on
/dev/nvme0n1p2  XXX   XXX   XXX   X%  /
```

**Also check with:**

```bash
lsblk
```

You should see `/dev/nvme0n1p2` mounted as `/`

**Check boot command line:**

```bash
cat /proc/cmdline
```

Should show `root=LABEL=writable`

---

### Step 15: Test Boot Without SD Card

**Now for the final test - boot without the SD card:**

1. Shut down completely: `sudo shutdown -h now`
2. Wait for Pi to power off completely
3. **Remove the SD card**
4. Power on the Pi

✅ **Success!** If it boots normally, your migration is complete!

❌ **If it fails to boot:** See the troubleshooting section below.

---

## Critical Lessons Learned

These are the key insights from the migration process that made the difference between success and failure:

### 1. Partition Table Type Matters

**Problem:** Using GPT partition table with EFI System type for boot partition caused the Pi to skip the NVMe during boot.

**Solution:** Must use MBR/DOS partition table with type 'c' (W95 FAT32 LBA) for the boot partition.

**Verification:**
```bash
sudo fdisk -l /dev/nvme0n1
```

Should show:
- `Disklabel type: dos` (NOT gpt)
- Boot partition type: `c W95 FAT32 (LBA)` (NOT EFI System)

---

### 2. Initramfs Regeneration is Critical

**Problem:** Without NVMe drivers in initramfs, kernel panics with "VFS: Unable to mount root fs on unknown-block(0,0)"

**Solution:** MUST run `sudo update-initramfs -u -k all` to include NVMe drivers in early boot.

**Why this matters:**
- The initramfs loads before the main kernel
- It needs NVMe drivers to find and mount the NVMe root partition
- Without these drivers, the kernel can't access the NVMe at all during early boot

---

### 3. Boot Order Configuration Strategy

**Problem:** Setting `BOOT_ORDER=0xf416` immediately caused boot failures during setup.

**Solution:** Use a phased approach:

**Phase 1 (Setup):** `BOOT_ORDER=0xf1` (SD card first)
- Allows booting from SD while configuring NVMe
- Provides fallback if something goes wrong
- Enables fixing issues without removing hardware

**Phase 2 (After initramfs update):** `BOOT_ORDER=0xf416` (NVMe first)
- Only switch after initramfs is regenerated
- Ensures NVMe has all necessary drivers

---

### 4. Label vs UUID Boot Parameters

**Finding:** U-Boot (the bootloader) on Raspberry Pi respects `LABEL=` better than `UUID=` in cmdline.txt.

**Best practice:** Use `root=LABEL=writable` instead of `root=UUID=...`

**Why:**
- More reliable across different boot scenarios
- Matches Ubuntu's default expectations
- Easier to read and verify

---

### 5. The rsync Exclude List is Important

**Critical excludes:**
```
/dev/* /proc/* /sys/* /tmp/* /run/* /mnt/* /media/* /lost+found
```

**Why each matters:**
- `/dev/*` = Virtual device files (created by kernel)
- `/proc/*` = Process information pseudo-filesystem
- `/sys/*` = System/kernel information
- `/tmp/*` = Temporary files (not needed)
- `/run/*` = Runtime variable data
- `/mnt/*` = Would create recursive loop (we're copying TO /mnt)
- `/media/*` = Mount points for removable media
- `/lost+found` = Filesystem recovery directory

---

### 6. Verification at Each Step

**Key checkpoints:**

After partitioning:
```bash
sudo fdisk -l /dev/nvme0n1  # Check partition table type and types
```

After formatting:
```bash
sudo blkid | grep nvme  # Verify labels and UUIDs
```

After mounting:
```bash
df -h | grep nvme  # Confirm mounts are correct
```

After boot:
```bash
df -h /  # Verify root is on NVMe
lsblk    # See complete storage layout
```

---

## Troubleshooting

### Problem 1: Kernel Panic - "Unable to mount root fs on unknown-block(0,0)"

**Symptoms:**
- System tries to boot
- Shows kernel messages
- Panics with "VFS: Unable to mount root fs on unknown-block(0,0)"
- System hangs

**Root Cause:**
Initramfs doesn't have NVMe drivers loaded early enough in boot sequence.

**Solution:**

1. **Power off and reinsert SD card**

2. **Change boot order to SD first:**
   ```bash
   sudo rpi-eeprom-config --edit
   ```
   Change to: `BOOT_ORDER=0xf1`
   Save and exit.

3. **Reboot from SD card:**
   ```bash
   sudo reboot
   ```

4. **Regenerate initramfs:**
   ```bash
   sudo update-initramfs -u -k all
   ```

5. **Change boot order back to NVMe first:**
   ```bash
   sudo rpi-eeprom-config --edit
   ```
   Change to: `BOOT_ORDER=0xf416`
   Save and exit.

6. **Reboot and test:**
   ```bash
   sudo reboot
   ```

---

### Problem 2: System Only Boots with SD Card Present

**Symptoms:**
- Works fine with SD card inserted
- Fails to boot when SD card removed
- Bootloader shows "Insert SD-Card"

**Root Cause:**
Bootloader is still trying SD card first, or initramfs wasn't properly regenerated.

**Solution:**

1. **Check boot order:**
   ```bash
   sudo rpi-eeprom-config
   ```
   Should show `BOOT_ORDER=0xf416`

2. **If boot order is wrong, fix it:**
   ```bash
   sudo rpi-eeprom-config --edit
   ```
   Change to: `BOOT_ORDER=0xf416`

3. **Verify initramfs was updated:**
   ```bash
   ls -lh /boot/firmware/initrd.img
   ```
   Check the timestamp - should be recent (from when you ran update-initramfs)

4. **If initramfs is old, regenerate:**
   ```bash
   sudo update-initramfs -u -k all
   ```

5. **Reboot and test without SD card**

---

### Problem 3: Bootloader Doesn't See NVMe

**Symptoms:**
- Bootloader cycles through boot devices
- Never attempts NVMe
- Falls back to SD card or shows "no bootable device"

**Root Cause:**
Wrong partition table type or boot partition type.

**Solution:**

1. **Check partition table:**
   ```bash
   sudo fdisk -l /dev/nvme0n1
   ```

2. **Verify you see:**
   - `Disklabel type: dos` (NOT gpt)
   - Partition 1 type: `c W95 FAT32 (LBA)` (NOT EFI System or Linux filesystem)

3. **If partition table is wrong, you need to repartition:**
   ⚠️ **This will erase the NVMe - backup if you've already copied data**

   ```bash
   sudo fdisk /dev/nvme0n1
   ```
   - Delete all partitions (`d`)
   - Create new DOS partition table if needed
   - Follow Step 2 in the main guide exactly

4. **After repartitioning, start from Step 3 (formatting) in the main guide**

---

### Problem 4: fstab Errors or "Waiting for /boot/firmware"

**Symptoms:**
- Long delay during boot
- Error messages about mounting /boot/firmware
- System drops to emergency shell

**Root Cause:**
Wrong UUIDs in fstab, or UUIDs swapped.

**Solution:**

1. **Boot from SD card** (set `BOOT_ORDER=0xf1` if needed)

2. **Mount NVMe and check fstab:**
   ```bash
   sudo mount /dev/nvme0n1p2 /mnt/root
   cat /mnt/root/etc/fstab
   ```

3. **Get correct UUIDs:**
   ```bash
   sudo blkid /dev/nvme0n1p1
   sudo blkid /dev/nvme0n1p2
   ```

4. **Edit fstab with correct UUIDs:**
   ```bash
   sudo nano /mnt/root/etc/fstab
   ```

   Correct format:
   ```
   UUID=<p2-uuid> / ext4 defaults 0 1
   UUID=<p1-uuid> /boot/firmware vfat defaults 0 2
   ```

   **Remember:**
   - p2 (ext4) mounts to `/`
   - p1 (vfat) mounts to `/boot/firmware`

5. **Save and unmount:**
   ```bash
   sudo umount /mnt/root
   ```

6. **Reboot**

---

### Problem 5: "Read-only file system" Errors

**Symptoms:**
- System boots but can't write files
- Error messages about read-only filesystem
- Can't install updates or save files

**Root Cause:**
Filesystem was mounted read-only due to errors.

**Solution:**

1. **Check filesystem for errors:**
   ```bash
   sudo fsck -f /dev/nvme0n1p2
   ```
   (You may need to boot from SD card and unmount NVMe first)

2. **If errors are found, let fsck fix them**

3. **Remount read-write:**
   ```bash
   sudo mount -o remount,rw /
   ```

4. **For permanent fix, check fstab has correct options**

---

### Problem 6: Extremely Slow Boot or System Hangs

**Symptoms:**
- Boot takes 5+ minutes
- System appears hung at boot screen
- Eventually boots but very slow

**Root Cause:**
systemd waiting for timeout on missing services or mounts.

**Solution:**

1. **Check boot logs:**
   ```bash
   journalctl -b
   ```

2. **Look for timeout messages or failed services**

3. **Common issues:**
   - Old fstab entries pointing to SD card partitions
   - Network shares that timeout
   - Services trying to access old paths

4. **Clean up fstab:**
   Remove any old SD card entries or non-essential mounts

---

### Problem 7: Different UUID After Each Reboot

**Symptoms:**
- UUID changes every time you run blkid
- Boot configuration keeps breaking

**Root Cause:**
Very rare, but can happen with certain SSD firmware.

**Solution:**
Use LABEL instead of UUID everywhere:
- In fstab: `LABEL=writable` and `LABEL=system-boot`
- In cmdline.txt: `root=LABEL=writable`

---

### Emergency Recovery

**If everything fails and system won't boot:**

1. **You still have your working SD card!**
   - Insert SD card
   - Boot from SD card
   - Your original system is intact

2. **Reset boot order to SD first:**
   ```bash
   sudo rpi-eeprom-config --edit
   ```
   Set: `BOOT_ORDER=0xf1`

3. **Try the migration again**, paying special attention to:
   - Partition table type (MBR/DOS)
   - Partition 1 type (c - W95 FAT32 LBA)
   - Running `update-initramfs -u -k all`

4. **If you want to start completely fresh:**
   ```bash
   sudo fdisk /dev/nvme0n1
   # Delete all partitions (d)
   # Start from Step 2 of main guide
   ```

---

## Performance Expectations

After successful migration, you should see dramatic improvements:

### Boot Performance
- **SD Card:** 60-90 seconds to desktop
- **NVMe:** 20-30 seconds to desktop
- **Improvement:** 60-70% faster boot

### Sequential Read/Write
- **SD Card (Class 10/U1):** 80-100 MB/s read, 50-80 MB/s write
- **SD Card (U3):** 90-120 MB/s read, 80-100 MB/s write
- **NVMe (Budget):** 400-500 MB/s read, 300-400 MB/s write
- **NVMe (High-end):** 1000-1500 MB/s read, 800-1200 MB/s write
- **Improvement:** 4-10x faster

### Random I/O (Most Important for System Responsiveness)
- **SD Card:** 1-2 MB/s (very slow)
- **NVMe:** 50-100 MB/s
- **Improvement:** 20-50x faster

### Real-World Impact
- Application launches: **2-5x faster**
- Package installations: **3-6x faster**
- System updates: **4-8x faster**
- Database operations: **10-20x faster**
- Docker container operations: **5-10x faster**
- Compilation times: **3-5x faster**

### Reliability
- **SD Cards:** Wear out with writes, typical lifespan 1-3 years with heavy use
- **NVMe:** Much more durable, typical lifespan 5-10+ years
- **Write endurance:** NVMe has 10-100x better write endurance

---

## Post-Migration Recommendations

### 1. Verify System Health

After first successful boot from NVMe:

```bash
# Check disk usage
df -h

# Check for filesystem errors
sudo dmesg | grep -i error

# Verify all services started
systemctl --failed

# Check system logs
journalctl -b -p err
```

---

### 2. Update System

Good time to ensure everything is current:

```bash
sudo apt update
sudo apt upgrade -y
sudo apt autoremove -y
```

---

### 3. Monitor NVMe Health

Install smartmontools to monitor SSD health:

```bash
sudo apt install smartmontools
sudo smartctl -a /dev/nvme0n1
```

Look for:
- Percentage used (wear level)
- Available spare
- Temperature

---

### 4. Optimize for NVMe

Enable TRIM support for SSD longevity:

```bash
# Check if TRIM is supported
sudo fstrim -v /

# Enable weekly TRIM timer
sudo systemctl enable fstrim.timer
sudo systemctl start fstrim.timer
```

---

### 5. What to Do with the SD Card

**Options:**

**Keep as backup:**
- Store it safely
- It's a complete bootable backup of your system
- Can boot from it if NVMe ever fails

**Repurpose:**
- Use in another Pi
- Use as general storage
- Reformat for other uses

**Update regularly (if keeping as backup):**
```bash
# Boot from SD, then clone NVMe back to SD periodically
# (Reverse of this guide's process)
```

---

### 6. Set Up Regular Backups

Now that you're on NVMe, set up automated backups:

```bash
# Example: Daily backup to external USB drive
# Add to cron: sudo crontab -e
0 2 * * * rsync -a --delete / /mnt/backup/ --exclude={/dev/*,/proc/*,/sys/*,/tmp/*,/run/*,/mnt/*,/media/*}
```

---

## Frequently Asked Questions

### Can I do this with Raspberry Pi OS (Raspbian) instead of Ubuntu?

Yes! The process is very similar. The main differences:
- Raspberry Pi OS may use slightly different partition labels
- The `raspi-config` tool can help with some steps
- Consider using `rpi-clone` utility (available for Raspberry Pi OS)

### Do I need to use exactly 512MB for the boot partition?

512MB is recommended and standard. You can use more (like 1GB) but there's no benefit. Don't use less than 256MB.

### Can I use a SATA SSD instead of NVMe?

Yes! The process is nearly identical. Just replace `/dev/nvme0n1` with `/dev/sda` (or whatever your SATA device shows as). Note: SATA will be slower than NVMe, but still much faster than SD card.

### Will this work on Raspberry Pi 4?

The process is similar but not identical:
- Pi 4 needs additional USB boot configuration
- EEPROM must be recent enough to support USB/NVMe boot
- Some steps differ in the bootloader configuration

### What if my NVMe is larger than my SD card?

Perfect! The root partition will automatically use all available space. You'll have much more storage after migration.

### What if I want to keep some data on the SD card?

This guide doesn't touch your SD card data - it remains intact. After migration, you can mount the SD card and access its files.

### Can I go back to booting from SD card later?

Yes! Just change the boot order:
```bash
sudo rpi-eeprom-config --edit
# Set BOOT_ORDER=0xf1
```
Your SD card remains unchanged and bootable.

### Do I need to reinstall any software?

No! Everything is cloned exactly as-is. All your software, configurations, and data come over.

### Why does the guide emphasize initramfs so much?

Because it's the #1 cause of boot failure. The initramfs loads before the main kernel and MUST have NVMe drivers, or the kernel can't access the NVMe to boot. This was the hardest-learned lesson from the migration.

### My NVMe is showing lower speeds than expected. Why?

Check:
- Are you measuring correctly? Use `sudo hdparm -t /dev/nvme0n1`
- Is the NVMe overheating? Check: `cat /sys/class/nvme/nvme0/hwmon*/temp1_input`
- Is your adapter/HAT limiting speed? Some adapters are PCIe Gen 2 only
- Raspberry Pi 5 has PCIe Gen 2 (not Gen 3), so max ~500 MB/s per lane

### Should I overclock after migrating to NVMe?

The faster I/O can benefit from faster CPU, but:
- Ensure adequate cooling
- Monitor temperatures
- NVMe generates heat too
- Don't overclock until you verify stable operation at stock speeds

---

## Conclusion

Migrating Ubuntu from SD card to NVMe on Raspberry Pi 5 provides massive performance improvements. The key to success is:

1. **Using the correct partition table type** (MBR/DOS, not GPT)
2. **Using the correct partition type** (W95 FAT32 LBA for boot)
3. **Regenerating initramfs** to include NVMe drivers
4. **Following the steps in order** without skipping
5. **Keeping the SD card as backup** during the process

The most critical step is regenerating the initramfs (`sudo update-initramfs -u -k all`). This ensures the kernel can find and mount the NVMe drive during early boot.

After migration, you'll enjoy:
- 60-70% faster boot times
- 4-10x faster sequential I/O
- 20-50x faster random I/O
- Much better system responsiveness
- Improved reliability and longevity

Your SD card remains intact and bootable as a backup, and can be safely removed once you verify the NVMe boot is working correctly.

---

## Additional Resources

**Official Documentation:**
- [Raspberry Pi 5 Bootloader Documentation](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#raspberry-pi-5-bootloader)
- [Ubuntu on Raspberry Pi](https://ubuntu.com/download/raspberry-pi)

**Useful Commands Reference:**

```bash
# Check boot device
df -h /

# View boot command line
cat /proc/cmdline

# Check boot order
sudo rpi-eeprom-config

# Monitor system resources
htop

# Check disk I/O
sudo iotop

# Check NVMe info
sudo nvme list

# Check filesystem health
sudo fsck -n /dev/nvme0n1p2

# View boot logs
journalctl -b

# Check for errors
dmesg | grep -i error
```

---

**Document Version:** 1.0  
**Last Updated:** November 2025  
**Based On:** Real-world Ubuntu migration on Raspberry Pi 5  
**Tested With:** Ubuntu 24.04 LTS on Raspberry Pi 5 (8GB)

---

## Credits

This guide is based on hands-on experience migrating a live Ubuntu system from SD card to NVMe SSD, including all the troubleshooting and lessons learned during the process. Special attention was paid to documenting the critical steps that are often missed in other guides, particularly the initramfs regeneration requirement.

---

*End of Guide*
