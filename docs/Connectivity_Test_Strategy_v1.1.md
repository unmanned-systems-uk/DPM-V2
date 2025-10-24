# Connectivity Test Strategy
## Testing Initial Communication Between Android App and Raspberry Pi

**Version:** 1.1
**Date:** October 22, 2025
**Purpose:** Comprehensive testing strategy for validating network connectivity
**Updated:** Added Air Side specific testing considerations

---

## Overview

This document outlines the testing strategy for validating the initial connectivity between the DPM Android app running on the H16 Ground Station and the Payload Manager service running on the Raspberry Pi.

### Test Objectives

1. **Verify network connectivity** between H16 and Raspberry Pi
2. **Validate protocol implementation** on both sides
3. **Test error handling** and recovery mechanisms
4. **Measure performance** (latency, bandwidth, reliability)
5. **Ensure robustness** under various conditions

---

## Air Side Specific Testing Notes

### Pre-Testing Checklist for Air Side

Before running any connectivity tests, verify the Air Side service is properly built and deployed:

#### Build Verification
```bash
# Verify binary exists
ls -lh /home/dpm/payload_manager/build/payload_manager

# Check binary is executable
file /home/dpm/payload_manager/build/payload_manager

# Verify all shared libraries are available
ldd /home/dpm/payload_manager/build/payload_manager
```

Expected: All dependencies resolved, no "not found" errors.

#### Service Startup Verification
```bash
# Start service manually for testing
cd /home/dpm/payload_manager/build
./payload_manager

# Should see log output indicating:
# - TCP server started on port 5000
# - UDP broadcaster started on port 5001
# - Heartbeat handler started on port 5002
# - No errors or crashes
```

#### Log File Verification
```bash
# Check logs are being written
tail -f /var/log/payload_manager.log

# Should see:
# - Initialization messages
# - Service startup confirmation
# - Network listener confirmation
# - Regular heartbeat and status messages
```

#### Process Monitoring
```bash
# Verify service is running
ps aux | grep payload_manager

# Check resource usage
top -p $(pidof payload_manager)

# Should see:
# - Process running continuously
# - CPU usage < 30%
# - Memory usage < 256 MB
```

### C++ Specific Testing Considerations

#### Memory Leak Detection
```bash
# Run with valgrind (development/testing only)
valgrind --leak-check=full \
         --show-leak-kinds=all \
         --track-origins=yes \
         --log-file=valgrind.log \
         ./payload_manager

# Let run for 5 minutes, then check log
# Expected: No memory leaks, all allocations freed
```

#### Thread Safety Verification
```bash
# Run with thread sanitizer (requires rebuild)
# In CMakeLists.txt: add -fsanitize=thread
cmake -DCMAKE_CXX_FLAGS="-fsanitize=thread" ..
make clean && make
./payload_manager

# Expected: No data race warnings
```

#### Performance Profiling
```bash
# Profile CPU usage
perf record -g ./payload_manager
# Run tests for 2 minutes, then Ctrl+C
perf report

# Check for hot spots, ensure no unexpected bottlenecks
```

### Phase 1 MVP Test Priorities

For the initial Phase 1 implementation, prioritize these tests:

**Critical (Must Pass):**
1. Test 1.1: Ping Test
2. Test 1.2: Port Availability  
3. Test 2.1: TCP Command Test (handshake)
4. Test 2.1: TCP Command Test (system.get_status)
5. Test 2.2: UDP Status Broadcast Test
6. Test 2.3: Heartbeat Exchange Test
7. Test 3.1: Connect Button Test

**Important (Should Pass):**
8. Test 3.2: Status Reception Test
9. Test 3.3: Disconnect Test
10. Test 4.1: Pi Unavailable Test
11. Test 4.2: Connection Loss Test

**Nice to Have (Can be refined):**
12. Test 4.3: Invalid Command Test
13. Test 4.4: Timeout Test
14. Test 5.1: Latency Measurement
15. Test 5.2: Status Broadcast Frequency

### Testing with Stub Camera

Since Phase 1 uses a camera stub (no real Sony SDK integration):

