package uk.unmannedsystems.dpm_android.network

/**
 * Network configuration settings for communication with Raspberry Pi
 */
data class NetworkSettings(
    val targetIp: String = "192.168.144.20",
    val commandPort: Int = 5000,
    val statusListenPort: Int = 5001,
    val heartbeatPort: Int = 5002,
    val connectionTimeoutMs: Long = 5000,
    val heartbeatIntervalMs: Long = 1000,
    val statusBroadcastIntervalMs: Long = 200
)

/**
 * Connection state
 */
enum class ConnectionState {
    DISCONNECTED,
    CONNECTING,
    CONNECTED,
    OPERATIONAL,
    ERROR
}

/**
 * Network connection status
 */
data class NetworkStatus(
    val state: ConnectionState = ConnectionState.DISCONNECTED,
    val lastHeartbeatMs: Long = 0,
    val roundTripTimeMs: Long = 0,
    val errorMessage: String? = null
)
