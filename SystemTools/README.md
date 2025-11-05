# DPM Windows Diagnostic Tool

**Version:** 1.0.0 (Phase 1 - Foundation)
**Platform:** Windows 11
**Python:** 3.8+

Comprehensive diagnostic and testing tool for DPM Payload Manager system.

---

## Quick Start

### 1. Install Python Dependencies

```bash
cd D:\DPM\DPM-V2\WindowsTools
pip install -r requirements.txt
```

**Note:** For Phase 1, only the following are needed:
- Python 3.8+ (with tkinter built-in)
- No external packages required for basic functionality!

For Phase 3 (Docker Logs) you'll need:
- `paramiko` (SSH client)
- `matplotlib` (graphs)

### 2. Run the Application

```bash
python main.py
```

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
WindowsTools/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── config.json            # User settings (auto-generated)
│
├── gui/                   # GUI components
│   ├── main_window.py     # Main window framework
│   ├── tab_connection.py  # Connection Monitor tab
│   ├── tab_config.py      # Configuration tab
│   └── widgets.py         # Reusable widgets
│
├── network/               # Network layer
│   ├── tcp_client.py      # TCP command client
│   └── protocol.py        # Protocol message formatting
│
├── utils/                 # Utilities
│   ├── config.py          # Configuration management
│   ├── logger.py          # Application logging
│   └── protocol_loader.py # Load protocol JSON files
│
└── logs/                  # Application logs (auto-generated)
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
