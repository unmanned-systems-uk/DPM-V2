# DPM H16 Ground Station - ADB & Log Analysis Cheat Sheet

**Version:** 1.1
**Created:** October 30, 2025
**Updated:** October 30, 2025 - Added H16 System Architecture section
**Purpose:** Comprehensive diagnostic commands for troubleshooting DPM connectivity and Ground-Side Android app issues

---

## Table of Contents

1. [H16 System Architecture](#h16-system-architecture) **← START HERE!**
2. [Quick Diagnostics](#quick-diagnostics)
3. [ADB Connection](#adb-connection)
4. [Network Diagnostics](#network-diagnostics)
5. [VXLAN Tunnel Diagnostics](#vxlan-tunnel-diagnostics)
6. [DPM Application Logs](#dpm-application-logs)
7. [Air-Side Connectivity Tests](#air-side-connectivity-tests)
8. [Port and Service Checks](#port-and-service-checks)
9. [System Resource Monitoring](#system-resource-monitoring)
10. [Troubleshooting Scenarios](#troubleshooting-scenarios)
11. [Log Analysis Patterns](#log-analysis-patterns)

---

## H16 System Architecture

### 🎯 **CRITICAL: Understanding the Three-Device System**

The DPM system consists of **THREE separate network devices**, not two:

```
┌─────────────────────────────────────────────────────────────────┐
│                         AIR SIDE                                 │
│                                                                  │
│  ┌──────────────┐                                               │
│  │ Sony Camera  │ USB                                           │
│  └──────┬───────┘                                               │
│         │                                                        │
│         ▼                                                        │
│  ┌─────────────────────────────────────────────────────┐       │
│  │        Raspberry Pi 4 (External Payload)             │       │
│  │        IP: 192.168.144.20 (documented)               │       │
│  │        Running: payload_server on port 5000          │       │
│  │        OS: Ubuntu Server 22.04 LTS                   │       │
│  │        Role: Camera control via Sony SDK             │       │
│  └─────────────────┬───────────────────────────────────┘       │
│                    │ Ethernet                                   │
│                    ▼                                            │
│  ┌─────────────────────────────────────────────────────┐       │
│  │        R16 Air Unit (Network Bridge)                 │       │
│  │        IP: 192.168.144.10                            │       │
│  │        Status: ✅ RESPONDS TO PING                   │       │
│  │        OS: Embedded Linux (not Android)              │       │
│  │        Role: Wireless link bridge                    │       │
│  └─────────────────┬───────────────────────────────────┘       │
└────────────────────┼─────────────────────────────────────────────┘
                     │
                     │ VXLAN Tunnel (over 2.4/5.8 GHz)
                     │ - Transport: lmi40 network (192.168.0.0/24)
                     │ - VXLAN ID: 1
                     │ - Port: 4789
                     │
┌────────────────────┼─────────────────────────────────────────────┐
│                GROUND SIDE                                       │
│                    │                                             │
│  ┌─────────────────┴───────────────────────────────────┐       │
│  │        H16 Ground Station                            │       │
│  │        IP: 192.168.144.11 (br-vxlan interface)       │       │
│  │        Status: ✅ ONLINE (you are here via ADB)      │       │
│  │        OS: Android 7.1.2                             │       │
│  │        Hardware: SkyDroid arowana-rc (ARM64)         │       │
│  │        Running: DPM Android App                      │       │
│  └─────────────────────────────────────────────────────┘       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Device Roles Explained

| Device | IP Address | Role | ADB Access | Current Status |
|--------|-----------|------|------------|----------------|
| **H16 Ground Station** | 192.168.144.11 | Ground control, runs Android app | ✅ YES | ✅ ONLINE |
| **R16 Air Unit** | 192.168.144.10 | Network bridge (wireless link) | ❌ NO | ✅ ONLINE, port 5000 closed |
| **Raspberry Pi 4** | 192.168.144.20 | Camera control (payload_server) | ❌ NO | ❌ UNREACHABLE |

### Network Flow

**Data Path for Camera Commands:**
```
DPM App → TCP → 192.168.144.10 or .20 → VXLAN Tunnel →
R16 Air Unit (.10) → Ethernet → Raspberry Pi (.20) → Sony SDK → Camera
```

**The Question:**
- 📋 **Documentation says:** Connect to RPi at `192.168.144.20`
- ⚙️ **Code default:** Connects to `192.168.144.10` (R16 Air Unit)
- ❓ **Reality:** Need to determine which device actually runs payload_server

### Critical Configuration Point

**In NetworkSettings.kt, the default IP is:**
```kotlin
val targetIp: String = "192.168.144.10",  // Air-Side Pi ethernet address
```

**But there are TWO air-side devices:**
- **192.168.144.10** - R16 Air Unit (network bridge, currently responds to ping)
- **192.168.144.20** - Raspberry Pi 4 (payload computer, currently unreachable)

### Diagnostic Strategy

**To determine the correct target:**

1. **Check if RPi is powered and connected:**
   ```bash
   # From H16, check if RPi (.20) is reachable
   adb shell ping -c 4 192.168.144.20
   ```

2. **Check if R16 (.10) can forward to RPi:**
   ```bash
   # R16 responds to ping
   adb shell ping -c 4 192.168.144.10

   # But does it have port 5000 open?
   adb logcat -d | grep "Connection refused"
   ```

3. **Possible configurations:**
   - **Option A:** Payload_server runs on RPi (.20), R16 (.10) forwards traffic
   - **Option B:** Payload_server runs directly on R16 (.10)
   - **Option C:** RPi IP changed from .20 to something else

### Common Confusion Points

❗ **"Air-Side" refers to TWO devices:**
- R16 Air Unit (bridge at .10)
- Raspberry Pi 4 (payload at .20)

❗ **R16 Air Unit is NOT Android:**
- Cannot ADB into it
- Embedded Linux or custom firmware
- Acts as network bridge only

❗ **RPi cannot be accessed via ADB:**
- Runs Ubuntu Server (not Android)
- Use SSH for access (if enabled)

### Physical Connection Check

**To verify the complete system:**

```bash
# 1. Check VXLAN tunnel is up
adb shell ip -d link show vxlan1
# Look for: remote 192.168.0.10

# 2. Check R16 Air Unit responding
adb shell ping -c 4 192.168.144.10
# Should: 0% packet loss

# 3. Check RPi responding
adb shell ping -c 4 192.168.144.20
# If fails: RPi powered off or not connected

# 4. Check which device has port 5000 open
adb logcat -d | grep "192.168.144" | grep -E "(5000|Connection)"
```

---

## Quick Diagnostics

**Run these commands first to get an overview:**

```bash
# 1. Check ADB connection
adb devices

# 2. Check br-vxlan interface (should be 192.168.144.11)
adb shell ip addr show br-vxlan

# 3. Ping R16 Air Unit (network bridge at .10)
adb shell ping -c 4 192.168.144.10

# 4. Ping Raspberry Pi (payload computer at .20)
adb shell ping -c 4 192.168.144.20

# 5. Check recent DPM app errors
adb logcat -d | grep -E "NetworkClient|DPM" | tail -50
```

**Expected Results:**
- ✅ Device shows as "device" (not "unauthorized" or "offline")
- ✅ br-vxlan has IP 192.168.144.11/24 and state UP
- ✅ R16 (.10) responds to ping with 0% packet loss
- ✅ RPi (.20) responds to ping with 0% packet loss
- ✅ No "Connection refused" errors in logs

**If RPi (.20) unreachable:**
- ❌ Check if Raspberry Pi is powered on
- ❌ Check if RPi ethernet is connected to R16 Air Unit
- ❌ Payload_server cannot run if RPi is offline

---

## ADB Connection

### Connect to H16

**USB Connection:**
```bash
# Enable USB debugging on H16 (Settings > Developer Options)
# Connect USB cable
adb devices

# If "unauthorized", check H16 screen for authorization prompt
```

**Wireless Connection:**
```bash
# Method 1: If you know H16's IP address
adb connect 10.0.1.92:5555

# Method 2: Connect via USB first, then enable wireless
adb tcpip 5555
adb connect <H16_IP>:5555

# Verify connection
adb devices
# Should show: <IP>:5555    device
```

**Disconnect:**
```bash
adb disconnect 10.0.1.92:5555
```

### ADB Troubleshooting

**Device not showing:**
```bash
# Restart ADB server
adb kill-server
adb start-server
adb devices

# Check ADB server status
adb version

# Windows: Check if device drivers installed
# Linux: Check udev rules for USB permissions
```

**"Unauthorized" status:**
```bash
# 1. Check H16 screen for USB debugging authorization dialog
# 2. Accept and check "Always allow from this computer"
# 3. Verify:
adb devices
```

**Multiple devices connected:**
```bash
# List all devices
adb devices

# Target specific device for commands
adb -s <device_id> shell <command>

# Example:
adb -s 10.0.1.92:5555 shell ping 192.168.144.20
```

---

## Network Diagnostics

### Network Interfaces

**List all interfaces:**
```bash
adb shell ip addr show
```

**Key Interfaces:**
- **wlan0** - WiFi (typically 10.0.1.x range for external network)
- **lmi40** - Internal mesh network (192.168.0.11)
- **br-vxlan** - VXLAN bridge to Air-Side (192.168.144.11)
- **vxlan1** - Actual VXLAN tunnel interface
- **eth0** - Ethernet (typically 192.168.45.1, no-carrier if unplugged)

**Check specific interface:**
```bash
# br-vxlan (DPM Air-Side link)
adb shell ip addr show br-vxlan

# WiFi
adb shell ip addr show wlan0

# Internal mesh
adb shell ip addr show lmi40
```

**Check interface status:**
```bash
# All interfaces
adb shell ip link show

# Specific interface
adb shell ip link show br-vxlan

# Look for: state UP (good) or state DOWN (bad)
```

### Routing

**Show routing table:**
```bash
adb shell ip route show
```

**Expected Routes:**
```
10.0.1.0/24 dev wlan0                    # External WiFi network
192.168.0.0/24 dev lmi40                 # Internal mesh network
192.168.144.0/24 dev br-vxlan            # DPM Air-Side network ✓
192.168.45.0/24 dev eth0 linkdown        # Ethernet (optional)
```

**Check route to Air-Side:**
```bash
# Show route to 192.168.144.20
adb shell ip route get 192.168.144.20

# Expected: 192.168.144.20 dev br-vxlan src 192.168.144.11
```

**Trace route to Air-Side:**
```bash
adb shell traceroute 192.168.144.20
```

### WiFi Status

**WiFi connection info:**
```bash
# Detailed WiFi status
adb shell dumpsys wifi | grep -A 10 "mNetworkInfo"

# WiFi SSID and signal
adb shell dumpsys wifi | grep -E "SSID:|RSSI:"

# IP address
adb shell ip addr show wlan0 | grep "inet "
```

**WiFi signal strength:**
```bash
adb shell dumpsys wifi | grep "RSSI"
```

### DNS Resolution

**Test DNS:**
```bash
# Resolve hostname
adb shell nslookup google.com

# Check DNS servers
adb shell getprop net.dns1
adb shell getprop net.dns2
```

---

## VXLAN Tunnel Diagnostics

### VXLAN Interface Status

**Check VXLAN tunnel configuration:**
```bash
# Detailed VXLAN info
adb shell ip -d link show vxlan1

# Expected output:
# vxlan id 1 remote 192.168.0.10 dev lmi40 srcport 0 0 dstport 4789
```

**Key VXLAN Parameters:**
- **vxlan id** - VXLAN network ID (should be 1)
- **remote** - Air-Side physical endpoint (should be 192.168.0.10)
- **dev** - Transport interface (should be lmi40)
- **dstport** - VXLAN port (should be 4789)

**Check bridge configuration:**
```bash
# Show bridge members
adb shell bridge link show

# Expected: vxlan1 should be part of br-vxlan
```

**Check VXLAN forwarding database:**
```bash
# Show FDB entries
adb shell bridge fdb show dev vxlan1

# Look for: dst 192.168.0.10 (Air-Side physical address)
```

### VXLAN Tunnel Health

**Test physical link (lmi40 network):**
```bash
# Ping Air-Side's physical address on lmi40
adb shell ping -c 4 192.168.0.10

# ✅ Should succeed if Air-Side is powered on
# ❌ "Destination Host Unreachable" = Air-Side offline
```

**Test VXLAN tunnel (br-vxlan network):**
```bash
# Ping Air-Side through VXLAN tunnel
adb shell ping -c 4 192.168.144.20

# ✅ Should succeed if tunnel and payload_server running
# ❌ "Destination Host Unreachable" = Tunnel or Air-Side problem
```

**Check VXLAN statistics:**
```bash
# Interface statistics
adb shell ip -s link show vxlan1

# Look for RX/TX packets and errors
```

---

## DPM Application Logs

### Live Logcat Monitoring

**Monitor DPM app in real-time:**
```bash
# All DPM-related logs
adb logcat | grep -E "DPM|NetworkClient|Camera|System"

# Only errors
adb logcat | grep -E "DPM|NetworkClient" | grep -E "ERROR|FATAL"

# With timestamps
adb logcat -v time | grep "NetworkClient"

# Specific log level (E=Error, W=Warning, I=Info, D=Debug)
adb logcat NetworkClient:E *:S
```

**Color-coded live monitoring:**
```bash
# On Linux/Mac with grep colors
adb logcat | grep --color=always -E "ERROR|WARNING|SUCCESS|$"
```

### Historical Logs

**Recent DPM logs (last 100 lines):**
```bash
adb logcat -d | grep -E "DPM|NetworkClient" | tail -100
```

**Filter by time:**
```bash
# Logs from last 5 minutes
adb logcat -t '5 minutes ago' | grep NetworkClient

# Logs since specific time
adb logcat -t '10-30 13:00:00.000' | grep DPM
```

**Save logs to file:**
```bash
# Save full logcat
adb logcat -d > logcat_full.txt

# Save DPM logs only
adb logcat -d | grep -E "DPM|NetworkClient" > dpm_logs.txt

# Save with timestamp
adb logcat -d -v time > logcat_$(date +%Y%m%d_%H%M%S).txt
```

### Clear Logs

```bash
# Clear logcat buffer (start fresh)
adb logcat -c

# Then monitor new logs
adb logcat | grep DPM
```

### Specific DPM Components

**Network connection logs:**
```bash
adb logcat -d | grep "NetworkClient"
```

**Camera-related logs:**
```bash
adb logcat -d | grep "CameraViewModel\|CameraState"
```

**System status logs:**
```bash
adb logcat -d | grep "SystemStatus"
```

**Settings logs:**
```bash
adb logcat -d | grep "SettingsViewModel\|SettingsRepository"
```

---

## Air-Side Connectivity Tests

### Ping Tests

**Basic ping to Air-Side:**
```bash
# Standard ping (4 packets)
adb shell ping -c 4 192.168.144.20

# Continuous ping (Ctrl+C to stop)
adb shell ping 192.168.144.20

# Ping with specific interval
adb shell ping -i 0.2 -c 20 192.168.144.20  # 5 pings/second
```

**Interpret ping results:**
```bash
# ✅ Success:
# 64 bytes from 192.168.144.20: icmp_seq=1 ttl=64 time=1.23 ms
# 4 packets transmitted, 4 received, 0% packet loss

# ❌ Air-Side offline:
# From 192.168.144.11: icmp_seq=1 Destination Host Unreachable
# 4 packets transmitted, 0 received, +4 errors, 100% packet loss

# ⚠️ Network congestion:
# 4 packets transmitted, 4 received, 25% packet loss (1 lost)
```

**Ping through specific interface:**
```bash
# Force ping via br-vxlan
adb shell ping -I br-vxlan -c 4 192.168.144.20
```

### TCP Port Tests

**Test TCP port 5000 (command port):**
```bash
# Method 1: netcat (if available)
adb shell nc -zv 192.168.144.20 5000

# Method 2: Telnet (if available)
adb shell telnet 192.168.144.20 5000

# Method 3: Check via netstat
adb shell netstat -an | grep 5000
```

**Expected results:**
```bash
# ✅ Port open (payload_server running):
# Connection to 192.168.144.20 5000 port [tcp] succeeded!

# ❌ Port closed/filtered:
# Connection to 192.168.144.20 5000 port [tcp] failed: Connection refused
```

---

## Port and Service Checks

### Check Active Connections

**Show all connections:**
```bash
adb shell netstat -an
```

**Check DPM protocol ports:**
```bash
# All DPM ports (5000, 5001, 5002)
adb shell netstat -an | grep -E "(5000|5001|5002)"

# TCP connections only
adb shell netstat -ant | grep -E "(5000|5001|5002)"

# UDP connections only
adb shell netstat -anu | grep -E "(5001|5002)"
```

**Expected when connected:**
```
# TCP command connection
tcp    ESTABLISHED 192.168.144.11:45678 192.168.144.20:5000

# UDP status listener
udp    192.168.144.11:5001

# UDP heartbeat
udp    192.168.144.11:5002
```

### Check Listening Ports

**Show listening ports:**
```bash
# All listening
adb shell netstat -ln

# TCP listening only
adb shell netstat -lnt

# UDP listening only
adb shell netstat -lnu
```

**DPM app should be listening on:**
- UDP port 5001 (status broadcasts from Air-Side)
- UDP port 5002 (heartbeat)

### Process and Socket Info

**Find DPM app process:**
```bash
# Find process ID
adb shell ps | grep dpm_android

# Get detailed process info
adb shell ps -ef | grep dpm_android
```

**Check sockets for process:**
```bash
# List open files/sockets for DPM app
adb shell lsof | grep dpm_android

# Alternative: Check /proc filesystem
adb shell cat /proc/$(adb shell pidof uk.unmannedsystems.dpm_android)/net/tcp
```

---

## System Resource Monitoring

### CPU and Memory

**Current resource usage:**
```bash
# Top command (all processes)
adb shell top -n 1

# Top for DPM app only
adb shell top -n 1 | grep dpm_android

# CPU usage
adb shell dumpsys cpuinfo | grep dpm_android

# Memory usage
adb shell dumpsys meminfo uk.unmannedsystems.dpm_android
```

### Storage

**Check free space:**
```bash
# Disk usage
adb shell df -h

# Internal storage
adb shell df -h /data

# SD card (if present)
adb shell df -h /sdcard
```

### Battery

**Battery status:**
```bash
adb shell dumpsys battery
```

**Key fields:**
- level - Battery percentage
- temperature - Battery temp (in 0.1°C units)
- status - Charging status

### System Uptime

```bash
# System uptime
adb shell uptime

# Boot time
adb shell cat /proc/uptime
```

---

## Troubleshooting Scenarios

### Scenario 1: "Cannot Connect to Air-Side"

**Step-by-step diagnosis:**

```bash
# 1. Verify H16 br-vxlan is configured
adb shell ip addr show br-vxlan
# Expected: inet 192.168.144.11/24, state UP

# 2. Test physical link (lmi40)
adb shell ping -c 4 192.168.0.10
# If fails → Air-Side powered off or lmi40 network issue

# 3. Test VXLAN tunnel
adb shell ping -c 4 192.168.144.20
# If fails → VXLAN tunnel or Air-Side offline

# 4. Check TCP port 5000
adb shell netstat -an | grep 5000
# If no connection → payload_server not running

# 5. Check DPM app logs
adb logcat -d | grep "NetworkClient" | tail -50
# Look for "Connection refused" or timeout errors
```

**Common causes:**
- ❌ **Air-Side powered off** - Most common
- ❌ **payload_server not started on Air-Side**
- ❌ **Firewall blocking ports 5000/5001/5002**
- ❌ **VXLAN tunnel misconfigured**
- ❌ **Wrong IP address in DPM app settings**

### Scenario 2: "Connected but No Camera Control"

```bash
# 1. Check TCP connection established
adb shell netstat -an | grep 5000
# Should show ESTABLISHED

# 2. Check UDP broadcasts received
adb logcat | grep "UDP" | grep "status"
# Should see periodic status messages (5 Hz)

# 3. Check camera status in logs
adb logcat -d | grep "Camera" | tail -50
# Look for camera connection status

# 4. Test sending a command
# Open DPM app, try "Capture" button, watch logs:
adb logcat | grep "camera.capture"
```

**Common causes:**
- ❌ **Camera not connected to Air-Side**
- ❌ **Sony SDK not initialized**
- ❌ **USB permissions issue on Air-Side**
- ❌ **Command protocol version mismatch**

### Scenario 3: "App Crashes on Startup"

```bash
# 1. Clear logcat
adb logcat -c

# 2. Launch app
adb shell am start -n uk.unmannedsystems.dpm_android/.MainActivity

# 3. Check for crash
adb logcat | grep -E "FATAL|AndroidRuntime"

# 4. Get full crash stack trace
adb logcat -d | grep -A 50 "FATAL EXCEPTION"
```

**Common causes:**
- ❌ **Null pointer exception** - Check initialization
- ❌ **Missing permission** - Check AndroidManifest.xml
- ❌ **Network on main thread** - Should use coroutines
- ❌ **Resource not found** - Clean and rebuild app

### Scenario 4: "UDP Status Not Updating"

```bash
# 1. Check UDP listeners are bound
adb shell netstat -anu | grep -E "(5001|5002)"

# 2. Monitor UDP traffic
adb logcat | grep "UDP"

# 3. Check firewall rules
adb shell iptables -L -n | grep -E "(5001|5002)"

# 4. Test with tcpdump (if available)
adb shell tcpdump -i br-vxlan -n port 5001 or port 5002
```

**Common causes:**
- ❌ **SO_REUSEADDR not set** - Port binding error
- ❌ **UDP listener crashed** - Check error logs
- ❌ **Air-Side not broadcasting** - Check Air-Side logs
- ❌ **Firewall blocking UDP** - Check iptables

### Scenario 5: "High Latency / Lag"

```bash
# 1. Ping test with statistics
adb shell ping -c 50 192.168.144.20
# Check: min/avg/max/mdev times

# 2. Check packet loss
# Look for: 0% packet loss (good), >5% (bad)

# 3. Check VXLAN interface errors
adb shell ip -s link show vxlan1
# Look for: RX/TX errors, dropped packets

# 4. Check CPU usage
adb shell top -n 1 | head -20
# High CPU can cause network lag

# 5. Check WiFi signal
adb shell dumpsys wifi | grep RSSI
# Weak signal (<-70 dBm) causes latency
```

**Common causes:**
- ❌ **Weak WiFi signal** - Move closer to AP
- ❌ **Network congestion** - Other devices using bandwidth
- ❌ **CPU overload** - Too many apps running
- ❌ **Thermal throttling** - Device overheating

---

## Log Analysis Patterns

### Connection Success Pattern

```
D NetworkClient: Attempting connection to 192.168.144.20:5000
D NetworkClient: TCP socket connected
D NetworkClient: Sending handshake...
D NetworkClient: Handshake response received
I NetworkClient: Connection established successfully
D NetworkClient: Starting UDP listeners
D NetworkClient: UDP status listener started on port 5001
D NetworkClient: UDP heartbeat sender started
I NetworkClient: Connection state: CONNECTED
```

### Connection Failure Pattern

```
D NetworkClient: Attempting connection to 192.168.144.20:5000
E NetworkClient: Connection failed
E NetworkClient: java.net.ConnectException: Connection refused
E NetworkClient:     at java.net.PlainSocketImpl.socketConnect(Native Method)
E NetworkClient: Connection state: ERROR
```

### Camera Command Pattern

```
D CameraViewModel: Capture button clicked
D NetworkClient: Sending command: camera.capture
D NetworkClient: Command sent, sequenceId=123
D NetworkClient: Response received for sequenceId=123
I CameraViewModel: Capture successful
D NetworkClient: UDP status update: capturing=true
```

### Camera Property Change Pattern

```
D CameraViewModel: Setting shutter_speed to 1/2000
D NetworkClient: Sending command: camera.set_property
D NetworkClient: Parameters: {property=shutter_speed, value=1/2000}
D NetworkClient: Response received: SUCCESS
D NetworkClient: UDP status update: shutter_speed=1/2000
I CameraViewModel: Updating UI with new shutter_speed
```

### System Status Update Pattern

```
D NetworkClient: UDP status broadcast received (5 Hz)
D SystemStatusViewModel: CPU: 45.2%, Memory: 62.1%, Disk: 23.4 GB free
D NetworkClient: Heartbeat received from Air-Side
D NetworkClient: Last heartbeat: 234ms ago
```

### Error Patterns

**Network timeout:**
```
E NetworkClient: Connection timeout after 5000ms
E NetworkClient: java.net.SocketTimeoutException
```

**Permission denied:**
```
E NetworkClient: java.lang.SecurityException: Permission denied
E NetworkClient: Missing INTERNET permission
```

**Invalid JSON:**
```
E NetworkClient: Failed to parse response
E NetworkClient: com.google.gson.JsonSyntaxException
```

**UDP binding error:**
```
E NetworkClient: Failed to bind UDP socket to port 5001
E NetworkClient: java.net.BindException: Address already in use
```

---

## Advanced Commands

### Network Traffic Capture

**Capture packets (requires root or tcpdump):**
```bash
# Capture on br-vxlan
adb shell tcpdump -i br-vxlan -w /sdcard/capture.pcap

# Capture specific ports
adb shell tcpdump -i br-vxlan port 5000 or port 5001 or port 5002

# Pull capture file
adb pull /sdcard/capture.pcap
# Analyze with Wireshark on PC
```

### Firewall Rules

**Check iptables:**
```bash
# List all rules
adb shell iptables -L -n -v

# Check INPUT chain
adb shell iptables -L INPUT -n

# Check if ports are allowed
adb shell iptables -L -n | grep -E "(5000|5001|5002)"
```

### Performance Profiling

**Monitor network I/O:**
```bash
# Network statistics
adb shell cat /proc/net/dev

# Continuous monitoring
adb shell watch -n 1 cat /proc/net/dev
```

**CPU profiling for DPM app:**
```bash
adb shell dumpsys cpuinfo | grep dpm -A 10
```

### App Control

**Force stop app:**
```bash
adb shell am force-stop uk.unmannedsystems.dpm_android
```

**Launch app:**
```bash
adb shell am start -n uk.unmannedsystems.dpm_android/.MainActivity
```

**Clear app data:**
```bash
adb shell pm clear uk.unmannedsystems.dpm_android
```

**Reinstall APK:**
```bash
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

---

## Quick Reference Card

### Top 10 Most Useful Commands

```bash
# 1. Check connection
adb devices

# 2. Check br-vxlan
adb shell ip addr show br-vxlan

# 3. Ping Air-Side
adb shell ping -c 4 192.168.144.20

# 4. Live DPM logs
adb logcat | grep NetworkClient

# 5. Recent errors
adb logcat -d | grep -E "ERROR|FATAL" | grep DPM | tail -20

# 6. Check ports
adb shell netstat -an | grep -E "(5000|5001|5002)"

# 7. Check VXLAN tunnel
adb shell ip -d link show vxlan1

# 8. Test physical link
adb shell ping -c 4 192.168.0.10

# 9. System resources
adb shell top -n 1 | head -20

# 10. Save logs
adb logcat -d > dpm_debug_$(date +%Y%m%d_%H%M%S).txt
```

### Common IP Addresses

| Device/Interface | IP Address | Purpose | Notes |
|---|---|---|---|
| **H16 Ground Station** | 192.168.144.11 | br-vxlan (DPM protocol) | Android, runs DPM app |
| **R16 Air Unit** | 192.168.144.10 | Network bridge | Wireless link bridge |
| **Raspberry Pi 4** | 192.168.144.20 | Payload server | Runs payload_server (port 5000) |
| **R16 Air Unit lmi40** | 192.168.0.10 | Physical mesh network | VXLAN remote endpoint |
| **H16 Ground lmi40** | 192.168.0.11 | Physical mesh network | VXLAN local endpoint |
| **H16 WiFi** | 10.0.1.92 (example) | External network | Varies by WiFi AP |
| **H16 Ethernet** | 192.168.45.1 | Wired connection | Optional, usually no-carrier |

### Common Ports

| Port | Protocol | Purpose | Direction |
|---|---|---|---|
| **5000** | TCP | Command channel | Ground → Air |
| **5001** | UDP | Status broadcasts | Air → Ground (5 Hz) |
| **5002** | UDP | Heartbeat | Bidirectional (1 Hz) |
| **4789** | UDP | VXLAN tunnel | Ground ↔ Air |
| **5555** | TCP | ADB wireless | PC → H16 |

---

## Troubleshooting Decision Tree

```
Cannot connect to Air-Side?
│
├─→ 1. Can ping R16 Air Unit at 192.168.144.10? (Network bridge test)
│   ├─→ NO → VXLAN tunnel or R16 Air Unit issue
│   │         Action: Check vxlan1 interface, check R16 powered on
│   │         Command: adb shell ip -d link show vxlan1
│   │
│   └─→ YES (✅ R16 reachable) → Continue to RPi test
│       │
│       ├─→ 2. Can ping Raspberry Pi at 192.168.144.20? (Payload computer test)
│       │   ├─→ NO → RPi powered off or not connected to R16
│       │   │         Action: Power on RPi / Check ethernet to R16
│       │   │         Note: RPi must be on for payload_server
│       │   │
│       │   └─→ YES (✅ RPi reachable) → Continue to service test
│       │       │
│       │       ├─→ 3. Which IP is DPM app configured for?
│       │       │   Check: NetworkSettings.kt targetIp value
│       │       │
│       │       │   ├─→ If 192.168.144.10 (.10)
│       │       │   │   └─→ payload_server must run on R16 Air Unit
│       │       │   │       OR R16 must forward port 5000 to RPi
│       │       │   │
│       │       │   └─→ If 192.168.144.20 (.20)
│       │       │       └─→ payload_server must run on RPi
│       │       │
│       │       └─→ 4. TCP port 5000 open on target device?
│       │           Command: adb logcat -d | grep "Connection refused"
│       │
│       │           ├─→ NO (Connection refused)
│       │           │   Action: Start payload_server on target device
│       │           │   - If RPi: SSH and start service
│       │           │   - If R16: Check R16 configuration
│       │           │
│       │           └─→ YES (Port open) → Check DPM app
│       │                 Action: Check app logs for protocol errors
│
├─→ br-vxlan configured correctly on H16?
│   Command: adb shell ip addr show br-vxlan
│   ├─→ NO → Check H16 network configuration
│   └─→ YES → Continue diagnostic
│
└─→ DPM app installed and permissions granted?
    ├─→ NO → Install APK / Grant INTERNET permission
    └─→ YES → Check application logs
```

### Quick Test Sequence

```bash
# Run this complete test sequence:

echo "=== Test 1: H16 Ground Station ==="
adb devices
adb shell ip addr show br-vxlan | grep "inet 192.168.144.11"

echo "=== Test 2: R16 Air Unit (.10) ==="
adb shell ping -c 4 192.168.144.10

echo "=== Test 3: Raspberry Pi (.20) ==="
adb shell ping -c 4 192.168.144.20

echo "=== Test 4: Port 5000 Status ==="
adb logcat -d | grep -E "192.168.144|Connection" | tail -20

echo "=== Test 5: DPM App Configuration ==="
# Check NetworkSettings.kt for targetIp value
```

---

## Appendix: Log Message Interpretation

### Log Levels

- **V (Verbose)** - Detailed diagnostic info
- **D (Debug)** - Debug information
- **I (Info)** - Informational messages
- **W (Warning)** - Warning messages
- **E (Error)** - Error messages
- **F (Fatal)** - Fatal errors (app crashes)

### Common Error Messages

| Error Message | Meaning | Solution |
|---|---|---|
| **Connection refused** | Target port not listening | Start payload_server on Air-Side |
| **Destination Host Unreachable** | Network route not available | Check Air-Side powered on, VXLAN tunnel |
| **SocketTimeoutException** | Connection attempt timeout | Increase timeout / Check network |
| **BindException: Address already in use** | Port already bound | Kill old process / Use SO_REUSEADDR |
| **Permission denied** | Missing app permission | Add INTERNET permission to manifest |
| **JsonSyntaxException** | Malformed JSON response | Check protocol version mismatch |
| **NullPointerException** | Uninitialized object | Check initialization order |

---

## Document Version History

| Version | Date | Changes |
|---|---|---|
| 1.0 | Oct 30, 2025 | Initial creation with comprehensive diagnostics |
| 1.1 | Oct 30, 2025 | **MAJOR UPDATE:** Added H16 System Architecture section<br>- Clarified three-device system (H16, R16, RPi)<br>- Distinguished R16 Air Unit (.10) from Raspberry Pi (.20)<br>- Updated Quick Diagnostics to test both devices<br>- Updated IP address reference table<br>- Enhanced troubleshooting decision tree<br>- Added Quick Test Sequence |

---

**Maintained By:** Claude Code (Ground-Side Development)
**For Questions:** Refer to CC_READ_THIS_FIRST.md workflow documentation
**Related Docs:**
- `PROGRESS_AND_TODO.md` - Ground-Side development status
- `commands.json` - Protocol command definitions
- `camera_properties.json` - Camera property specifications
- `Updated_System_Architecture_H16.md` - Complete system architecture
