# DPM Windows Diagnostic Tool - Implementation Plan

**Version:** 1.0
**Date:** October 29, 2025
**Platform:** Windows 11
**Language:** Python 3.x with tkinter GUI
**Purpose:** Comprehensive testing, diagnostics, and monitoring tool for DPM system

---

## 1. OVERVIEW

### 1.1 Purpose
A powerful, user-friendly GUI tool for:
- Real-time monitoring of Air-Side (Pi SBC) and Ground-Side (H16 Android) systems
- Protocol testing and debugging
- Pre-implementation testing of new commands
- Live diagnostics and troubleshooting
- Docker log analysis
- Network connectivity monitoring

### 1.2 Target Users
- Developers testing new features
- System integrators debugging issues
- Field engineers diagnosing problems
- QA testing protocol compliance

### 1.3 Network Configuration
```
Windows 11 Machine (This PC)
    ↓ WiFi
Local Network (10.0.1.x)
    ├─ Air-Side Pi: 10.0.1.53 (SSH: dpm@10.0.1.53, password: 2350)
    │  └─ Docker Container: payload-manager
    └─ Ground-Side H16: 10.0.1.92
```

---

## 2. FEATURE SPECIFICATION

### 2.1 Tab-Based Interface

#### Tab 1: **Connection Monitor** 🔌
**Purpose:** Real-time connection status and network diagnostics

**Features:**
- **Connection Status Display:**
  - Air-Side TCP connection status (port 5000)
  - Air-Side UDP status listener (port 5001)
  - Air-Side heartbeat sender/receiver (port 5002)
  - H16 connection status (if accessible)
  - Visual indicators: ✅ Connected / ❌ Disconnected / 🟡 Connecting

- **Live Metrics:**
  - Heartbeat sent/received count
  - Heartbeat interval (actual vs expected 1 Hz)
  - Last heartbeat timestamp
  - Heartbeat timeout detection (>10s warning)
  - UDP status broadcast reception (5 Hz)
  - TCP command round-trip latency (ms)
  - Packet loss percentage

- **Network Diagnostics:**
  - Ping Air-Side Pi (10.0.1.53)
  - Ping H16 (10.0.1.92)
  - Port availability check (5000, 5001, 5002)
  - Network quality graph (latency over time)
  - Auto-reconnect toggle

- **Visual Elements:**
  - Real-time connection timeline graph
  - Heartbeat pulse animation
  - Connection quality meter
  - Event log (connect/disconnect events)

---

#### Tab 2: **Protocol Inspector** 🔍
**Purpose:** Deep protocol analysis and message inspection

**Features:**
- **Message Capture:**
  - Live capture of all TCP commands (sent/received)
  - Live capture of all UDP status broadcasts (received)
  - Live capture of all heartbeat messages (sent/received)
  - Message filtering by type
  - Search/filter by content

- **Message Display:**
  - Pretty-printed JSON with syntax highlighting
  - Message metadata (timestamp, direction, sequence ID)
  - Message type indicator (command/response/status/heartbeat)
  - Error highlighting (error responses in red)

- **Statistics:**
  - Total messages sent/received
  - Message type breakdown (pie chart)
  - Average message size
  - Messages per second
  - Error rate percentage

- **Export:**
  - Save message log to JSON file
  - Export filtered messages
  - Copy individual message to clipboard

---

#### Tab 3: **Command Sender** 🚀
**Purpose:** Manual command testing and protocol experimentation

**Features:**
- **Quick Commands (One-Click):**
  - Handshake
  - camera.capture
  - system.get_status
  - camera.get_properties (all)
  - Disconnect

- **Camera Property Setter:**
  - Dropdown for property name (shutter_speed, aperture, iso, etc.)
  - Dynamic value input based on property type
  - Pre-filled with valid values from camera_properties.json
  - Validation before sending
  - "Send" button

- **Custom Command Builder:**
  - JSON editor for manual command construction
  - Template dropdown (pre-filled common commands)
  - Syntax validation
  - Sequence ID auto-increment
  - "Send Custom Command" button

- **Response Display:**
  - Last command sent (formatted JSON)
  - Last response received (formatted JSON)
  - Success/error indicator
  - Response time (ms)
  - History of last 10 commands/responses

---

#### Tab 4: **Camera Dashboard** 📷
**Purpose:** Real-time camera status and property monitoring

