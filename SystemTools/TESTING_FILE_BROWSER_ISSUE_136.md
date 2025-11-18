# Testing Guide: File Browser Sub-Tabs (Issue #136)

**Issue:** [#136](https://github.com/unmanned-systems-uk/DPM-V2/issues/136)
**Feature:** Enhanced File Browser with Images and Docker Logs sub-tabs
**Date:** 2025-11-17

---

## Overview

The File Browser tab has been enhanced with sub-tabs to support:
1. **Images Tab** - Camera images from `/home/dpm/camera_images` (existing functionality)
2. **Docker Logs Tab** - Comprehensive Air-Side log downloads from 3 sources

---

## Unit Test Results ✅

**Test Script:** `SystemTools/test_file_browser.py`

```bash
cd /home/anthony/DPM-V2/SystemTools
python3 test_file_browser.py
```

**Results:**
- ✅ Module import successful
- ✅ GUI components created without errors
- ✅ Sub-tab notebook structure verified
- ✅ Images sub-tab exists
- ✅ Docker Logs sub-tab exists
- ✅ Log source selector (default: "Host Logs")
- ✅ Tail count selector (default: "1000")
- ✅ All 6 download handlers exist:
  - `_download_host_log`
  - `_download_container_log`
  - `_download_docker_output`
  - `_load_host_logs`
  - `_load_container_logs`
  - `_load_docker_output_entry`

---

## Integration Testing Required

### Prerequisites

1. **Air-Side Connection:**
   - Air-Side Pi 5 powered on and connected to network
   - IP: `10.0.1.53` (configurable in SystemTools config)
   - SSH access: `dpm@10.0.1.53` (password: `2350`)
   - Docker container `payload-manager` running

2. **SystemTools Setup:**
   ```bash
   cd /home/anthony/DPM-V2/SystemTools
   python3 DPM_Management_System.py
   ```
   *(Note: Also works with old system: `python3 main.py`)*

3. **Navigate to File Browser tab (Tab 7)** in DPM Management System

---

## Test Plan

### Test 1: Images Sub-Tab (Existing Functionality)

**Purpose:** Verify existing camera image download functionality still works

1. Click **📷 Images** sub-tab
2. Click **🔌 Connect**
3. Wait for connection confirmation
4. Click **🔄 Refresh**
5. Verify file list populates from `/home/dpm/camera_images`
6. Select a file
7. Click **📥 Download Selected File**
8. Choose save location
9. Verify download completes with progress bar
10. Verify file saved correctly

**Expected Results:**
- ✅ Connection establishes via SFTP
- ✅ File list populates
- ✅ Download works with progress tracking
- ✅ File saved to chosen location

**Status:** ⏳ Pending user testing

---

### Test 2: Docker Logs - SOURCE 1 (Host Logs)

**Purpose:** Test direct SFTP download of host-mounted logs

1. Click **📋 Docker Logs** sub-tab
2. Click **🔌 Connect**
3. Wait for SSH connection confirmation
4. Verify **Log Source** dropdown shows "Host Logs" (default)
5. Click **🔄 Refresh**
6. Verify file list shows logs from `/home/dpm/DPM-V2/sbc/logs/`:
   - `payload_manager.log`
   - Other `.log` files
7. Select `payload_manager.log`
8. Click **📥 Download Selected Log**
9. Choose save location (default: `~/Downloads/air-side-files/logs/`)
10. Verify download completes with progress bar
11. Open downloaded file and verify contents

**Expected Results:**
- ✅ SSH connection establishes
- ✅ Host logs listed with file sizes
- ✅ Download via SFTP works
- ✅ Progress bar updates
- ✅ File saved correctly
- ✅ File contents match remote file

**Status:** ⏳ Pending user testing

---

### Test 3: Docker Logs - SOURCE 2 (Container Logs)

**Purpose:** Test docker cp + SFTP download of container-internal logs

1. In **📋 Docker Logs** sub-tab (connected)
2. Change **Log Source** dropdown to "Container Logs"
3. Click **🔄 Refresh**
4. Verify file list shows logs from container's `/var/log/dpm/`:
   - `air-side.jsonl`
   - `air-side.1.jsonl`
   - `air-side.2.jsonl`
   - `air-side.3.jsonl`
   - File sizes displayed
5. Select `air-side.jsonl`
6. Click **📥 Download Selected Log**
7. Choose save location
8. Watch progress bar:
   - 30% (docker cp starting)
   - 50% (SFTP download starting)
   - 90% (download complete)
   - 95% (cleanup)
   - 100% (done)
9. Verify download completes
10. Open downloaded file and verify JSON Lines format
11. SSH to Air-Side and verify `/tmp/air-side.jsonl` was cleaned up:
    ```bash
    ssh dpm@10.0.1.53
    ls -la /tmp/air-side*
    # Should show: No such file or directory
    ```

**Expected Results:**
- ✅ Docker container running check passes
- ✅ Container logs listed (`.jsonl` files only)
- ✅ Docker cp command executes successfully
- ✅ SFTP download from /tmp works
- ✅ Progress bar shows granular updates (30% → 50% → 90% → 95% → 100%)
- ✅ File saved correctly
- ✅ Temp file cleaned up automatically

**Status:** ⏳ Pending user testing

---

### Test 4: Docker Logs - SOURCE 3 (Docker Output)

**Purpose:** Test docker logs streaming and save to file

1. In **📋 Docker Logs** sub-tab (connected)
2. Change **Log Source** dropdown to "Docker Output"
3. Verify **Tail** dropdown shows "1000" (default)
4. Click **🔄 Refresh**
5. Verify single entry appears:
   - Name: "docker logs payload-manager (tail=1000)"
   - Size: "Stream"
   - Source: "Docker Output"
6. Select the entry
7. Click **📥 Download Selected Log**
8. Choose save location
   - Default filename: `docker-logs-YYYYMMDD_HHMMSS.log`
9. Wait for download (may take longer for large logs)
10. Verify progress bar updates
11. Open downloaded file
12. Verify contents:
    - Contains docker logs output
    - Shows last 1000 lines (or specified tail count)
    - May include stderr section if present

**Test with different tail counts:**
- Repeat steps 2-11 with:
  - Tail = 100
  - Tail = 500
  - Tail = 5000
  - Tail = All (may be very large!)

**Expected Results:**
- ✅ Docker container running check passes
- ✅ Single "Docker Output" entry appears
- ✅ Download initiates SSH `docker logs` command
- ✅ Output saved to local file
- ✅ File contains expected number of lines
- ✅ Both stdout and stderr captured

**Status:** ⏳ Pending user testing

---

### Test 5: Docker Logs - SOURCE 4 (System Logs) **[NEW]**

**Purpose:** Test system log downloads for hardware/system debugging

1. In **📋 Docker Logs** sub-tab (connected)
2. Change **Log Source** dropdown to "System Logs"
3. Click **🔄 Refresh**
4. Verify file list shows logs from `/var/log/`:
   - `syslog` (current)
   - `syslog.1`, `syslog.2.gz`, etc. (rotated)
   - `kern.log` (current)
   - `kern.log.1`, `kern.log.2.gz`, etc. (rotated)
   - `auth.log` (current)
   - `auth.log.1`, `auth.log.2.gz`, etc. (rotated)
   - `dmesg`, `dmesg.0`
   - File sizes displayed
5. Select `kern.log` (for USB/camera debugging)
6. Click **📥 Download Selected Log**
7. Choose save location (default: `~/Downloads/air-side-files/logs/`)
8. Verify download completes with progress bar
9. Open downloaded file
10. Verify contents show kernel messages (USB events, camera detection, etc.)

**Test other system logs:**
- Download `syslog` - verify system-wide messages
- Download `auth.log` - verify SSH/authentication events
- Download `dmesg` - verify kernel/hardware messages
- Download rotated logs (`.gz` files) - verify compressed files download correctly

**Expected Results:**
- ✅ System logs listed from `/var/log/`
- ✅ Only relevant files shown (syslog, kern.log, auth.log, dmesg variants)
- ✅ Download via SFTP works (same as Host Logs)
- ✅ Progress bar updates
- ✅ File saved correctly
- ✅ Compressed (.gz) files download correctly

**Use Cases:**
- **kern.log** - Debug USB device detection, camera connection issues (#127, #102, #129)
- **syslog** - System-wide context, service status
- **auth.log** - SSH access logs, security audit
- **dmesg** - Boot messages, hardware initialization

**Status:** ⏳ Pending user testing

---

### Test 6: Error Handling

**Purpose:** Verify graceful error handling

**Test 6.1: Container Not Running**
1. SSH to Air-Side and stop container:
   ```bash
   ssh dpm@10.0.1.53
   docker stop payload-manager
   ```
2. In SystemTools Docker Logs tab:
3. Select "Container Logs" source
4. Click **🔄 Refresh**
5. Verify error dialog:
   - "Docker container 'payload-manager' is not running"
   - Clear error message
6. Restart container:
   ```bash
   docker start payload-manager
   ```

**Expected:**
- ✅ Clear error message
- ✅ No crash
- ✅ Graceful recovery after restart

**Test 6.2: Network Disconnection**
1. Disconnect from Air-Side
2. Try to download a file
3. Verify error handling

**Expected:**
- ✅ "Not connected" warning
- ✅ No crash

**Test 6.3: Missing Files**
1. Connect to Docker Logs
2. Select "Host Logs"
3. Try to download non-existent file (if possible)
4. Verify error dialog

**Expected:**
- ✅ Clear error message
- ✅ No crash

**Status:** ⏳ Pending user testing

---

## Performance Testing

### Large File Download
- Test downloading large log files (>10MB)
- Verify progress bar updates smoothly
- Verify download completes successfully

### Multiple Downloads
- Test sequential downloads
- Verify previous download completes before starting next
- Verify "Download in Progress" warning works

**Status:** ⏳ Pending user testing

---

## Success Criteria

All tests must pass:
- ✅ Unit tests (PASSED)
- ⏳ Images sub-tab works (existing functionality preserved)
- ⏳ Docker Logs SOURCE 1 works (Host Logs via SFTP)
- ⏳ Docker Logs SOURCE 2 works (Container Logs via docker cp)
- ⏳ Docker Logs SOURCE 3 works (Docker Output via SSH streaming)
- ⏳ Docker Logs SOURCE 4 works (System Logs via SFTP) **[NEW]**
- ⏳ Error handling is graceful and clear
- ⏳ Progress tracking works for all sources
- ⏳ Temp file cleanup works
- ⏳ No runtime errors or crashes

---

## Known Limitations

1. **Single Download at a Time:** Only one download can be in progress at a time (by design)
2. **Docker Output "All" Logs:** May be very large and take time to download
3. **Container Must Be Running:** SOURCE 2 and 3 require container to be running

---

## Next Steps

1. **User Testing:** User should run through complete test plan with live Air-Side connection
2. **Feedback:** Report any issues or edge cases discovered
3. **Documentation Update:** Update main README if successful
4. **Issue Status:** Mark issue #136 as tested/fixed after successful testing

---

**WHO:** CC-Dev-Tools
**Date:** 2025-11-17
**Test Results:** Unit tests ✅ PASSED | Integration tests ⏳ PENDING user testing
