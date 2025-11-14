# DPM SystemTools - Diagnostic Suite

**Version:** 1.9.0+ (Phase 2 Complete)
**Platform:** Cross-platform (Linux/Windows/macOS)
**Python:** 3.8+

Comprehensive multi-mode diagnostic and testing suite for DPM Payload Manager system.

---

## Quick Start

### 1. Install Python Dependencies

```bash
cd /path/to/DPM-V2/SystemTools
pip install -r requirements.txt
```

**Dependencies:**
- Python 3.8+ (with tkinter built-in)
- `rich>=13.7.0` (Terminal UI for log aggregator)
- `paramiko>=3.4.0` (SSH client for Air-Side access)
- Additional dependencies listed in requirements.txt

### 2. Run the Application

**GUI Mode (default):**
```bash
python main.py
```

**CLI Mode (headless):**
```bash
python cli_interface.py
```

**Log Aggregator (standalone):**
```bash
python log_aggregator.py
```

---

## Tri-Domain Log Aggregator (NEW - Issue #74)

### Overview

The **Log Aggregator** is a critical diagnostic tool that merges logs from Air-Side (UDP) and Ground-Side (TCP) into a unified, chronological timeline. This provides a complete view of the entire DPM system behavior.

**Key Features:**
- 📡 **Dual Protocol Support:** UDP for Air-Side, TCP for Ground-Side
- 🎨 **Color-Coded Display:** Blue for AIR, Purple for GROUND
- 🔍 **Powerful Filtering:** By level, context, domain, text search, time range
- 💾 **Export Options:** JSON, CSV, or human-readable text
- 🔄 **Replay Mode:** Replay logs from saved files for analysis

### Setup

**Prerequisites:**
```bash
# Install required library
pip install rich
```

**For Ground-Side (via ADB):**
```bash
# Forward Ground-Side logs from H16 to SystemTools
adb forward tcp:5008 tcp:5008
```

### Usage

**Start Log Aggregator (listen on both Air + Ground):**
```bash
cd SystemTools
python log_aggregator.py
```

**Filter by log level:**
```bash
python log_aggregator.py --level=ERROR
```

**Filter by domain:**
```bash
python log_aggregator.py --domain=AIR
```

**Search for text:**
```bash
python log_aggregator.py --search="aperture"
```

**Time range filtering:**
```bash
python log_aggregator.py --since="2025-11-13T10:30:00" --until="2025-11-13T10:35:00"
```

**Export to file:**
```bash
# Export to JSON (default)
python log_aggregator.py --export=logs_20251113.json

# Export to CSV
python log_aggregator.py --export=logs_20251113.csv --export-format=csv

# Export to text
python log_aggregator.py --export=logs_20251113.txt --export-format=text
```

**Replay from saved file:**
```bash
python log_aggregator.py --replay=logs_20251113.json
```

**Combine filters:**
```bash
# Only show Air-Side errors with "camera" in message
python log_aggregator.py --domain=AIR --level=ERROR --search="camera"
```

### Example Output

```
10:30:45.100 [GROUND] [INFO] [UI] Button pressed
  └─ button_id: set_aperture
  └─ value: f/2.8
10:30:45.112 [AIR] [INFO] [COMMAND] Command received
  └─ latency: 12ms
  └─ queue_depth: 2
10:30:45.140 [AIR] [DEBUG] [CAMERA] SDK call started
10:30:45.168 [AIR] [INFO] [CAMERA] SDK call complete
  └─ latency: 28ms
  └─ property: aperture
10:30:45.182 [GROUND] [INFO] [VM] Update received
  └─ total_latency: 82ms
```

### Network Ports

- **Air-Side (UDP):** Port 5007
- **Ground-Side (TCP):** Port 5008 (via ADB forward)

### Configuration

Configuration file: `SystemTools/config/log_aggregator.json`

Customize:
- Network ports
- Display colors
- Buffer size (default: 10,000 entries)
- Default filters
- Export settings

### Troubleshooting

**Ground-Side not connecting:**
```bash
# Verify ADB connection
adb devices

# Verify port forward
adb forward --list

# Re-establish forward
adb forward tcp:5008 tcp:5008
```

