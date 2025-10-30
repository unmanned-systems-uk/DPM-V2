# DPM Diagnostic Tool v1.5.1 - Testing Checklist
## Phase 3 - Smart Diagnostics Testing

**Build Date:** 2025-10-30
**Version:** v1.5.1 (Phase 3 - Smart Diagnostics)
**Test Date:** 2025-10-30

---

## ✅ 1. Application Startup
- [x] Application starts without errors
- [x] Correct version displayed: v1.5.1 (Phase 3 - Smart Diagnostics)
- [x] Build date displayed correctly: 2025-10-30
- [x] All 10 tabs load successfully
- [x] Protocol definitions loaded (4 commands, 10 properties)
- [x] Configuration loaded correctly
- [x] ADB availability check passed
- [x] No errors in log file on startup

**Status:** ✅ PASSED - Clean startup with correct version info

---

## 2. Configuration Tab
### Network Settings Section
- [ ] Network Architecture information displayed correctly
  - [ ] Air-Side Pi WiFi: 10.0.1.53 (SSH access)
  - [ ] H16 WiFi: 10.0.1.92 (ADB access)
  - [ ] Air-Side Pi VXLAN: 192.168.144.10 (DPM Protocol)
  - [ ] H16 br-vxlan: 192.168.144.11 (Bridge to Air-Side)
- [ ] Air-Side IP field with helper text
- [ ] H16 IP field with helper text
- [ ] Client ID field with helper text
- [ ] TCP Port configuration
- [ ] UDP Status Port configuration
- [ ] UDP Heartbeat Port configuration
- [ ] Timeout configuration

### SSH Settings Section
- [ ] SSH Host configuration
- [ ] SSH Port configuration
- [ ] SSH Username configuration
- [ ] SSH Password configuration (hidden)
- [ ] Save password checkbox with warning

### UI Settings Section
- [ ] Auto-connect on startup option
- [ ] Font size configuration
- [ ] Enable audio alerts option

### Data & Files Section
- [ ] Log save location path display
- [ ] Browse button for log directory selection

### Buttons
- [ ] Save Settings button works
- [ ] Reset to Defaults button works with confirmation

**Test Cases:**
1. Verify network architecture info is visible and correct
2. Change settings and save
3. Reset to defaults and verify
4. Browse for log directory and verify path update

---

## 3. Connection Monitor Tab
- [ ] Connection status indicator
- [ ] Connect button functionality
- [ ] Disconnect button functionality
- [ ] TCP connection status display
- [ ] UDP listeners status display
- [ ] Heartbeat sender status display
- [ ] Real-time connection events log

**Test Cases:**
1. Connect to Air-Side (requires live system)
2. Verify UDP listeners start automatically
3. Verify heartbeat sender starts
4. Disconnect and verify cleanup

---

## 4. Protocol Inspector Tab
- [ ] Message list displays sent/received messages
- [ ] Filter by direction (All/Sent/Received)
- [ ] Message details panel shows JSON
- [ ] Auto-scroll option works
- [ ] Clear messages button
- [ ] Export messages to file
- [ ] Copy selected message

**Test Cases:**
1. Verify messages appear when TCP connection active
2. Test filtering functionality
3. Test export feature
4. Test copy selected

---

## 5. Command Sender Tab
- [ ] Command dropdown populated with protocol commands
- [ ] Command parameters form updates per command
- [ ] Send Command button (requires TCP connection)
- [ ] Command history display
- [ ] Response display
- [ ] Quick commands section

**Test Cases:**
1. Select different commands and verify parameter forms
2. Send command (requires live connection)
3. Verify command appears in history
4. Verify response displayed

---

## 6. Camera Dashboard Tab
- [ ] Camera status display (from UDP status broadcasts)
- [ ] Camera connection indicator
- [ ] Camera properties display
- [ ] Real-time updates when UDP status received

**Test Cases:**
1. Connect and verify camera status updates from UDP
2. Verify status changes reflected in real-time

---

## 7. System Monitor Tab
- [ ] System status display (from UDP status broadcasts)
- [ ] CPU/Memory monitoring
- [ ] Service status display
- [ ] Real-time updates when UDP status received

**Test Cases:**
1. Connect and verify system status updates from UDP
2. Verify all metrics displayed correctly

---

## 8. Log Inspector Tab
- [ ] SSH connection controls
- [ ] Log file browser
- [ ] Log content display
- [ ] Camera status comparison (UDP vs Log)
- [ ] Search/filter functionality
- [ ] Auto-refresh option
- [ ] Export log to file