**Features:**
- **Camera Connection Status:**
  - Connected/Disconnected indicator
  - Camera model display
  - Battery level (percentage + visual bar)
  - Remaining shots count

- **Current Properties Display:**
  - Shutter Speed (large, prominent)
  - Aperture (large, prominent)
  - ISO (large, prominent)
  - White Balance (mode + temperature if applicable)
  - Focus Mode
  - File Format
  - Drive Mode
  - Exposure Compensation

- **Property History:**
  - Timeline graph showing property changes over time
  - Select property to graph
  - Last 5 minutes of history

- **Auto-Refresh:**
  - Toggle auto-query properties
  - Configurable interval (1s, 5s, 10s, 30s)
  - Manual "Refresh Now" button

- **Visual Layout:**
  - Exposure triangle visualization (Shutter/Aperture/ISO)
  - Color-coded values (normal/warning)
  - Large, readable fonts

---

#### Tab 5: **System Monitor** 📊
**Purpose:** Air-Side system health monitoring

**Features:**
- **Real-Time Metrics:**
  - CPU Usage (% + graph)
  - Memory Usage (% + graph, MB used/total)
  - Storage Free (GB + percentage bar)
  - Uptime (formatted: Xd Xh Xm Xs)
  - Network Stats (if available)

- **Historical Graphs:**
  - CPU usage over time (last 5 minutes)
  - Memory usage over time
  - Selectable time range (1m, 5m, 15m, 1h)

- **Alerts:**
  - CPU >80% warning
  - Memory >90% warning
  - Storage <5GB warning
  - Visual + audio alert options

- **System Info:**
  - Pi model (Raspberry Pi 5)
  - OS version (Ubuntu)
  - Kernel version
  - IP addresses (ethernet + WiFi)

- **Auto-Refresh:**
  - Configurable interval (1s, 5s, 10s)
  - Manual "Refresh Now" button

---

#### Tab 6: **Docker Logs** 📋
**Purpose:** Live Docker container log viewing and analysis

**Features:**
- **SSH Connection to Pi:**
  - Auto-connect using saved credentials (10.0.1.53, dpm, 2350)
  - Connection status indicator
  - Manual connect/disconnect buttons

- **Log Viewer:**
  - Live streaming of `docker logs -f payload-manager`
  - Auto-scroll to newest (toggle)
  - Line numbers
  - Timestamp display (toggle with `-t` flag)
  - Color-coded log levels:
    - [DEBUG]: Gray
    - [INFO ]: White (note: space in tag)
    - [WARN]: Yellow
    - [ERROR]: Red

- **Smart Filtering (Based on LOG_ANALYSIS_GUIDE.md):**
  - **Quick Filters (Dropdown):**
    - All Logs (no filter)
    - Errors Only (`grep "\[ERROR\]"`)
    - Errors + Warnings (`grep -E "\[ERROR\]|\[WARN"`)
    - No Debug (cleaner) (`grep -v "\[DEBUG\]"`)
    - Camera Events (`grep -i "camera.*connect|disconnect|ready"`)
    - Camera Errors (`grep -i "camera" | grep "\[ERROR\]"`)
    - Camera Properties (`grep -E "Setting property|Getting property|Raw SDK value"`)
    - Network Events (`grep -i "tcp\|udp\|connection\|accepted"`)
    - Heartbeat Activity (`grep -i "heartbeat"`)
    - Commands Received (`grep "Processing command:"`)
    - ISO Related (`grep -i "iso"`)
    - Shutter Related (`grep -i "shutter"`)
    - Aperture Related (`grep -i "aperture"`)

  - **Time Filters:**
    - Last 50 lines (`--tail 50`)
    - Last 100 lines (`--tail 100`)
    - Last 30 minutes (`--since 30m`)
    - Last 1 hour (`--since 1h`)
    - Last 2 hours (`--since 2h`)

  - **Custom Regex:**
    - Text input for custom grep pattern
    - Case-sensitive/insensitive toggle
    - Context lines (before/after) selector

- **Log Control:**
  - Pause/Resume streaming
  - Clear display
  - Save logs to file
  - Save filtered logs to file
  - Copy selected lines
  - Jump to bottom/top
  - Show/hide timestamps