**Expected Camera Status in Messages:**
```json
"camera": {
  "connected": false,
  "model": "stub_camera",
  "battery_percent": 0,
  "remaining_shots": 0,
  "status": "not_connected"
}
```

**Do NOT test:**
- Camera property changes
- Image capture
- Camera-specific commands (will return "not implemented" error)

**DO test:**
- Stub camera status included in broadcasts
- Graceful error responses for camera commands
- System continues working despite no camera

### Automated Test Script Template

```bash
#!/bin/bash
# automated_phase1_test.sh
# Automated connectivity testing for Phase 1

set -e

PI_IP="192.168.144.20"
LOG_FILE="test_results_$(date +%Y%m%d_%H%M%S).log"

echo "=== DPM Phase 1 Connectivity Test ===" | tee $LOG_FILE
echo "Target: $PI_IP" | tee -a $LOG_FILE
echo "Start: $(date)" | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE

# Test 1.1: Ping
echo "Test 1.1: Ping Test" | tee -a $LOG_FILE
if ping -c 5 -W 1 $PI_IP > /dev/null 2>&1; then
    echo "  ✅ PASS: Ping successful" | tee -a $LOG_FILE
else
    echo "  ❌ FAIL: Ping failed" | tee -a $LOG_FILE
fi

# Test 1.2: Port Availability
echo "Test 1.2: Port Availability" | tee -a $LOG_FILE
if nc -zv $PI_IP 5000 2>&1 | grep -q "succeeded"; then
    echo "  ✅ PASS: TCP port 5000 open" | tee -a $LOG_FILE
else
    echo "  ❌ FAIL: TCP port 5000 not accessible" | tee -a $LOG_FILE
fi

# Test 2.1: TCP Command (handshake)
echo "Test 2.1: TCP Handshake" | tee -a $LOG_FILE
RESPONSE=$(echo '{"protocol_version":"1.0","message_type":"command","sequence_id":1,"timestamp":1729339200,"payload":{"command":"handshake","parameters":{"client_id":"test","client_version":"1.0.0"}}}' | nc -w 5 $PI_IP 5000)
if echo "$RESPONSE" | jq -e '.payload.status == "success"' > /dev/null 2>&1; then
    echo "  ✅ PASS: Handshake successful" | tee -a $LOG_FILE
else
    echo "  ❌ FAIL: Handshake failed or invalid response" | tee -a $LOG_FILE
fi

# Test 2.1: TCP Command (system.get_status)
echo "Test 2.1: System Status Command" | tee -a $LOG_FILE
RESPONSE=$(echo '{"protocol_version":"1.0","message_type":"command","sequence_id":2,"timestamp":1729339200,"payload":{"command":"system.get_status","parameters":{}}}' | nc -w 5 $PI_IP 5000)
if echo "$RESPONSE" | jq -e '.payload.status == "success"' > /dev/null 2>&1; then
    echo "  ✅ PASS: System status command successful" | tee -a $LOG_FILE
else
    echo "  ❌ FAIL: System status command failed" | tee -a $LOG_FILE
fi

# Test 2.2: UDP Status Broadcast
echo "Test 2.2: UDP Status Broadcast" | tee -a $LOG_FILE
BROADCAST=$(timeout 2 nc -u -l 5001 2>/dev/null || true)
if echo "$BROADCAST" | jq -e '.message_type == "status"' > /dev/null 2>&1; then
    echo "  ✅ PASS: Status broadcast received" | tee -a $LOG_FILE
else
    echo "  ❌ FAIL: No status broadcast received" | tee -a $LOG_FILE
fi

echo "" | tee -a $LOG_FILE
echo "Test complete: $(date)" | tee -a $LOG_FILE
echo "Full results in: $LOG_FILE"
```

### Integration with Android App

**Test Sequence with Real Android App:**

1. **Start Air Side service** on Raspberry Pi
2. **Verify logs** show service running
3. **Open DPM Android app** on H16
4. **Navigate to Settings** → Network Configuration
5. **Verify settings:**
   - IP: 192.168.144.20
   - Command Port: 5000
   - Status Port: 5001
   - Heartbeat Port: 5002