**Air-Side not receiving logs:**
- Check Air-Side is running and StructuredLogger is enabled (Issue #72)
- Verify firewall isn't blocking UDP port 5007
- Check Air-Side is configured to send logs to SystemTools IP

**High volume logging:**
- Aggregator buffers last 10,000 entries (configurable)
- Consider filtering by level/context to reduce noise
- Export to file for long-term storage

---

## Current Features (Version 1.9.0+, Phase 2 Complete)

### GUI Tabs (12 Total)

1. **Connection Monitor Tab**
   - Multi-domain connection management (Air-Side, Ground-Side, SSH, ADB)
   - TCP/UDP status indicators
   - Smart connection with auto-detection
   - Connection event log with color-coding
   - Real-time status indicators
   - Save log to file, copy to clipboard

2. **Configuration Tab**
   - Network settings (Air-Side IP, ports)
   - SSH settings (Air-Side Docker access)
   - ADB settings (H16 diagnostics)
   - UI preferences (auto-connect, font size, audio alerts)
   - Log save location
   - Save/load settings, reset to defaults

3. **Protocol Inspector Tab**
   - Protocol message inspection and validation
   - Real-time message monitoring
   - Message format verification

4. **Command Sender Tab**
   - Interactive command construction
   - Command testing and validation
   - Response monitoring

5. **Camera Dashboard Tab**
   - Camera control testing panel
   - Debug mode features (Focus controls, AF Hold, property setter)
   - Real-time diagnostics output
   - Response validation and error analysis

6. **System Monitor Tab**
   - System health and resource monitoring
   - CPU, memory, disk usage tracking
   - Network statistics

7. **Log Inspector Tab**
   - Real-time log viewing and analysis
   - Multi-format log parsing (JSON, text)
   - SSH log retrieval from Air-Side

8. **Activity Log Tab**
   - Activity timeline and event tracking
   - Chronological event visualization

9. **Remote Control Tab**
   - Remote system control features
   - Advanced operational controls

10. **H16 Diagnostics Tab**
    - Android H16 ADB connection diagnostics
    - Ping and port testing (PowerShell Test-NetConnection)
    - ADB server management (reconnect, kill, start)
    - Full reset & reconnect sequence
    - H16 app running status detection
    - Complete diagnostic suite with recommendations
    - Windows Firewall troubleshooting guidance

11. **GitHub Integration Tab**
    - GitHub issue management from SystemTools
    - Issue creation, viewing, and tracking
    - Direct GitHub API integration

12. **Git Helper Tab**
    - Git workflow assistance
    - Commit and branch management helpers

---

## Default Configuration

**Network Settings:**
- Air-Side IP: `10.0.1.53`
- TCP Command Port: `5000`
- UDP Status Port: `5001`
- UDP Heartbeat Port: `5002`
- H16 IP: `10.0.1.92`

**SSH Settings:**
- SSH Host: `10.0.1.53`
- Username: `dpm`
- Password: `2350`

---

## Usage

### Connect to Air-Side

1. Launch the application: `python main.py`
2. Go to **Connection Monitor** tab
3. Click **Connect**
4. Once connected, click **Send Handshake**
5. Monitor connection log for responses

### Change Settings

1. Go to **Configuration** tab
2. Modify network/SSH settings as needed
3. Click **Save Settings**
4. Reconnect if already connected

---

## Project Structure

```
SystemTools/
├── main.py                        # GUI application entry point
├── cli_interface.py               # CLI mode (headless)
├── log_aggregator.py              # Tri-domain log aggregator (standalone)
├── requirements.txt               # Python dependencies
├── config.json                    # User settings (auto-generated)
├── devtools_config.py             # DevTools configuration
├── version.py                     # Version management
│
├── config/                        # Configuration files
│   └── log_aggregator.json        # Log aggregator config
│
├── gui/                           # GUI components (12 tabs)
│   ├── main_window.py             # Main window framework
│   ├── tab_connection.py          # Connection Monitor tab
│   ├── tab_config.py              # Configuration tab
│   ├── tab_protocol.py            # Protocol Inspector tab
│   ├── tab_command.py             # Command Sender tab
│   ├── tab_camera.py              # Camera Dashboard tab
│   ├── tab_system.py              # System Monitor tab
│   ├── tab_logs.py                # Log Inspector tab
│   ├── tab_activity.py            # Activity Log tab
│   ├── tab_remote_control.py     # Remote Control tab
│   ├── tab_h16_diagnostics.py    # H16 Diagnostics tab
│   ├── tab_github_integration.py # GitHub Integration tab
│   ├── tab_git_helper.py          # Git Helper tab
│   └── widgets.py                 # Reusable widgets
│
├── network/                       # Network layer
│   ├── tcp_client.py              # TCP command client
│   ├── udp_listener.py            # UDP status/heartbeat listener
│   ├── ssh_client.py              # SSH client for Air-Side
│   ├── adb_client.py              # ADB client for H16
│   ├── protocol.py                # Protocol message formatting
│   ├── heartbeat.py               # Heartbeat sender
│   └── diagnostic_client.py      # Diagnostic protocols
│
├── utils/                         # Utilities
│   ├── config.py                  # Configuration management
│   ├── logger.py                  # Application logging
│   ├── protocol_loader.py         # Load protocol JSON files
│   └── log_parser.py              # Multi-format log parsing
│
├── docs/                          # Documentation
│   ├── Cheat_Sheet_ADB_H16.md     # H16 ADB troubleshooting guide
│   └── SESSION_*.md               # Development session notes
│
└── logs/                          # Application logs (auto-generated)
    └── exports/                   # Exported log files
```

---

## Logs

Application logs are saved to: `WindowsTools/logs/`

Log files are named: `dpm_diagnostic_YYYYMMDD_HHMMSS.log`

---

## Troubleshooting

### Application won't start

**Error:** `ModuleNotFoundError: No module named 'tkinter'`
- **Solution:** tkinter should be built into Python. Reinstall Python with tkinter support.

### Can't connect to Air-Side

**Check:**
1. Air-Side Pi is powered on and connected to network
2. IP address is correct in Configuration tab
3. Ports are correct (5000 for TCP)
4. Windows Firewall isn't blocking outgoing connections
5. Air-Side payload-manager Docker container is running

**Test connectivity:**
```bash
ping 10.0.1.53
```

### No response after sending handshake

**Check:**
1. Air-Side logs: `docker logs payload-manager`
2. Verify Air-Side is receiving the message
3. Check protocol format in Connection Log

---

## Development Status

### ✅ Phase 1 - Foundation (COMPLETE)
- [x] Project setup
- [x] Configuration management
- [x] TCP client
- [x] Basic GUI (2 tabs)
- [x] Connection monitoring
- [x] Protocol message formatting

### 📋 Phase 2 - Core Monitoring (NEXT)
- [ ] UDP status listener
- [ ] UDP heartbeat sender
- [ ] Protocol Inspector tab
- [ ] Command Sender tab
- [ ] Camera Dashboard tab
- [ ] System Monitor tab

### 🔜 Phase 3 - Advanced Features
- [ ] Docker Logs tab (SSH + log streaming)
- [ ] Real-time graphs
- [ ] Custom command builder
- [ ] Property setter

### 🔜 Phase 4 - Test Automation
- [ ] Pre-defined test sequences
- [ ] Stress testing
- [ ] Test reporting

### 🔜 Phase 5 - Polish
- [ ] Error handling
- [ ] Audio alerts
- [ ] Dark mode
- [ ] User documentation

---

## Protocol Files

The tool automatically loads protocol definitions from:
- `D:\DPM\DPM-V2\protocol\commands.json`
- `D:\DPM\DPM-V2\protocol\camera_properties.json`

These files define valid commands and camera properties for validation.

---

## Support

- **Documentation:** See `DIAGNOSTIC_TOOL_PLAN.md` for full feature specifications
- **Progress:** See `PROGRESS_AND_TODO.md` for development status
- **Issues:** Check `logs/` directory for application logs

---

## Version History

**v1.0.0 - Phase 1** (October 29, 2025)
- Initial release
- Basic connectivity and configuration
- Connection Monitor and Configuration tabs
- TCP client implementation
- Settings persistence

---

**Next Update:** Phase 2 - Core Monitoring (UDP listeners, protocol inspection, command sending)