- **Log Analysis Panel:**
  - **Message Counts:**
    - Total lines displayed
    - ERROR count
    - WARN count
    - INFO count
    - DEBUG count
  - **Recent Errors:**
    - Last 5 errors in sidebar
    - Click to jump to error in log
  - **Component Activity:**
    - Camera connection status (from logs)
    - Network activity indicator
    - Commands processed (count)
  - **Export Summary:**
    - Generate summary report (like LOG_ANALYSIS_GUIDE.md template)
    - Include log level counts, recent errors, camera status, network status

---

#### Tab 7: **Test Automation** 🧪
**Purpose:** Automated testing sequences

**Features:**
- **Pre-Defined Test Sequences:**
  - Connection stress test (connect/disconnect 100x)
  - Heartbeat reliability test (monitor for 5 minutes)
  - Command latency test (send 100 commands, measure timing)
  - Camera property cycle test (set all properties sequentially)
  - Error handling test (send invalid commands)

- **Test Results:**
  - Pass/Fail indicator
  - Success rate percentage
  - Average latency
  - Error count
  - Detailed log

- **Custom Test Sequences:**
  - Define sequence of commands
  - Add delays between commands
  - Set expected responses
  - Loop count
  - Save/load test sequences

- **Stress Testing:**
  - High-frequency command sending
  - Concurrent connection testing
  - Long-duration stability testing
  - Memory leak detection

---

#### Tab 8: **Configuration** ⚙️
**Purpose:** Tool settings and preferences

**Features:**
- **Network Settings:**
  - Air-Side IP (default: 10.0.1.53)
  - Air-Side Ports (TCP: 5000, UDP: 5001, 5002)
  - H16 IP (default: 10.0.1.92)
  - Connection timeout (ms)
  - Retry attempts

- **SSH Settings:**
  - SSH host (10.0.1.53)
  - SSH username (dpm)
  - SSH password (encrypted storage)
  - SSH port (22)

- **UI Settings:**
  - Auto-connect on startup
  - Auto-refresh intervals
  - Color theme (Light/Dark)
  - Font size
  - Enable audio alerts

- **Data Settings:**
  - Log file location
  - Message capture file location
  - Auto-save settings
  - Clear history

- **Import/Export:**
  - Export settings to JSON
  - Import settings from JSON
  - Reset to defaults

---

## 3. TECHNICAL ARCHITECTURE

### 3.1 Technology Stack

**GUI Framework:** tkinter (built-in Python)
- Reason: No external dependencies, native Windows support
- ttk widgets for modern appearance
- Notebook widget for tabs

**Networking:**
- **TCP:** `socket` module (built-in)
- **UDP:** `socket` module (built-in)
- **Async:** `asyncio` for non-blocking I/O
- **Threading:** `threading` for background tasks

**SSH/Docker:**
- **paramiko:** SSH client for Pi connection
- Execute `docker logs -f payload-manager` over SSH

**Data Visualization:**
- **matplotlib:** Embedded graphs in tkinter
- Real-time updating plots

**Data Storage:**
- **JSON:** Settings and log export
- **Protocol definitions:** Load from `protocol/commands.json` and `protocol/camera_properties.json`

### 3.2 Project Structure

```
WindowsTools/
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
├── README.md                    # User documentation
├── DIAGNOSTIC_TOOL_PLAN.md     # This file
│
├── gui/
│   ├── __init__.py
│   ├── main_window.py          # Main GUI window + tabs
│   ├── tab_connection.py       # Connection Monitor tab
│   ├── tab_protocol.py         # Protocol Inspector tab
│   ├── tab_command.py          # Command Sender tab
│   ├── tab_camera.py           # Camera Dashboard tab
│   ├── tab_system.py           # System Monitor tab
│   ├── tab_docker.py           # Docker Logs tab
│   ├── tab_testing.py          # Test Automation tab
│   ├── tab_config.py           # Configuration tab
│   └── widgets.py              # Reusable GUI widgets
│
├── network/
│   ├── __init__.py
│   ├── tcp_client.py           # TCP command client
│   ├── udp_listener.py         # UDP status/heartbeat listener
│   ├── heartbeat.py            # Heartbeat sender
│   └── protocol.py             # Protocol message formatting
│
├── utils/
│   ├── __init__.py
│   ├── ssh_client.py           # SSH/Docker log access
│   ├── logger.py               # Application logging
│   ├── config.py               # Settings management
│   ├── validators.py           # JSON validation
│   └── protocol_loader.py      # Load protocol definitions
│
├── templates/
│   ├── command_templates.json  # Pre-defined command templates
│   └── test_sequences.json     # Pre-defined test sequences
│
└── logs/
    └── (auto-generated log files)
```

