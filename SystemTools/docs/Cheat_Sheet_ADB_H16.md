# ADB Cheat Sheet for H16 Development

**Date:** October 25, 2025  
**Target Device:** SkyDroid H16 Ground Station (10.0.1.92:5555)  
**Project:** Drone Payload Manager (DPM)

---

## 🔌 Connection Management

### Connect to H16

```cmd
# Connect to H16 wirelessly:
adb connect 10.0.1.92:5555

# Disconnect from H16:
adb disconnect 10.0.1.92:5555

# Disconnect all devices:
adb disconnect
```

### Check Connected Devices

```cmd
# List all connected devices:
adb devices

# Expected output:
# List of devices attached
# 10.0.1.92:5555  device

# List with more details:
adb devices -l
```

### ADB Server Management

```cmd
# Kill ADB server (use when troubleshooting):
adb kill-server

# Start ADB server:
adb start-server

# Restart ADB server (full reset):
adb kill-server && adb start-server

# Check ADB version:
adb version
```

### Fix "Offline" Device

```cmd
# Quick reconnect:
adb disconnect 10.0.1.92:5555 && adb connect 10.0.1.92:5555

# Full reset and reconnect:
adb kill-server && adb start-server && adb connect 10.0.1.92:5555 && adb devices
```

---

## 📦 App Installation & Management

### Install APK

```cmd
# Install app:
adb install app-debug.apk

# Install with full path:
adb install C:\path\to\app-debug.apk

# Reinstall (replace existing):
adb install -r app-debug.apk

# Install to specific device (if multiple connected):
adb -s 10.0.1.92:5555 install app-debug.apk

# Install and grant all permissions:
adb install -g app-debug.apk
```

### Uninstall App

```cmd
# Uninstall by package name:
adb uninstall com.yourcompany.payloadmanager

# Keep app data:
adb uninstall -k com.yourcompany.payloadmanager

# Uninstall from specific device:
adb -s 10.0.1.92:5555 uninstall com.yourcompany.payloadmanager
```

### List Installed Apps

```cmd
# List all packages:
adb shell pm list packages

# List 3rd party (user) apps only:
adb shell pm list packages -3

# List system apps:
adb shell pm list packages -s

# Search for specific app:
adb shell pm list packages | findstr payload

# List with file paths:
adb shell pm list packages -f

# List disabled apps:
adb shell pm list packages -d

# List enabled apps:
adb shell pm list packages -e
```

### App Information

```cmd
# Get detailed app info:
adb shell dumpsys package com.yourcompany.payloadmanager

# Get app installation path:
adb shell pm path com.yourcompany.payloadmanager

# Get app version:
adb shell dumpsys package com.yourcompany.payloadmanager | findstr versionName

# Get app permissions:
adb shell dumpsys package com.yourcompany.payloadmanager | findstr permission

# Check if app is installed:
adb shell pm list packages | findstr payloadmanager
```

---

## 🚀 Launch & Control Apps

### Start Activity

```cmd
# Launch your app's main activity:
adb shell am start -n com.yourcompany.payloadmanager/.MainActivity

# Launch with action:
adb shell am start -a android.intent.action.MAIN

# Launch with data:
adb shell am start -n com.yourcompany.payloadmanager/.MainActivity -d "content://data"

# Launch specific device:
adb -s 10.0.1.92:5555 shell am start -n com.yourcompany.payloadmanager/.MainActivity
```

### Stop App

```cmd
# Force stop app:
adb shell am force-stop com.yourcompany.payloadmanager

# Kill app process:
adb shell am kill com.yourcompany.payloadmanager
```

### Clear App Data

```cmd
# Clear all app data and cache:
adb shell pm clear com.yourcompany.payloadmanager

# This is like "Clear Data" in Settings
```

### Broadcast Intent

```cmd
# Send broadcast:
adb shell am broadcast -a android.intent.action.BOOT_COMPLETED

# Send custom broadcast to your app:
adb shell am broadcast -a com.yourcompany.payloadmanager.CUSTOM_ACTION
```

---

## 📱 Device Information

### System Properties

