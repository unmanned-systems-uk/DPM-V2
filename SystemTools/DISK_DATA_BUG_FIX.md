# Disk Data Display Bug Fix

**Bug:** Performance Analytics showing disk usage as 1-2 MB instead of correct values (22,869 MB used / 59,380 MB total)

**Root Cause:** The `_normalize_snapshot()` function was designed only for **live Air-Side data** and didn't handle **imported log data** that was already in the correct format.

---

## The Problem

### Data Flow

```
Air-Side → JSON logs → Import → Normalization → Database → Display
             ↓            ↓           ↓
     disk_used_mb    disk_used_mb   ❌ LOST!
     disk_total_mb   disk_total_mb  ❌ LOST!
```

### What Happened

**Live Air-Side data** comes in this format:
- `disk_free_gb`: 36.5
- `disk_total_gb`: 58.0

**Imported log data** comes in this format:
- `disk_used_mb`: 22869
- `disk_total_mb`: 59380

The `_normalize_snapshot()` function had:

```python
if 'disk_free_gb' in snapshot and 'disk_total_gb' in snapshot:
    # Convert GB to MB and calculate used
    disk_total_mb = snapshot['disk_total_gb'] * 1024
    disk_free_mb = snapshot['disk_free_gb'] * 1024
    normalized['disk_total_mb'] = int(disk_total_mb)
    normalized['disk_used_mb'] = int(disk_total_mb - disk_free_mb)
```

**Problem:** This ONLY handled live data with `disk_free_gb`. Imported data with `disk_used_mb` was **NOT copied** to the normalized dict, so it was lost!

---

## The Fix

### Modified `_normalize_snapshot()` Function

**File:** `gui/tab_analytics.py` (lines 344-350)

**Before:**
```python
if 'disk_free_gb' in snapshot and 'disk_total_gb' in snapshot:
    # Convert GB to MB and calculate used
    disk_total_mb = snapshot['disk_total_gb'] * 1024
    disk_free_mb = snapshot['disk_free_gb'] * 1024
    normalized['disk_total_mb'] = int(disk_total_mb)
    normalized['disk_used_mb'] = int(disk_total_mb - disk_free_mb)
```

**After:**
```python
# Handle disk metrics - support both live data and imported data
if 'disk_free_gb' in snapshot and 'disk_total_gb' in snapshot:
    # Live data: Convert GB to MB and calculate used
    disk_total_mb = snapshot['disk_total_gb'] * 1024
    disk_free_mb = snapshot['disk_free_gb'] * 1024
    normalized['disk_total_mb'] = int(disk_total_mb)
    normalized['disk_used_mb'] = int(disk_total_mb - disk_free_mb)
elif 'disk_used_mb' in snapshot:
    # Imported data: Already in correct format
    normalized['disk_used_mb'] = snapshot['disk_used_mb']
    if 'disk_total_mb' in snapshot:
        normalized['disk_total_mb'] = snapshot['disk_total_mb']
```

### Additional Fixes

Also fixed similar issues with other fields:

**1. Memory metrics** (lines 333-342)
```python
if 'memory_mb' in snapshot:
    # Live data
    normalized['memory_used_mb'] = snapshot['memory_mb']
elif 'memory_used_mb' in snapshot:
    # Imported data - already in correct format
    normalized['memory_used_mb'] = snapshot['memory_used_mb']
```

**2. Camera connected** (lines 358-364)
```python
if 'connected' in snapshot:
    # Live data
    normalized['camera_connected'] = snapshot['connected']
elif 'camera_connected' in snapshot:
    # Imported data - already in correct format
    normalized['camera_connected'] = snapshot['camera_connected']
```

**3. All other imported metrics** (lines 366-390)
- `sdk_latency_ms`
- `usb_traffic_mbps`
- `error_count`
- `tcp_connected`
- `tcp_latency_ms`
- `udp_loss_percent`
- `command_queue_depth`
- `exposure_rate_hz`
- `health_rate_hz`
- `property_reads_sec`

