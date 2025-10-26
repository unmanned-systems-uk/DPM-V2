# DPM Android Connection Monitoring Guide

## Quick Start

Double-click any of these batch files to start monitoring:

### 1. `monitor_connection.bat` - **RECOMMENDED FOR MOST USERS**
**What it shows:**
- Connection status (CONNECTED, ERROR, DISCONNECTED)
- Commands being sent to Air-Side
- Heartbeat activity
- Errors and warnings

**Best for:** General monitoring and troubleshooting

---

### 2. `monitor_commands_only.bat` - **CLEAN VIEW**
**What it shows:**
- ONLY commands sent to Air-Side
- Camera property changes (shutter, aperture, ISO)
- Command responses
- Errors

**Best for:** Watching what commands are being sent without status spam

**Example output:**
```
22:31:05.123 D/CameraViewModel: Setting camera property: shutter_speed = 1/1000
22:31:05.125 D/NetworkClient: Sending command: {"command":"camera.set_property"...}
22:31:10.234 E/NetworkClient: Error sending command: SocketTimeoutException
```

---

### 3. `monitor_detailed.bat` - **DEBUG MODE**
**What it shows:**
- EVERYTHING (very verbose!)
- All network debug messages
- Full JSON payloads
- Internal state changes

**Best for:** Deep debugging and development

---

## What to Look For

### ✅ **Healthy Connection**
```
Connection status updated: CONNECTED
```
- Appears every ~1 second
- Indicates active UDP status broadcasts

### ⚠️ **Commands Being Sent**
```
Setting camera property: shutter_speed = 1/1000
Sending command: {"message_type":"command"...}
```
- Shows user actions (tapping UI)
- Commands are sent via TCP

### ❌ **Air-Side Not Responding**
```
ERROR: Read timed out
ERROR: Heartbeat timeout: No response for 5000ms
Connection status updated: ERROR
```
- Air-Side software not running or crashed
- Network disconnected
- Pi unreachable

### 🟢 **Heartbeats Received**
```
Heartbeat received from Air-Side at 1234567890
```
- Confirms Air-Side is alive and responding
- Should appear every 1-2 seconds

---

## Command Line Monitoring (Alternative)

If you prefer command line, you can use these directly:

### Basic Monitoring
```cmd
adb -s 10.0.1.92:5555 logcat -v time NetworkClient:I NetworkManager:I CameraViewModel:I *:S
```

### Commands Only
```cmd
adb -s 10.0.1.92:5555 logcat -v time NetworkClient:D CameraViewModel:D *:S | findstr "Sending command"
```

### Full Debug
```cmd
adb -s 10.0.1.92:5555 logcat -v time NetworkClient:D NetworkManager:D CameraViewModel:D *:S
```

---

## Understanding Log Levels

- `D` = Debug (detailed information)
- `I` = Info (important events)
- `W` = Warning (potential issues)
- `E` = Error (failures)

---

## Troubleshooting

**No output appearing?**
1. Check device is connected: `adb devices`
2. Ensure app is running on device
3. Try clearing log first: `adb -s 10.0.1.92:5555 logcat -c`

**Too much spam?**
- Use `monitor_commands_only.bat` for cleaner output
- Connection status updates every second are normal

**Connection shows ERROR?**
- Check if Air-Side software is running on Pi
- Verify IP address: 192.168.144.20
- Check Pi is reachable: `ping 192.168.144.20`

---

## Current Configuration

- **Target IP:** 192.168.144.20
- **Command Port:** 5000 (TCP)
- **Status Port:** 5001 (UDP receive)
- **Heartbeat Port:** 5002 (UDP send)
- **Heartbeat Receive Port:** 6002 (UDP receive)
- **Heartbeat Timeout:** 5 seconds

---

*Created: 2025-10-26*
*Location: D:\DPM\DPM-V2\android\*