**Test Cases:**
1. Connect via SSH to Air-Side Pi
2. Browse and view log files
3. Verify camera status comparison works
4. Test search/filter
5. Test export

---

## 9. Remote Control Tab
### Smart Diagnostic Section
- [ ] 🧠 Run Smart Diagnostic button
- [ ] Smart diagnostic output display with colored results
- [ ] Health score calculation
- [ ] Issue detection and categorization
- [ ] Intelligent recommendations

### SDK Testing Mode Section (NEW)
- [ ] 🔧 Switch to SDK Test Mode button
  - [ ] Stops payload-manager container
  - [ ] Starts remotecli-v2 container
  - [ ] Verifies successful switch
  - [ ] Shows confirmation message
- [ ] 🚀 Switch to Production Mode button
  - [ ] Stops remotecli-v2 container
  - [ ] Starts payload-manager container
  - [ ] Verifies successful switch
  - [ ] Shows confirmation message
- [ ] Check Current Mode button
  - [ ] Identifies running containers
  - [ ] Displays current mode
  - [ ] Shows container status

### DPM Service Management Section
- [ ] Start/Stop/Restart DPM service buttons
- [ ] Service status display

### Quick Commands Section
- [ ] Execute common commands
- [ ] Command output display

**Test Cases:**
1. Run Smart Diagnostic and verify comprehensive analysis
2. Switch to SDK Test Mode and verify containers
3. Switch back to Production Mode and verify
4. Check Current Mode at various states
5. Test service management buttons
6. Execute quick commands

---

## 10. Activity Log Tab
- [ ] Real-time event logging
- [ ] Category filter (All/TCP/UDP/Camera/System/GUI/Error/Info)
- [ ] Search functionality
- [ ] Event count statistics
- [ ] Auto-scroll option
- [ ] Clear All button
- [ ] Export to File button
- [ ] Copy Selected button (NEW)
- [ ] Color-coded event categories

**Test Cases:**
1. Verify events logged during various operations
2. Test category filtering
3. Test search
4. Test export
5. Select multiple events and copy to clipboard
6. Verify color coding works

---

## 11. H16 ADB Diagnostics Tab (NEW - PRIMARY TESTING FOCUS)

### ADB Connection Management
- [ ] Connect to H16 button
  - [ ] Initiates ADB connection to H16 IP (10.0.1.92:5555)
  - [ ] Updates connection status indicator
  - [ ] Shows success/error message
- [ ] Disconnect button
  - [ ] Cleanly disconnects ADB
  - [ ] Updates connection status
- [ ] Connection status indicator (visual feedback)
- [ ] Device info display when connected

### Quick Diagnostics Section
- [ ] 🔍 Run Smart Diagnostic button (FEATURED)
  - [ ] System Information check (Android version, model, battery)
  - [ ] Network Health check (br-vxlan, VXLAN tunnel, WiFi)
  - [ ] Air-Side Connectivity check (ping 192.168.144.10, routing)
  - [ ] DPM Application Status (app running, ports)
  - [ ] Recent Errors analysis (logcat)
  - [ ] Resource Usage check (storage, memory)
  - [ ] Health score calculation (0-100)
  - [ ] Critical issues list
  - [ ] Warnings list
  - [ ] Intelligent recommendations
  - [ ] Colored output (green=good, yellow=warning, red=critical)
- [ ] 📊 System Info button
  - [ ] Quick system information display
- [ ] 📡 Network Check button
  - [ ] Quick network diagnostics
- [ ] 🔗 Air-Side Test button
  - [ ] Quick Air-Side connectivity test

### Network Diagnostics Sub-Tab
- [ ] Check br-vxlan Interface button
  - [ ] Shows br-vxlan IP (should be 192.168.144.11)
  - [ ] Displays interface status
- [ ] Check VXLAN Tunnel button
  - [ ] Shows VXLAN tunnel configuration
  - [ ] Displays tunnel status
- [ ] Ping Air-Side Pi button
  - [ ] Pings 192.168.144.10 (corrected from .20)
  - [ ] Shows ping results and latency
- [ ] Check Route to Pi button
  - [ ] Displays routing table for 192.168.144.0/24
  - [ ] Verifies correct routing
