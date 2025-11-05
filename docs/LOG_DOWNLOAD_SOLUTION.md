# DPM Log Download Solution
**Created:** November 5, 2025
**Status:** ✅ Code Changes Complete - Requires Rebuild & Testing

---

## Problem Summary

**Issue:** Flight logs from November 3rd, 2025 appeared to be missing.

**Root Cause:**
- Aircraft had no internet connectivity during flights
- Raspberry Pi RTC lost time when powered off (no backup battery)
- System booted with wrong timestamp (stuck at Nov 1st)
- All flight logs from Nov 2-3 were saved with November 1st timestamps
- Docker logs saved correctly but with wrong timestamps

**Impact:**
- Flight logs exist but are timestamped incorrectly
- Hard to identify which logs correspond to which flight
- Application logging was failing (wrong file path)

---

## Complete Solution Implemented

### ✅ Part 1: Fix Application Logging

**File:** `/home/dpm/DPM-V2/sbc/src/config.h` (line 42-43)

**Changed:**
```cpp
// OLD (wrong path):
constexpr const char* LOG_FILE = "/home/dpm/DPM/sbc/logs/payload_manager.log";

// NEW (correct - maps to volume mount):
// Container path - maps to host: /home/dpm/DPM-V2/sbc/logs/payload_manager.log
constexpr const char* LOG_FILE = "/app/logs/payload_manager.log";
```

**Result:**
- Application logs will now write to accessible file on Pi filesystem
- Logs persist across container restarts
- Easy to download via SFTP

---

### ✅ Part 2: Add SFTP Download to WindowsTools

**File:** `/home/dpm/DPM-V2/WindowsTools/network/ssh_client.py`

**Added Methods:**
- `download_file(remote_path, local_path, progress_callback)` - Download files via SFTP
- `list_directory(remote_path)` - List files in remote directory

**Features:**
- Progress callback support (for future progress bar)
- File size detection
- Error handling

---

### ✅ Part 3: Add Download Button to Log Inspector

**File:** `/home/dpm/DPM-V2/WindowsTools/gui/tab_logs.py`

**Added:**
- "Download Log File..." button in Log Inspector tab
- `_download_log_file()` method for SFTP download
- Background thread download (non-blocking UI)
- Success/error notifications

**User Experience:**
1. Connect SSH in WindowsTools
2. Click "Download Log File..." button
3. Choose save location
4. Log file downloads directly from Pi
5. Shows file size and success message

---

## Hardware Solution: RTC Battery

**Ordered:** Pi 5 RTC backup battery

**Battery Specs:**
- CR2032 coin cell with JST-SH 1mm connector
- Or rechargeable ML2032 / LiPo battery pack
- Connects to J5 connector on Raspberry Pi 5

**When Battery Arrives:**
1. Power off Pi
2. Connect battery to J5 connector (near GPIO header)
3. Power on with internet to sync time once
4. Test: Power off, wait 10 min, power on without internet - time should persist

**Result:** System will keep correct time across power cycles, no wrong timestamps

---

## Next Steps

### 1. Rebuild Air-Side Container

The config.h fix requires rebuilding the payload_manager:

```bash
cd /home/dpm/DPM-V2/sbc

# Build Docker image
./build_container.sh

# Stop old container
docker stop payload-manager
docker rm payload-manager

# Start new container
./run_container.sh prod
```

### 2. Verify Logging Works

```bash
# Check log file is being created
ls -lh /home/dpm/DPM-V2/sbc/logs/

# Should see:
# payload_manager.log  (growing file)

# Verify container is writing to it
tail -f /home/dpm/DPM-V2/sbc/logs/payload_manager.log
```

### 3. Test WindowsTools Download

On Windows PC:
1. Open WindowsTools Diagnostic Tool
2. Go to "Log Inspector" tab
3. Click "Connect SSH"
4. Enter Pi credentials (dpm@192.168.144.10)
5. Click "Download Log File..." button
6. Verify download succeeds

---

## Log Access Options

