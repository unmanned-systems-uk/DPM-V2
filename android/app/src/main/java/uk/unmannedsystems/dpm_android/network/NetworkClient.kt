package uk.unmannedsystems.dpm_android.network

import android.util.Log
import com.google.gson.Gson
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import uk.unmannedsystems.dpm_android.eventlog.EventCategory
import uk.unmannedsystems.dpm_android.eventlog.EventLevel
import uk.unmannedsystems.dpm_android.eventlog.EventLogViewModel
import java.io.BufferedReader
import java.io.InputStreamReader
import java.io.PrintWriter
import java.net.DatagramPacket
import java.net.DatagramSocket
import java.net.InetAddress
import java.net.Socket
import java.net.SocketException
import java.util.concurrent.atomic.AtomicInteger

/**
 * Network client for communication with Raspberry Pi payload manager
 * Implements the command protocol specification v1.0
 */
class NetworkClient(
    private val settings: NetworkSettings = NetworkSettings(),
    private val clientId: String = "H16"
) {
    companion object {
        private const val TAG = "NetworkClient"
        private const val CLIENT_VERSION = "1.0.0"
    }

    private val gson = Gson()
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    private val sequenceId = AtomicInteger(0)

    // Sockets
    private var tcpSocket: Socket? = null
    private var tcpWriter: PrintWriter? = null
    private var tcpReader: BufferedReader? = null
    private var udpSocket: DatagramSocket? = null
    private var heartbeatSendSocket: DatagramSocket? = null
    private var heartbeatReceiveSocket: DatagramSocket? = null

    // State flows
    private val _connectionStatus = MutableStateFlow(NetworkStatus())
    val connectionStatus: StateFlow<NetworkStatus> = _connectionStatus.asStateFlow()

    private val _cameraStatus = MutableStateFlow<CameraStatusInfo?>(null)
    val cameraStatus: StateFlow<CameraStatusInfo?> = _cameraStatus.asStateFlow()

    private val _systemStatus = MutableStateFlow<SystemStatus?>(null)
    val systemStatus: StateFlow<SystemStatus?> = _systemStatus.asStateFlow()

    // Jobs
    private var connectJob: Job? = null
    private var statusListenerJob: Job? = null
    private var heartbeatJob: Job? = null
    private var heartbeatReceiverJob: Job? = null
    private var heartbeatWatchdogJob: Job? = null

    /**
     * Connect to the Raspberry Pi
     */
    fun connect() {
        if (_connectionStatus.value.state == ConnectionState.CONNECTED ||
            _connectionStatus.value.state == ConnectionState.CONNECTING) {
            Log.w(TAG, "Already connected or connecting")
            addConnectionLog("Already connected or connecting", LogLevel.WARNING)
            return
        }

        connectJob = scope.launch {
            updateConnectionState(
                ConnectionState.CONNECTING,
                logMessage = "Attempting to connect to ${settings.targetIp}:${settings.commandPort}",
                logLevel = LogLevel.INFO
            )

            // Store target IP and port for display
            _connectionStatus.value = _connectionStatus.value.copy(
                targetIp = settings.targetIp,
                targetPort = settings.commandPort
            )

            try {
                // Connect TCP socket
                addConnectionLog("Connecting TCP socket to ${settings.targetIp}:${settings.commandPort}...", LogLevel.INFO)
                connectTcp()
                addConnectionLog("TCP socket connected successfully", LogLevel.SUCCESS)

                // Send handshake
                addConnectionLog("Sending handshake...", LogLevel.INFO)
                sendHandshake()
                addConnectionLog("Handshake completed", LogLevel.SUCCESS)

                // Start UDP status listener
                addConnectionLog("Starting UDP status listener on port ${settings.statusListenPort}...", LogLevel.INFO)
                startUdpStatusListener()
                addConnectionLog("UDP status listener started", LogLevel.SUCCESS)

                // Start heartbeat sender
                addConnectionLog("Starting heartbeat sender on port ${settings.heartbeatPort}...", LogLevel.INFO)
                startHeartbeatSender()
                addConnectionLog("Heartbeat sender started", LogLevel.SUCCESS)

                // Start heartbeat receiver
                addConnectionLog("Starting heartbeat receiver...", LogLevel.INFO)
                startHeartbeatReceiver()
                addConnectionLog("Heartbeat receiver started", LogLevel.SUCCESS)

                // Start heartbeat watchdog
                addConnectionLog("Starting heartbeat watchdog...", LogLevel.INFO)
                startHeartbeatWatchdog()
                addConnectionLog("Heartbeat watchdog started", LogLevel.SUCCESS)

                // Set connection start time for heartbeat monitoring
                val connectionStartTime = System.currentTimeMillis()
                _connectionStatus.value = _connectionStatus.value.copy(
                    connectionStartedMs = connectionStartTime
                )

                // Note: Connection state already set to OPERATIONAL by sendHandshake()
                // Do not overwrite it here
                Log.i(TAG, "Connected to ${settings.targetIp}")

            } catch (e: Exception) {
                Log.e(TAG, "Connection failed", e)
                val errorMsg = "Connection failed: ${e.message}"
                updateConnectionState(
                    ConnectionState.ERROR,
                    errorMessage = errorMsg,
                    logMessage = errorMsg,
                    logLevel = LogLevel.ERROR
                )

                // Retry connection after delay
                addConnectionLog("Retrying connection in 2 seconds...", LogLevel.WARNING)
                delay(2000)
                connect()
            }
        }
    }

    /**
     * Disconnect from the Raspberry Pi
     */
    fun disconnect() {
        // Use runBlocking to ensure disconnect completes before returning
        runBlocking {
            addConnectionLog("Disconnecting from ${settings.targetIp}...", LogLevel.INFO)
            try {
                // Send disconnect message
                sendDisconnect()
                addConnectionLog("Disconnect message sent", LogLevel.INFO)
            } catch (e: Exception) {
                Log.e(TAG, "Error sending disconnect", e)
                addConnectionLog("Error sending disconnect: ${e.message}", LogLevel.WARNING)
            }

            cleanup()
            updateConnectionState(
                ConnectionState.DISCONNECTED,
                logMessage = "Disconnected from ${settings.targetIp}",
                logLevel = LogLevel.INFO
            )

            // Give sockets time to fully close
            delay(100)
        }
    }

    /**
     * Send a command to the Raspberry Pi
     */
    suspend fun sendCommand(command: String, parameters: Map<String, Any> = emptyMap()): Result<ResponsePayload> {
        return withContext(Dispatchers.IO) {
            try {
                val message = BaseMessage(
                    messageType = "command",
                    sequenceId = sequenceId.incrementAndGet(),
                    timestamp = System.currentTimeMillis() / 1000,
                    payload = CommandPayload(command, parameters)
                )

                val json = gson.toJson(message)
                Log.d(TAG, "Sending command: $json")

                tcpWriter?.println(json)
                tcpWriter?.flush()

                // Read response
                val response = tcpReader?.readLine()
                if (response != null) {
                    Log.d(TAG, "Received response: $response")
                    val responseMessage = gson.fromJson(response, BaseMessage::class.java)
                    val responsePayload = gson.fromJson(
                        gson.toJson(responseMessage.payload),
                        ResponsePayload::class.java
                    )
                    Result.success(responsePayload)
                } else {
                    Result.failure(Exception("No response received"))
                }
            } catch (e: Exception) {
                Log.e(TAG, "Error sending command", e)
                Result.failure(e)
            }
        }
    }

    /**
     * Set camera property
     */
    suspend fun setCameraProperty(property: String, value: Any): Result<ResponsePayload> {
        return sendCommand(
            "camera.set_property",
            mapOf("property" to property, "value" to value)
        )
    }

    /**
     * Capture image
     */
    suspend fun captureImage(mode: String = "single"): Result<ResponsePayload> {
        return sendCommand(
            "camera.capture",
            mapOf("mode" to mode)
        )
    }

    /**
     * Get camera properties
     */
    suspend fun getCameraProperties(properties: List<String>): Result<ResponsePayload> {
        return sendCommand(
            "camera.get_properties",
            mapOf("properties" to properties)
        )
    }

    /**
     * Get system status
     */
    suspend fun getSystemStatus(): Result<ResponsePayload> {
        return sendCommand("system.get_status")
    }

    private suspend fun connectTcp() {
        val address = InetAddress.getByName(settings.targetIp)
        tcpSocket = withContext(Dispatchers.IO) {
            Socket(address, settings.commandPort).apply {
                soTimeout = settings.connectionTimeoutMs.toInt()
            }
        }
        tcpWriter = PrintWriter(tcpSocket!!.getOutputStream(), true)
        tcpReader = BufferedReader(InputStreamReader(tcpSocket!!.getInputStream()))
    }

    private suspend fun sendHandshake() {
        val handshake = BaseMessage(
            messageType = "handshake",
            sequenceId = sequenceId.incrementAndGet(),
            timestamp = System.currentTimeMillis() / 1000,
            payload = HandshakePayload(
                clientId = clientId,
                clientVersion = CLIENT_VERSION,
                requestedFeatures = listOf(
                    "camera_control",
                    "gimbal_control",
                    "content_download"
                )
            )
        )

        val json = gson.toJson(handshake)
        tcpWriter?.println(json)
        tcpWriter?.flush()

        // Wait for handshake response
        val response = tcpReader?.readLine()
        if (response != null) {
            Log.i(TAG, "Handshake response: $response")
            // Parse and validate handshake response
            updateConnectionState(ConnectionState.OPERATIONAL)
        }
    }

    private fun startUdpStatusListener() {
        statusListenerJob = scope.launch {
            try {
                udpSocket = DatagramSocket(settings.statusListenPort)
                val buffer = ByteArray(4096)

                while (isActive) {
                    val packet = DatagramPacket(buffer, buffer.size)
                    udpSocket?.receive(packet)

                    val json = String(packet.data, 0, packet.length)
                    try {
                        val statusMessage = gson.fromJson(json, BaseMessage::class.java)
                        val statusPayload = gson.fromJson(
                            gson.toJson(statusMessage.payload),
                            StatusPayload::class.java
                        )

                        // Update state flows
                        _cameraStatus.value = statusPayload.camera
                        _systemStatus.value = statusPayload.system

                    } catch (e: Exception) {
                        Log.e(TAG, "Error parsing status message", e)
                    }
                }
            } catch (e: Exception) {
                Log.e(TAG, "UDP status listener error", e)
            }
        }
    }

    /**
     * Start sending heartbeats to Air-Side
     */
    private fun startHeartbeatSender() {
        heartbeatJob = scope.launch {
            try {
                heartbeatSendSocket = DatagramSocket()
                val address = InetAddress.getByName(settings.targetIp)
                val startTime = System.currentTimeMillis()

                while (isActive) {
                    val heartbeat = BaseMessage(
                        messageType = "heartbeat",
                        sequenceId = sequenceId.incrementAndGet(),
                        timestamp = System.currentTimeMillis() / 1000,
                        payload = HeartbeatPayload(
                            sender = "ground",
                            clientId = clientId,  // From settings (e.g., H16, WPC, custom)
                            uptimeSeconds = (System.currentTimeMillis() - startTime) / 1000
                        )
                    )

                    val json = gson.toJson(heartbeat)
                    val bytes = json.toByteArray()
                    val packet = DatagramPacket(
                        bytes,
                        bytes.size,
                        address,
                        settings.heartbeatPort
                    )

                    heartbeatSendSocket?.send(packet)

                    // Update last heartbeat SENT time
                    _connectionStatus.value = _connectionStatus.value.copy(
                        lastHeartbeatSentMs = System.currentTimeMillis()
                    )

                    delay(settings.heartbeatIntervalMs)
                }
            } catch (e: Exception) {
                Log.e(TAG, "Heartbeat sender error", e)
            }
        }
    }

    /**
     * Start receiving heartbeats from Air-Side
     */
    private fun startHeartbeatReceiver() {
        heartbeatReceiverJob = scope.launch {
            try {
                // Bind to port 5002 to receive heartbeats from Air-Side
                val receivePort = settings.heartbeatPort  // Same port Air-Side sends to
                heartbeatReceiveSocket = DatagramSocket(receivePort)
                heartbeatReceiveSocket?.soTimeout = 0  // Non-blocking for continuous receive

                Log.d(TAG, "Heartbeat receiver listening on port $receivePort")

                val buffer = ByteArray(4096)
                while (isActive) {
                    try {
                        val packet = DatagramPacket(buffer, buffer.size)
                        heartbeatReceiveSocket?.receive(packet)

                        val json = String(packet.data, 0, packet.length)
                        Log.d(TAG, "Received heartbeat: ${json.take(200)}")

                        // Parse heartbeat
                        try {
                            val message = gson.fromJson(json, BaseMessage::class.java)
                            if (message.messageType == "heartbeat") {
                                // Update last heartbeat RECEIVED time
                                val now = System.currentTimeMillis()
                                _connectionStatus.value = _connectionStatus.value.copy(
                                    lastHeartbeatReceivedMs = now
                                )
                                Log.d(TAG, "Heartbeat received from Air-Side at $now")
                            }
                        } catch (e: Exception) {
                            Log.w(TAG, "Failed to parse heartbeat: ${e.message}")
                        }

                    } catch (e: SocketException) {
                        if (isActive) {
                            Log.w(TAG, "Heartbeat receiver socket error: ${e.message}")
                        }
                        break
                    } catch (e: Exception) {
                        if (isActive) {
                            Log.w(TAG, "Heartbeat receiver error: ${e.message}")
                        }
                    }
                }
            } catch (e: Exception) {
                Log.e(TAG, "Heartbeat receiver init error", e)
            }
        }
    }

    /**
     * Monitor heartbeat timeout and update connection state
     */
    private fun startHeartbeatWatchdog() {
        heartbeatWatchdogJob = scope.launch {
            // Wait a bit before starting monitoring (give time for first heartbeat)
            delay(3000)
            Log.d(TAG, "Heartbeat watchdog monitoring started")

            while (isActive) {
                val status = _connectionStatus.value

                // Only check if we're supposed to be connected
                if (status.state == ConnectionState.CONNECTED ||
                    status.state == ConnectionState.OPERATIONAL) {

                    val isAlive = status.isHeartbeatAlive(5000)
                    val timeSince = status.timeSinceLastHeartbeat()
                    val timeSinceConnect = System.currentTimeMillis() - status.connectionStartedMs

                    Log.d(TAG, "Watchdog check - isAlive: $isAlive, lastRx: ${status.lastHeartbeatReceivedMs}, " +
                              "timeSinceLastRx: ${timeSince}ms, timeSinceConnect: ${timeSinceConnect}ms")

                    if (!isAlive) {
                        val errorMsg = if (status.lastHeartbeatReceivedMs == 0L) {
                            "Heartbeat timeout: No response from Air-Side after ${timeSinceConnect}ms (never received)"
                        } else {
                            "Heartbeat timeout: No response from Air-Side for ${timeSince}ms"
                        }
                        Log.e(TAG, errorMsg)

                        updateConnectionState(
                            ConnectionState.ERROR,
                            errorMessage = errorMsg,
                            logMessage = errorMsg,
                            logLevel = LogLevel.ERROR
                        )
                    }
                }

                delay(1000)  // Check every second
            }
        }
    }

    private suspend fun sendDisconnect() {
        val disconnect = BaseMessage(
            messageType = "disconnect",
            sequenceId = sequenceId.incrementAndGet(),
            timestamp = System.currentTimeMillis() / 1000,
            payload = mapOf("reason" to "user_requested")
        )

        val json = gson.toJson(disconnect)
        tcpWriter?.println(json)
        tcpWriter?.flush()
    }

    private fun cleanup() {
        // Cancel jobs first
        connectJob?.cancel()
        statusListenerJob?.cancel()
        heartbeatJob?.cancel()
        heartbeatReceiverJob?.cancel()
        heartbeatWatchdogJob?.cancel()

        // Close all I/O streams and sockets in proper order
        try {
            tcpWriter?.close()
        } catch (e: Exception) {
            Log.e(TAG, "Error closing TCP writer", e)
        }

        try {
            tcpReader?.close()
        } catch (e: Exception) {
            Log.e(TAG, "Error closing TCP reader", e)
        }

        try {
            // Shutdown socket gracefully before closing
            tcpSocket?.shutdownInput()
            tcpSocket?.shutdownOutput()
        } catch (e: Exception) {
            // Ignore - socket may already be closed
        }

        try {
            tcpSocket?.close()
        } catch (e: Exception) {
            Log.e(TAG, "Error closing TCP socket", e)
        }

        try {
            udpSocket?.close()
        } catch (e: Exception) {
            Log.e(TAG, "Error closing UDP socket", e)
        }

        try {
            heartbeatSendSocket?.close()
        } catch (e: Exception) {
            Log.e(TAG, "Error closing heartbeat send socket", e)
        }

        try {
            heartbeatReceiveSocket?.close()
        } catch (e: Exception) {
            Log.e(TAG, "Error closing heartbeat receive socket", e)
        }

        // Null out references
        tcpSocket = null
        tcpWriter = null
        tcpReader = null
        udpSocket = null
        heartbeatSendSocket = null
        heartbeatReceiveSocket = null
    }

    private fun updateConnectionState(
        state: ConnectionState,
        errorMessage: String? = null,
        logMessage: String? = null,
        logLevel: LogLevel = LogLevel.INFO
    ) {
        val currentLogs = _connectionStatus.value.connectionLogs
        val newLogs = if (logMessage != null) {
            val newEntry = ConnectionLogEntry(
                timestamp = System.currentTimeMillis(),
                level = logLevel,
                message = logMessage
            )
            // Keep only last 50 log entries to prevent memory issues
            (currentLogs + newEntry).takeLast(50)
        } else {
            currentLogs
        }

        _connectionStatus.value = _connectionStatus.value.copy(
            state = state,
            errorMessage = errorMessage,
            connectionLogs = newLogs
        )
    }

    private fun addConnectionLog(message: String, level: LogLevel = LogLevel.INFO) {
        val currentLogs = _connectionStatus.value.connectionLogs
        val newEntry = ConnectionLogEntry(
            timestamp = System.currentTimeMillis(),
            level = level,
            message = message
        )
        _connectionStatus.value = _connectionStatus.value.copy(
            connectionLogs = (currentLogs + newEntry).takeLast(50)
        )

        // Also log to the global event log
        val eventLevel = when (level) {
            LogLevel.INFO -> EventLevel.INFO
            LogLevel.SUCCESS -> EventLevel.INFO
            LogLevel.WARNING -> EventLevel.WARNING
            LogLevel.ERROR -> EventLevel.ERROR
        }
        EventLogViewModel.logEvent(EventCategory.NETWORK, eventLevel, message)
    }

    fun close() {
        disconnect()
        scope.cancel()
    }
}
