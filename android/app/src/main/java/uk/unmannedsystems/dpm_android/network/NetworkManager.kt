package uk.unmannedsystems.dpm_android.network

import android.util.Log
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

/**
 * Singleton manager for network connection
 * Ensures single connection instance shared across the app
 */
object NetworkManager {
    private const val TAG = "NetworkManager"

    private val scope = CoroutineScope(Dispatchers.Main + SupervisorJob())

    private var networkClient: NetworkClient? = null

    // Stable StateFlow that survives networkClient recreation
    private val _connectionStatus = MutableStateFlow(NetworkStatus())
    val connectionStatus: StateFlow<NetworkStatus> = _connectionStatus.asStateFlow()

    private val _currentSettings = MutableStateFlow(NetworkSettings())
    val currentSettings: StateFlow<NetworkSettings> = _currentSettings.asStateFlow()

    private val _systemStatus = MutableStateFlow<SystemStatus?>(null)
    val systemStatus: StateFlow<SystemStatus?> = _systemStatus.asStateFlow()

    private val _cameraStatus = MutableStateFlow<CameraStatusInfo?>(null)
    val cameraStatus: StateFlow<CameraStatusInfo?> = _cameraStatus.asStateFlow()

    // Auto-reconnect state
    private var autoReconnectEnabled = false
    private var autoReconnectIntervalSeconds = 5
    private var reconnectJob: kotlinx.coroutines.Job? = null
    private var isManualDisconnect = false

    /**
     * Initialize or reinitialize network client with new settings
     */
    fun initialize(settings: NetworkSettings) {
        Log.d(TAG, "Initializing with settings: ${settings.targetIp}:${settings.commandPort}")

        // Disconnect and cleanup old client
        networkClient?.close()

        // Create new client
        networkClient = NetworkClient(settings)
        _currentSettings.value = settings

        // Forward connection status to our stable StateFlow
        scope.launch {
            networkClient?.connectionStatus?.collect { status ->
                _connectionStatus.value = status
                Log.d(TAG, "Connection status updated: ${status.state}")
            }
        }

        // Forward system status to our stable StateFlow
        scope.launch {
            networkClient?.systemStatus?.collect { status ->
                _systemStatus.value = status
            }
        }

        // Forward camera status to our stable StateFlow
        scope.launch {
            networkClient?.cameraStatus?.collect { status ->
                _cameraStatus.value = status
            }
        }
    }

    /**
     * Connect to Air-Side
     */
    fun connect() {
        Log.d(TAG, "Connect requested")
        isManualDisconnect = false  // Reset manual disconnect flag
        networkClient?.connect() ?: Log.w(TAG, "NetworkClient not initialized")
    }

    /**
     * Disconnect from Air-Side
     */
    fun disconnect() {
        Log.d(TAG, "Disconnect requested")
        isManualDisconnect = true
        stopAutoReconnect()
        networkClient?.disconnect()
    }

    /**
     * Request system status from Air-Side
     */
    suspend fun getSystemStatus(): Result<ResponsePayload> {
        val client = networkClient
        return if (client != null) {
            client.getSystemStatus()
        } else {
            Result.failure(Exception("NetworkClient not initialized"))
        }
    }

    /**
     * Get the current network client instance
     */
    fun getClient(): NetworkClient? = networkClient

    /**
     * Check if client is initialized
     */
    fun isInitialized(): Boolean = networkClient != null

    /**
     * Configure auto-reconnect settings
     */
    fun configureAutoReconnect(enabled: Boolean, intervalSeconds: Int) {
        Log.d(TAG, "Configuring auto-reconnect: enabled=$enabled, interval=${intervalSeconds}s")
        autoReconnectEnabled = enabled
        autoReconnectIntervalSeconds = intervalSeconds

        if (enabled) {
            startAutoReconnectMonitoring()
        } else {
            stopAutoReconnect()
        }
    }

    /**
     * Start monitoring connection state for auto-reconnect
     */
    private fun startAutoReconnectMonitoring() {
        // Cancel existing monitoring
        reconnectJob?.cancel()

        // Start new monitoring job
        reconnectJob = scope.launch {
            connectionStatus.collect { status ->
                // Only attempt reconnect if:
                // 1. Auto-reconnect is enabled
                // 2. Connection is disconnected or in error state
                // 3. Not a manual disconnect
                if (autoReconnectEnabled &&
                    !isManualDisconnect &&
                    (status.state == ConnectionState.DISCONNECTED || status.state == ConnectionState.ERROR)) {

                    Log.d(TAG, "Connection lost, will attempt reconnect in ${autoReconnectIntervalSeconds}s")
                    kotlinx.coroutines.delay(autoReconnectIntervalSeconds * 1000L)

                    // Check again after delay to make sure we still need to reconnect
                    if (autoReconnectEnabled &&
                        !isManualDisconnect &&
                        (connectionStatus.value.state == ConnectionState.DISCONNECTED ||
                         connectionStatus.value.state == ConnectionState.ERROR)) {

                        Log.d(TAG, "Attempting auto-reconnect...")
                        isManualDisconnect = false  // Reset manual disconnect flag
                        networkClient?.connect()
                    }
                }
            }
        }
    }

    /**
     * Stop auto-reconnect monitoring
     */
    private fun stopAutoReconnect() {
        Log.d(TAG, "Stopping auto-reconnect")
        reconnectJob?.cancel()
        reconnectJob = null
    }
}