```cmd
# Get Android version:
adb shell getprop ro.build.version.release

# Get API level:
adb shell getprop ro.build.version.sdk

# Get device model:
adb shell getprop ro.product.model

# Get device manufacturer:
adb shell getprop ro.product.manufacturer

# Get serial number:
adb shell getprop ro.serialno

# List all properties:
adb shell getprop

# Get specific property:
adb shell getprop [property.name]
```

### Device Status

```cmd
# Get device info:
adb shell dumpsys

# Get battery info:
adb shell dumpsys battery

# Get memory info:
adb shell dumpsys meminfo

# Get CPU info:
adb shell cat /proc/cpuinfo

# Get storage info:
adb shell df -h

# Get network info:
adb shell ip addr show

# Get running services:
adb shell dumpsys activity services
```

### Display Information

```cmd
# Get screen size:
adb shell wm size

# Get screen density:
adb shell wm density

# Get display info:
adb shell dumpsys display
```

---

## 📝 Logging & Debugging

### Logcat (View Logs)

```cmd
# View all logs (live):
adb logcat

# Clear logs first, then view:
adb logcat -c && adb logcat

# Filter by tag:
adb logcat | findstr "PayloadManager"

# Filter by package name:
adb logcat | findstr "com.yourcompany"

# Filter by log level (Error only):
adb logcat *:E

# Filter by log level (Warning and above):
adb logcat *:W

# Save logs to file:
adb logcat > C:\logs\h16-log.txt

# View logs with timestamp:
adb logcat -v time

# View logs with thread info:
adb logcat -v threadtime

# Specific device logs:
adb -s 10.0.1.92:5555 logcat
```

### Log Levels

```
V - Verbose (lowest priority)
D - Debug
I - Info
W - Warning
E - Error
F - Fatal
S - Silent (highest priority, nothing)
```

### Advanced Logcat

```cmd
# Filter by tag AND level:
adb logcat PayloadManager:D *:S

# Multiple tags:
adb logcat PayloadManager:D NetworkClient:D *:S

# View last 100 lines:
adb logcat -t 100

# Dump logs and exit (don't follow):
adb logcat -d

# Clear log buffer:
adb logcat -c

# View specific buffer:
adb logcat -b main      # Main log buffer
adb logcat -b system    # System log buffer
adb logcat -b radio     # Radio log buffer
adb logcat -b events    # Event log buffer
adb logcat -b crash     # Crash log buffer
```

---

## 💾 File Transfer

### Push (PC → Device)

```cmd
# Push file to device:
adb push local-file.txt /sdcard/

# Push with full paths:
adb push C:\files\config.json /sdcard/Download/

# Push entire folder:
adb push C:\folder /sdcard/folder

# Push to app's private directory (if app has permission):
adb push file.txt /data/data/com.yourcompany.payloadmanager/files/
```

### Pull (Device → PC)

```cmd
# Pull file from device:
adb pull /sdcard/file.txt C:\downloads\

# Pull without destination (saves to current directory):
adb pull /sdcard/file.txt

# Pull entire folder:
adb pull /sdcard/Download C:\downloads\

# Pull app APK:
adb pull /data/app/com.yourcompany.payloadmanager-1/base.apk

# Pull database:
adb pull /data/data/com.yourcompany.payloadmanager/databases/app.db
```

---

## 🖥️ Shell Commands

### Interactive Shell

```cmd
# Open shell on device:
adb shell

# Once in shell, you can run Linux commands:
# ls, cd, cat, grep, ps, top, etc.

# Exit shell:
exit
```

### Single Commands

```cmd
# Run single command (no interactive shell):
adb shell ls /sdcard/

# Echo test:
adb shell echo "Hello from H16"

# Check if file exists:
adb shell ls /sdcard/myfile.txt

# Read file contents:
adb shell cat /sdcard/file.txt

# Search in file:
adb shell grep "error" /sdcard/log.txt

# Get file size:
adb shell du -h /sdcard/large-file.mp4
```

### Process Management

```cmd
# List running processes:
adb shell ps

# Find specific process:
adb shell ps | findstr payload

# Kill process by name:
adb shell pkill -9 com.yourcompany.payloadmanager

# Kill process by PID:
adb shell kill 1234

# Top (CPU usage):
adb shell top -n 1
```

### Network Commands

