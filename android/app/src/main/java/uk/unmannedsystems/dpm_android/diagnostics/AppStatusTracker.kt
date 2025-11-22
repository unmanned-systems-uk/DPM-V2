package uk.unmannedsystems.dpm_android.diagnostics

import android.app.ActivityManager
import android.content.Context
import android.content.pm.PackageManager
import android.os.Debug
import android.os.Process
import timber.log.Timber
import uk.unmannedsystems.dpm_android.BuildConfig
import uk.unmannedsystems.dpm_android.logging.LogContext
import uk.unmannedsystems.dpm_android.network.NetworkManager
import java.text.SimpleDateFormat
import java.util.*

/**
 * Tracks H16 Payload Manager app status for diagnostics
 *
 * Provides information about:
 * - App running state, version, PID
 * - App uptime
 * - Last error information
 * - Active connections (air-side, camera, gimbal)
 * - Thread count, memory usage
 *
 * Reference: protocol/diagnostics_protocol.json
 */
class AppStatusTracker(private val context: Context) {
    companion object {
        // Singleton instance to track errors and state across app
        @Volatile
        private var instance: AppStatusTracker? = null

        fun getInstance(context: Context): AppStatusTracker {
            return instance ?: synchronized(this) {
                instance ?: AppStatusTracker(context.applicationContext).also { instance = it }
            }
        }
    }

    private val startTimeMs = System.currentTimeMillis()

    // Error tracking
    private var lastError: String? = null
    private var lastErrorTime: String? = null

    /**
     * Get comprehensive app status
     *
     * @return Map with app status matching diagnostics_protocol.json format
     */
    fun getStatus(): Map<String, Any> {
        return mapOf(
            "app_running" to true,  // If we're executing this code, app is running
            "app_version" to getAppVersion(),
            "app_state" to getAppState(),
            "pid" to getPid(),
            "uptime_seconds" to getUptimeSeconds(),
            "last_error" to (lastError ?: "null"),
            "last_error_time" to (lastErrorTime ?: "null"),
            "active_connections" to getActiveConnections(),
            "thread_count" to getThreadCount(),
            "memory_usage_mb" to getMemoryUsageMb()
        )
    }

    /**
     * Get app version string
     *
     * Uses BuildConfig.VERSION_NAME from Gradle
     */
    private fun getAppVersion(): String {
        return try {
            BuildConfig.VERSION_NAME
        } catch (e: Exception) {
            // Fallback to PackageManager
            try {
                val packageInfo = context.packageManager.getPackageInfo(context.packageName, 0)
                packageInfo.versionName ?: "unknown"
            } catch (e2: Exception) {
                Timber.tag(LogContext.SYSTEM.label).e(e2, "Error getting app version")
                "unknown"
            }
        }
    }

    /**
     * Get current app state
     *
     * @return "running", "starting", "stopping", or "error"
     */
    private fun getAppState(): String {
        // For now, if we're executing, we're running
        // Could be enhanced to track lifecycle states
        return "running"
    }

    /**
     * Get process ID
     *
     * API: Process.myPid()
     */
    private fun getPid(): Int {
        return Process.myPid()
    }

    /**
     * Get app uptime in seconds
     */
    private fun getUptimeSeconds(): Long {
        val uptimeMs = System.currentTimeMillis() - startTimeMs
        return uptimeMs / 1000
    }

    /**
     * Get active connection status
     *
     * Checks NetworkManager for Air-Side connection
     * TODO: Add camera and gimbal connection status when available
     */
    private fun getActiveConnections(): Map<String, Boolean> {
        val airSideConnected = try {
            val connectionStatus = NetworkManager.connectionStatus.value
            connectionStatus.state == uk.unmannedsystems.dpm_android.network.ConnectionState.OPERATIONAL ||
            connectionStatus.state == uk.unmannedsystems.dpm_android.network.ConnectionState.CONNECTED
        } catch (e: Exception) {
            Timber.tag(LogContext.SYSTEM.label).e(e, "Error checking Air-Side connection")
            false
        }

        // Camera and gimbal connections not directly tracked yet
        // These would need to be integrated with camera/gimbal managers
        return mapOf(
            "air_side_connected" to airSideConnected,
            "camera_connected" to false,  // TODO: Integrate with camera manager
            "gimbal_connected" to false   // TODO: Integrate with gimbal manager
        )
    }

    /**
     * Get active thread count for this process
     *
     * Uses ActivityManager to query process info
     */
    private fun getThreadCount(): Int {
        return try {
            val activityManager = context.getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager
            val processes = activityManager.runningAppProcesses ?: return -1

            val myPid = Process.myPid()
            val myProcess = processes.find { it.pid == myPid }

            // Thread count not directly available via ActivityManager
            // Fallback: count threads via Thread API
            Thread.activeCount()

        } catch (e: Exception) {
            Timber.tag(LogContext.SYSTEM.label).e(e, "Error getting thread count")
            -1
        }
    }

    /**
     * Get app memory usage in MB
     *
     * API: Debug.MemoryInfo
     */
    private fun getMemoryUsageMb(): Float {
        return try {
            val activityManager = context.getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager
            val pid = Process.myPid()

            val memoryInfo = activityManager.getProcessMemoryInfo(intArrayOf(pid))
            if (memoryInfo.isNotEmpty()) {
                val totalPss = memoryInfo[0].totalPss  // in kB
                (totalPss / 1024f)  // Convert to MB
            } else {
                -1f
            }

        } catch (e: Exception) {
            Timber.tag(LogContext.SYSTEM.label).e(e, "Error getting memory usage")
            -1f
        }
    }

    /**
     * Record an error for diagnostic tracking
     *
     * @param error Error message
     */
    fun recordError(error: String) {
        lastError = error
        lastErrorTime = getCurrentTimestampISO()
        Timber.tag(LogContext.SYSTEM.label).e("Error recorded: $error at $lastErrorTime")
    }

    /**
     * Clear last error
     */
    fun clearError() {
        lastError = null
        lastErrorTime = null
        Timber.tag(LogContext.SYSTEM.label).d("Error cleared")
    }

    /**
     * Get current timestamp in ISO 8601 format
     */
    private fun getCurrentTimestampISO(): String {
        val sdf = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'", Locale.US)
        sdf.timeZone = TimeZone.getTimeZone("UTC")
        return sdf.format(Date())
    }
}
