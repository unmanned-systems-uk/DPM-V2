# Protocol Implementation Quick Start Guide

## Phase 1, Task 1: Command Protocol Implementation

**Goal:** Get basic command/response working between Android app and Pi service

---

## Week 1: Basic Protocol Implementation

### Day 1-2: Raspberry Pi TCP Server

**Objective:** Create TCP server that accepts connections and echoes commands

```python
# File: payload_server.py

import socket
import json
import time

class SimplePayloadServer:
    def __init__(self):
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
    def start(self):
        self.tcp_socket.bind(('0.0.0.0', 5000))
        self.tcp_socket.listen(5)
        print("Server listening on port 5000...")
        
        while True:
            client, addr = self.tcp_socket.accept()
            print(f"Client connected: {addr}")
            self.handle_client(client)
    
    def handle_client(self, client):
        buffer = ""
        while True:
            try:
                data = client.recv(4096).decode('utf-8')
                if not data:
                    break
                
                buffer += data
                
                # Process line-delimited JSON
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    try:
                        message = json.loads(line)
                        print(f"Received: {message['payload']['command']}")
                        
                        # Echo back a success response
                        response = {
                            'protocol_version': '1.0',
                            'message_type': 'response',
                            'sequence_id': message['sequence_id'],
                            'timestamp': int(time.time()),
                            'payload': {
                                'command': message['payload']['command'],
                                'status': 'success',
                                'result': {'echoed': True}
                            }
                        }
                        
                        client.send((json.dumps(response) + '\n').encode('utf-8'))
                        
                    except json.JSONDecodeError as e:
                        print(f"Invalid JSON: {e}")
                        
            except Exception as e:
                print(f"Error: {e}")
                break
        
        client.close()
        print("Client disconnected")

if __name__ == '__main__':
    server = SimplePayloadServer()
    server.start()
```

**Test it:**
```bash
# On Pi
python3 payload_server.py

# From another terminal
echo '{"protocol_version":"1.0","message_type":"command","sequence_id":1,"timestamp":1729339200,"payload":{"command":"test","parameters":{}}}' | nc 192.168.144.20 5000
```

### Day 3-4: Android TCP Client

**Objective:** Create Android app that connects and sends commands

```kotlin
// File: NetworkClient.kt

package com.example.payloadmanager

import kotlinx.coroutines.*
import java.io.BufferedReader
import java.io.InputStreamReader
import java.io.PrintWriter
import java.net.Socket
import com.google.gson.Gson

class NetworkClient(
    private val serverIp: String = "192.168.144.20",
    private val serverPort: Int = 5000
) {
    private var socket: Socket? = null
    private var reader: BufferedReader? = null
    private var writer: PrintWriter? = null
    private val gson = Gson()
    private var sequenceId = 0
    
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    
    var onResponse: ((Response) -> Unit)? = null
    var onConnectionChanged: ((Boolean) -> Unit)? = null
    
    fun connect() {
        scope.launch {
            try {
                socket = Socket(serverIp, serverPort)
                reader = BufferedReader(InputStreamReader(socket?.getInputStream()))
                writer = PrintWriter(socket?.getOutputStream(), true)
                
                withContext(Dispatchers.Main) {
                    onConnectionChanged?.invoke(true)
                }
                
                // Start listening for responses
                listenForResponses()
                
            } catch (e: Exception) {
                e.printStackTrace()
                withContext(Dispatchers.Main) {
                    onConnectionChanged?.invoke(false)
                }
            }
        }
    }
    
    private suspend fun listenForResponses() {
        while (true) {
            try {
                val line = reader?.readLine() ?: break
                val response = gson.fromJson(line, Response::class.java)
                
                withContext(Dispatchers.Main) {
                    onResponse?.invoke(response)
                }
            } catch (e: Exception) {
                e.printStackTrace()
                break
            }
        }
    }
    
    fun sendCommand(command: String, parameters: Map<String, Any> = emptyMap()) {
        scope.launch {
            try {
                val message = Message(
                    protocol_version = "1.0",
                    message_type = "command",
                    sequence_id = sequenceId++,
                    timestamp = System.currentTimeMillis() / 1000,
                    payload = Payload(command, parameters)
                )
                
                val json = gson.toJson(message)
                writer?.println(json)
                
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }
    
    fun disconnect() {
        scope.cancel()
        writer?.close()
        reader?.close()
        socket?.close()
    }
}

// Data classes
data class Message(
    val protocol_version: String,
    val message_type: String,
    val sequence_id: Int,
    val timestamp: Long,
    val payload: Payload
)

data class Payload(
    val command: String,
    val parameters: Map<String, Any>
)

data class Response(
    val protocol_version: String,
    val message_type: String,
    val sequence_id: Int,
    val timestamp: Long,
    val payload: ResponsePayload
)

data class ResponsePayload(
    val command: String,
    val status: String,
    val result: Map<String, Any>?
)
```

