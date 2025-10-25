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
    }

    /**
     * Connect to Air-Side
     */
    fun connect() {
        Log.d(TAG, "Connect requested")
        networkClient?.connect() ?: Log.w(TAG, "NetworkClient not initialized")
    }

    /**
     * Disconnect from Air-Side
     */
    fun disconnect() {
        Log.d(TAG, "Disconnect requested")
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
}