```cmd
# Show network interfaces:
adb shell ip addr show

# Show network statistics:
adb shell netstat

# Ping from device:
adb shell ping -c 4 10.0.1.20

# Check port:
adb shell netstat -an | findstr 5555

# DNS lookup:
adb shell nslookup google.com

# Test connection (if nc available):
adb shell nc -zv 10.0.1.20 5000
```

---

## 📸 Screenshots & Screen Recording

### Screenshot

```cmd
# Take screenshot:
adb shell screencap -p /sdcard/screen.png

# Take and pull in one command:
adb shell screencap -p /sdcard/screen.png && adb pull /sdcard/screen.png

# Save directly to PC (without intermediate storage):
adb exec-out screencap -p > C:\screenshots\screen.png
```

### Screen Recording

```cmd
# Record screen (up to 3 minutes default):
adb shell screenrecord /sdcard/demo.mp4

# Press Ctrl+C to stop recording

# Record with time limit (seconds):
adb shell screenrecord --time-limit 30 /sdcard/demo.mp4

# Record at lower resolution:
adb shell screenrecord --size 1280x720 /sdcard/demo.mp4

# Record with bit rate (default 4Mbps):
adb shell screenrecord --bit-rate 6000000 /sdcard/demo.mp4

# Pull recorded video:
adb pull /sdcard/demo.mp4 C:\videos\
```

---

## ⚙️ System Control

### Reboot & Power

```cmd
# Reboot device:
adb reboot

# Reboot to bootloader:
adb reboot bootloader

# Reboot to recovery:
adb reboot recovery

# Power off (if supported):
adb shell reboot -p
```

### Input Simulation

```cmd
# Simulate key press:
adb shell input keyevent KEYCODE_HOME
adb shell input keyevent KEYCODE_BACK
adb shell input keyevent KEYCODE_MENU
adb shell input keyevent 3    # Home (by code)

# Simulate text input:
adb shell input text "Hello"

# Simulate tap (x y coordinates):
adb shell input tap 500 500

# Simulate swipe (x1 y1 x2 y2 duration):
adb shell input swipe 500 1000 500 300 500
```

### Settings

```cmd
# Get setting:
adb shell settings get global airplane_mode_on

# Set setting:
adb shell settings put global airplane_mode_on 0

# List all settings:
adb shell settings list global
adb shell settings list system
adb shell settings list secure
```

---

## 🔐 Permissions

### Grant/Revoke Permissions

```cmd
# Grant permission:
adb shell pm grant com.yourcompany.payloadmanager android.permission.CAMERA

# Revoke permission:
adb shell pm revoke com.yourcompany.payloadmanager android.permission.CAMERA

# Grant all permissions at install:
adb install -g app-debug.apk

# List all permissions for app:
adb shell dumpsys package com.yourcompany.payloadmanager | findstr permission
```

### Common Permissions

```cmd
android.permission.INTERNET
android.permission.ACCESS_NETWORK_STATE
android.permission.ACCESS_WIFI_STATE
android.permission.CAMERA
android.permission.WRITE_EXTERNAL_STORAGE
android.permission.READ_EXTERNAL_STORAGE
android.permission.ACCESS_FINE_LOCATION
android.permission.ACCESS_COARSE_LOCATION
android.permission.RECORD_AUDIO
android.permission.WAKE_LOCK
```

---

## 🌐 Network & Wireless ADB

### Enable Wireless ADB (From Shell)

```cmd
# Enable wireless ADB on port 5555:
adb shell setprop service.adb.tcp.port 5555
adb shell stop adbd
adb shell start adbd

# Disable wireless ADB (back to USB):
adb shell setprop service.adb.tcp.port -1
adb shell stop adbd
adb shell start adbd
```

### WiFi Management

```cmd
# Turn WiFi on:
adb shell svc wifi enable

# Turn WiFi off:
adb shell svc wifi disable

# Get WiFi status:
adb shell dumpsys wifi | findstr "Wi-Fi is"

# Get current WiFi network:
adb shell dumpsys wifi | findstr "SSID"

# Get IP address:
adb shell ip addr show wlan0
```

---

## 🧰 Troubleshooting Commands

### Connection Issues

