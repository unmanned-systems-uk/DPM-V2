# Performance Analytics - Import Display Fix

**Issue:** Data imported from historical log files (air-side.jsonl) was not showing in graphs or Statistics tab, despite successful import into database (858 snapshots confirmed).

**Root Cause:** The graphs and Statistics tab pull data from `self.data_buffer` (in-memory), but imported data only went into the database. The buffer was never populated with historical data.

**Solution:** Added `_load_data_from_database()` method that loads recent snapshots from database into the buffer after import.

---

## Changes Made

**File:** `gui/tab_analytics.py`

### 1. Modified `_manual_refresh()` (Lines 682-691)

**Before:**
```python
def _manual_refresh(self):
    """Manual refresh button handler"""
    logger.debug("Manual refresh triggered")
    self._update_graphs()
    self._update_statistics()
    self._update_status()
```

**After:**
```python
def _manual_refresh(self):
    """Manual refresh button handler"""
    logger.debug("Manual refresh triggered")

    # Load data from database into buffer for graphing
    self._load_data_from_database()

    self._update_graphs()
    self._update_statistics()
    self._update_status()
```

### 2. Added `_load_data_from_database()` (Lines 693-721)

```python
def _load_data_from_database(self):
    """Load recent data from database into data_buffer for graphing

    This is called after importing historical logs to populate the buffer
    with database content so graphs can display the imported data.
    """
    try:
        # Query latest snapshots (up to buffer size)
        snapshots = self.db.query_latest(limit=self.max_buffer_size)

        if not snapshots:
            logger.debug("No data in database to load")
            return

        # Clear current buffer
        self.data_buffer.clear()

        # Add snapshots to buffer (reverse order - oldest first)
        for snapshot in reversed(snapshots):
            # Convert timestamp string to datetime if needed
            if isinstance(snapshot.get('timestamp'), str):
                snapshot['timestamp'] = datetime.fromisoformat(snapshot['timestamp'].replace('Z', '+00:00'))

            self.data_buffer.append(snapshot)

        logger.info(f"Loaded {len(self.data_buffer)} snapshots from database into buffer")

    except Exception as e:
        logger.error(f"Failed to load data from database: {e}")
```

---

## How It Works

### Data Flow - Before Fix

```
Import air-side.jsonl
    ↓
Parse 858 snapshots
    ↓
Insert into DATABASE ✅
    ↓
(data_buffer remains EMPTY ❌)
    ↓
Graphs query data_buffer
    ↓
NO DATA TO DISPLAY ❌
```

### Data Flow - After Fix

```
Import air-side.jsonl
    ↓
Parse 858 snapshots
    ↓
Insert into DATABASE ✅
    ↓
Call _manual_refresh()
    ↓
_load_data_from_database()
    ↓
Query database.query_latest(720)
    ↓
Load into data_buffer ✅
    ↓
Graphs query data_buffer
    ↓
DATA DISPLAYED ✅
```

---

## Usage After Fix

### Steps to View Imported Data

1. **Import historical logs** (File Browser → Download logs → Performance Analytics → Import)
2. **Click "Refresh" button** in Performance Analytics tab
   - This triggers `_manual_refresh()`
   - Which calls `_load_data_from_database()`
   - Which loads the last 720 snapshots (1 hour @ 5Hz) into buffer
3. **Data appears** in both Graphs and Statistics tabs!

### Automatic Refresh on Import

The import process already calls `_manual_refresh()` automatically (line 891 in tab_analytics.py):

```python
# Refresh graphs and stats
self._manual_refresh()  # ← This now loads data from database!
```

So you should see data **immediately after import completes**, without needing to click Refresh manually.

---

## Technical Details

### Buffer Size

- `self.max_buffer_size = 720` (line 68 in tab_analytics.py)
- This means 720 snapshots = 1 hour of data at 5 Hz sampling rate
- `query_latest(720)` loads the most recent 720 snapshots from database

### Timestamp Handling

The fix handles both timestamp formats:
- **String format:** `"2025-11-18T00:27:11.123Z"` (from database)
- **datetime format:** Already converted datetime objects

Conversion happens automatically on line 714:
```python
if isinstance(snapshot.get('timestamp'), str):
    snapshot['timestamp'] = datetime.fromisoformat(snapshot['timestamp'].replace('Z', '+00:00'))
```

### Memory Management

- Old buffer data is cleared: `self.data_buffer.clear()` (line 708)
- New data loaded in correct order: `reversed(snapshots)` ensures oldest-first
- Buffer is a `deque` with `maxlen=720`, so it automatically discards old data

---

## Testing Checklist

- [x] Code syntax verified
- [ ] Import 858 snapshots from air-side.jsonl
- [ ] Verify graphs populate after import
- [ ] Verify Statistics tab shows data
- [ ] Check that "Last update" status shows correct time
- [ ] Verify manual Refresh button works
- [ ] Check Time Window selector (1m, 5m, 30m, 1h, All) works
- [ ] Verify no errors in console/logs

---

## Expected Behavior

After importing 858 snapshots:

1. **Graphs Tab:**
   - CPU Usage graph shows data points
   - Memory Usage graph shows data points
   - Disk Usage graph shows data points
   - Network Traffic graph shows RX/TX data
   - Camera Connection graph shows connection state

2. **Statistics Tab:**
   - Shows "Data Points: 720" (or less if fewer imported)
   - Displays statistical summary for each metric:
     - Mean, Median, Std Dev
     - Min, Max, Range
     - Percentiles (P50, P75, P90, P95, P99)
   - Shows "Last updated" timestamp

3. **Status Bar:**
   - Shows "Buffer: 720 snapshots" (or actual count)
   - Shows "Last update: Xs ago" based on newest snapshot

---

## Troubleshooting

### If data still doesn't appear:

1. **Check database has data:**
   - Look for log message: "Imported 858 health snapshots from 1 files"
   - Database file: `data/performance.db`

2. **Check buffer loaded:**
   - Look for log message: "Loaded XXX snapshots from database into buffer"
   - Should show immediately after import

3. **Check time window:**
   - Try selecting "All Time" from Time Window dropdown
   - Your imported data might be older than current 1-hour window

4. **Manual refresh:**
   - Click the "🔄 Refresh" button
   - This explicitly calls `_load_data_from_database()`

5. **Check for errors:**
   - Look in console/logs for any database query errors
   - Check file permissions on `data/performance.db`

---

## Future Enhancements

1. **Smart Time Window Selection:**
   - Automatically adjust time window to match imported data range
   - If imported data is from yesterday, auto-select appropriate window

2. **Partial Buffer Loading:**
   - Only load data matching current time window
   - More efficient for large databases

3. **Background Loading:**
   - Load database data in background thread
   - Show progress indicator for large datasets

4. **Data Range Selector:**
   - Allow user to select specific date/time range from database
   - Useful for analyzing specific incidents

---

**Status:** ✅ Fix complete and syntax-verified
**Impact:** High - enables viewing of imported historical data
**Testing Required:** Import and verify graphs populate
