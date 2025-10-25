package uk.unmannedsystems.dpm_android.network

import android.util.Log
import com.google.gson.Gson
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
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
    private val settings: NetworkSettings = NetworkSettings()
) {
    companion object {
        private const val TAG = "NetworkClient"
        private const val CLIENT_ID = "h16_gcs_001"
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
    private var heartbeatSocket: DatagramSocket? = null

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

    /**
     * Connect to the Raspberry Pi
     */
    fun connect() {
        if (_connectionStatus.value.state == ConnectionState.CONNECTED ||
            _connectionStatus.value.state == ConnectionState.CONNECTING) {
            Log.w(TAG, "Already connected or connecting")
            return
        }

        connectJob = scope.launch {
            updateConnectionState(ConnectionState.CONNECTING)

            try {
                // Connect TCP socket
                connectTcp()

                // Send handshake
                sendHandshake()

                // Start UDP status listener
                startUdpStatusListener()

                // Start heartbeat
                startHeartbeat()

                updateConnectionState(ConnectionState.CONNECTED)
                Log.i(TAG, "Connected to ${settings.targetIp}")

            } catch (e: Exception) {
                Log.e(TAG, "Connection failed", e)
                updateConnectionState(
                    ConnectionState.ERROR,
                    "Connection failed: ${e.message}"
                )

                // Retry connection after delay
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
            try {
                // Send disconnect message
                sendDisconnect()
            } catch (e: Exception) {
                Log.e(TAG, "Error sending disconnect", e)
            }

            cleanup()
            updateConnectionState(ConnectionState.DISCONNECTED)

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
                clientId = CLIENT_ID,
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

    private fun startHeartbeat() {
        heartbeatJob = scope.launch {
            try {
                heartbeatSocket = DatagramSocket()
                val address = InetAddress.getByName(settings.targetIp)
                val startTime = System.currentTimeMillis()

                while (isActive) {
                    val heartbeat = BaseMessage(
                        messageType = "heartbeat",
                        sequenceId = sequenceId.incrementAndGet(),
                        timestamp = System.currentTimeMillis() / 1000,
                        payload = HeartbeatPayload(
                            sender = "ground",
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

                    heartbeatSocket?.send(packet)

                    // Update last heartbeat time
                    _connectionStatus.value = _connectionStatus.value.copy(
                        lastHeartbeatMs = System.currentTimeMillis()
                    )

                    delay(settings.heartbeatIntervalMs)
                }
            } catch (e: Exception) {
                Log.e(TAG, "Heartbeat error", e)
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
            heartbeatSocket?.close()
        } catch (e: Exception) {
            Log.e(TAG, "Error closing heartbeat socket", e)
        }

        // Null out references
        tcpSocket = null
        tcpWriter = null
        tcpReader = null
        udpSocket = null
        heartbeatSocket = null
    }

    private fun updateConnectionState(state: ConnectionState, errorMessage: String? = null) {
        _connectionStatus.value = _connectionStatus.value.copy(
            state = state,
            errorMessage = errorMessage
        )
    }

    fun close() {
        disconnect()
        scope.cancel()
    }
}