6. **Tap "Connect"**
7. **Observe connection status** changes to CONNECTED
8. **Observe status updates** appearing on camera screen
9. **Check Air Side logs** for connection messages
10. **Tap "Disconnect"**
11. **Verify clean shutdown** in logs

**Android LogCat Commands:**
```bash
# View all DPM-related logs
adb logcat | grep -E "DPM|NetworkClient|PayloadManager"

# View only errors
adb logcat *:E | grep -E "DPM|NetworkClient"

# Clear logs before test
adb logcat -c

# Save logs after test
adb logcat -d > android_test_logs.txt
```

---

## Test Environment Setup

### Hardware Requirements

```
┌─────────────────────┐         ┌──────────────────────┐
│  H16 Ground Station │         │   Raspberry Pi SBC   │
│                     │         │                      │
│  - Android App      │◄───────►│  - Payload Manager  │
│  - IP: .144.11     │ Ethernet │  - IP: .144.20      │
└─────────────────────┘         └──────────────────────┘
         │                               │
         └───────────── Network ─────────┘
              192.168.144.0/24
```

### Software Requirements

**Android App:**
- DPM Android v1.0+ installed on H16
- Network settings configured correctly
- Logging enabled

**Raspberry Pi:**
- Payload Manager service installed
- Network configured (192.168.144.20)
- Service enabled and running
- Logging enabled

### Network Configuration Verification

Before testing, verify:

```bash
# On Raspberry Pi
ip addr show eth0 | grep inet  # Should show 192.168.144.20

# Test ping from Pi to H16
ping -c 5 192.168.144.11

# Verify services are listening
sudo netstat -tulpn | grep -E '5000|5001|5002'
```

Expected output:
```
tcp   0.0.0.0:5000   LISTEN   12345/payload_manager
udp   0.0.0.0:5001   LISTEN   12345/payload_manager
udp   0.0.0.0:5002   LISTEN   12345/payload_manager
```

---

## Test Phases

### Phase 1: Network Layer Tests

**Purpose:** Verify basic network connectivity

#### Test 1.1: Ping Test
```bash
# From H16 (if shell access available)
ping -c 10 192.168.144.20

# Expected: < 10ms latency, 0% packet loss
```

**Success Criteria:**
- [ ] Ping successful
- [ ] Average RTT < 10ms
- [ ] 0% packet loss

#### Test 1.2: Port Availability
```bash
# From H16 or test machine
nc -zv 192.168.144.20 5000  # TCP command port
nc -zuv 192.168.144.20 5001 # UDP status port
nc -zuv 192.168.144.20 5002 # UDP heartbeat port
```

**Success Criteria:**
- [ ] TCP port 5000 is open
- [ ] UDP ports 5001, 5002 are accessible

#### Test 1.3: Network Throughput
```bash
# Install iperf3 on both sides
# On Pi: iperf3 -s
# On H16: iperf3 -c 192.168.144.20 -t 30

# Expected: > 10 Mbps
```

**Success Criteria:**
- [ ] Throughput > 10 Mbps
- [ ] No packet loss during test

---

### Phase 2: Protocol Layer Tests

**Purpose:** Verify message format and protocol compliance

#### Test 2.1: Manual TCP Command Test

Use a simple TCP client to send a test command:

```bash
# Using netcat
echo '{"protocol_version":"1.0","message_type":"command","sequence_id":1,"timestamp":1729339200,"payload":{"command":"system.get_status","parameters":{}}}' | nc 192.168.144.20 5000
```

**Expected Response:**
```json
{
  "protocol_version": "1.0",
  "message_type": "response",
  "sequence_id": 1,
  "timestamp": 1729339201,
  "payload": {
    "command": "system.get_status",
    "status": "success",
    "result": {
      "uptime_seconds": 3600,
      ...
    }
  }
}
```

**Success Criteria:**
- [ ] Response received within 5 seconds
- [ ] JSON is valid
- [ ] sequence_id matches request
- [ ] status is "success"

#### Test 2.2: UDP Status Broadcast Test

Listen for status broadcasts:

```bash
# On H16 or test machine
nc -u -l 5001

# Should receive messages every 200ms
```