### 3.3 Key Design Patterns

**Singleton Pattern:**
- NetworkClient (single TCP connection)
- SSHClient (single SSH connection)
- ConfigManager (single settings instance)

**Observer Pattern:**
- GUI tabs subscribe to network events
- Real-time updates when data arrives

**Command Pattern:**
- Protocol commands encapsulated as objects
- Easy to log, replay, and test

**MVC-like Architecture:**
- GUI (View) separated from network logic (Model)
- ViewModel layer for state management

---

## 4. IMPLEMENTATION PHASES

### Phase 1: Foundation (Priority: HIGH)
**Estimated Time:** 2-3 hours

- ✅ Create project structure
- ✅ Implement main window with tab framework
- ✅ Implement Configuration tab (settings UI + persistence)
- ✅ Implement basic TCP client
- ✅ Implement Connection Monitor tab (basic)
- ✅ Test basic connectivity

**Deliverable:** Tool can connect to Air-Side and show connection status

---

### Phase 2: Core Monitoring (Priority: HIGH)
**Estimated Time:** 2-3 hours

- ✅ Implement UDP listeners (status + heartbeat)
- ✅ Implement Protocol Inspector tab
- ✅ Implement Command Sender tab (basic commands)
- ✅ Implement Camera Dashboard tab (basic)
- ✅ Implement System Monitor tab (basic)

**Deliverable:** Tool can monitor all protocol messages and send basic commands

---

### Phase 3: Advanced Features (Priority: MEDIUM)
**Estimated Time:** 2-3 hours

- ✅ Implement Docker Logs tab with SSH
- ✅ Add real-time graphs (matplotlib integration)
- ✅ Add command history and replay
- ✅ Add custom command builder with templates
- ✅ Add filtering and search

**Deliverable:** Tool has full monitoring and command capabilities

---

### Phase 4: Testing & Automation (Priority: MEDIUM)
**Estimated Time:** 1-2 hours

- ✅ Implement Test Automation tab
- ✅ Add pre-defined test sequences
- ✅ Add stress testing
- ✅ Add test result reporting

**Deliverable:** Tool can run automated tests

---

### Phase 5: Polish & Documentation (Priority: LOW)
**Estimated Time:** 1 hour

- ✅ Add error handling and validation
- ✅ Add audio/visual alerts
- ✅ Create user documentation
- ✅ Add keyboard shortcuts
- ✅ Add dark mode theme
- ✅ Performance optimization

**Deliverable:** Production-ready tool

---

## 5. USER INTERFACE MOCKUP

