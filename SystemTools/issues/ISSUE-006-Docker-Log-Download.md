# Issue #6: Implement Full Docker Log Download in SystemTools

**Status:** 🟡 Open
**Priority:** Medium
**Category:** Feature Enhancement
**Component:** SystemTools - Log Inspector Tab
**Created:** 2025-11-05
**Target Version:** v1.8.0

---

## Summary

Add capability to download complete Docker container logs from Air-Side Pi to Windows PC via SystemTools diagnostic tool, complementing the existing application log file download feature.

---

## Current State

### What We Have (v1.7.0):
✅ **Application Log File Download**
- Downloads: `/home/dpm/DPM-V2/sbc/logs/payload_manager.log`
- Method: SFTP via `SSHClient.download_file()`
- Button: "Download Log File..." in Log Inspector tab
- Works for application-level logs only

✅ **Docker Log Viewing**
- Views logs via SSH: `docker logs payload-manager`
- Can tail, filter, and search in UI
- Can save displayed logs to file (limited to what's shown)

### What's Missing:
❌ **Complete Docker log download** to file
❌ **Full log history** download (not just displayed portion)
❌ **Docker log export** with all container metadata
❌ **Startup messages** and initialization logs included

---

## Problem Statement

**Current Limitation:**
Users can view Docker logs in the SystemTools UI and save what's currently displayed, but cannot download the **complete Docker log history** directly to a file for:
- Post-flight analysis
- Troubleshooting startup issues
- Archiving complete system logs
- Sharing logs with support/developers

**Example Scenario:**
After a flight, user wants to download **all logs** including:
1. Container startup messages
2. System initialization logs
3. Complete camera SDK logs
4. Full error history
5. All debug output

Currently they must:
- SSH manually to Pi
- Run `docker logs payload-manager > logfile.log`
- Transfer file separately
- Or settle for partial logs via UI

---

## Proposed Solution

### Feature: "Download Docker Logs..." Button

Add a second download option in the Log Inspector tab:

**UI Layout:**
```
Bottom Controls:
[Clear Display]  [Save to File...]  [Download Log File...]  [Download Docker Logs...]  [Copy All]
                                     ↑ Existing              ↑ NEW
```

**Functionality:**
1. User clicks "Download Docker Logs..." button
2. Dialog shows options:
   - ☑ Include startup messages (header)
   - ☑ Include stderr output
   - ☑ Full history (or specify time range)
   - Tail limit: [All] or [Last ____ lines]
3. SSH executes: `docker logs payload-manager 2>&1`
4. Streams output to temp file on Pi
5. Downloads via SFTP to PC
6. Cleans up temp file on Pi

---

## Technical Implementation

### Method 1: Stream Docker Logs via SSH (Recommended)

**Advantages:**
- No temp files needed on Pi
- Memory efficient for large logs
- Real-time progress tracking
- Clean implementation

**Implementation:**
```python
def download_docker_logs(self):
    """Download complete Docker container logs"""
    # 1. SSH command to get logs
    command = "docker logs payload-manager 2>&1"

    # 2. Execute and stream to local file
    exit_code, stdout, stderr = self.ssh_client.execute_command(
        command,
        timeout=120  # Allow time for large logs
    )

    # 3. Save directly to user-chosen location
    filepath = filedialog.asksaveasfilename(
        title="Save Docker Logs",
        initialfile=f"docker_logs_payload_manager_{timestamp}.log",
        defaultextension=".log"
    )

    # 4. Write logs to file
    with open(filepath, 'w') as f:
        f.write(stdout)
        if stderr:
            f.write("\n\n=== STDERR ===\n")
            f.write(stderr)
```

### Method 2: Temp File + SFTP

**Advantages:**
- Can resume if interrupted
- Better for very large logs
- Uses existing SFTP infrastructure

**Implementation:**
```python
def download_docker_logs_sftp(self):
    """Download Docker logs via temp file"""
    # 1. Create temp file on Pi
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_file = f"/tmp/docker_logs_{timestamp}.log"

    # 2. Export logs to temp file
    command = f"docker logs payload-manager > {temp_file} 2>&1"
    self.ssh_client.execute_command(command)

    # 3. Download via SFTP
    self.ssh_client.download_file(
        remote_path=temp_file,
        local_path=local_filepath,
        progress_callback=self._update_progress
    )

    # 4. Cleanup temp file
    self.ssh_client.execute_command(f"rm {temp_file}")
```

---

## User Interface Design

### Option A: Separate Button (Recommended)

**Log Inspector Bottom Bar:**
```
┌─────────────────────────────────────────────────────────────────┐
│ [Clear Display] [Save Displayed...] [▼ Download ▼] [Copy All]   │
│                                                                   │
│ Dropdown Menu:                                                    │
│   • Download Application Log File... (New!)                       │
│   • Download Docker Logs...          (New!)                       │
│   • Download Both...                 (Future)                     │
└─────────────────────────────────────────────────────────────────┘
```

### Option B: Two Separate Buttons

**Log Inspector Bottom Bar:**
```
┌─────────────────────────────────────────────────────────────────┐
│ [Clear] [Save Displayed...] [📄 App Log] [🐳 Docker Logs] [Copy]│
└─────────────────────────────────────────────────────────────────┘
```

### Download Options Dialog

When "Download Docker Logs..." clicked:
```
┌─────────────────────────────────────────────────┐
│  Download Docker Logs                           │
├─────────────────────────────────────────────────┤
│  Container: payload-manager                     │
│                                                  │
│  Options:                                        │
│  ☑ Include startup banner                       │
│  ☑ Include stderr output                        │
│  ☐ Tail only (last 10000 lines)                 │
│  ☑ Full history                                  │
│                                                  │
│  Time Range (optional):                          │
│  Since: [________________]  (e.g., 5m, 1h, 24h) │
│                                                  │
│  Estimated size: ~47k lines, ~15 MB             │
│                                                  │
│       [Cancel]              [Download]           │
└─────────────────────────────────────────────────┘
```

---

## File Format & Naming

### Default Filename Format:
```
docker_logs_payload_manager_YYYYMMDD_HHMMSS.log
```

**Examples:**
- `docker_logs_payload_manager_20251105_143022.log`
- `docker_logs_payload_manager_flight_site_alpha.log` (user renamed)

### File Header (Optional):
```
========================================
DPM Docker Container Logs
========================================
Container:    payload-manager
Downloaded:   2025-11-05 14:30:22
Source:       dpm@192.168.144.10
Command:      docker logs payload-manager
Lines:        47,627
Size:         15.2 MB
========================================

[Logs begin below]
```

---

## Implementation Checklist

### Phase 1: Basic Implementation
- [ ] Add `download_docker_logs()` method to `SSHClient` class
- [ ] Add "Download Docker Logs..." button to Log Inspector tab
- [ ] Implement file save dialog with default naming
- [ ] Execute `docker logs payload-manager 2>&1` via SSH
- [ ] Save output to user-chosen file
- [ ] Show success/error notifications
- [ ] Update UI with download progress indication

### Phase 2: Options & Filtering
- [ ] Add download options dialog
- [ ] Implement tail limit option (last N lines)
- [ ] Implement time range filtering (`--since`, `--until`)
- [ ] Add include/exclude stderr toggle
- [ ] Show estimated log size before download

### Phase 3: Progress & UX
- [ ] Add progress bar for large downloads
- [ ] Show line count and size estimation
- [ ] Add cancel button during download
- [ ] Background download (non-blocking UI)
- [ ] Toast notification when complete

### Phase 4: Advanced Features
- [ ] Download both logs (app + Docker) in one click
- [ ] Automatic log archiving with flight metadata
- [ ] Compare logs between different flights
- [ ] Log parsing and error highlighting

---

## Testing Requirements

### Unit Tests:
- [ ] SSH command construction with various options
- [ ] File naming with timestamps
- [ ] Error handling for SSH failures
- [ ] Cleanup of temp files on failure

### Integration Tests:
- [ ] Download small log (< 1 MB)
- [ ] Download large log (> 100 MB)
- [ ] Download with tail limit
- [ ] Download with time filtering
- [ ] Cancel during download
- [ ] Handle SSH disconnection during download

### User Acceptance Tests:
- [ ] Download logs after real flight
- [ ] Verify all startup messages included
- [ ] Verify stderr output included
- [ ] Verify file is complete and readable
- [ ] Compare Docker log download vs manual SSH download

---

## Dependencies

### Required:
- ✅ SSH connection to Air-Side Pi
- ✅ Docker container running
- ✅ Paramiko SSH client (already available)
- ✅ File system write permissions on Windows PC

### Optional:
- Progress tracking for large files
- Async download to prevent UI blocking

---

## Benefits

### For Users:
1. **One-click complete log download** - No manual SSH required
2. **Post-flight analysis** - Download all logs after landing
3. **Troubleshooting** - Get complete system logs easily
4. **Archiving** - Save logs per-flight for records
5. **Support** - Easy to share logs with developers

### For Developers:
1. **Better diagnostics** - Users can provide complete logs
2. **Reproduce issues** - Full log history available
3. **Performance analysis** - See complete system behavior
4. **Testing** - Verify log completeness after changes

---

## Comparison: Application Log vs Docker Log

| Feature | Application Log File | Docker Logs |
|---------|---------------------|-------------|
| **What it contains** | Runtime application logs | All container output |
| **Includes startup** | ❌ No (starts after init) | ✅ Yes (from container start) |
| **Includes SDK logs** | ✅ Yes | ✅ Yes |
| **Container metadata** | ❌ No | ✅ Yes (timestamps, IDs) |
| **Size** | Smaller (~5-50 MB) | Larger (~15-200 MB) |
| **Best for** | Runtime debugging | Complete system view |
| **Download method** | SFTP file transfer | SSH command streaming |

**Recommendation:** Provide both options, let users choose based on needs.

---

## Edge Cases & Error Handling

### Large Log Files (> 100 MB):
- Show warning before download
- Implement streaming download with progress bar
- Consider compression option

### Container Not Running:
- Show helpful error: "Container 'payload-manager' is not running"
- Suggest checking container status first

### Disk Space Issues:
- Check available disk space before download
- Estimate log size and warn if insufficient space

### SSH Timeout:
- Increase timeout for large log downloads
- Allow user to retry or cancel

### Incomplete Download:
- Detect partial downloads
- Offer to retry
- Clean up incomplete files

---

## Future Enhancements (Post v1.8.0)

### v1.9.0 or Later:
- [ ] **Log filtering by level** (INFO, WARN, ERROR only)
- [ ] **Log compression** (download as .log.gz)
- [ ] **Multi-container support** (if more containers added)
- [ ] **Automatic log rotation** detection and download
- [ ] **Log diff tool** (compare logs between flights)
- [ ] **Real-time log streaming** to file (live download)
- [ ] **Log parsing** with structured view
- [ ] **Export to JSON/CSV** for analysis
- [ ] **Integration with flight log database**

---

## Related Issues

- Issue #5: ??? (Unknown - v1.6.0 features)
- Related to Air-Side logging fix (commit 10ba985)
- Related to SFTP implementation (commit 33aa548)

---

## Success Criteria

**This issue is complete when:**
1. ✅ "Download Docker Logs..." button exists in Log Inspector
2. ✅ Button downloads complete Docker logs via SSH
3. ✅ Logs include startup messages and all output
4. ✅ Download works for logs up to 200 MB
5. ✅ User can choose filename and location
6. ✅ Success/error notifications displayed
7. ✅ Documentation updated in user guide
8. ✅ Feature tested with real flight logs

---

## Implementation Notes

**Code Location:**
- `SystemTools/network/ssh_client.py` - Add download method
- `SystemTools/gui/tab_logs.py` - Add UI button and handler

**Estimated Effort:** 4-6 hours
- Basic implementation: 2 hours
- Options dialog: 1 hour
- Progress tracking: 1 hour
- Testing & polish: 1-2 hours

**Recommended Approach:**
Start with **Method 1 (SSH streaming)** for simplicity, add **Method 2 (SFTP)** later if needed for resume capability.

---

## Questions for Review

1. Should we combine app log + Docker log into one download action?
2. Do we need log compression for large files?
3. Should there be a "Quick Download" (last 1000 lines) option?
4. Do we need to handle Docker log rotation?
5. Should logs be automatically archived per-flight?

---

**Issue Created By:** Claude Code
**Review Status:** Awaiting approval
**Target Milestone:** v1.8.0 Release