```cmd
# Full connection reset:
adb disconnect
adb kill-server
adb start-server
adb connect 10.0.1.92:5555
adb devices

# Check if device is reachable:
ping 10.0.1.92

# Check if port is open:
telnet 10.0.1.92 5555

# Clear cached device:
adb reconnect
```
## 🧰 Troubleshooting port Commands
You can check if a port is open on Windows 11 using the Command Prompt or PowerShell. Use netstat -an in Command Prompt to see all listening ports, or Test-NetConnection in PowerShell to test a specific port on a remote host. 
Method 1: Using Command Prompt
Open Command Prompt by pressing Win + R, typing cmd, and pressing Enter.
To see all ports that are actively listening, type netstat -an | find "LISTEN" and press Enter.
To find which process is using a specific port, use the command netstat -ano | find "LISTEN" to show the Process ID (PID), then use netstat -an | find "<PID>" to identify the process.
To check if a specific port is open (e.g., port 80), type netstat -an | find ":80" and press Enter. 
Method 2: Using PowerShell
Open PowerShell as an administrator. Click the Start menu, type PowerShell, right-click Windows PowerShell, and select Run as administrator.
To check a specific port on a remote computer, use the command Test-NetConnection <hostname or IP address> -Port <port number>. For example, Test-NetConnection google.com -Port 443. 
Method 3: Using Telnet (requires enabling the client) 
Enable the Telnet client: Search for "Turn Windows features on or off," check the box for "Telnet Client," and click OK.
Open Command Prompt.
Type telnet <hostname or IP address> <port number> (e.g., telnet google.com 80). If the port is open, a blinking cursor will appear. If it's closed, you will see a "Connection failed" message. 


### Performance Issues

```cmd
# Check memory usage:
adb shell dumpsys meminfo com.yourcompany.payloadmanager

# Check CPU usage:
adb shell top -n 1 | findstr payload

# Check storage:
adb shell df -h

# Check battery:
adb shell dumpsys battery

# Monitor memory in real-time:
adb shell watch cat /proc/meminfo
```

### App Issues

```cmd
# Check if app is running:
adb shell ps | findstr payload

# Check app's current activity:
adb shell dumpsys activity activities | findstr payload

# Get app crash logs:
adb logcat -b crash

# Get ANR (Application Not Responding) logs:
adb pull /data/anr/traces.txt
```

---

## 🎯 DPM-Specific Quick Commands

### Deploy & Test Your App

```cmd
# Build, install, and launch (one-liner):
adb install -r app-debug.apk && adb shell am start -n com.yourcompany.payloadmanager/.MainActivity

# Install and follow logs:
adb install -r app-debug.apk && adb logcat | findstr PayloadManager

# Clear data and restart:
adb shell pm clear com.yourcompany.payloadmanager && adb shell am start -n com.yourcompany.payloadmanager/.MainActivity
```

### Monitor Network Connectivity

```cmd
# Check if can reach Pi:
adb shell ping -c 3 10.0.1.20

# Check if Pi port is reachable:
adb shell nc -zv 10.0.1.20 5000

# Monitor network in real-time:
adb shell netstat -an | findstr 5000
```

### Debug Camera Connection

```cmd
# List USB devices (camera):
adb shell lsusb

# Check USB permissions:
adb shell ls -l /dev/bus/usb/

# Monitor USB events:
adb logcat | findstr -i usb
```

---

## 📋 Batch Scripts for Common Tasks

### reconnect-h16.bat

```batch
@echo off
adb disconnect
adb kill-server
timeout /t 2 /nobreak >nul
adb start-server
adb connect 10.0.1.92:5555
adb devices
pause
```

### deploy-and-test.bat

```batch
@echo off
echo Building APK...
cd /d C:\path\to\your\project
call gradlew assembleDebug

echo Installing to H16...
adb -s 10.0.1.92:5555 install -r app\build\outputs\apk\debug\app-debug.apk

echo Launching app...
adb -s 10.0.1.92:5555 shell am start -n com.yourcompany.payloadmanager/.MainActivity

echo Monitoring logs...
adb -s 10.0.1.92:5555 logcat | findstr PayloadManager

pause
```

### clean-install.bat

