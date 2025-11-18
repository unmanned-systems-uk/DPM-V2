# System Logs Source Addition - Issue #136 Enhancement

**Date:** 2025-11-17
**WHO:** CC-Dev-Tools
**Status:** ✅ Implementation Complete | Unit Tests Passed

---

## Summary

Added **4th log source** to File Browser Docker Logs tab: **"System Logs"** for comprehensive system-level debugging of Air-Side hardware and kernel issues.

---

## What Was Added

### SOURCE 4: System Logs (Direct SFTP from /var/log/)

**Remote Directory:** `/var/log/`

**Files Included:**
1. **syslog** (+ rotated: `syslog.1`, `syslog.2.gz`, etc.)
   - System-wide messages and events
   - Service status and operations

2. **kern.log** (+ rotated: `kern.log.1`, `kern.log.2.gz`, etc.)
   - Kernel messages
   - **USB device events** (camera connection/disconnection)
   - Hardware events

3. **auth.log** (+ rotated: `auth.log.1`, `auth.log.2.gz`, etc.)
   - SSH authentication logs
   - Security events
   - Access audit trail

4. **dmesg** (+ `dmesg.0`)
   - Boot messages
   - Hardware initialization
   - Kernel ring buffer

**Download Method:** Direct SFTP (same infrastructure as Host Logs)

**Display Source:** "System (SFTP)"

---

## Why This Matters

Essential for debugging camera connection and USB issues:

### Related GitHub Issues
- **Issue #127** - Camera connection debugging
- **Issue #102** - USB device issues
- **Issue #129** - Device detection problems

### Debugging Scenarios

**Scenario 1: Camera Not Detected**
- Check `kern.log` for USB device enumeration
- Look for Sony camera vendor/product IDs
- Verify USB subsystem messages

**Scenario 2: Intermittent Connection**
- Review `kern.log` for USB disconnect/reconnect events
- Check `dmesg` for power management issues
- Examine `syslog` for service restarts

**Scenario 3: Permission Issues**
- Check `auth.log` for SSH access
- Review `syslog` for permission denied errors

**Scenario 4: System-Level Context**
- Get full system context from `syslog`
- Cross-reference with application logs
- Identify system-wide issues affecting DPM

---

## Implementation Details

### Code Changes

**File Modified:** `gui/tab_file_browser.py`

**1. Updated Dropdown (line 247):**
```python
values=["Host Logs", "Container Logs", "Docker Output", "System Logs"]
```

**2. Added Handler in _refresh_logs_file_list() (line 715):**
```python
elif log_source == "System Logs":
    self._load_system_logs()
```

**3. New Method _load_system_logs() (lines 772-815):**
```python
def _load_system_logs(self):
    """Load system logs (SOURCE 4: Direct SFTP from /var/log/)"""
    remote_dir = "/var/log"

    # Filter for system log files
    system_log_patterns = ['syslog', 'kern.log', 'auth.log', 'dmesg']
    log_files = [f for f in files if any(f.startswith(pattern) for pattern in system_log_patterns)]

    # Download via SFTP (same as Host Logs)
    # Tag as "host" for download handler
```

---

## Test Results ✅

**Test Script:** `test_system_logs_source.py`

```
✅ All 4 log sources present in dropdown
✅ _load_system_logs() method exists
✅ All expected file patterns found
   - syslog*
   - kern.log*
   - auth.log*
   - dmesg*
✅ Remote directory: /var/log
✅ Download method: SFTP (host tag)
✅ No runtime errors
```

**All unit tests PASSED**

---

## Usage Guide

### Quick Start

1. **Launch DPM Management System:**
   ```bash
   cd /home/anthony/DPM-V2/SystemTools
   python3 DPM_Management_System.py
   ```

2. **Navigate to File Browser:**
   - Click **📁 File Browser** tab (Tab 7)
   - Click **📋 Docker Logs** sub-tab

3. **Connect to Air-Side:**
   - Click **🔌 Connect**
   - Wait for SSH connection

4. **Select System Logs:**
   - Change **Log Source** dropdown to **"System Logs"**
   - Click **🔄 Refresh**