- [ ] Check DPM Ports button
  - [ ] Shows TCP port 5000 status
  - [ ] Shows UDP ports 5001/5002 status
  - [ ] Displays process IDs if ports are in use
- [ ] Check WiFi Status button
  - [ ] Displays WiFi connection info
  - [ ] Shows IP address and signal strength
- [ ] Full Network Report button
  - [ ] Comprehensive network diagnostic report
  - [ ] All checks in one output
- [ ] Copy Output button
  - [ ] Copies diagnostic output to clipboard
- [ ] Clear Output button
  - [ ] Clears diagnostic text display

### Logcat Monitoring Sub-Tab
- [ ] Start Live DPM Logs button
  - [ ] Starts streaming DPM-related logs
  - [ ] Auto-scrolls output
- [ ] Stop Logs button
  - [ ] Stops log streaming
- [ ] Show Errors Only button
  - [ ] Filters for ERROR/FATAL level logs
- [ ] Network Logs button
  - [ ] Filters for network-related logs
- [ ] Camera Logs button
  - [ ] Filters for camera-related logs
- [ ] System Logs button
  - [ ] Filters for system-related logs
- [ ] Clear Logs button
  - [ ] Clears log output display
- [ ] Copy Selected button (NEW)
  - [ ] Copies selected log lines to clipboard
- [ ] Export Logs button
  - [ ] Saves logs to file
- [ ] Auto-scroll checkbox
  - [ ] Controls automatic scrolling

### System Info Sub-Tab
- [ ] Get Device Info button
  - [ ] Android version
  - [ ] Device model
  - [ ] Build information
- [ ] Check Battery button
  - [ ] Battery level
  - [ ] Charging status
  - [ ] Battery health
- [ ] Check Storage button
  - [ ] Available storage
  - [ ] Used storage
  - [ ] Storage breakdown
- [ ] Check Memory button
  - [ ] RAM usage
  - [ ] Free memory
  - [ ] Memory statistics
- [ ] Check DPM App button
  - [ ] DPM app version
  - [ ] App running status
  - [ ] Process information
- [ ] Full System Report button
  - [ ] Comprehensive system information
- [ ] Copy Output button
  - [ ] Copies system info to clipboard
- [ ] Clear Output button
  - [ ] Clears system info display

### Custom Commands Sub-Tab
- [ ] Command input field
  - [ ] Enter any ADB shell command
- [ ] Execute Command button
  - [ ] Runs custom ADB command
  - [ ] Displays output
- [ ] Command history dropdown
  - [ ] Stores recent commands
  - [ ] Quick recall functionality
- [ ] Common commands quick buttons
  - [ ] Pre-configured useful commands
  - [ ] One-click execution
- [ ] Output display
  - [ ] Shows command results
  - [ ] Scrollable text area
- [ ] Copy Output button
  - [ ] Copies command output to clipboard
- [ ] Clear Output button
  - [ ] Clears output display

**Critical Test Cases for H16 ADB Diagnostics:**

1. **ADB Connection Test**
   - Connect to H16 at 10.0.1.92:5555
   - Verify connection status updates
   - Verify device info appears
   - Disconnect and verify cleanup

2. **Smart Diagnostic Full Test** (PRIMARY FEATURE)
   - Click "🔍 Run Smart Diagnostic"
   - Verify all 6 diagnostic areas execute:
     * System Information
     * Network Health
     * Air-Side Connectivity (ping 192.168.144.10)
     * DPM Application Status
     * Recent Errors
     * Resource Usage
   - Verify health score calculated (0-100)
   - Verify issues categorized (critical vs warnings)
   - Verify recommendations are relevant and helpful
   - Verify colored output (green/yellow/red)
   - Test with various system states (good, degraded, critical)

3. **Network Diagnostics Tests**
   - Check br-vxlan (expect 192.168.144.11)
   - Check VXLAN tunnel status
   - Ping Air-Side Pi at 192.168.144.10 (NOT .20)
   - Check routing to 192.168.144.0/24
   - Check DPM ports (5000, 5001, 5002)
   - Verify WiFi status
   - Run full network report
   - Test copy/clear buttons

4. **Logcat Monitoring Tests**
   - Start live DPM logs
   - Verify logs streaming
   - Test "Errors Only" filter
   - Test category filters (Network, Camera, System)
   - Stop logs
   - Select log lines and copy
   - Export logs to file
   - Test auto-scroll