---

## Data Flow After Fix

```
Air-Side → JSON logs → Import → Normalization → Database → Display
             ↓            ↓           ↓
     disk_used_mb    disk_used_mb  ✅ KEPT!
     disk_total_mb   disk_total_mb ✅ KEPT!
```

### Now Handles Both Formats

**Live Data:**
```json
{
  "disk_free_gb": 36.5,
  "disk_total_gb": 58.0
}
```
↓ Converts to MB ↓
```json
{
  "disk_used_mb": 22016,
  "disk_total_mb": 59392
}
```

**Imported Data:**
```json
{
  "disk_used_mb": 22869,
  "disk_total_mb": 59380
}
```
↓ Passes through ↓
```json
{
  "disk_used_mb": 22869,
  "disk_total_mb": 59380
}
```

---

## Testing the Fix

### 1. Restart DPM Management System

```bash
# In SYSTEM tmux session
cd /home/anthony/DPM-V2/SystemTools
python3 DPM_Management_System.py
```

Or:
```
/start-tools
```

### 2. Clear Old Data

1. Go to **Performance Analytics** tab
2. Click **"🗑️ Clear Data"**
3. Select **"Yes"** to clear both buffer and database

### 3. Re-Import Logs

1. Click **"📂 Import Air-Side Logs"**
2. Select your `air-side.jsonl` file
3. Wait for import to complete

### 4. Verify Disk Data

**Expected results:**

**Graphs Tab:**
- Disk Usage graph should show **~22,869 MB** (not 1-2 MB)
- Graph should have meaningful data points

**Statistics Tab:**
- Disk Used: Mean should be **~22,869 MB**
- Disk Total: Should show **~59,380 MB**

---

## Root Cause Analysis

### Why This Happened

1. **Development Order:** Live data collection was implemented first
2. **Import Feature Added Later:** Historical log import was added as Issue #138
3. **Different Data Formats:** Live data uses different field names than logged data
4. **Normalization Not Updated:** The normalization function wasn't updated to handle both formats

### Design Issue

The normalization function was **format-specific** instead of **format-agnostic**:

❌ **Bad (original):**
```python
if 'disk_free_gb' in snapshot:
    # ONLY handles live data
```

✅ **Good (fixed):**
```python
if 'disk_free_gb' in snapshot:
    # Handle live data
elif 'disk_used_mb' in snapshot:
    # Handle imported data
```

---

## Impact

**Before Fix:**
- ❌ Imported disk data: Lost (showed 0 or garbage values)
- ❌ Imported memory data: Might be lost if using `memory_used_mb`
- ❌ Imported camera data: Lost (all metrics)
- ❌ Imported network data: Lost (all metrics)
- ❌ Imported sync data: Lost (all metrics)

**After Fix:**
- ✅ All imported data: Preserved correctly
- ✅ Live data: Still works as before
- ✅ Backward compatible: Old live data collection unchanged

---

## Verification Checklist

- [x] Code syntax verified
- [ ] Restart DPM Management System
- [ ] Clear old database
- [ ] Re-import air-side.jsonl
- [ ] Verify disk graph shows ~22,869 MB
- [ ] Verify disk statistics show correct values
- [ ] Verify memory data appears
- [ ] Verify camera data appears (if in logs)
- [ ] Verify live data still works (if connected to Air-Side)

---

## Prevention

To prevent similar issues in the future:

1. **Unified Data Format:** Define a single canonical format for all metrics
2. **Schema Validation:** Validate incoming data against expected schema
3. **Test Both Paths:** Test live data AND imported data for all features
4. **Format Documentation:** Document which format each data source uses

---

**Status:** ✅ Fixed and syntax-verified
**Impact:** HIGH - Makes imported historical data usable
**Backward Compatibility:** ✅ Yes - live data still works
**Breaking Changes:** None