```batch
@echo off
echo Uninstalling old version...
adb -s 10.0.1.92:5555 uninstall com.yourcompany.payloadmanager

echo Installing fresh copy...
adb -s 10.0.1.92:5555 install app-debug.apk

echo Granting permissions...
adb -s 10.0.1.92:5555 shell pm grant com.yourcompany.payloadmanager android.permission.INTERNET
adb -s 10.0.1.92:5555 shell pm grant com.yourcompany.payloadmanager android.permission.WAKE_LOCK

echo Launching app...
adb -s 10.0.1.92:5555 shell am start -n com.yourcompany.payloadmanager/.MainActivity

pause
```

---

## 🚀 Quick Reference Card

### Most Used Commands

```cmd
# Connect
adb connect 10.0.1.92:5555

# Check connection
adb devices

# Install app
adb install -r app-debug.apk

# Launch app
adb shell am start -n com.yourcompany.payloadmanager/.MainActivity

# View logs
adb logcat | findstr PayloadManager

# Stop app
adb shell am force-stop com.yourcompany.payloadmanager

# Uninstall app
adb uninstall com.yourcompany.payloadmanager

# Reboot device
adb reboot

# Shell access
adb shell
```

---

## 💡 Pro Tips

### Multiple Devices

When you have both H16 and emulator connected:

```cmd
# Always specify device:
adb -s 10.0.1.92:5555 [command]
adb -s emulator-5554 [command]

# Or set environment variable:
set ANDROID_SERIAL=10.0.1.92:5555
# Now all adb commands target H16 by default
```

### Alias for Quick Access

Create shortcuts in your shell:

```cmd
# In PowerShell profile:
function h16 { adb -s 10.0.1.92:5555 $args }

# Now use:
h16 install app-debug.apk
h16 logcat
h16 shell
```

### Save Frequent Commands

Create `.bat` files for your most-used command sequences and keep them in your project root.

---

## 📞 Emergency Commands

```cmd
# Device frozen:
adb reboot

# Connection lost:
adb kill-server && adb start-server && adb connect 10.0.1.92:5555

# App won't stop:
adb shell am force-stop com.yourcompany.payloadmanager
adb shell pm clear com.yourcompany.payloadmanager

# Can't find device IP:
for /L %i in (1,1,254) do @ping -n 1 -w 100 10.0.1.%i | findstr "Reply"

# Wireless ADB stopped working:
# Re-enable on H16 via Settings → Developer Options → ADB over network
```

---

## 📱 H16-SIDE DIAGNOSTICS & TROUBLESHOOTING

**When PC-side troubleshooting fails, diagnose from H16 using Termux**

### Access H16 via Termux

```bash
# On H16, open Termux app and run these commands
```

### Check ADB Daemon Status

```bash
# Check if adbd (ADB daemon) is running:
ps -A | grep adbd

# Expected output:
# u0_a123  12345  1234  1234567  12345 0 S adbd

# If not running, ADB is not active on H16
```

### Check Network Interfaces

```bash
# Show all network interfaces and IP addresses:
ip addr show

# Check WiFi interface (typically wlan0):
ip addr show wlan0

# Verify H16 has correct IP (should be 10.0.1.92):
ip addr show | grep "inet 10.0.1"

# Expected output:
# inet 10.0.1.92/24 brd 10.0.1.255 scope global wlan0
```

### Check Port 5555 Status

```bash
# Check if something is listening on port 5555:
netstat -anp | grep 5555

# Alternative (if netstat not available):
ss -tulpn | grep 5555

# Expected output if ADB is running:
# tcp    0    0 0.0.0.0:5555    0.0.0.0:*    LISTEN    12345/adbd
# tcp    0    0 10.0.1.92:5555  10.0.1.37:65204  ESTABLISHED  12345/adbd

# If no output, port 5555 is not open (ADB over network not enabled)
```

### Check Active Connections

```bash
# Show all TCP connections:
netstat -ant

# Show only ESTABLISHED connections:
netstat -ant | grep ESTABLISHED

# Check for connections from PC (10.0.1.37):
netstat -ant | grep 10.0.1.37

# If you see connections on random ports but not 5555, ADB over network is disabled
```

### Check ADB Over Network Setting

