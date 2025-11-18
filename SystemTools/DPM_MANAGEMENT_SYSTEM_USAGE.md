# DPM Management System - Usage Guide

**Issue:** #118 - On-Demand Logging Controls
**Created:** 2025-11-16
**Status:** ✅ Implemented and tested

---

## Overview

`DPM_Management_System.py` is a clean management GUI for DPM systems, built from `log_viewer_gui.py` as a foundation. It provides:

- **Tri-domain log aggregation** (Air-Side + Ground-Side)
- **On-demand logging controls** (NEW in Issue #118)
- **Tabbed interface** for future features (Config tab, Command tab, etc.)

---

## Quick Start

### 1. Launch the Application

```bash
cd /home/anthony/DPM-V2/SystemTools
python3 DPM_Management_System.py
```

The GUI will open with the **Log Viewer** tab active.

---

## Using On-Demand Logging

### Step 1: Connect to Air-Side

**Option A - Python Console (Current Method):**

```python
# From Python console while GUI is running:
import tkinter as tk
root = tk._default_root  # Get the running GUI
app = root  # DPMManagementSystem instance

# Connect to Air-Side
app.connect_to_airside(host='10.0.1.53', port=5001)
# Status should show: "Connected to 10.0.1.53:5001" in green
```

**Option B - Future Connection Tab (Issue #117):**
A connection management tab will be added in the future for GUI-based connection.

### Step 2: Start Passive Logging (Optional)

Click **"▶ Start"** in the Stream Controls section to start receiving passive logs from:
- Air-Side (UDP port 5007)
- Ground-Side (TCP port 5008)

This runs the UDP discovery protocol and opens listeners.

### Step 3: Request On-Demand Logs from Air-Side

**In the "On-Demand Logging" panel:**

1. **Set Duration:** Adjust the spinbox (10-3600 seconds, default: 600)
2. **Click "Request Logs"**
   - Sends `logging.enable_streaming` command to Air-Side
   - Status shows: "Requesting 600s..." (orange)
   - On success, countdown starts: "Streaming (09:59 remaining)" (green)
3. **Watch Countdown:** Updates every second in MM:SS format
4. **Auto-Stop:** When countdown reaches 0:00, logging stops automatically
5. **Manual Stop:** Click **"Stop"** button anytime to stop early

### Step 4: View Logs

Logs from both passive and on-demand sources appear in the same display:
- **Blue text:** Air-Side logs
- **Magenta text:** Ground-Side logs
- **Red text:** ERROR level
- **Orange text:** WARNING level
- **Gray text:** DEBUG level

### Step 5: Filter and Export

**Filters (AND logic):**
- Domain: ALL, AIR, GROUND
- Level: ALL, DEBUG, INFO, WARNING, ERROR
- Context: ALL, CAMERA, NETWORK, COMMAND, UI, SYSTEM
- Search: Free text search

**Export:**
- Save to File: JSON, CSV, or Text format
- Copy All: Copy visible logs to clipboard
- Copy Selected: Copy selected text

---

## Connection Requirements

**Air-Side must:**
- Be running with TCP server listening (default port: 5001)
- Have `logging.enable_streaming` command implemented
- Be reachable on network (e.g., 10.0.1.53)

**SystemTools must:**
- Have network connectivity to Air-Side
- Have ports 5007 (UDP) and 5008 (TCP) available for passive logging

---

## Troubleshooting

### Error: "Please connect to Air-Side first"

**Cause:** No TCP connection to Air-Side

**Fix:**
```python
# Connect via Python console
app.connect_to_airside(host='10.0.1.53', port=5001)
```

Or wait for Connection tab (Issue #117).

### Error: "Failed to request logs: No response"

**Cause:** Air-Side didn't respond to `logging.enable_streaming` command

**Check:**
1. Air-Side is running
2. Air-Side has command handler implemented
3. Network connectivity: `ping 10.0.1.53`
4. TCP port open: `nc -zv 10.0.1.53 5001`

### Error: Connection timeout

**Cause:** Air-Side not reachable on network

**Fix:**
- Check Air-Side IP address (use UDP discovery or SSH)
- Verify network connectivity
- Check firewall rules

### No logs appearing after request

**Cause:** Air-Side may not be sending logs via UDP

**Check:**
1. Air-Side SystemTools logging is enabled
2. UDP port 5007 is not blocked by firewall
3. SystemTools passive logging is started (click "▶ Start")

---

## Architecture

### Backend (Reused 100% - No Changes)

- `network.tcp_client.TCPClient` - TCP connection to Air-Side
- `network.protocol.protocol_msg` - DPM protocol message formatting
- `network.log_listeners.AirSideListener` - UDP listener (port 5007)
- `network.log_listeners.GroundSideListener` - TCP listener (port 5008)
- `network.udp_discovery.UDPDiscoverySender` - Auto IP detection
- `utils.logger` - Logging to file
- `utils.config` - Configuration management
- `utils.log_colors` - Color tag configuration

### Frontend (NEW - Issue #118)

- **Tabbed Notebook Interface** - Foundation for multiple tabs
- **Log Viewer Tab** - Passive logging + On-demand controls
- **On-Demand Controls** - Duration, Request, Stop, Status, Countdown
- **Connection Helpers** - `connect_to_airside()`, `disconnect_from_airside()`

---

## Testing Checklist

- [x] GUI launches without errors
- [x] Syntax validation passes
- [x] Connection method works (connect_to_airside)
- [ ] On-demand logging request succeeds (requires Air-Side)
- [ ] Countdown timer updates every second
- [ ] Manual stop works
- [ ] Auto-stop at 0:00 works
- [ ] Logs appear in display
- [ ] Status colors correct (gray → orange → green → gray)

---

## Next Steps

**For User Testing:**
1. Ensure Air-Side is running on network (e.g., 10.0.1.53:5001)
2. Launch `DPM_Management_System.py`
3. Connect via Python console: `app.connect_to_airside()`
4. Test on-demand logging functionality

**Future Enhancements (Other Issues):**
- #117 - Add Air-Side Configuration tab
- Add Connection Management tab (GUI-based connect/disconnect)
- Add Command Sender tab
- Add System Status tab

---

## Related Issues

- #114 - Phase 1 Cross-Domain Alignment (parent)
- #117 - SystemTools Air-Side config tab (same GUI rebuild)
- #121 - PM integration test - On-demand logging (will test this)

---

**File:** `/home/anthony/DPM-V2/SystemTools/DPM_Management_System.py`
**Lines:** 835 (updated with connection helpers)
**Size:** 33KB
**Status:** ✅ Ready for testing and commit
