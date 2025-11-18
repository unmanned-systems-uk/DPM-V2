# Docker Image ID Display Feature

**Date:** 2025-11-17
**WHO:** CC-Dev-Tools
**Status:** ✅ Implementation Complete | Ready for Testing

---

## Overview

Enhanced the File Browser's Docker Logs tab to display Docker Image IDs in a separate column. This helps track which version of the payload-manager container is running when viewing logs.

---

## What Changed

### 1. New Column: "Image ID"

The Docker Logs tab TreeView now has **4 columns** (previously 3):

| Column | Description | Width |
|--------|-------------|-------|
| Log File | Filename or log entry name | 250px |
| Size (KB) | File size in kilobytes | 80px |
| Source | Log source type | 150px |
| **Image ID** | **Docker image ID (12 chars)** | **120px** |

### 2. Image ID Display by Source

| Log Source | Image ID Displayed | Example |
|------------|-------------------|---------|
| **Container Logs** | ✅ Yes - from `docker inspect` | `a1b2c3d4e5f6` |
| **Docker Output** | ✅ Yes - from `docker inspect` | `a1b2c3d4e5f6` |
| **Host Logs** | ❌ No - shows "N/A" | `N/A` |
| **System Logs** | ❌ No - shows "N/A" | `N/A` |

---

## Technical Implementation

### Files Modified

**gui/tab_file_browser.py** - Enhanced with Image ID column

#### Changes Made:

1. **Added 4th column to TreeView** (line 276):
   ```python
   columns = ("name", "size", "source", "image_id")
   ```

2. **Added Image ID column heading** (line 289):
   ```python
   self.logs_tree.heading("image_id", text="Image ID", ...)
   ```

3. **New helper method `_get_docker_image_id()`** (lines 819-842):
   ```python
   def _get_docker_image_id(self, container_name="payload-manager"):
       """Get Docker image ID for a container (shortened to 12 chars like docker ps)"""
       # Uses: docker inspect <container> --format '{{.Image}}'
       # Returns: First 12 chars of image ID (e.g., "a1b2c3d4e5f6")
   ```

4. **Updated `_load_container_logs()`** (line 856):
   - Retrieves image ID when loading container logs
   - Passes image ID to TreeView insert

5. **Updated `_load_docker_output_entry()`** (line 922):
   - Retrieves image ID when loading Docker output
   - Passes image ID to TreeView insert

6. **Updated `_load_host_logs()` and `_load_system_logs()`**:
   - Both now pass "N/A" for image_id column

---

## How It Works

### Docker Command Used

```bash
docker inspect payload-manager --format '{{.Image}}'
```

**Example output:**
```
sha256:a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456
```

### Parsing Logic

1. Execute `docker inspect` via SSH
2. Extract full image ID from output
3. Remove `sha256:` prefix if present
4. Take first 12 characters (standard Docker short ID)
5. Display in TreeView

**Example:**
- Full ID: `sha256:a1b2c3d4e5f6789012345678901234567890abcdef...`
- Displayed: `a1b2c3d4e5f6`

---

## Benefits

### For Users
✅ **Track Container Version** - See which Docker image version is running
✅ **Debugging** - Correlate logs with specific container builds
✅ **Deployment Verification** - Confirm correct image is deployed
✅ **Troubleshooting** - Identify if issue is image-specific

### For Development
✅ **Clean Implementation** - Single helper method used by both sources
✅ **Error Handling** - Returns "N/A" if unable to retrieve ID
✅ **Consistent Format** - Uses standard Docker 12-char short ID
✅ **Non-Breaking** - Existing functionality unchanged

---

## Testing

### Unit Tests

**Test Script:** `test_docker_image_id.py`

**Results:**
```
✅ ALL TESTS PASSED

Test 1: FileBrowserTab import - PASSED
Test 2: TreeView column structure - PASSED
  - Columns: ('name', 'size', 'source', 'image_id')
  - Image ID column present
  - Column width: 120px
Test 3: _get_docker_image_id() method exists - PASSED
Test 4: Image ID parsing logic - PASSED
  - sha256:abcdef... → abcdef123456 ✓
  - Short IDs handled correctly ✓
```

### Integration Testing

⏳ **Pending** - Requires live Air-Side connection

**Test Plan:**
1. Launch DPM Management System
2. Go to File Browser → Docker Logs tab
3. Connect to Air-Side (10.0.1.53)
4. Select "Container Logs" source
5. Click Refresh
6. **Verify:** Image ID column shows 12-character ID (e.g., `a1b2c3d4e5f6`)
7. Select "Docker Output" source
8. Click Refresh
9. **Verify:** Image ID column shows same ID
10. Select "Host Logs" source
11. Click Refresh
12. **Verify:** Image ID column shows "N/A"