```
╔══════════════════════════════════════════════════════════════════════╗
║  DPM Diagnostic Tool v1.0                                      [_][□][X] ║
╠══════════════════════════════════════════════════════════════════════╣
║ Connection Monitor | Protocol Inspector | Command Sender | Camera   ║
║ System Monitor | Docker Logs | Test Automation | Configuration      ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  [Current Tab Content Here]                                          ║
║                                                                      ║
║                                                                      ║
║                                                                      ║
║                                                                      ║
╠══════════════════════════════════════════════════════════════════════╣
║ Status: Connected ✅ | Air-Side: 10.0.1.53 | Uptime: 2h 34m        ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## 6. TESTING STRATEGY

### 6.1 Unit Testing
- Test each network client independently
- Test protocol message formatting
- Test configuration save/load
- Test validators

### 6.2 Integration Testing
- Test with real Air-Side Pi
- Test with protocol responses
- Test with Docker logs
- Test all tabs together

### 6.3 Stress Testing
- 1000+ rapid commands
- Long-duration operation (24h)
- Connection interruption recovery
- Memory leak detection

---

## 7. SECURITY CONSIDERATIONS

- **SSH Password Storage:**
  - Encrypted using Windows DPAPI or base64 (minimal)
  - Option to prompt each session (no storage)

- **Network Security:**
  - Local network only (10.0.1.x)
  - No external connections
  - No data sent outside local network

---

## 8. FUTURE ENHANCEMENTS

**Post-MVP Features:**
- Export reports (PDF/HTML)
- Email alerts on errors
- Remote control of H16 Android app
- Protocol version negotiation testing
- Performance profiling
- Gimbal testing interface (when implemented)
- Content download interface (when implemented)
- Multi-device monitoring (multiple Pis)
- Comparison mode (compare two sessions)
- Machine learning anomaly detection

---

## 9. DEPENDENCIES

**Required Python Packages:**
```
paramiko>=3.4.0          # SSH client
matplotlib>=3.8.0        # Graphs
```

**Optional Python Packages:**
```
jsonschema>=4.20.0       # JSON validation
ping3>=4.0.0             # ICMP ping (may require admin)
```

**Built-in Python Modules:**
- tkinter (GUI)
- socket (networking)
- asyncio (async I/O)
- threading (background tasks)
- json (data parsing)
- datetime (timestamps)
- logging (application logs)

---

## 10. SUCCESS CRITERIA

**Must Have (MVP):**
- ✅ Connect to Air-Side TCP/UDP
- ✅ Monitor heartbeats
- ✅ Send basic commands
- ✅ View camera properties
- ✅ View system status
- ✅ View Docker logs

**Should Have:**
- ✅ Protocol message inspection
- ✅ Custom command sending
- ✅ Real-time graphs
- ✅ Connection quality monitoring
- ✅ Configuration persistence

**Nice to Have:**
- ✅ Test automation
- ✅ Stress testing
- ✅ Dark mode
- ✅ Audio alerts

---

## 11. RISKS & MITIGATIONS

| Risk | Impact | Mitigation |
|------|--------|------------|
| SSH connection fails | Can't view Docker logs | Add fallback to manual log file upload |
| Network latency | Slow updates | Add configurable refresh rates |
| tkinter performance | Slow GUI with many messages | Implement message buffering and pagination |
| Protocol changes | Tool breaks | Load protocol from JSON files (auto-adapt) |
| Windows firewall | Blocks connections | Document firewall configuration |

---

## 12. CONCLUSION

This diagnostic tool will be an invaluable asset for:
- **Development:** Testing new features before implementing in Android app
- **Debugging:** Deep inspection of protocol messages and system state
- **Monitoring:** Real-time visibility into Air-Side health
- **Quality Assurance:** Automated testing and validation

The tool is designed to be:
- **User-Friendly:** Clear GUI, no command-line required
- **Powerful:** Full protocol access and diagnostics
- **Extensible:** Easy to add new features as system evolves
- **Reliable:** Robust error handling and recovery

**Estimated Total Development Time:** 8-11 hours (can be done incrementally)

**Next Step:** Get approval for this plan, then start Phase 1 implementation.

---

## Related Documentation & Resources

**Project Documentation:**
- [PROGRESS_AND_TODO.md](./PROGRESS_AND_TODO.md) - WindowsTools task tracker and progress
- [../docs/CC_READ_THIS_FIRST.md](../docs/CC_READ_THIS_FIRST.md) - Claude Code workflow rules

**Protocol Definitions:**
- [../protocol/commands.json](../protocol/commands.json) - Command specifications (load at runtime)
- [../protocol/camera_properties.json](../protocol/camera_properties.json) - Property definitions and validation

**Log Analysis:**
- [../docs/LOG_ANALYSIS_GUIDE.md](../docs/LOG_ANALYSIS_GUIDE.md) - Air-Side log filtering patterns
  - **Used extensively for Docker Logs tab design**
  - Contains all grep patterns for camera, network, property, and error analysis
  - Pre-defined filters copied directly from this guide

**Air-Side Progress:**
- [../sbc/docs/PROGRESS_AND_TODO.md](../sbc/docs/PROGRESS_AND_TODO.md) - Air-Side status

**Ground-Side Progress:**
- [../android/docs/PROGRESS_AND_TODO.md](../android/docs/PROGRESS_AND_TODO.md) - Ground-Side status

---

**Document Version:** 1.1
**Created:** October 29, 2025
**Last Updated:** October 29, 2025 - Enhanced Docker Logs tab with LOG_ANALYSIS_GUIDE.md patterns
**Author:** Claude Code
**Status:** Enhanced - Awaiting Approval
