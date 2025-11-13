# DPM Windows Diagnostic Tool

**Version:** 1.0.0 (Phase 1 - Foundation)
**Platform:** Windows 11
**Python:** 3.8+

Comprehensive diagnostic and testing tool for DPM Payload Manager system.

---

## Quick Start

### 1. Install Python Dependencies

```bash
cd D:\DPM\DPM-V2\SystemTools
pip install -r requirements.txt
```

**Dependencies:**
- Python 3.8+ (with tkinter built-in)
- `rich>=13.7.0` (Terminal UI for log aggregator)
- `paramiko>=3.4.0` (SSH client - Phase 3)
- `matplotlib>=3.8.0` (Graphs - Phase 3)

### 2. Run the Application

```bash
python main.py
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

## Phase 1 Features (Current)

### Connection Monitor Tab
- Connect/disconnect to Air-Side Pi
- TCP connection status
- Send handshake
- Connection event log with color-coding
- Real-time status indicator
- **Save log to file** (with customizable location)
- **Copy log to clipboard**
- Clear log

### Configuration Tab
- Network settings (Air-Side IP, ports)
- SSH settings (for future Docker logs)
- UI preferences (auto-connect, font size, audio alerts)
- **Log save location** (specify where to save exported logs)
- Save/load settings
- Reset to defaults

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
├── main.py                    # GUI application entry point
├── log_aggregator.py          # Tri-domain log aggregator (NEW)
├── requirements.txt           # Python dependencies
├── config.json               # User settings (auto-generated)
│
├── config/                   # Configuration files
│   └── log_aggregator.json   # Log aggregator config (NEW)
│
├── gui/                      # GUI components
│   ├── main_window.py        # Main window framework
│   ├── tab_connection.py     # Connection Monitor tab
│   ├── tab_config.py         # Configuration tab
│   └── widgets.py            # Reusable widgets
│
├── network/                  # Network layer
│   ├── tcp_client.py         # TCP command client
│   └── protocol.py           # Protocol message formatting
│
├── utils/                    # Utilities
│   ├── config.py             # Configuration management
│   ├── logger.py             # Application logging
│   └── protocol_loader.py    # Load protocol JSON files
│
└── logs/                     # Application logs (auto-generated)
    └── exports/              # Exported log files (NEW)
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