---

## Example UI Display

### Container Logs Source:
```
┌────────────────────────────────────────────────────────────────────┐
│ Log File            │ Size (KB) │ Source              │ Image ID   │
├────────────────────────────────────────────────────────────────────┤
│ air-side.jsonl      │ 1024.5    │ Container (docker)  │ a1b2c3d4e5f6│
│ air-side.1.jsonl    │ 2048.7    │ Container (docker)  │ a1b2c3d4e5f6│
│ air-side.2.jsonl    │ 1536.2    │ Container (docker)  │ a1b2c3d4e5f6│
└────────────────────────────────────────────────────────────────────┘
```

### Host Logs Source:
```
┌────────────────────────────────────────────────────────────────────┐
│ Log File            │ Size (KB) │ Source              │ Image ID   │
├────────────────────────────────────────────────────────────────────┤
│ payload_manager.log │ 512.3     │ Host (SFTP)         │ N/A        │
│ system.log          │ 128.9     │ Host (SFTP)         │ N/A        │
└────────────────────────────────────────────────────────────────────┘
```

---

## Error Handling

### Scenarios

1. **Container not running:**
   - Image ID retrieval fails
   - Returns "N/A"
   - Log warning: "Failed to get Docker image ID"

2. **SSH connection issue:**
   - Command execution fails
   - Returns "N/A"
   - Graceful degradation (logs still load)

3. **Invalid docker inspect output:**
   - Parsing fails
   - Returns "N/A"
   - No impact on log browsing

---

## Use Cases

### Use Case 1: Verify Deployment

**Scenario:** After deploying new payload-manager image, verify it's running.

**Steps:**
1. Open File Browser → Docker Logs
2. Connect to Air-Side
3. Select "Container Logs"
4. Click Refresh
5. Check Image ID column
6. Compare with expected image ID from build/deployment

### Use Case 2: Debug Image-Specific Issue

**Scenario:** Camera disconnect issue reported with specific Docker image version.

**Steps:**
1. Download logs using File Browser
2. Note Image ID from column
3. Check if Image ID matches problematic version
4. Import logs into Performance Analytics for analysis
5. Correlate issue with specific container build

### Use Case 3: Track Image History

**Scenario:** Review which images were running over time.

**Steps:**
1. Download historical logs from multiple days
2. Check Image ID for each log file
3. Identify when image was updated
4. Correlate performance changes with image updates

---

## Known Limitations

1. **12-Character ID Only** - Full sha256 hash not displayed (standard Docker behavior)
2. **Single Container** - Assumes "payload-manager" container name
3. **SSH Required** - Image ID retrieved via SSH command (requires connection)
4. **No Image Tag** - Only shows ID, not tag name (e.g., "latest", "v1.2.3")

---

## Future Enhancements

Potential future improvements:

- [ ] Add tooltip with full sha256 image hash on hover
- [ ] Display image tag name in addition to ID
- [ ] Support multiple containers (dropdown selector)
- [ ] Cache image ID to reduce SSH calls
- [ ] Add "Copy Image ID" context menu option
- [ ] Show image build date/time

---

## Related Issues

- Issue #136 - File Browser Sub-Tabs (parent feature)
- Issue #138 - Analytics Log Import (uses downloaded logs)
- Issue #127, #102, #129 - Camera issues (debuggable with version tracking)

---

## Success Criteria ✅

- ✅ Image ID column added to TreeView
- ✅ Column displays for Container Logs source
- ✅ Column displays for Docker Output source
- ✅ Column shows "N/A" for Host/System Logs
- ✅ Image ID shortened to 12 characters
- ✅ Helper method `_get_docker_image_id()` implemented
- ✅ Error handling graceful (returns "N/A" on failure)
- ✅ Unit tests pass
- ⏳ Integration test pending (live Air-Side)

---

## Commit Message

```
[SYSTEMTOOLS][ENHANCEMENT] Add Docker Image ID column to File Browser Docker Logs tab

- Add 4th column "Image ID" to Docker Logs TreeView
- Implement _get_docker_image_id() helper method
- Display 12-char Docker image ID for Container Logs and Docker Output sources
- Show "N/A" for Host Logs and System Logs (non-Docker sources)
- Add unit test test_docker_image_id.py (all tests pass)
- Helps track payload-manager container version when viewing logs

Related: Issue #136 (File Browser Sub-Tabs)
```

---

**WHO:** CC-Dev-Tools
**Date:** 2025-11-17
**Files Modified:** 1 (gui/tab_file_browser.py)
**Files Created:** 2 (test_docker_image_id.py, DOCKER_IMAGE_ID_FEATURE.md)
**Lines Added:** ~50
**Status:** ✅ Ready for Testing with Live Air-Side