**Success Criteria:**
- [ ] Messages received at ~5 Hz (200ms interval)
- [ ] JSON is valid
- [ ] Contains system, camera status
- [ ] sequence_id increments monotonically

#### Test 2.3: Heartbeat Exchange Test

Send and receive heartbeat messages:

```python
import socket
import json
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', 5002))

while True:
    # Send heartbeat
    heartbeat = {
        'protocol_version': '1.0',
        'message_type': 'heartbeat',
        'sequence_id': int(time.time()),
        'timestamp': int(time.time()),
        'payload': {
            'sender': 'ground',
            'uptime_seconds': 0
        }
    }
    sock.sendto(json.dumps(heartbeat).encode(), ('192.168.144.20', 5002))

    # Receive heartbeat
    sock.settimeout(2.0)
    try:
        data, addr = sock.recvfrom(4096)
        print(f"Received: {data.decode()}")
    except socket.timeout:
        print("No heartbeat received")

    time.sleep(1)
```

**Success Criteria:**
- [ ] Heartbeat sent successfully
- [ ] Heartbeat received from Pi within 2 seconds
- [ ] Heartbeat exchange continues every ~1 second

---

### Phase 3: Application Layer Tests

**Purpose:** Test Android app connectivity features

#### Test 3.1: Connect Button Test

**Procedure:**
1. Open DPM Android app
2. Navigate to Settings
3. Verify network settings:
   - Target IP: 192.168.144.20
   - Command Port: 5000
   - Status Port: 5001
   - Heartbeat Port: 5002
4. Tap "Connect to Raspberry Pi"

**Success Criteria:**
- [ ] Connection status changes to "CONNECTING"
- [ ] Connection status changes to "CONNECTED" within 5 seconds
- [ ] No error messages displayed
- [ ] Android log shows handshake exchange

**Expected Log Output:**
```
NetworkClient: Connecting to 192.168.144.20
NetworkClient: Sending command: {"protocol_version":"1.0",...}
NetworkClient: Handshake response: {"protocol_version":"1.0",...}
NetworkClient: Connected to 192.168.144.20
```

#### Test 3.2: Status Reception Test

**Procedure:**
1. With connection established
2. Observe camera screen
3. Verify status updates appear

**Success Criteria:**
- [ ] Battery level updates (even if stub/0%)
- [ ] Camera connection status shows correctly
- [ ] Remaining shots count updates (even if 0)
- [ ] Updates occur smoothly (no freezing)

#### Test 3.3: Disconnect Test

**Procedure:**
1. With connection established
2. Navigate to Settings
3. Tap "Disconnect"

**Success Criteria:**
- [ ] Connection status changes to "DISCONNECTED"
- [ ] Status updates stop
- [ ] No crash or error messages
- [ ] Pi logs show graceful disconnect

---

### Phase 4: Error Handling Tests

**Purpose:** Verify robustness and error recovery

#### Test 4.1: Pi Unavailable Test

**Procedure:**
1. Stop Payload Manager service on Pi
2. Attempt to connect from Android app

**Success Criteria:**
- [ ] Connection status shows "ERROR"
- [ ] Error message displayed: "Connection failed"
- [ ] App doesn't crash
- [ ] Automatic retry begins after 2 seconds

#### Test 4.2: Connection Loss Test

**Procedure:**
1. Establish connection
2. Disconnect network cable on Pi
3. Reconnect network cable after 10 seconds

**Success Criteria:**
- [ ] App detects connection loss within 5 seconds
- [ ] Connection status changes to "ERROR"
- [ ] Automatic reconnection occurs when network restored
- [ ] Connection re-established within 5 seconds of network restore

#### Test 4.3: Invalid Command Test

Send an invalid command via the app (requires debug feature):

```json
{
  "command": "invalid.command",
  "parameters": {}
}
```

**Success Criteria:**
- [ ] Response received with status "error"
- [ ] Error code 5003 (Unknown command)
- [ ] App handles error gracefully
- [ ] No crash

#### Test 4.4: Timeout Test

**Procedure:**
1. Modify Pi service to delay response by 10 seconds
2. Send command from app