**Basic Activity:**
```kotlin
// File: MainActivity.kt

package com.example.payloadmanager

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import android.widget.Button
import android.widget.TextView

class MainActivity : AppCompatActivity() {
    
    private lateinit var networkClient: NetworkClient
    private lateinit var statusText: TextView
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        statusText = findViewById(R.id.statusText)
        val connectButton: Button = findViewById(R.id.connectButton)
        val testButton: Button = findViewById(R.id.testButton)
        
        networkClient = NetworkClient()
        
        networkClient.onConnectionChanged = { connected ->
            statusText.text = if (connected) {
                "Connected to Pi"
            } else {
                "Disconnected"
            }
        }
        
        networkClient.onResponse = { response ->
            statusText.append("\nReceived: ${response.payload.command} - ${response.payload.status}")
        }
        
        connectButton.setOnClickListener {
            networkClient.connect()
        }
        
        testButton.setOnClickListener {
            networkClient.sendCommand("test", mapOf("value" to 123))
        }
    }
    
    override fun onDestroy() {
        super.onDestroy()
        networkClient.disconnect()
    }
}
```

**Layout:**
```xml
<!-- File: res/layout/activity_main.xml -->
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:padding="16dp">
    
    <Button
        android:id="@+id/connectButton"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="Connect to Pi" />
    
    <Button
        android:id="@+id/testButton"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="Send Test Command" />
    
    <ScrollView
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1">
        
        <TextView
            android:id="@+id/statusText"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:text="Status: Not connected"
            android:fontFamily="monospace" />
    </ScrollView>
    
</LinearLayout>
```

**AndroidManifest.xml permissions:**
```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
```

**build.gradle dependencies:**
```gradle
dependencies {
    implementation 'com.google.code.gson:gson:2.10.1'
    implementation 'org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3'
}
```

### Day 5: Test TCP Communication

**Test Checklist:**
- [ ] Pi server starts and listens
- [ ] Android app connects successfully
- [ ] Commands sent from Android reach Pi
- [ ] Responses from Pi reach Android
- [ ] Multiple commands work in sequence
- [ ] Reconnection works after disconnect

---

## Week 2: Add UDP Status Broadcasting

### Day 6-7: Pi UDP Status Broadcaster

Add to `payload_server.py`:

```python
import threading
from socket import *

class PayloadServer:
    # ... previous code ...
    
    def __init__(self):
        self.tcp_socket = socket(AF_INET, SOCK_STREAM)
        self.udp_socket = socket(AF_INET, SOCK_DGRAM)
        self.running = True
        self.status_sequence = 0
        
    def start(self):
        # Start TCP listener
        threading.Thread(target=self.tcp_listener, daemon=True).start()
        
        # Start UDP status broadcaster
        threading.Thread(target=self.udp_broadcaster, daemon=True).start()
        
        # Keep main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.running = False
    
    def udp_broadcaster(self):
        ground_addr = ('192.168.144.11', 5001)
        
        while self.running:
            status = {
                'protocol_version': '1.0',
                'message_type': 'status',
                'sequence_id': self.status_sequence,
                'timestamp': int(time.time()),
                'payload': {
                    'system': {
                        'uptime_seconds': 100,
                        'cpu_usage_percent': 35.0
                    },
                    'camera': {
                        'connected': True,
                        'battery_percent': 85
                    }
                }
            }
            
            try:
                self.udp_socket.sendto(
                    json.dumps(status).encode('utf-8'),
                    ground_addr
                )
            except Exception as e:
                print(f"UDP send error: {e}")
            
            self.status_sequence += 1
            time.sleep(0.2)  # 5 Hz
```