```bash
# Check if ADB over network is enabled (requires root or special permissions):
getprop service.adb.tcp.port

# Expected output:
# 5555  (if enabled)
# -1    (if disabled - USB only mode)

# Check ADB status:
getprop init.svc.adbd

# Expected output:
# running  (ADB daemon is active)
# stopped  (ADB daemon not running)
```

### Check Firewall Rules (Requires Root)

```bash
# Check if iptables is blocking port 5555 (requires root):
su
iptables -L -n -v | grep 5555

# Check all INPUT chain rules:
iptables -L INPUT -n -v

# Check if there are any DROP or REJECT rules affecting port 5555
```

### Test Network Connectivity to PC

```bash
# Ping the PC (10.0.1.37):
ping -c 4 10.0.1.37

# Expected output should show replies:
# 64 bytes from 10.0.1.37: icmp_seq=1 ttl=128 time=5.2 ms

# If "Destination Host Unreachable" or 100% packet loss:
# - PC firewall blocking ICMP
# - Network routing issue
# - Not on same network
```

### Test Reverse Connection

```bash
# Try to connect to PC's ADB server (port 5037):
# This tests if PC can receive connections
nc -zv 10.0.1.37 5037

# Or using telnet:
telnet 10.0.1.37 5037

# If connection refused:
# - PC firewall blocking incoming connections
# - PC ADB server not running
```

### Check Running Processes

```bash
# Check what processes are using network:
lsof -i -n | head -20

# Check specifically for ADB-related processes:
ps -A | grep -E 'adb|daemon'

# Check for DPM Ground-Side app:
ps -A | grep payloadmanager

# Get PID of DPM app:
pidof com.uksystems.payloadmanager
```

### Restart ADB on H16

```bash
# Method 1: Toggle ADB setting via settings command (no root needed):
# Disable ADB over network:
settings put global adb_wifi_enabled 0

# Wait 2 seconds:
sleep 2

# Enable ADB over network:
settings put global adb_wifi_enabled 1

# Method 2: Restart ADB daemon (requires root):
su
stop adbd
sleep 2
start adbd

# Method 3: Via Android settings (Manual):
# Settings → Developer Options → Wireless debugging → Toggle OFF/ON
# or
# Settings → Developer Options → ADB over network → Toggle OFF/ON
```

### Check Developer Options Settings

```bash
# Check if Developer Options are enabled:
settings get global development_settings_enabled

# Expected output:
# 1  (enabled)
# 0  (disabled)

# Check USB debugging status:
settings get global adb_enabled

# Expected output:
# 1  (enabled)
# 0  (disabled)

# Check wireless ADB:
settings get global adb_wifi_enabled

# Expected output:
# 1  (enabled)
# 0  (disabled)
```

### View System Logs

```bash
# View recent system logs related to ADB:
logcat -d -s adbd:*

# View logs with timestamp:
logcat -d -v time -s adbd:*

# Watch live ADB logs:
logcat -s adbd:*

# Look for errors:
logcat -d -s adbd:E

# Common errors to look for:
# - "failed to bind"  (port already in use)
# - "connection refused"  (PC side issue)
# - "permission denied"  (security/SELinux issue)
```

### Check SELinux Status

```bash
# Check if SELinux is enforcing (may block ADB):
getenforce

# Expected outputs:
# Enforcing  (strict security, may block ADB)
# Permissive (relaxed, usually allows ADB)
# Disabled   (no SELinux)

# If Enforcing, check SELinux denials related to ADB:
dmesg | grep -i avc | grep -i adbd

# Temporarily set to Permissive for testing (requires root):
su
setenforce 0
```

### Complete H16 Diagnostic Script

