package uk.unmannedsystems.dpm_android.diagnostics

import android.content.Context
import timber.log.Timber
import uk.unmannedsystems.dpm_android.logging.LogContext
import uk.unmannedsystems.dpm_android.network.ResponsePayload
import uk.unmannedsystems.dpm_android.network.ErrorInfo
import java.text.SimpleDateFormat
import java.util.*

/**
 * Handles diagnostic commands for H16 Ground-Side system monitoring
 *
 * Implements diagnostic protocol commands:
 * - diagnostics.ping
 * - diagnostics.get_system_info
 * - diagnostics.get_app_status
 *
 * Protocol: protocol/diagnostics_protocol.json
 */
class DiagnosticsCommandHandler(private val context: Context) {
    companion object {
        // Diagnostic error codes (6000-6999)
        const val ERROR_NOT_AVAILABLE = 6000
        const val ERROR_TIMEOUT = 6001
        const val ERROR_PERMISSION_DENIED = 6002
        const val ERROR_DATA_UNAVAILABLE = 6003
        const val ERROR_COMMAND_FAILED = 6004

        // Cache TTL in milliseconds
        private const val CACHE_TTL_MS = 1000L  // 1 second for system_info and app_status
    }

    private val systemInfoCollector = SystemInfoCollector(context)
    private val appStatusTracker = AppStatusTracker(context)

    // Cache for system_info to prevent excessive computation
    private data class CachedValue<T>(
        val value: T,
        val timestamp: Long
    ) {
        fun isValid(ttlMs: Long): Boolean {
            return System.currentTimeMillis() - timestamp < ttlMs
        }
    }

    private var systemInfoCache: CachedValue<Map<String, Any>>? = null
    private var appStatusCache: CachedValue<Map<String, Any>>? = null

    /**
     * Handle incoming diagnostic command
     *
     * @param command Command name (e.g., "diagnostics.ping")
     * @param parameters Command parameters
     * @return ResponsePayload with success/error and data
     */
    fun handleCommand(command: String, parameters: Map<String, Any>): ResponsePayload {
        Timber.tag(LogContext.COMMAND.label).d("Handling diagnostic command: $command")

        return try {
            when (command) {
                "diagnostics.ping" -> handlePing()
                "diagnostics.get_system_info" -> handleGetSystemInfo()
                "diagnostics.get_app_status" -> handleGetAppStatus()
                "diagnostics.get_network_stats" -> handleGetNetworkStats()
                "diagnostics.get_adb_status" -> handleGetAdbStatus()
                "diagnostics.get_logs" -> handleGetLogs(parameters)
                else -> ResponsePayload(
                    command = command,
                    status = "error",
                    error = ErrorInfo(
                        code = ERROR_NOT_AVAILABLE,
                        message = "DIAGNOSTIC_NOT_AVAILABLE: Command not implemented: $command"
                    )
                )
            }
        } catch (e: Exception) {
            Timber.tag(LogContext.COMMAND.label).e(e, "Error handling diagnostic command: $command")
            ResponsePayload(
                command = command,
                status = "error",
                error = ErrorInfo(
                    code = ERROR_COMMAND_FAILED,
                    message = "DIAGNOSTIC_COMMAND_FAILED: ${e.message}",
                    details = e.stackTraceToString()
                )
            )
        }
    }

    /**
     * Handle diagnostics.ping command
     * Simple alive check - respond immediately with timestamp
     */
    private fun handlePing(): ResponsePayload {
        val data = mapOf(
            "pong" to true,
            "timestamp" to getCurrentTimestampISO(),
            "source" to "ground"
        )

        return ResponsePayload(
            command = "diagnostics.ping",
            status = "success",
            result = data
        )
    }

    /**
     * Handle diagnostics.get_system_info command
     * Get comprehensive H16 system information with caching
     */
    private fun handleGetSystemInfo(): ResponsePayload {
        // Check cache first
        val cached = systemInfoCache
        if (cached != null && cached.isValid(CACHE_TTL_MS)) {
            Timber.tag(LogContext.COMMAND.label).d("Returning cached system info")
            return ResponsePayload(
                command = "diagnostics.get_system_info",
                status = "success",
                result = cached.value
            )
        }

        // Collect fresh data
        val data = systemInfoCollector.collect()

        // Update cache
        systemInfoCache = CachedValue(data, System.currentTimeMillis())

        return ResponsePayload(
            command = "diagnostics.get_system_info",
            status = "success",
            result = data
        )
    }

    /**
     * Handle diagnostics.get_app_status command
     * Get H16 Payload Manager app detailed status with caching
     */
    private fun handleGetAppStatus(): ResponsePayload {
        // Check cache first
        val cached = appStatusCache
        if (cached != null && cached.isValid(CACHE_TTL_MS)) {
            Timber.tag(LogContext.COMMAND.label).d("Returning cached app status")
            return ResponsePayload(
                command = "diagnostics.get_app_status",
                status = "success",
                result = cached.value
            )
        }

        // Collect fresh data
        val data = appStatusTracker.getStatus()

        // Update cache
        appStatusCache = CachedValue(data, System.currentTimeMillis())

        return ResponsePayload(
            command = "diagnostics.get_app_status",
            status = "success",
            result = data
        )
    }

    /**
     * Handle diagnostics.get_network_stats command (Phase 2)
     */
    private fun handleGetNetworkStats(): ResponsePayload {
        return ResponsePayload(
            command = "diagnostics.get_network_stats",
            status = "error",
            error = ErrorInfo(
                code = ERROR_NOT_AVAILABLE,
                message = "DIAGNOSTIC_NOT_AVAILABLE: Phase 2 command not yet implemented"
            )
        )
    }

    /**
     * Handle diagnostics.get_adb_status command (Phase 2)
     */
    private fun handleGetAdbStatus(): ResponsePayload {
        return ResponsePayload(
            command = "diagnostics.get_adb_status",
            status = "error",
            error = ErrorInfo(
                code = ERROR_NOT_AVAILABLE,
                message = "DIAGNOSTIC_NOT_AVAILABLE: Phase 2 command not yet implemented"
            )
        )
    }

    /**
     * Handle diagnostics.get_logs command (Phase 2)
     */
    private fun handleGetLogs(parameters: Map<String, Any>): ResponsePayload {
        return ResponsePayload(
            command = "diagnostics.get_logs",
            status = "error",
            error = ErrorInfo(
                code = ERROR_NOT_AVAILABLE,
                message = "DIAGNOSTIC_NOT_AVAILABLE: Phase 2 command not yet implemented"
            )
        )
    }

    /**
     * Get current timestamp in ISO 8601 format
     */
    private fun getCurrentTimestampISO(): String {
        val sdf = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'", Locale.US)
        sdf.timeZone = TimeZone.getTimeZone("UTC")
        return sdf.format(Date())
    }

    /**
     * Clear all caches (useful for testing or on-demand refresh)
     */
    fun clearCache() {
        systemInfoCache = null
        appStatusCache = null
        Timber.tag(LogContext.COMMAND.label).d("Diagnostic caches cleared")
    }
}