### Day 8-9: Android UDP Status Receiver

Add to `NetworkClient.kt`:

```kotlin
import java.net.DatagramSocket
import java.net.DatagramPacket

class NetworkClient(
    private val serverIp: String = "192.168.144.20",
    private val tcpPort: Int = 5000,
    private val udpPort: Int = 5001
) {
    // ... previous code ...
    
    private var udpSocket: DatagramSocket? = null
    
    var onStatusReceived: ((Status) -> Unit)? = null
    
    fun connect() {
        scope.launch {
            try {
                // Connect TCP
                socket = Socket(serverIp, tcpPort)
                // ... TCP setup ...
                
                // Start UDP receiver
                startUdpReceiver()
                
                withContext(Dispatchers.Main) {
                    onConnectionChanged?.invoke(true)
                }
                
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }
    
    private fun startUdpReceiver() {
        scope.launch {
            try {
                udpSocket = DatagramSocket(udpPort)
                val buffer = ByteArray(4096)
                
                while (isActive) {
                    val packet = DatagramPacket(buffer, buffer.size)
                    udpSocket?.receive(packet)
                    
                    val json = String(packet.data, 0, packet.length)
                    val statusMsg = gson.fromJson(json, StatusMessage::class.java)
                    
                    withContext(Dispatchers.Main) {
                        onStatusReceived?.invoke(statusMsg.payload)
                    }
                }
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }
}

data class StatusMessage(
    val protocol_version: String,
    val message_type: String,
    val sequence_id: Int,
    val timestamp: Long,
    val payload: Status
)

data class Status(
    val system: SystemStatus,
    val camera: CameraStatus
)

data class SystemStatus(
    val uptime_seconds: Int,
    val cpu_usage_percent: Float
)

data class CameraStatus(
    val connected: Boolean,
    val battery_percent: Int
)
```

Update `MainActivity.kt`:

```kotlin
networkClient.onStatusReceived = { status ->
    statusText.append("\nStatus: Battery ${status.camera.battery_percent}%")
}
```

### Day 10: Test UDP Status

**Test Checklist:**
- [ ] Pi broadcasts status at 5 Hz
- [ ] Android receives status messages
- [ ] Status updates displayed in UI
- [ ] No packet loss at 5 Hz rate
- [ ] Works alongside TCP commands

---

## Week 3: Add Camera Commands

### Day 11-13: Implement Camera Control on Pi

```python
# Placeholder for Sony SDK integration
class CameraController:
    def set_property(self, property_name, value):
        print(f"Setting {property_name} to {value}")
        # TODO: Call Sony SDK
        return True
    
    def capture(self):
        print("Capturing image...")
        # TODO: Call Sony SDK
        return "DSC00123.JPG"
    
    def get_battery(self):
        # TODO: Read from Sony SDK
        return 85

class PayloadServer:
    def __init__(self):
        # ... previous code ...
        self.camera = CameraController()
    
    def handle_command(self, message):
        command = message['payload']['command']
        params = message['payload'].get('parameters', {})
        
        if command == 'camera.set_property':
            prop = params['property']
            value = params['value']
            success = self.camera.set_property(prop, value)
            
            return {
                'protocol_version': '1.0',
                'message_type': 'response',
                'sequence_id': message['sequence_id'],
                'timestamp': int(time.time()),
                'payload': {
                    'command': command,
                    'status': 'success' if success else 'error',
                    'result': {
                        'property': prop,
                        'value': value
                    }
                }
            }
        
        elif command == 'camera.capture':
            image_id = self.camera.capture()
            
            return {
                'protocol_version': '1.0',
                'message_type': 'response',
                'sequence_id': message['sequence_id'],
                'timestamp': int(time.time()),
                'payload': {
                    'command': command,
                    'status': 'success',
                    'result': {
                        'image_id': image_id
                    }
                }
            }
        
        # ... more commands ...
```