```bash
#!/bin/bash
# Save as h16-adb-diagnostic.sh and run in Termux

echo "======================================"
echo "H16 ADB Diagnostic Report"
echo "======================================"

echo -e "\n1. ADB Daemon Status:"
ps -A | grep adbd || echo "  [!] adbd not running!"

echo -e "\n2. Network Interfaces:"
ip addr show | grep -E "inet |wlan0|eth0"

echo -e "\n3. Port 5555 Status:"
netstat -anp 2>/dev/null | grep 5555 || echo "  [!] Port 5555 not in use!"

echo -e "\n4. ADB TCP Port Setting:"
PORT=$(getprop service.adb.tcp.port)
if [ "$PORT" = "5555" ]; then
  echo "  [✓] ADB over network enabled (port $PORT)"
else
  echo "  [!] ADB over network DISABLED (port $PORT)"
fi

echo -e "\n5. ADB Daemon Service:"
STATUS=$(getprop init.svc.adbd)
if [ "$STATUS" = "running" ]; then
  echo "  [✓] adbd is running"
else
  echo "  [!] adbd is $STATUS"
fi

echo -e "\n6. Developer Settings:"
DEV=$(settings get global development_settings_enabled)
ADB=$(settings get global adb_enabled)
WIFI=$(settings get global adb_wifi_enabled)
echo "  Developer Options: $DEV (1=enabled, 0=disabled)"
echo "  USB Debugging: $ADB (1=enabled, 0=disabled)"
echo "  ADB WiFi: $WIFI (1=enabled, 0=disabled)"

echo -e "\n7. Test Ping to PC (10.0.1.37):"
ping -c 2 10.0.1.37 2>/dev/null && echo "  [✓] PC reachable" || echo "  [!] PC unreachable"

echo -e "\n8. Active Connections:"
netstat -ant 2>/dev/null | grep ESTABLISHED | head -5

echo -e "\n9. DPM App Status:"
if pidof com.uksystems.payloadmanager > /dev/null; then
  echo "  [✓] DPM app is running"
else
  echo "  [!] DPM app is NOT running"
fi

echo -e "\n======================================"
echo "Diagnostic Complete"
echo "======================================"
```

### Quick H16 Fixes

```bash
# Fix 1: Restart ADB network service
settings put global adb_wifi_enabled 0
sleep 2
settings put global adb_wifi_enabled 1

# Fix 2: Check and fix IP address
# If H16 has wrong IP, reconnect to WiFi

# Fix 3: Enable ADB if disabled
settings put global adb_enabled 1
settings put global adb_wifi_enabled 1

# Fix 4: View recent ADB errors
logcat -d -s adbd:E -t 50
```

### Common H16-Side Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Port 5555 not listening | ADB over network disabled | Enable in Developer Options or `settings put global adb_wifi_enabled 1` |
| adbd not running | ADB service stopped | Restart phone or toggle Developer Options |
| Wrong IP address | DHCP changed IP or wrong network | Check `ip addr show` and reconnect WiFi |
| Connection immediately drops | SELinux blocking | Check `getenforce`, try `setenforce 0` (root) |
| "Connection refused" | Firewall or adbd not bound to 0.0.0.0 | Check `netstat -anp \| grep 5555` |
| Port shows LISTEN but PC can't connect | H16 firewall/iptables | Check `iptables -L INPUT` (root) |
| Can ping but can't connect ADB | Port 5555 blocked | Check firewall rules, toggle ADB setting |

### Interpreting Netstat Output

```bash
# Good - ADB is listening and has connection:
tcp    0    0 0.0.0.0:5555    0.0.0.0:*       LISTEN      12345/adbd
tcp    0    0 10.0.1.92:5555  10.0.1.37:65204 ESTABLISHED 12345/adbd

# Bad - No port 5555 at all:
# (no output) = ADB over network not enabled

# Bad - Listening but no ESTABLISHED connection:
tcp    0    0 0.0.0.0:5555    0.0.0.0:*       LISTEN      12345/adbd
# PC is not connected or connection dropped
```

### Enable ADB Over Network (Manual Steps)

1. **Via Settings App:**
   ```
   Settings → About Phone → Tap "Build Number" 7 times
   Settings → Developer Options → Enable "Developer Options"
   Settings → Developer Options → Enable "USB debugging"
   Settings → Developer Options → Enable "ADB over network" or "Wireless debugging"
   ```

2. **Via Termux (No Root):**
   ```bash
   settings put global development_settings_enabled 1
   settings put global adb_enabled 1
   settings put global adb_wifi_enabled 1
   ```

3. **Via Termux (Root):**
   ```bash
   su
   setprop service.adb.tcp.port 5555
   stop adbd
   start adbd
   ```

---

**Document Version:** 1.1
**Last Updated:** November 7, 2025
**Target:** SkyDroid H16 Ground Station
**IP:** 10.0.1.92:5555
**Project:** Drone Payload Manager

---