5. **System Info Tests**
   - Get device info
   - Check battery status
   - Check storage
   - Check memory
   - Check DPM app status
   - Run full system report
   - Test copy/clear buttons

6. **Custom Commands Tests**
   - Execute custom ADB command
   - Verify output display
   - Test command history recall
   - Test common commands buttons
   - Test copy/clear buttons

7. **Integration Tests**
   - Run diagnostics while connected via TCP/UDP
   - Verify Activity Log captures H16 ADB events
   - Switch to SDK mode from Remote Control, then check H16 app status
   - Compare camera status between Camera Dashboard and H16 logs

---

## 12. Integration Testing

### Cross-Tab Functionality
- [ ] Activity Log captures events from all tabs
- [ ] Configuration changes apply correctly
- [ ] SDK mode switch affects H16 app status
- [ ] Camera status consistent across tabs (Camera Dashboard vs Log Inspector vs H16 Diagnostics)

### Network Flow Testing
- [ ] TCP connection triggers UDP listener start
- [ ] Heartbeat sender starts with TCP connection
- [ ] Status broadcasts update Camera Dashboard and System Monitor
- [ ] Protocol Inspector captures all TCP/UDP messages

### Error Handling
- [ ] Connection failures handled gracefully
- [ ] Invalid ADB commands show appropriate errors
- [ ] SSH connection failures reported correctly
- [ ] Missing files/paths handled properly

---

## 13. Performance Testing
- [ ] Application startup time acceptable (< 3 seconds)
- [ ] GUI remains responsive during operations
- [ ] Background threads don't block UI
- [ ] Memory usage reasonable during extended use
- [ ] No memory leaks during connect/disconnect cycles

---

## 14. Documentation & Version
- [x] Version displayed correctly (v1.5.1)
- [x] Build date correct (2025-10-30)
- [ ] Help text/tooltips accurate
- [ ] Configuration tab helper text clear and helpful

---

## Test Summary

### Application Initialization: ✅ PASSED
- Clean startup
- All tabs loaded
- Correct version info
- No errors in log

### Tabs to Test: 10 total
1. Configuration Tab
2. Connection Monitor Tab
3. Protocol Inspector Tab
4. Command Sender Tab
5. Camera Dashboard Tab
6. System Monitor Tab
7. Log Inspector Tab
8. Remote Control Tab
9. Activity Log Tab
10. **H16 ADB Diagnostics Tab** ⭐ (PRIMARY FOCUS)

### Key New Features to Test:
1. ⭐ **Smart Diagnostic** - Comprehensive H16 health analysis (most important)
2. **SDK Testing Mode** - Quick switch between production and test modes
3. **Copy Selected** - Added to Activity Log and H16 Diagnostics tabs
4. **Network Architecture Info** - Added to Configuration tab
5. **Corrected IP Addresses** - 192.168.144.10 for Pi (was .20)

### Priority Testing Areas:
1. 🔴 **HIGH**: H16 Smart Diagnostic functionality
2. 🔴 **HIGH**: SDK Mode switching in Remote Control
3. 🟡 **MEDIUM**: Network diagnostics with correct IPs
4. 🟡 **MEDIUM**: Copy Selected functionality
5. 🟢 **LOW**: Configuration tab network architecture display

---

## Notes
- Most tabs require live DPM system connection for full testing
- H16 ADB Diagnostics requires H16 Ground Station on WiFi at 10.0.1.92
- SDK mode switching requires Air-Side Pi SSH access
- Some tests can be done offline (GUI functionality, layout, etc.)
- Smart Diagnostic provides the most value - thoroughly test all 6 diagnostic areas

---

## Test Results Log

### Application Startup Test (2025-10-30 18:49:13)
**Result:** ✅ PASSED

Details:
- Version: v1.5.1 (Phase 3 - Smart Diagnostics) ✅
- Build Date: 2025-10-30 ✅
- Tabs Loaded: 10/10 ✅
- Protocol Commands: 4 ✅
- Protocol Properties: 10 ✅
- ADB Available: Yes ✅
- Log Errors: None ✅
- Startup Time: ~1 second ✅

### (Add more test results as testing progresses...)

---

## Known Issues
- (None identified during initial startup testing)

---

## Recommendations for Next Phase
1. Consider adding version info to main window title bar
2. Add tooltips to buttons in H16 Diagnostics tab
3. Consider adding progress indicators for long-running diagnostics
4. Add keyboard shortcuts for common operations
5. Consider adding dark mode theme option