### Day 14-15: Add Camera UI to Android

```kotlin
// CameraViewModel.kt
class CameraViewModel : ViewModel() {
    private val networkClient = NetworkClient()
    
    private val _batteryLevel = MutableLiveData<Int>()
    val batteryLevel: LiveData<Int> = _batteryLevel
    
    init {
        networkClient.onStatusReceived = { status ->
            _batteryLevel.postValue(status.camera.battery_percent)
        }
    }
    
    fun connect() {
        networkClient.connect()
    }
    
    fun setISO(value: Int) {
        networkClient.sendCommand(
            "camera.set_property",
            mapOf(
                "property" to "iso",
                "value" to value
            )
        )
    }
    
    fun setShutterSpeed(numerator: Int, denominator: Int) {
        networkClient.sendCommand(
            "camera.set_property",
            mapOf(
                "property" to "shutter_speed",
                "value" to mapOf(
                    "numerator" to numerator,
                    "denominator" to denominator
                )
            )
        )
    }
    
    fun captureImage() {
        networkClient.sendCommand("camera.capture")
    }
}

// CameraControlFragment.kt
class CameraControlFragment : Fragment() {
    private val viewModel: CameraViewModel by viewModels()
    
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val view = inflater.inflate(R.layout.fragment_camera_control, container, false)
        
        // Battery display
        val batteryText: TextView = view.findViewById(R.id.batteryText)
        viewModel.batteryLevel.observe(viewLifecycleOwner) { level ->
            batteryText.text = "Battery: $level%"
        }
        
        // ISO control
        val isoSeekBar: SeekBar = view.findViewById(R.id.isoSeekBar)
        isoSeekBar.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onStopTrackingTouch(seekBar: SeekBar) {
                val iso = isoValueFromProgress(seekBar.progress)
                viewModel.setISO(iso)
            }
            override fun onProgressChanged(s: SeekBar, progress: Int, fromUser: Boolean) {}
            override fun onStartTrackingTouch(seekBar: SeekBar) {}
        })
        
        // Capture button
        val captureButton: Button = view.findViewById(R.id.captureButton)
        captureButton.setOnClickListener {
            viewModel.captureImage()
        }
        
        return view
    }
    
    private fun isoValueFromProgress(progress: Int): Int {
        // Map 0-100 progress to ISO values (100-12800)
        val isoValues = listOf(100, 200, 400, 800, 1600, 3200, 6400, 12800)
        val index = (progress / 100.0 * (isoValues.size - 1)).toInt()
        return isoValues[index]
    }
}
```

---

## Testing Checklist

### Basic Protocol ✅
- [ ] TCP connection established
- [ ] Commands sent successfully
- [ ] Responses received
- [ ] UDP status broadcasts working
- [ ] JSON parsing works both ways

### Camera Control ✅
- [ ] ISO command works
- [ ] Shutter speed command works
- [ ] Aperture command works
- [ ] Capture command works
- [ ] Status updates show changes

### Error Handling ✅
- [ ] Invalid command handled
- [ ] Network disconnection handled
- [ ] Reconnection works
- [ ] Timeout handling works

---

## Next Steps

1. **Sony SDK Integration** - Replace placeholder with real Sony SDK calls
2. **Add More Commands** - White balance, focus, file format, etc.
3. **Gimbal Control** - Add gimbal commands
4. **Download Manager** - Implement content download
5. **UI Polish** - Improve Android UI/UX

---

## Summary

**Week 1:** Basic TCP command/response  
**Week 2:** UDP status broadcasting  
**Week 3:** Camera control commands  

**Result:** Working prototype with basic camera control over H16 network! 🎉

---

**Status:** Ready to implement ✅  
**Date:** October 19, 2025