**Success Criteria:**
- [ ] App times out after 5 seconds
- [ ] Appropriate error message shown
- [ ] Connection remains stable (no crash)

---

### Phase 5: Performance Tests

**Purpose:** Measure system performance under normal conditions

#### Test 5.1: Latency Measurement

**Procedure:**
1. Send 100 commands sequentially
2. Measure round-trip time for each
3. Calculate average, min, max latency

**Tools:**
```python
import time

latencies = []
for i in range(100):
    start = time.time()
    response = await network_client.sendCommand("system.get_status")
    end = time.time()
    latencies.append((end - start) * 1000)  # ms

print(f"Avg: {sum(latencies)/len(latencies):.2f}ms")
print(f"Min: {min(latencies):.2f}ms")
print(f"Max: {max(latencies):.2f}ms")
```

**Success Criteria:**
- [ ] Average latency < 50ms
- [ ] Max latency < 200ms
- [ ] No timeouts

#### Test 5.2: Status Broadcast Frequency

**Procedure:**
1. Record timestamps of 100 status messages
2. Calculate inter-arrival times
3. Verify 5 Hz rate (200ms ± 50ms)

**Success Criteria:**
- [ ] Average interval: 200ms ± 20ms
- [ ] No missed messages
- [ ] Jitter < 50ms

#### Test 5.3: High-Frequency Command Test

**Procedure:**
1. Send camera property changes rapidly (10/second)
2. Monitor for command loss or errors
3. Run for 60 seconds

**Success Criteria:**
- [ ] All commands receive responses
- [ ] No errors due to rate limiting
- [ ] System remains responsive

---

### Phase 6: Integration Tests

**Purpose:** Test complete workflows

#### Test 6.1: Camera Control Workflow

**Procedure:**
1. Connect to Pi
2. Attempt to change shutter speed using app UI
3. Attempt to change aperture using app UI
4. Attempt to change ISO using app UI
5. Attempt capture using capture button

**Success Criteria (Phase 1 with stub):**
- [ ] All commands receive responses
- [ ] Responses indicate "not implemented" or "camera not connected"
- [ ] No crashes or hangs
- [ ] Status continues to update

#### Test 6.2: Connection Lifecycle Test

**Procedure:**
1. Start with app closed and Pi service running
2. Open app
3. Connect to Pi
4. Use app for 5 minutes (attempt commands)
5. Disconnect
6. Close app
7. Repeat 3 times

**Success Criteria:**
- [ ] Connection succeeds every time
- [ ] No memory leaks (check with Android Profiler)
- [ ] No connection hangs
- [ ] Clean disconnect every time

---

## Test Tools and Utilities

### Command-Line Testing Scripts

#### 1. Simple TCP Test Client

```python
#!/usr/bin/env python3
"""Simple TCP test client for DPM protocol"""

import socket
import json
import sys
import time

def send_command(ip, port, command, parameters):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))

    message = {
        'protocol_version': '1.0',
        'message_type': 'command',
        'sequence_id': 1,
        'timestamp': int(time.time()),
        'payload': {
            'command': command,
            'parameters': parameters
        }
    }

    sock.send((json.dumps(message) + '\n').encode())
    response = sock.recv(4096).decode()

    print("Response:", json.dumps(json.loads(response), indent=2))
    sock.close()

if __name__ == '__main__':
    send_command('192.168.144.20', 5000, 'system.get_status', {})
```

#### 2. UDP Status Listener

```python
#!/usr/bin/env python3
"""Listen for UDP status broadcasts"""

import socket
import json

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', 5001))

print("Listening for status broadcasts on port 5001...")

while True:
    data, addr = sock.recvfrom(4096)
    message = json.loads(data.decode())
    print(f"[{message['timestamp']}] seq={message['sequence_id']} "
          f"battery={message['payload']['camera']['battery_percent']}%")
```

#### 3. Heartbeat Monitor

```python
#!/usr/bin/env python3
"""Monitor heartbeat exchange"""

import socket
import json
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', 5002))
sock.settimeout(2.0)

last_heartbeat = 0

while True:
    try:
        data, addr = sock.recvfrom(1024)
        now = time.time()
        interval = now - last_heartbeat if last_heartbeat else 0
        print(f"Heartbeat from {addr} interval={interval:.3f}s")
        last_heartbeat = now
    except socket.timeout:
        print("WARNING: No heartbeat received in 2 seconds")
```

