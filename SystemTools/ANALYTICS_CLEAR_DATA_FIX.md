# Performance Analytics - Clear Data on Open Fix

**Issue:** When opening Performance Analytics tab, old data from previous sessions appears in graphs and statistics, even though no new data has been collected.

**User Request:** "We need a clear data on open I think"

**Root Cause:** The database persists between app runs, and the refresh mechanism was loading all database data into the buffer, even old/stale data from previous sessions.

**Solution:**
1. Added **"🗑️ Clear Data"** button for manual data clearing
2. Modified **"Refresh Now"** to NOT auto-load database data
3. Data only loads from database **after importing historical logs**
4. Tab starts with **empty buffer** by default (fresh state)

---

## Changes Made

### 1. Added Clear Data Button (gui/tab_analytics.py, Lines 138-143)

```python
# Clear data button
ttk.Button(
    controls_frame,
    text="🗑️ Clear Data",
    command=self._clear_data
).pack(side=tk.LEFT, padx=5)
```

### 2. Modified Manual Refresh (Lines 689-694)

**Before:**
```python
def _manual_refresh(self):
    """Manual refresh button handler"""
    logger.debug("Manual refresh triggered")

    # Load data from database into buffer for graphing
    self._load_data_from_database()  # ← AUTO-LOADED OLD DATA!

    self._update_graphs()
    self._update_statistics()
    self._update_status()
```

**After:**
```python
def _manual_refresh(self):
    """Manual refresh button handler - refresh display without loading from database"""
    logger.debug("Manual refresh triggered")
    self._update_graphs()
    self._update_statistics()
    self._update_status()
```

**Key Change:** Removed auto-load from database. Now only refreshes the display with current buffer data.

### 3. Added Clear Data Function (Lines 696-730)

```python
def _clear_data(self):
    """Clear all data from buffer and optionally from database"""
    result = messagebox.askyesnocancel(
        "Clear Data",
        "Clear data from:\n\n"
        "• Yes = Clear buffer AND database (permanent)\n"
        "• No = Clear buffer only (temporary)\n"
        "• Cancel = Don't clear anything",
        icon='question'
    )

    if result is None:  # Cancel
        return

    # Clear buffer
    self.data_buffer.clear()
    logger.info("Cleared data buffer")

    # Clear database if user chose "Yes"
    if result is True:
        try:
            count = self.db.clear_all_snapshots()
            logger.info(f"Cleared {count} snapshots from database")
            messagebox.showinfo("Data Cleared", f"Cleared buffer and {count} snapshots from database")
        except Exception as e:
            logger.error(f"Failed to clear database: {e}")
            messagebox.showerror("Error", f"Failed to clear database:\n{e}")
    else:
        messagebox.showinfo("Data Cleared", "Cleared buffer only")

    # Refresh UI to show empty state
    self._update_graphs()
    self._update_statistics()
    self._update_status()
    self._update_db_status()
```

**Features:**
- **Three options:** Yes (buffer + database), No (buffer only), Cancel (do nothing)
- **Smart clearing:** Can preserve database while clearing display
- **Immediate feedback:** Shows count of deleted snapshots
- **UI refresh:** Updates graphs to show empty state

### 4. Updated Import Process (Lines 963-970)

**Before:**
```python
# Refresh graphs and stats
self._manual_refresh()  # ← This didn't load database data anymore!
```

**After:**
```python
# Load imported data from database into buffer and refresh display
self._load_data_from_database()  # ← Explicitly load after import
self._update_graphs()
self._update_statistics()
self._update_status()
```

**Key Change:** Import process now **explicitly** loads database data, ensuring imported logs appear in graphs.

### 5. Added Database Clear Method (analytics/data_storage.py, Lines 317-341)

```python
def clear_all_snapshots(self) -> int:
    """
    Clear all health snapshots from the database

    Returns:
        Number of snapshots deleted
    """
    with self.lock:
        try:
            cursor = self.conn.cursor()

            # Get count before deleting
            cursor.execute('SELECT COUNT(*) FROM health_snapshots')
            count = cursor.fetchone()[0]

            # Delete all snapshots
            cursor.execute('DELETE FROM health_snapshots')
            self.conn.commit()

            logger.info(f"Cleared {count} snapshots from database")
            return count

        except Exception as e:
            logger.error(f"Failed to clear snapshots: {e}")
            return 0
```

---

## New Behavior

### On Tab Open (Fresh State)

```
Performance Analytics tab opens
    ↓
Buffer is EMPTY (deque created with maxlen=720)
    ↓
Graphs show "No data available"
    ↓
Statistics show "No data available for current time window"
    ↓
Status shows "Waiting for data..."
```

### When Live Data Arrives

```
UDP/TCP data received
    ↓
update_with_snapshot() called
    ↓
Data added to buffer
    ↓
Auto-refresh updates graphs (if enabled)
    ↓
Graphs show LIVE data only
```

### When Importing Historical Logs

