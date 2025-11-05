# Payload Manager Command Protocol Specification
## Android App ↔ Raspberry Pi SBC Communication Protocol

**Version:** 1.0  
**Date:** October 19, 2025  
**Status:** Draft for Review

---

## Table of Contents

1. [Overview](#overview)
2. [Transport Layer](#transport-layer)
3. [Message Format](#message-format)
4. [Command Messages (Ground → Air)](#command-messages)
5. [Status Messages (Air → Ground)](#status-messages)
6. [Error Handling](#error-handling)
7. [Connection Management](#connection-management)
8. [Implementation Examples](#implementation-examples)
9. [Protocol Evolution](#protocol-evolution)

---

## Overview

### Purpose
Define a reliable, efficient communication protocol between the Android ground control application running on the H16 Ground Station and the Payload Manager service running on the Raspberry Pi SBC.

### Design Principles
1. **Simplicity:** Easy to implement and debug
2. **Reliability:** Handle network interruptions gracefully
3. **Efficiency:** Minimize bandwidth usage
4. **Extensibility:** Easy to add new commands/features
5. **Human-readable:** Use JSON for debuggability

### Communication Pattern
```
┌─────────────────────────┐         ┌──────────────────────────┐
│   Android App (H16)     │         │  Raspberry Pi Service    │
│                         │         │                          │
│  Commands (TCP) ─────────────────>│  Execute & Respond       │
│                         │         │                          │
│  Status (UDP)  <─────────────────│  Periodic Broadcast      │
│                         │         │                          │
│  Heartbeat (UDP) <─────────────>│  Keep-alive              │
└─────────────────────────┘         └──────────────────────────┘
```

---

## Transport Layer

### Network Configuration

#### Air Side (Raspberry Pi)
```yaml
Network Interface: eth0
IP Address: 192.168.144.20 (static)
Subnet Mask: 255.255.255.0
Gateway: 192.168.144.1

Services:
  TCP Command Server:
    Port: 5000
    Purpose: Receive commands from ground
    Protocol: TCP (reliable delivery)
  
  UDP Status Publisher:
    Port: 5001
    Purpose: Broadcast status to ground
    Protocol: UDP (low latency)
    Frequency: 5 Hz (200ms interval)
  
  UDP Heartbeat:
    Port: 5002
    Purpose: Connection keep-alive
    Protocol: UDP (bidirectional)
    Frequency: 1 Hz (1000ms interval)
```

#### Ground Side (H16 Android)
```yaml
Network Interface: H16 internal interface
IP Address: 192.168.144.11 (assigned by H16)

Clients:
  TCP Command Client:
    Target: 192.168.144.20:5000
    Purpose: Send commands to Pi
  
  UDP Status Receiver:
    Listen Port: 5001
    Purpose: Receive status updates
  
  UDP Heartbeat:
    Target/Listen: 192.168.144.20:5002
    Purpose: Bidirectional keep-alive
```

### Protocol Stack
```
┌─────────────────────────────────────────┐
│  Application Layer (JSON Messages)      │
├─────────────────────────────────────────┤
│  Session Layer (Connection Management)  │
├─────────────────────────────────────────┤
│  Transport Layer (TCP/UDP)              │
├─────────────────────────────────────────┤
│  Network Layer (IP)                     │
├─────────────────────────────────────────┤
│  Data Link (Ethernet)                   │
├─────────────────────────────────────────┤
│  Physical (H16 R16 Digital Link)        │
└─────────────────────────────────────────┘
```

---

## Message Format

### General Message Structure

All messages use **JSON format** for human readability and ease of implementation.

#### Base Message Schema
```json
{
  "protocol_version": "1.0",
  "message_type": "command|status|heartbeat|response",
  "sequence_id": 12345,
  "timestamp": 1729339200,
  "payload": {
    // Message-specific content
  }
}
```

#### Field Definitions
- **protocol_version** (string): Protocol version (semantic versioning)
- **message_type** (string): Type of message (command, status, heartbeat, response)
- **sequence_id** (integer): Monotonically increasing sequence number
- **timestamp** (integer): Unix timestamp (seconds since epoch)
- **payload** (object): Message-specific data

### Message Size Limits
- **TCP Messages:** Max 64 KB (typical: 1-4 KB)
- **UDP Messages:** Max 1472 bytes (safe for single packet)
- **JSON encoding:** UTF-8

---

## Command Messages (Ground → Air)

### Command Message Format
```json
{
  "protocol_version": "1.0",
  "message_type": "command",
  "sequence_id": 12345,
  "timestamp": 1729339200,
  "payload": {
    "command": "command_name",
    "parameters": {
      // Command-specific parameters
    }
  }
}
```

### Camera Control Commands

#### 1. Set Camera Property
```json
{
  "protocol_version": "1.0",
  "message_type": "command",
  "sequence_id": 1001,
  "timestamp": 1729339200,
  "payload": {
    "command": "camera.set_property",
    "parameters": {
      "property": "shutter_speed|aperture|iso|white_balance|focus_mode|file_format",
      "value": "property-specific-value"
    }
  }
}
```

**Examples:**

**Shutter Speed:**
```json
{
  "payload": {
    "command": "camera.set_property",
    "parameters": {
      "property": "shutter_speed",
      "value": {
        "numerator": 1,
        "denominator": 1000
      }
    }
  }
}
```

**Aperture:**
```json
{
  "payload": {
    "command": "camera.set_property",
    "parameters": {
      "property": "aperture",
      "value": 2.8
    }
  }
}
```

**ISO:**
```json
{
  "payload": {
    "command": "camera.set_property",
    "parameters": {
      "property": "iso",
      "value": 400
    }
  }
}
```

**White Balance Mode:**
```json
{
  "payload": {
    "command": "camera.set_property",
    "parameters": {
      "property": "white_balance",
      "value": {
        "mode": "auto|daylight|cloudy|tungsten|fluorescent|flash|color_temp|custom",
        "color_temp": 5600,  // optional, if mode is "color_temp"
        "fine_tune": {       // optional
          "green_magenta": 0,  // -9 to +9
          "amber_blue": 0      // -9 to +9
        }
      }
    }
  }
}
```

**Focus Mode:**
```json
{
  "payload": {
    "command": "camera.set_property",
    "parameters": {
      "property": "focus_mode",
      "value": "manual|af_single|af_continuous|af_auto"
    }
  }
}
```

**File Format:**
```json
{
  "payload": {
    "command": "camera.set_property",
    "parameters": {
      "property": "file_format",
      "value": {
        "format": "jpeg|raw|jpeg_raw",
        "jpeg_quality": "extra_fine|fine|standard",  // if format includes jpeg
        "image_size": "large|medium|small"
      }
    }
  }
}
```

#### 2. Focus Control
```json
{
  "payload": {
    "command": "camera.focus",
    "parameters": {
      "action": "near|far|stop",
      "speed": 3  // 1-7, optional (default: 3)
    }
  }
}
```

#### 3. Focus Area Selection
```json
{
  "payload": {
    "command": "camera.set_focus_area",
    "parameters": {
      "mode": "wide|zone|center|spot_s|spot_m|spot_l",
      "position": {  // optional, for spot modes
        "x": 0.5,    // normalized 0.0-1.0
        "y": 0.5
      }
    }
  }
}
```

#### 4. Capture Image
```json
{
  "payload": {
    "command": "camera.capture",
    "parameters": {
      "mode": "single|burst",
      "burst_count": 5  // optional, if mode is "burst"
    }
  }
}
```

#### 5. Video Recording Control
```json
{
  "payload": {
    "command": "camera.record",
    "parameters": {
      "action": "start|stop|pause|resume"
    }
  }
}
```

#### 6. Get Camera Properties
```json
{
  "payload": {
    "command": "camera.get_properties",
    "parameters": {
      "properties": [
        "shutter_speed",
        "aperture",
        "iso",
        "white_balance",
        "focus_mode",
        "battery",
        "storage"
      ]
    }
  }
}
```

### Gimbal Control Commands

#### 7. Set Gimbal Angle
```json
{
  "payload": {
    "command": "gimbal.set_angle",
    "parameters": {
      "pitch": -45.0,  // degrees, -90 to +30 typical
      "yaw": 0.0,      // degrees, -180 to +180
      "roll": 0.0      // degrees, typically 0
    }
  }
}
```

#### 8. Set Gimbal Rate
```json
{
  "payload": {
    "command": "gimbal.set_rate",
    "parameters": {
      "pitch_rate": 10.0,  // degrees per second
      "yaw_rate": 15.0,
      "roll_rate": 0.0
    }
  }
}
```

#### 9. Set Gimbal Mode
```json
{
  "payload": {
    "command": "gimbal.set_mode",
    "parameters": {
      "mode": "follow|lock|home|fpv"
    }
  }
}
```

#### 10. Gimbal Home Position
```json
{
  "payload": {
    "command": "gimbal.home",
    "parameters": {}
  }
}
```

#### 11. Set Gimbal Parameters
```json
{
  "payload": {
    "command": "gimbal.set_parameters",
    "parameters": {
      "follow_speed": 0.5,    // 0.0-1.0
      "control_gain": 0.8,    // 0.0-1.0
      "smoothing": 0.6        // 0.0-1.0
    }
  }
}
```

### Content Management Commands

#### 12. List Content
```json
{
  "payload": {
    "command": "content.list",
    "parameters": {
      "type": "all|images|videos",
      "start_index": 0,     // for pagination
      "count": 50           // max items to return
    }
  }
}
```

#### 13. Download Content
```json
{
  "payload": {
    "command": "content.download",
    "parameters": {
      "content_id": "DSC00123.ARW",
      "priority": "high|normal|low",
      "delete_after": false  // delete from camera after download
    }
  }
}
```

#### 14. Delete Content
```json
{
  "payload": {
    "command": "content.delete",
    "parameters": {
      "content_id": "DSC00123.ARW"
    }
  }
}
```

### System Commands

#### 15. Get System Status
```json
{
  "payload": {
    "command": "system.get_status",
    "parameters": {}
  }
}
```

#### 16. Reboot System
```json
{
  "payload": {
    "command": "system.reboot",
    "parameters": {
      "delay_seconds": 5  // delay before reboot
    }
  }
}
```

#### 17. Set Configuration
```json
{
  "payload": {
    "command": "system.set_config",
    "parameters": {
      "config_key": "auto_download_images",
      "config_value": true
    }
  }
}
```

---

## Response Messages (Air → Ground)

### Response Message Format

Every command receives a response (acknowledgment).

```json
{
  "protocol_version": "1.0",
  "message_type": "response",
  "sequence_id": 12345,  // matches command sequence_id
  "timestamp": 1729339201,
  "payload": {
    "command": "camera.set_property",  // echoed from command
    "status": "success|error|in_progress",
    "result": {
      // Command-specific result data
    },
    "error": {  // only if status is "error"
      "code": 1001,
      "message": "Human-readable error description"
    }
  }
}
```

### Success Response Examples

**Property Set Success:**
```json
{
  "payload": {
    "command": "camera.set_property",
    "status": "success",
    "result": {
      "property": "iso",
      "value": 400,
      "confirmed": true
    }
  }
}
```

**Capture Success:**
```json
{
  "payload": {
    "command": "camera.capture",
    "status": "success",
    "result": {
      "image_id": "DSC00456.ARW",
      "timestamp": 1729339205,
      "file_size_bytes": 45678912,
      "format": "raw"
    }
  }
}
```

**Content List Response:**
```json
{
  "payload": {
    "command": "content.list",
    "status": "success",
    "result": {
      "total_count": 127,
      "returned_count": 50,
      "content": [
        {
          "id": "DSC00123.ARW",
          "type": "image",
          "format": "raw",
          "size_bytes": 48000000,
          "timestamp": 1729339100,
          "downloaded": false
        },
        {
          "id": "DSC00124.JPG",
          "type": "image",
          "format": "jpeg",
          "size_bytes": 8500000,
          "timestamp": 1729339105,
          "downloaded": true
        }
        // ... more items
      ]
    }
  }
}
```

### Error Response Examples

**Invalid Parameter:**
```json
{
  "payload": {
    "command": "camera.set_property",
    "status": "error",
    "error": {
      "code": 1001,
      "message": "Invalid ISO value: 12800 not supported by camera"
    }
  }
}
```

**Camera Not Connected:**
```json
{
  "payload": {
    "command": "camera.capture",
    "status": "error",
    "error": {
      "code": 2001,
      "message": "Camera not connected or not responding"
    }
  }
}
```

**Operation In Progress:**
```json
{
  "payload": {
    "command": "content.download",
    "status": "in_progress",
    "result": {
      "content_id": "DSC00456.ARW",
      "progress_percent": 45,
      "bytes_downloaded": 21600000,
      "total_bytes": 48000000,
      "estimated_time_remaining_seconds": 15
    }
  }
}
```

---

## Status Messages (Air → Ground)

### Status Message Format

Status messages are broadcast periodically (5 Hz) via UDP.

```json
{
  "protocol_version": "1.0",
  "message_type": "status",
  "sequence_id": 54321,
  "timestamp": 1729339200,
  "payload": {
    "system": { /* system status */ },
    "camera": { /* camera status */ },
    "gimbal": { /* gimbal status */ },
    "downloads": { /* download status */ }
  }
}
```

### Complete Status Example

```json
{
  "protocol_version": "1.0",
  "message_type": "status",
  "sequence_id": 54321,
  "timestamp": 1729339200,
  "payload": {
    "system": {
      "uptime_seconds": 3600,
      "cpu_usage_percent": 35.2,
      "memory_usage_percent": 42.8,
      "storage_free_gb": 85.3,
      "network_latency_ms": 45,
      "mavlink_connected": true
    },
    "camera": {
      "connected": true,
      "model": "Sony A1",
      "firmware_version": "1.52",
      "battery_percent": 85,
      "battery_minutes_remaining": 120,
      "recording": false,
      "storage": {
        "total_mb": 128000,
        "free_mb": 64000,
        "remaining_images": 1250,
        "remaining_video_minutes": 180
      },
      "current_settings": {
        "mode": "manual",
        "shutter_speed": "1/1000",
        "aperture": "F2.8",
        "iso": 400,
        "white_balance": {
          "mode": "daylight",
          "color_temp": null
        },
        "focus_mode": "manual",
        "file_format": {
          "format": "jpeg_raw",
          "jpeg_quality": "fine",
          "image_size": "large"
        }
      }
    },
    "gimbal": {
      "connected": true,
      "type": "gremsy",
      "model": "T3",
      "mode": "follow",
      "attitude": {
        "pitch": -45.2,
        "yaw": 12.5,
        "roll": 0.3
      },
      "moving": false
    },
    "downloads": {
      "queue_size": 3,
      "active_download": {
        "content_id": "DSC00456.ARW",
        "progress_percent": 67,
        "speed_mbps": 2.5,
        "estimated_time_remaining_seconds": 12
      }
    }
  }
}
```

---

## Heartbeat Messages

### Heartbeat Format

Heartbeat messages are exchanged bidirectionally via UDP (1 Hz).

```json
{
  "protocol_version": "1.0",
  "message_type": "heartbeat",
  "sequence_id": 99999,
  "timestamp": 1729339200,
  "payload": {
    "sender": "ground|air",
    "uptime_seconds": 3600
  }
}
```

### Purpose
- Detect connection loss
- Measure round-trip time (RTT)
- Trigger reconnection logic
- Monitor link quality

### Heartbeat Logic

**Ground Station:**
```
Every 1 second:
  - Send heartbeat to Pi
  - Expect heartbeat from Pi within 3 seconds
  - If no heartbeat received in 5 seconds:
    - Mark connection as lost
    - Show warning to user
    - Attempt TCP reconnection
```

**Raspberry Pi:**
```
Every 1 second:
  - Send heartbeat to ground
  - Track last received heartbeat time
  - If no heartbeat received in 10 seconds:
    - Log warning
    - Continue operation (may be flying out of range)
```

---

## Error Handling

### Error Codes

| Code Range | Category | Description |
|------------|----------|-------------|
| 1000-1999 | Camera Errors | Sony camera related errors |
| 2000-2999 | Gimbal Errors | Gimbal control errors |
| 3000-3999 | Network Errors | Communication errors |
| 4000-4999 | System Errors | SBC system errors |
| 5000-5999 | Protocol Errors | Message format/protocol errors |

### Common Error Codes

```
1001: Invalid camera property value
1002: Camera not connected
1003: Camera busy (operation in progress)
1004: Camera error (hardware issue)
1005: Unsupported operation for this camera model

2001: Gimbal not connected
2002: Gimbal communication error
2003: Invalid gimbal command
2004: Gimbal at limit (mechanical limit reached)

3001: Network timeout
3002: Message too large
3003: Connection lost

4001: Insufficient storage space
4002: File not found
4003: Permission denied
4004: System overload

5001: Invalid JSON format
5002: Missing required field
5003: Unknown command
5004: Protocol version mismatch
5005: Invalid sequence ID
```

### Error Response Format

```json
{
  "payload": {
    "command": "camera.set_property",
    "status": "error",
    "error": {
      "code": 1001,
      "message": "Invalid ISO value: 12800 not supported by camera",
      "details": {
        "property": "iso",
        "requested_value": 12800,
        "valid_range": [100, 102400],
        "suggested_value": 6400
      }
    }
  }
}
```

---

## Connection Management

### Connection Lifecycle

```
┌──────────────────────────────────────────────────────────┐
│                    Connection States                      │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  [Disconnected] ──(connect)──> [Connecting]              │
│       ↑                              │                    │
│       │                              │                    │
│       │                         (success)                 │
│       │                              │                    │
│       │                              ▼                    │
│       │                        [Connected]                │
│       │                              │                    │
│       │                              │                    │
│       │                      (active operation)           │
│       │                              │                    │
│       │                              ▼                    │
│       │                        [Operational]              │
│       │                              │                    │
│       │                              │                    │
│       └────(timeout/error)───────────┘                    │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

### Connection Sequence

#### Initial Connection (Ground → Air)

1. **Ground:** Connect TCP socket to 192.168.144.20:5000
2. **Ground:** Send connection handshake
3. **Air:** Respond with capabilities and status
4. **Ground:** Start UDP status receiver on port 5001
5. **Ground:** Start heartbeat exchange on port 5002
6. **Both:** Enter operational state

#### Handshake Message

**Ground → Air:**
```json
{
  "protocol_version": "1.0",
  "message_type": "handshake",
  "sequence_id": 1,
  "timestamp": 1729339200,
  "payload": {
    "client_id": "h16_gcs_001",
    "client_version": "1.0.0",
    "requested_features": [
      "camera_control",
      "gimbal_control",
      "content_download"
    ]
  }
}
```

**Air → Ground:**
```json
{
  "protocol_version": "1.0",
  "message_type": "handshake_response",
  "sequence_id": 1,
  "timestamp": 1729339201,
  "payload": {
    "server_id": "payload_mgr_001",
    "server_version": "1.0.0",
    "supported_features": [
      "camera_control",
      "gimbal_control",
      "content_download",
      "mavlink_integration"
    ],
    "camera_connected": true,
    "camera_model": "Sony A1",
    "gimbal_connected": true,
    "gimbal_type": "gremsy_t3"
  }
}
```

### Reconnection Logic

**On Connection Loss:**

1. **Detect:** No heartbeat received for 5 seconds
2. **Close:** Close existing TCP/UDP sockets
3. **Wait:** 2 second delay
4. **Retry:** Attempt reconnection
5. **Backoff:** If failed, exponential backoff (2s, 4s, 8s, max 30s)
6. **Notify:** Show connection status to user
7. **Continue:** Keep attempting indefinitely

### Graceful Disconnection

**Ground → Air:**
```json
{
  "protocol_version": "1.0",
  "message_type": "disconnect",
  "sequence_id": 99999,
  "timestamp": 1729339200,
  "payload": {
    "reason": "user_requested|app_closing|switching_mode"
  }
}
```

**Air → Ground:**
```json
{
  "protocol_version": "1.0",
  "message_type": "disconnect_ack",
  "sequence_id": 99999,
  "timestamp": 1729339201,
  "payload": {
    "acknowledged": true
  }
}
```

---

## Implementation Examples

### Python (Raspberry Pi Service - Simplified)

```python
import socket
import json
import threading
import time

class PayloadManagerServer:
    def __init__(self):
        self.tcp_socket = None
        self.udp_socket = None
        self.running = False
        self.sequence_id = 0
        
    def start(self):
        # Start TCP server for commands
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcp_socket.bind(('0.0.0.0', 5000))
        self.tcp_socket.listen(5)
        
        # Start UDP socket for status broadcast
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind(('0.0.0.0', 5001))
        
        self.running = True
        
        # Start threads
        threading.Thread(target=self.tcp_listener, daemon=True).start()
        threading.Thread(target=self.status_broadcaster, daemon=True).start()
        threading.Thread(target=self.heartbeat_handler, daemon=True).start()
        
    def tcp_listener(self):
        while self.running:
            client, addr = self.tcp_socket.accept()
            print(f"Client connected: {addr}")
            threading.Thread(target=self.handle_client, args=(client,), daemon=True).start()
    
    def handle_client(self, client):
        buffer = ""
        while self.running:
            try:
                data = client.recv(4096).decode('utf-8')
                if not data:
                    break
                    
                buffer += data
                
                # Process complete JSON messages
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    try:
                        message = json.loads(line)
                        response = self.process_command(message)
                        client.send((json.dumps(response) + '\n').encode('utf-8'))
                    except json.JSONDecodeError:
                        pass
                        
            except Exception as e:
                print(f"Error: {e}")
                break
        
        client.close()
    
    def process_command(self, message):
        command = message['payload']['command']
        
        if command == 'camera.set_property':
            return self.handle_set_property(message)
        elif command == 'camera.capture':
            return self.handle_capture(message)
        # ... more command handlers
        
        return self.error_response(message, 5003, "Unknown command")
    
    def handle_set_property(self, message):
        params = message['payload']['parameters']
        property_name = params['property']
        value = params['value']
        
        # Call Sony SDK to set property
        # camera.set_property(property_name, value)
        
        return {
            'protocol_version': '1.0',
            'message_type': 'response',
            'sequence_id': message['sequence_id'],
            'timestamp': int(time.time()),
            'payload': {
                'command': 'camera.set_property',
                'status': 'success',
                'result': {
                    'property': property_name,
                    'value': value,
                    'confirmed': True
                }
            }
        }
    
    def status_broadcaster(self):
        ground_addr = ('192.168.144.11', 5001)
        
        while self.running:
            status = self.gather_status()
            message = {
                'protocol_version': '1.0',
                'message_type': 'status',
                'sequence_id': self.sequence_id,
                'timestamp': int(time.time()),
                'payload': status
            }
            
            self.udp_socket.sendto(
                json.dumps(message).encode('utf-8'),
                ground_addr
            )
            
            self.sequence_id += 1
            time.sleep(0.2)  # 5 Hz
    
    def gather_status(self):
        # Gather status from camera, gimbal, system
        return {
            'system': {
                'uptime_seconds': int(time.time() - self.start_time),
                'cpu_usage_percent': 35.2,
                # ... more
            },
            'camera': {
                'connected': True,
                'model': 'Sony A1',
                # ... more
            },
            'gimbal': {
                'connected': True,
                # ... more
            }
        }

if __name__ == '__main__':
    server = PayloadManagerServer()
    server.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
```

### Kotlin (Android App - Simplified)

```kotlin
import kotlinx.coroutines.*
import java.net.Socket
import java.net.DatagramSocket
import java.net.DatagramPacket
import java.net.InetAddress
import com.google.gson.Gson

class NetworkClient(
    private val serverIp: String = "192.168.144.20",
    private val tcpPort: Int = 5000,
    private val udpPort: Int = 5001
) {
    private var tcpSocket: Socket? = null
    private var udpSocket: DatagramSocket? = null
    private val gson = Gson()
    private var sequenceId = 0
    
    var onStatusReceived: ((CameraStatus) -> Unit)? = null
    var onConnectionChanged: ((Boolean) -> Unit)? = null
    
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    
    fun connect() {
        scope.launch {
            try {
                // Connect TCP
                tcpSocket = Socket(serverIp, tcpPort)
                
                // Send handshake
                sendHandshake()
                
                // Start UDP receiver
                udpSocket = DatagramSocket(udpPort)
                startUdpListener()
                
                // Start heartbeat
                startHeartbeat()
                
                onConnectionChanged?.invoke(true)
                
            } catch (e: Exception) {
                e.printStackTrace()
                onConnectionChanged?.invoke(false)
                // Retry connection
                delay(2000)
                connect()
            }
        }
    }
    
    fun sendCommand(command: Command) {
        scope.launch {
            try {
                val message = CommandMessage(
                    protocol_version = "1.0",
                    message_type = "command",
                    sequence_id = sequenceId++,
                    timestamp = System.currentTimeMillis() / 1000,
                    payload = command
                )
                
                val json = gson.toJson(message) + "\n"
                tcpSocket?.getOutputStream()?.write(json.toByteArray())
                
                // Wait for response
                // ... handle response
                
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }
    
    private fun startUdpListener() {
        scope.launch {
            val buffer = ByteArray(4096)
            
            while (isActive) {
                try {
                    val packet = DatagramPacket(buffer, buffer.size)
                    udpSocket?.receive(packet)
                    
                    val json = String(packet.data, 0, packet.length)
                    val status = gson.fromJson(json, StatusMessage::class.java)
                    
                    withContext(Dispatchers.Main) {
                        onStatusReceived?.invoke(status.payload.camera)
                    }
                    
                } catch (e: Exception) {
                    e.printStackTrace()
                }
            }
        }
    }
    
    private fun sendHandshake() {
        val handshake = HandshakeMessage(
            protocol_version = "1.0",
            message_type = "handshake",
            sequence_id = 1,
            timestamp = System.currentTimeMillis() / 1000,
            payload = HandshakePayload(
                client_id = "h16_gcs_001",
                client_version = "1.0.0",
                requested_features = listOf(
                    "camera_control",
                    "gimbal_control",
                    "content_download"
                )
            )
        )
        
        val json = gson.toJson(handshake) + "\n"
        tcpSocket?.getOutputStream()?.write(json.toByteArray())
        
        // Wait for handshake response
        // ... handle response
    }
    
    fun setCameraProperty(property: String, value: Any) {
        val command = Command(
            command = "camera.set_property",
            parameters = mapOf(
                "property" to property,
                "value" to value
            )
        )
        sendCommand(command)
    }
    
    fun captureImage() {
        val command = Command(
            command = "camera.capture",
            parameters = mapOf("mode" to "single")
        )
        sendCommand(command)
    }
    
    fun disconnect() {
        scope.cancel()
        tcpSocket?.close()
        udpSocket?.close()
    }
}

// Data classes
data class CommandMessage(
    val protocol_version: String,
    val message_type: String,
    val sequence_id: Int,
    val timestamp: Long,
    val payload: Command
)

data class Command(
    val command: String,
    val parameters: Map<String, Any>
)

data class StatusMessage(
    val protocol_version: String,
    val message_type: String,
    val sequence_id: Int,
    val timestamp: Long,
    val payload: Status
)

data class Status(
    val system: SystemStatus,
    val camera: CameraStatus,
    val gimbal: GimbalStatus
)

data class CameraStatus(
    val connected: Boolean,
    val model: String,
    val battery_percent: Int,
    val recording: Boolean,
    // ... more fields
)
```

---

## Protocol Evolution

### Versioning Strategy

- **Current Version:** 1.0
- **Version Format:** MAJOR.MINOR
- **Backward Compatibility:** MINOR version changes are backward compatible
- **Breaking Changes:** MAJOR version changes may break compatibility

### Adding New Commands

1. Define new command in specification
2. Assign command name (namespace.action format)
3. Document parameters and response format
4. Update protocol_version if breaking change
5. Implement in both client and server
6. Test thoroughly

### Deprecation Process

1. Mark command as deprecated in spec
2. Continue supporting for 2+ major versions
3. Log deprecation warnings
4. Provide migration path to new command
5. Eventually remove in future major version

---

## Testing & Validation

### Protocol Testing Checklist

- [ ] All commands send valid JSON
- [ ] All responses are received within timeout
- [ ] Error cases handled gracefully
- [ ] Connection recovery works after interruption
- [ ] Heartbeat detects disconnection
- [ ] Large messages handled correctly
- [ ] High message rate doesn't cause issues
- [ ] Sequence IDs increment correctly
- [ ] Timestamps are accurate
- [ ] Status broadcast works at 5 Hz

### Tools for Testing

**Command Line Testing:**
```bash
# Test TCP command
echo '{"protocol_version":"1.0","message_type":"command","sequence_id":1,"timestamp":1729339200,"payload":{"command":"system.get_status","parameters":{}}}' | nc 192.168.144.20 5000

# Listen for UDP status
nc -u -l 5001
```

**Python Test Client:**
```python
# Simple test client
import socket
import json

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('192.168.144.20', 5000))

command = {
    'protocol_version': '1.0',
    'message_type': 'command',
    'sequence_id': 1,
    'timestamp': 1729339200,
    'payload': {
        'command': 'system.get_status',
        'parameters': {}
    }
}

sock.send((json.dumps(command) + '\n').encode())
response = sock.recv(4096).decode()
print(json.dumps(json.loads(response), indent=2))
```

---

## Summary

### Protocol Characteristics

| Feature | Specification |
|---------|--------------|
| **Format** | JSON (UTF-8) |
| **Command Transport** | TCP (port 5000) |
| **Status Transport** | UDP (port 5001) |
| **Heartbeat Transport** | UDP (port 5002) |
| **Status Frequency** | 5 Hz (200ms) |
| **Heartbeat Frequency** | 1 Hz (1000ms) |
| **Max Message Size (TCP)** | 64 KB |
| **Max Message Size (UDP)** | 1472 bytes |
| **Timeout (Command)** | 5 seconds |
| **Timeout (Heartbeat)** | 5 seconds |
| **Reconnection** | Automatic with exponential backoff |

### Next Steps

1. **Review Protocol** - Validate all commands meet requirements
2. **Refine Details** - Add any missing commands or parameters
3. **Begin Implementation** - Start with basic command/response
4. **Test Incrementally** - Test each command as implemented
5. **Document Changes** - Keep protocol spec updated

---

**Document Status:** Draft for Review ✅  
**Ready for:** Implementation  
**Date:** October 19, 2025