---

## Test Reporting

### Test Report Template

```markdown
# DPM Connectivity Test Report

**Date:** YYYY-MM-DD
**Tester:** Name
**Environment:** H16 + Raspberry Pi Model X

## Summary
- Total Tests: XX
- Passed: XX
- Failed: XX
- Skipped: XX

## Phase 1: Network Layer
- [ ] Test 1.1: Ping Test - PASS/FAIL
- [ ] Test 1.2: Port Availability - PASS/FAIL
- [ ] Test 1.3: Network Throughput - PASS/FAIL

## Phase 2: Protocol Layer
- [ ] Test 2.1: TCP Command Test - PASS/FAIL
- [ ] Test 2.2: UDP Status Test - PASS/FAIL
- [ ] Test 2.3: Heartbeat Test - PASS/FAIL

## Phase 3: Application Layer
- [ ] Test 3.1: Connect Button - PASS/FAIL
- [ ] Test 3.2: Status Reception - PASS/FAIL
- [ ] Test 3.3: Disconnect - PASS/FAIL

## Phase 4: Error Handling
- [ ] Test 4.1: Pi Unavailable - PASS/FAIL
- [ ] Test 4.2: Connection Loss - PASS/FAIL
- [ ] Test 4.3: Invalid Command - PASS/FAIL
- [ ] Test 4.4: Timeout - PASS/FAIL

## Phase 5: Performance
- [ ] Test 5.1: Latency (avg __ms, max __ms) - PASS/FAIL
- [ ] Test 5.2: Broadcast Freq (avg __ms) - PASS/FAIL
- [ ] Test 5.3: High Freq Commands - PASS/FAIL

## Phase 6: Integration
- [ ] Test 6.1: Camera Workflow - PASS/FAIL
- [ ] Test 6.2: Lifecycle Test - PASS/FAIL

## Issues Found
1. Issue description
   - Severity: High/Medium/Low
   - Steps to reproduce
   - Expected vs Actual

## Performance Metrics
- Average latency: __ms
- Status broadcast interval: __ms
- Connection time: __ms

## Recommendations
- List any recommendations
```

---

## Debugging Tips

### Android App Debugging

```bash
# View Android logs in real-time
adb logcat | grep -i "NetworkClient\|DPM"

# Filter for errors only
adb logcat *:E | grep NetworkClient

# Save logs to file
adb logcat -d > dpm_android_log.txt
```

### Raspberry Pi Debugging

```bash
# View service logs
tail -f /var/log/payload_manager.log

# Check network traffic
sudo tcpdump -i eth0 -n port 5000 or port 5001 or port 5002

# Monitor system resources
htop
```

### Network Packet Analysis

```bash
# Capture packets on Pi
sudo tcpdump -i eth0 -w dpm_traffic.pcap

# Analyze with Wireshark
wireshark dpm_traffic.pcap
```

---

## Success Criteria Summary

The initial connectivity implementation is considered successful when:

- [ ] All Phase 1 tests pass (Network Layer)
- [ ] All Phase 2 tests pass (Protocol Layer)
- [ ] All Phase 3 tests pass (Application Layer)
- [ ] At least 80% of Phase 4 tests pass (Error Handling)
- [ ] Performance metrics meet targets (Phase 5)
- [ ] Core workflows function correctly (Phase 6)
- [ ] No critical bugs identified
- [ ] System stable for 1-hour continuous operation

---

## Next Steps After Testing

1. **Document all findings** in test report
2. **Fix critical issues** identified during testing
3. **Re-test** failed test cases
4. **Update protocol** if necessary based on learnings
5. **Verify build and deployment process** is reproducible
6. **Begin Phase 2 development** (Camera Control) only after Phase 1 complete

---

**Document Status:** Complete ✅
**Ready for:** Testing
**Version:** 1.1
**Last Updated:** October 22, 2025
**Added:** Air Side testing considerations and automated test scripts