### Option A: Direct File Access (Recommended)
**Location:** `/home/dpm/DPM-V2/sbc/logs/payload_manager.log` on Pi
- ✅ Plain text, human-readable
- ✅ Easy to archive per-flight
- ✅ Download via SFTP from WindowsTools
- ✅ Can be backed up before each flight

### Option B: Docker Logs (Still Available)
**Command:** `docker logs payload-manager`
- ✅ Always works
- ✅ Includes startup messages
- ⚠️ Requires Docker access
- ⚠️ JSON format in storage

### Option C: Both (Dual Logging)
- Application file logs: Detailed, accessible
- Docker logs: Backup/debugging
- Best for production use

---

## Pre-Flight Checklist (New)

Before each flight, optionally archive the previous log:

```bash
# On Pi before flight:
cd /home/dpm/DPM-V2/sbc/logs
cp payload_manager.log payload_manager_flight_$(date +%Y%m%d).log

# Or clear it for fresh start:
> payload_manager.log
```

After flight, download from WindowsTools:
- Click "Download Log File..." in Log Inspector tab
- Save with flight-specific name: `flight_YYYYMMDD_location.log`

---

## Files Changed

### Air-Side (Requires Rebuild)
- ✅ `/home/dpm/DPM-V2/sbc/src/config.h` - Fixed log file path

### WindowsTools (Ready to Use)
- ✅ `/home/dpm/DPM-V2/WindowsTools/network/ssh_client.py` - Added SFTP download
- ✅ `/home/dpm/DPM-V2/WindowsTools/gui/tab_logs.py` - Added download button

### No Changes Needed
- Docker configuration already has volume mount
- SSH already configured on Pi
- WindowsTools already has SSH client

---

## Testing Checklist

### After Rebuild:

- [ ] Container starts without errors
- [ ] Log file created: `/home/dpm/DPM-V2/sbc/logs/payload_manager.log`
- [ ] Log file grows as system runs
- [ ] No "Failed to open log file" message in Docker logs

### WindowsTools Testing:

- [ ] SSH connection successful
- [ ] "Download Log File..." button visible
- [ ] Download completes successfully
- [ ] Downloaded file readable and contains logs
- [ ] File size shown correctly

### Flight Testing (When Battery Arrives):

- [ ] Battery installed on Pi 5
- [ ] Power off, wait 10 min, power on without internet
- [ ] Time is correct (not defaulting to old date)
- [ ] Logs have correct timestamps

---

## Troubleshooting

### "Failed to download log file"
**Check:**
1. Container rebuilt with fixed config.h?
2. Container running?
3. Log file exists: `ls /home/dpm/DPM-V2/sbc/logs/payload_manager.log`
4. SSH credentials correct?

### "Log file empty or not growing"
**Check:**
1. Container rebuilt?
2. Check Docker logs: `docker logs payload-manager | grep LOG`
3. Check file permissions: `ls -l /home/dpm/DPM-V2/sbc/logs/`

### "Still getting wrong timestamps"
**Temporary until battery arrives:**
- Logs will have wrong timestamps until RTC battery installed
- Use sequence IDs in logs to track different flights
- After battery: timestamps will be correct

---

## Summary

**What Was Done:**
1. ✅ Fixed application log file path in config.h
2. ✅ Added SFTP download capability to WindowsTools SSH client
3. ✅ Added "Download Log File..." button to Log Inspector
4. ✅ Ordered RTC battery for Raspberry Pi 5

**What You Need to Do:**
1. Rebuild air-side container (`./build_container.sh && ./run_container.sh prod`)
2. Test log file creation and download
3. Install RTC battery when it arrives
4. Test timestamp persistence after battery install

**Result:**
- Easy log download from WindowsTools
- Correct timestamps after battery install
- Professional flight log management

---

**Status:** ✅ Ready for rebuild and testing
**Priority:** Medium (current workaround: logs exist with wrong timestamps)
**Timeline:** Rebuild today, battery arrives in 1-3 days
