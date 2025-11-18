# TCP Connect Button Fix - Air-Side Config Tab

**Issue:** User clicking "Get Config (from Air-Side)" in Air-Side Config tab gets error: "Please connect to Air-Side first. The GUI will auto-connect on startup."

**Root Cause:**
1. TCP connection required but no connect button in UI
2. Auto-connect mentioned in error message but never implemented
3. User had no way to establish TCP connection

---

## The Problem

### Required Connection

The Air-Side Config tab requires a **TCP connection** to Air-Side to:
- Get config: `system.get_config` command (line 893)
- Apply config: `system.update_config` command (line 1002)

### Check in Code

```python
# Line 883-886
if not self.tcp_client or not self.tcp_client.is_connected():
    messagebox.showerror("Not Connected", "Please connect to Air-Side first.\n\n" +
                       "The GUI will auto-connect on startup.")
    return
```

### Missing UI Elements

**Before fix:**
- ✅ TCP connection status indicator (shows "Not Connected")
- ✅ TCP connect method `connect_to_airside()` exists
- ❌ **NO TCP connect button in UI**
- ❌ **NO auto-connect on startup**

User could see "Not Connected" but had no way to connect!

---

## The Fix

### Added TCP Connect/Disconnect Buttons

**File:** `DPM_Management_System.py` (lines 230-237)

**Before:**
```python
ttk.Label(connection_frame, text="Air-Side:").pack(side=tk.LEFT, padx=5)
self.airside_connection_status = ttk.Label(connection_frame, text="Not Connected",
                                            foreground="red", font=('Arial', 9, 'bold'))
self.airside_connection_status.pack(side=tk.LEFT, padx=5)
```

**After:**
```python
ttk.Label(connection_frame, text="Air-Side TCP:").pack(side=tk.LEFT, padx=5)
self.airside_connection_status = ttk.Label(connection_frame, text="Not Connected",
                                            foreground="red", font=('Arial', 9, 'bold'))
self.airside_connection_status.pack(side=tk.LEFT, padx=5)

# TCP Connect/Disconnect buttons
ttk.Button(connection_frame, text="Connect", command=self._tcp_connect, width=10).pack(side=tk.LEFT, padx=5)
ttk.Button(connection_frame, text="Disconnect", command=self.disconnect_from_airside, width=10).pack(side=tk.LEFT, padx=2)
```

### Added Connect Button Handler

**File:** `DPM_Management_System.py` (lines 821-823)

```python
def _tcp_connect(self):
    """TCP Connect button handler - connects to Air-Side with default settings"""
    self.connect_to_airside(host="10.0.1.53", port=5000, timeout_ms=5000)
```

This wraps the existing `connect_to_airside()` method with default Air-Side connection parameters.

---

## Button Location

**Log Viewer Tab (Top Right):**

```
📊 Tri-Domain Log Aggregation Viewer          [Air-Side TCP: Not Connected] [Connect] [Disconnect]
```

The buttons are in the **Log Viewer tab** header, next to the connection status indicator.

---

## Usage Instructions

### To Use Air-Side Config Features

1. **Go to Log Viewer tab** (Tab 1)
2. **Click "Connect"** button (top right, next to "Air-Side TCP: Not Connected")
3. **Wait for connection** - status will change to "Connected to 10.0.1.53:5000" (green)
4. **Switch to Air-Side Config tab** (Tab 2)
5. **Click "📥 Get Config"** - now works!

### Connection Requirements

**Air-Side must be running:**
- TCP server listening on **10.0.1.53:5000**
- `payload-manager` container running
- Network accessible from SystemTools machine

**If connection fails:**
- Check Air-Side is powered on and running
- Verify network connection: `ping 10.0.1.53`
- Check Air-Side logs: `docker logs payload-manager`
- Ensure port 5000 is not blocked by firewall

---

## Connection vs Streaming

### TCP Connection (for Commands)

**Purpose:** Send commands to Air-Side
- Get/update configuration
- Request on-demand logs
- Send control commands

**Button:** "Connect" in Log Viewer tab
**Status:** "Air-Side TCP: Connected to 10.0.1.53:5000"

### Passive Streaming (for Logs)

**Purpose:** Receive broadcast UDP logs from Air-Side
- Real-time log viewing
- No commands sent

**Button:** "▶ Start" in Log Viewer tab
**Status:** "Passive Logging: Running"

**Note:** These are **independent**! You can:
- Stream logs WITHOUT TCP connection (passive only)
- Have TCP connection WITHOUT streaming (commands only)
- Have both at once (full functionality)

---

## What Gets Fixed

**Before Fix:**
1. User opens Air-Side Config tab
2. Clicks "Get Config"
3. Error: "Please connect to Air-Side first"
4. User confused - no connect button visible
5. Feature unusable

**After Fix:**
1. User goes to Log Viewer tab
2. Clicks "Connect" button
3. Connection established
4. Status shows "Connected" (green)
5. User goes to Air-Side Config tab
6. Clicks "Get Config"
7. ✅ **Works!** Config loads successfully

---

## Related Features That Need TCP

All these features require TCP connection (now accessible via Connect button):

**Air-Side Config Tab:**
- 📥 Get Config (from Air-Side)
- ⚡ Apply Changes (Runtime)
- 💾 Save to Default (Persistent)

**Log Viewer Tab:**
- Request Logs (on-demand logging)
- Stop Logs

---

## Future Enhancement

### Optional: Auto-Connect on Startup

To implement the auto-connect mentioned in the error message:

```python
# In __init__ method, after UI creation:
def __init__(self):
    # ... existing init code ...

    # Auto-connect to Air-Side after UI is ready
    self.after(1000, self._auto_connect_airside)

def _auto_connect_airside(self):
    """Auto-connect to Air-Side on startup (optional)"""
    try:
        logger.info("Attempting auto-connect to Air-Side...")
        success = self.connect_to_airside(host="10.0.1.53", port=5000, timeout_ms=3000)
        if success:
            logger.info("Auto-connect successful")
        else:
            logger.warning("Auto-connect failed - user can connect manually")
    except Exception as e:
        logger.warning(f"Auto-connect error: {e}")
```

**Pros:**
- Automatic - no user action needed
- Matches error message expectation

**Cons:**
- Adds startup delay if Air-Side not available
- May fail silently if network not ready
- User might not want auto-connect

**Recommendation:** Keep manual connect for now, add auto-connect as config option later.

---

## Testing Checklist

- [x] Code syntax verified
- [ ] Restart DPM Management System
- [ ] Go to Log Viewer tab
- [ ] See Connect/Disconnect buttons in top right
- [ ] Click Connect (with Air-Side running)
- [ ] Status changes to "Connected" (green)
- [ ] Go to Air-Side Config tab
- [ ] Click "Get Config"
- [ ] Config loads successfully
- [ ] Click "Disconnect" in Log Viewer
- [ ] Status changes to "Not Connected" (red)
- [ ] Try "Get Config" again - shows error (expected)

---

## Connection Parameters

**Default Settings (hardcoded):**
```python
host = "10.0.1.53"  # Air-Side Pi 5 IP
port = 5000         # TCP command server port
timeout_ms = 5000   # 5 second connection timeout
```

**To change connection settings:**

Currently requires editing code. Future enhancement: Add connection settings dialog.

Temporary workaround (from Python console):
```python
app.connect_to_airside(host="10.0.1.100", port=6000, timeout_ms=10000)
```

---

**Status:** ✅ Fixed and syntax-verified
**Impact:** HIGH - Makes Air-Side Config tab usable
**Backward Compatibility:** ✅ Yes - adds missing functionality
**Breaking Changes:** None
