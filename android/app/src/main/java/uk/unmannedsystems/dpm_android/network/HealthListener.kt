package uk.unmannedsystems.dpm_android.network

import com.google.gson.Gson
import com.google.gson.JsonSyntaxException
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import timber.log.Timber
import uk.unmannedsystems.dpm_android.logging.LogContext
import uk.unmannedsystems.dpm_android.model.HealthSnapshot
import java.net.DatagramPacket
import java.net.DatagramSocket
import java.net.SocketException
import java.net.SocketTimeoutException

/**
 * UDP listener for Air-Side health broadcasts
 *
 * Listens on port 5004 for health broadcasts from Air-Side at 5 Hz (200ms interval)
 * Part of Issue #73 - Phase 1: Foundation Infrastructure
 *
 * Features:
 * - Non-blocking UDP reception
 * - JSON parsing with Gson
 * - Automatic stale data detection (>15 seconds)
 * - Connection state tracking
 * - Error handling and recovery
 */
class HealthListener(
    private val port: Int = 5004,
    private val bufferSize: Int = 4096
) {
    companion object {
            private const val SOCKET_TIMEOUT_MS = 5000 // 5 seconds
        private const val STALE_THRESHOLD_MS = 15000L // 15 seconds
    }

    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    private val gson = Gson()

    private var socket: DatagramSocket? = null
    private var isRunning = false

    // Latest health snapshot
    private val _latestHealth = MutableStateFlow<HealthSnapshot?>(null)
    val latestHealth: StateFlow<HealthSnapshot?> = _latestHealth.asStateFlow()

    // Connection state
    private val _isConnected = MutableStateFlow(false)
    val isConnected: StateFlow<Boolean> = _isConnected.asStateFlow()

    // Stale data indicator
    private val _isStale = MutableStateFlow(false)
    val isStale: StateFlow<Boolean> = _isStale.asStateFlow()

    // Last received timestamp
    private val _lastReceivedTime = MutableStateFlow(0L)
    val lastReceivedTime: StateFlow<Long> = _lastReceivedTime.asStateFlow()

    // Error count for monitoring
    private val _errorCount = MutableStateFlow(0)
    val errorCount: StateFlow<Int> = _errorCount.asStateFlow()

    /**
     * Start listening for health broadcasts
     */
    fun start() {
        if (isRunning) {
            Timber.tag(LogContext.HEALTH.label).w( "HealthListener already running")
            return
        }

        Timber.tag(LogContext.HEALTH.label).i( "Starting HealthListener on port $port")
        isRunning = true

        // Launch UDP listener coroutine
        scope.launch {
            try {
                socket = DatagramSocket(port).apply {
                    soTimeout = SOCKET_TIMEOUT_MS
                    reuseAddress = true
                }

                Timber.tag(LogContext.HEALTH.label).i( "UDP socket bound to port $port")
                _isConnected.value = true

                listenLoop()

            } catch (e: SocketException) {
                Timber.tag(LogContext.HEALTH.label).e(e, "Failed to create UDP socket: ${e.message}")
                _isConnected.value = false
                _errorCount.value += 1
            } finally {
                cleanup()
            }
        }

        // Launch stale data monitor coroutine
        scope.launch {
            monitorStaleData()
        }
    }

    /**
     * Main UDP listening loop
     */
    private suspend fun listenLoop() {
        val buffer = ByteArray(bufferSize)
        val packet = DatagramPacket(buffer, buffer.size)

        while (isRunning) {
            try {
                socket?.receive(packet)

                val data = String(packet.data, 0, packet.length)
                Timber.tag(LogContext.HEALTH.label).d( "Received health broadcast (${packet.length} bytes) from ${packet.address}:${packet.port}")

                // Parse JSON to HealthSnapshot
                val health = parseHealthSnapshot(data)
                if (health != null) {
                    _latestHealth.value = health
                    _lastReceivedTime.value = System.currentTimeMillis()
                    _isStale.value = false

                    Timber.tag(LogContext.HEALTH.label).v("Health update: CPU=${health.system.cpuPercent}%, " +
                            "MEM=${health.system.memoryPercent.toInt()}%, " +
                            "CAM=${if (health.camera.connected) "connected" else "disconnected"}")
                } else {
                    Timber.tag(LogContext.HEALTH.label).w( "Failed to parse health broadcast")
                    _errorCount.value += 1
                }

            } catch (e: SocketTimeoutException) {
                // Timeout is normal - continue listening
                Timber.tag(LogContext.HEALTH.label).v("Socket timeout (no data received in ${SOCKET_TIMEOUT_MS}ms)")

            } catch (e: SocketException) {
                if (isRunning) {
                    Timber.tag(LogContext.HEALTH.label).e(e, "Socket error: ${e.message}")
                    _errorCount.value += 1
                }
                break

            } catch (e: Exception) {
                Timber.tag(LogContext.HEALTH.label).e(e, "Unexpected error in listen loop: ${e.message}")
                _errorCount.value += 1
            }
        }
    }

    /**
     * Monitor for stale data (no updates for >15 seconds)
     */
    private suspend fun monitorStaleData() {
        while (isRunning) {
            kotlinx.coroutines.delay(1000) // Check every second

            val lastReceived = _lastReceivedTime.value
            if (lastReceived > 0) {
                val elapsed = System.currentTimeMillis() - lastReceived
                val isCurrentlyStale = elapsed > STALE_THRESHOLD_MS

                if (isCurrentlyStale != _isStale.value) {
                    _isStale.value = isCurrentlyStale
                    if (isCurrentlyStale) {
                        Timber.tag(LogContext.HEALTH.label).w( "Health data is STALE (no updates for ${elapsed}ms)")
                    } else {
                        Timber.tag(LogContext.HEALTH.label).i( "Health data is FRESH again")
                    }
                }
            }
        }
    }

    /**
     * Parse JSON string to HealthSnapshot
     */
    private fun parseHealthSnapshot(json: String): HealthSnapshot? {
        return try {
            gson.fromJson(json, HealthSnapshot::class.java)
        } catch (e: JsonSyntaxException) {
            Timber.tag(LogContext.HEALTH.label).e(e, "JSON parsing error: ${e.message}")
            Timber.tag(LogContext.HEALTH.label).e("Invalid JSON: $json")
            null
        } catch (e: Exception) {
            Timber.tag(LogContext.HEALTH.label).e(e, "Unexpected parsing error: ${e.message}")
            null
        }
    }

    /**
     * Stop listening for health broadcasts
     */
    fun stop() {
        if (!isRunning) {
            Timber.tag(LogContext.HEALTH.label).w( "HealthListener not running")
            return
        }

        Timber.tag(LogContext.HEALTH.label).i( "Stopping HealthListener")
        isRunning = false
        cleanup()
    }

    /**
     * Cleanup resources
     */
    private fun cleanup() {
        try {
            socket?.close()
            socket = null
            _isConnected.value = false
            Timber.tag(LogContext.HEALTH.label).i( "HealthListener stopped and cleaned up")
        } catch (e: Exception) {
            Timber.tag(LogContext.HEALTH.label).e(e, "Error during cleanup: ${e.message}")
        }
    }

    /**
     * Get current connection statistics
     */
    fun getStats(): HealthListenerStats {
        val health = _latestHealth.value
        return HealthListenerStats(
            isRunning = isRunning,
            isConnected = _isConnected.value,
            isStale = _isStale.value,
            errorCount = _errorCount.value,
            lastReceivedTime = _lastReceivedTime.value,
            hasData = health != null
        )
    }
}

/**
 * Health listener statistics for monitoring
 */
data class HealthListenerStats(
    val isRunning: Boolean,
    val isConnected: Boolean,
    val isStale: Boolean,
    val errorCount: Int,
    val lastReceivedTime: Long,
    val hasData: Boolean
)