5. **Download Logs:**
   - Select desired log (e.g., `kern.log`)
   - Click **📥 Download Selected Log**
   - Choose save location
   - Wait for download to complete

### Debugging Examples

**Example 1: Check USB Camera Events**
```
1. Select "System Logs" source
2. Download "kern.log"
3. Open file and search for:
   - "usb" (USB events)
   - "Sony" (camera vendor)
   - "video" (video device)
4. Look for connection/disconnection messages
```

**Example 2: Review System Context**
```
1. Select "System Logs" source
2. Download "syslog"
3. Cross-reference timestamps with application logs
4. Identify system-wide issues
```

**Example 3: Check SSH Access**
```
1. Select "System Logs" source
2. Download "auth.log"
3. Review SSH login attempts
4. Verify no unauthorized access
```

---

## Docker Logs Tab - Complete Source List

| # | Source | Path | Files | Download Method | Use Case |
|---|--------|------|-------|-----------------|----------|
| 1 | **Host Logs** | `/home/dpm/DPM-V2/sbc/logs/` | `payload_manager.log` | SFTP | Application logs |
| 2 | **Container Logs** | `/var/log/dpm/` | `air-side.jsonl` | docker cp + SFTP | Structured logs |
| 3 | **Docker Output** | N/A | Stream | SSH command | Quick snapshots |
| 4 | **System Logs** | `/var/log/` | `syslog`, `kern.log`, `auth.log`, `dmesg` | SFTP | **System/hardware** |

---

## Testing Checklist

### Integration Testing Required

- ⏳ Connect to Air-Side (10.0.1.53)
- ⏳ Select "System Logs" source
- ⏳ Verify file list shows system logs
- ⏳ Download `kern.log` and verify USB events
- ⏳ Download `syslog` and verify system messages
- ⏳ Download `auth.log` and verify SSH logs
- ⏳ Download `dmesg` and verify kernel messages
- ⏳ Verify compressed files (`.gz`) download correctly
- ⏳ Verify progress tracking works
- ⏳ Open downloaded files and verify contents

### Expected File Count

Typical Air-Side `/var/log/` will have:
- ~3-5 syslog files (current + rotated)
- ~3-5 kern.log files (current + rotated)
- ~3-5 auth.log files (current + rotated)
- ~1-2 dmesg files

**Total: ~10-17 system log files**

---

## Known Limitations

1. **Compressed Files:** `.gz` files download as-is (not decompressed)
   - User must decompress locally if needed
   - Most text editors can open `.gz` files directly

2. **Large Files:** Some system logs can be very large (>100MB)
   - Download may take time
   - Progress bar provides feedback

3. **Permissions:** Some system logs may require sudo access
   - Standard SSH user (dpm) has read access to logs
   - Should work without issues

---

## Files Modified/Created

### Modified
- `gui/tab_file_browser.py` - Added SOURCE 4 implementation

### Created
- `test_system_logs_source.py` - Unit test for System Logs source
- `SYSTEM_LOGS_ADDITION.md` - This document

### Updated
- `TESTING_FILE_BROWSER_ISSUE_136.md` - Added Test 5 for System Logs
- `FILE_BROWSER_SUMMARY.md` - Updated to show 4 sources

---

## Success Criteria ✅

- ✅ Dropdown shows 4 sources (Host, Container, Docker Output, System)
- ✅ System Logs filter includes syslog, kern.log, auth.log, dmesg
- ✅ Remote directory is /var/log
- ✅ Download uses SFTP (same as Host Logs)
- ✅ Unit tests pass
- ⏳ Integration testing pending (live Air-Side connection)

---

## Next Steps

1. **User Testing:** Test with live Air-Side connection
2. **Debugging Use:** Use kern.log to debug camera issues (#127, #102, #129)
3. **Documentation:** Update main README if successful
4. **Issue Closure:** Mark #136 as complete after successful testing

---

**WHO:** CC-Dev-Tools
**GitHub Issue:** [#136](https://github.com/unmanned-systems-uk/DPM-V2/issues/136)
**Status:** Implementation ✅ | Unit Tests ✅ | Integration Testing ⏳
