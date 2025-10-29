package uk.unmannedsystems.dpm_android.network

/**
 * Network configuration settings for communication with Raspberry Pi
 */
data class NetworkSettings(
    val targetIp: String = "192.168.144.10",  // Air-Side Pi ethernet address
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
 * Connection log entry for diagnostics
 */
data class ConnectionLogEntry(
    val timestamp: Long = System.currentTimeMillis(),
    val level: LogLevel,
    val message: String
)

enum class LogLevel {
    INFO,
    SUCCESS,
    WARNING,
    ERROR
}

/**
 * Network connection status
 */
data class NetworkStatus(
    val state: ConnectionState = ConnectionState.DISCONNECTED,
    val lastHeartbeatSentMs: Long = 0,       // When we last sent a heartbeat
    val lastHeartbeatReceivedMs: Long = 0,   // When we last received a heartbeat from Air-Side
    val connectionStartedMs: Long = 0,       // When the connection was established
    val roundTripTimeMs: Long = 0,
    val errorMessage: String? = null,
    val connectionLogs: List<ConnectionLogEntry> = emptyList(),
    val targetIp: String? = null,
    val targetPort: Int? = null
) {
    /**
     * Check if connection is healthy (received heartbeat recently)
     * @param timeoutMs Maximum time since last heartbeat before considering connection dead
     */
    fun isHeartbeatAlive(timeoutMs: Long = 5000): Boolean {
        // If we've never received a heartbeat from Air-Side
        if (lastHeartbeatReceivedMs == 0L) {
            // Grace period: Allow 10 seconds after connection for first heartbeat
            // After that, if still no heartbeat received, consider connection dead
            if (connectionStartedMs == 0L) return true  // Not yet connected
            val gracePeriodMs = 10000L
            val timeSinceConnect = System.currentTimeMillis() - connectionStartedMs
            return timeSinceConnect < gracePeriodMs
        }
        // Normal check: has it been too long since last heartbeat?
        return System.currentTimeMillis() - lastHeartbeatReceivedMs < timeoutMs
    }

    /**
     * Time since last heartbeat received in milliseconds
     */
    fun timeSinceLastHeartbeat(): Long {
        if (lastHeartbeatReceivedMs == 0L) return 0L
        return System.currentTimeMillis() - lastHeartbeatReceivedMs
    }
}

/**
 * Video stream settings for RTSP video display
 */
data class VideoStreamSettings(
    val enabled: Boolean = true,
    val rtspUrl: String = "rtsp://192.168.1.10:8554/H264Video",
    val aspectRatioMode: AspectRatioMode = AspectRatioMode.FILL,
    val bufferDurationMs: Long = 500  // Low latency: 500ms buffer
)

/**
 * Aspect ratio mode for video display
 */
enum class AspectRatioMode {
    AUTO,   // Detect from stream
    FILL,   // Fill entire screen
    FIT     // Fit to screen maintaining aspect ratio
}