```
User clicks "📂 Import Air-Side Logs"
    ↓
Selects air-side.jsonl files
    ↓
Data parsed and inserted into DATABASE
    ↓
_load_data_from_database() called explicitly
    ↓
Last 720 snapshots loaded into buffer
    ↓
Graphs populate with imported data
```

### When Clicking "Refresh Now"

```
User clicks "Refresh Now"
    ↓
_manual_refresh() called
    ↓
Graphs refresh with CURRENT buffer data
    ↓
NO database loading
    ↓
Only displays what's already in buffer
```

### When Clicking "Clear Data"

```
User clicks "🗑️ Clear Data"
    ↓
Dialog appears with 3 options
    ↓
[YES] Clear buffer + database (permanent)
[NO] Clear buffer only (temporary)
[CANCEL] Do nothing
    ↓
Buffer cleared immediately
    ↓
Database cleared if YES selected
    ↓
Graphs update to show empty state
```

---

## Usage Scenarios

### Scenario 1: Fresh Start (No Old Data)

**What happens:**
1. Open Performance Analytics tab
2. See empty graphs (expected - no data yet)
3. Start receiving live data OR import logs
4. Graphs populate

**No action needed!**

### Scenario 2: Old Data Visible (Previous Session)

**What happens:**
1. Open Performance Analytics tab
2. See old data from yesterday (unwanted)

**Fix:**
1. Click **"🗑️ Clear Data"**
2. Select **"Yes"** to clear buffer + database
3. Graphs now empty and ready for new data

### Scenario 3: Testing with Imported Data

**Workflow:**
1. Click **"📂 Import Air-Side Logs"**
2. Select air-side.jsonl file
3. Wait for import to complete
4. Graphs automatically populate with imported data

**To clear after testing:**
1. Click **"🗑️ Clear Data"**
2. Select **"Yes"** to remove test data
3. Fresh slate for next test

### Scenario 4: Keep Database, Clear Display

**Use case:** Database has 7 days of history, but you want to see only new incoming data.

**Steps:**
1. Click **"🗑️ Clear Data"**
2. Select **"No"** (buffer only)
3. Display clears but database preserved
4. New live data will populate graphs
5. Can re-import from database anytime

---

## Button Locations

```
[Time Window: 5min 15min 30min 1hour] [Auto-refresh ☑] [Refresh Now] [📂 Import Air-Side Logs] [🗑️ Clear Data]
```

**Position:** Clear Data button is right after Import button for easy access.

---

## Benefits

1. **Clean Startup:** No old data confusion when opening tab
2. **User Control:** Clear data when needed, not automatic
3. **Preserve Database:** Option to keep historical data while clearing display
4. **Testing Friendly:** Easy to clear test data between sessions
5. **Explicit Loading:** Only loads database data when importing, not on every refresh

---

## Migration from Old Behavior

### Old Behavior (Problematic)

- **On open:** Empty buffer
- **On "Refresh Now":** Loaded ALL database data into buffer
- **Result:** Old sessions' data would reappear unexpectedly

### New Behavior (Fixed)

- **On open:** Empty buffer
- **On "Refresh Now":** Refreshes current buffer only
- **On import:** Explicitly loads imported data
- **On "Clear Data":** User can remove old data manually
- **Result:** Predictable, user-controlled data display

---

## Testing Checklist

- [x] Code syntax verified (both files)
- [ ] Open tab → graphs empty (no old data)
- [ ] Import logs → graphs populate
- [ ] Click "Refresh Now" → graphs update (same data)
- [ ] Click "Clear Data" → "No" → buffer clears, graphs empty
- [ ] Re-import same logs → graphs populate again
- [ ] Click "Clear Data" → "Yes" → buffer + database clear
- [ ] Check database empty (no snapshots)
- [ ] Receive live data → graphs populate with new data only

---

## Database File Location

**Path:** `data/performance.db`

**To manually check/delete:**
```bash
# Check if database exists
ls -lh /home/anthony/DPM-V2/SystemTools/data/performance.db

# Count snapshots
sqlite3 /home/anthony/DPM-V2/SystemTools/data/performance.db "SELECT COUNT(*) FROM health_snapshots;"

# Manually delete database file (nuclear option)
rm /home/anthony/DPM-V2/SystemTools/data/performance.db
```

**Note:** Deleting the database file will force recreation on next app start.

---

## Future Enhancements

1. **Auto-Clear on Startup:** Add config option to always start with empty buffer
2. **Clear Old Data Only:** Option to clear data older than X days
3. **Selective Clear:** Clear by date range or specific metrics
4. **Export Before Clear:** Prompt to save data before clearing
5. **Clear Confirmation:** Add "Are you sure?" for database clear

---

**Status:** ✅ Complete and syntax-verified
**Impact:** High - solves confusing old data display issue
**User Control:** Full control via Clear Data button
**Safe:** Three-way choice (Yes/No/Cancel) prevents accidental data loss
