package uk.unmannedsystems.dpm_android.diagnostics

import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.os.BatteryManager
import android.os.Build
import android.os.StatFs
import java.io.BufferedReader
import java.io.File
import java.io.FileReader
import java.text.SimpleDateFormat
import java.util.*
import timber.log.Timber
import uk.unmannedsystems.dpm_android.logging.LogContext

/**
 * Collects H16 system information for diagnostics
 *
 * Gathers metrics using Android APIs and Linux proc filesystem:
 * - Battery level, status, temperature
 * - CPU usage percentage
 * - Memory (total, available, used)
 * - Storage (total, available, used)
 * - CPU temperature
 * - System uptime
 * - Android version, kernel version
 *
 * Reference: protocol/system_properties.json
 */
class SystemInfoCollector(private val context: Context) {
    companion object {
        }

    // Track last CPU stats for usage calculation
    private data class CpuStats(
        val total: Long,
        val idle: Long,
        val timestamp: Long
    )

    private var lastCpuStats: CpuStats? = null

    /**
     * Collect comprehensive system information
     *
     * @return Map with all system properties matching diagnostics_protocol.json format
     */
    fun collect(): Map<String, Any> {
        return mapOf(
            "battery_percent" to getBatteryPercent(),
            "cpu_usage_percent" to getCpuUsagePercent(),
            "memory_total_mb" to getMemoryTotalMb(),
            "memory_available_mb" to getMemoryAvailableMb(),
            "memory_used_mb" to getMemoryUsedMb(),
            "storage_total_gb" to getStorageTotalGb(),
            "storage_available_gb" to getStorageAvailableGb(),
            "storage_used_gb" to getStorageUsedGb(),
            "cpu_temperature_c" to getCpuTemperature(),
            "uptime_seconds" to getUptimeSeconds(),
            "system_time" to getCurrentTimestampISO(),
            "android_version" to getAndroidVersion(),
            "kernel_version" to getKernelVersion()
        )
    }

    /**
     * Get battery charge percentage (0-100)
     *
     * API: BatteryManager.BATTERY_PROPERTY_CAPACITY
     */
    private fun getBatteryPercent(): Int {
        return try {
            val batteryManager = context.getSystemService(Context.BATTERY_SERVICE) as BatteryManager
            batteryManager.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY)
        } catch (e: Exception) {
            Timber.tag(LogContext.SYSTEM.label).e(e, "Error getting battery percent")
            // Fallback to Intent-based approach
            try {
                val intentFilter = IntentFilter(Intent.ACTION_BATTERY_CHANGED)
                val batteryStatus = context.registerReceiver(null, intentFilter)
                val level = batteryStatus?.getIntExtra(BatteryManager.EXTRA_LEVEL, -1) ?: -1
                val scale = batteryStatus?.getIntExtra(BatteryManager.EXTRA_SCALE, -1) ?: -1
                if (level >= 0 && scale > 0) {
                    (level * 100 / scale)
                } else {
                    -1
                }
            } catch (e2: Exception) {
                Timber.tag(LogContext.SYSTEM.label).e(e2, "Error getting battery percent via intent")
                -1
            }
        }
    }

    /**
     * Get CPU usage percentage (0-100)
     *
     * Method: Parse /proc/stat and calculate delta
     */
    private fun getCpuUsagePercent(): Float {
        return try {
            val reader = BufferedReader(FileReader("/proc/stat"))
            val line = reader.readLine()
            reader.close()

            // Parse: cpu  user nice system idle iowait irq softirq
            val parts = line.split("\\s+".toRegex())
            if (parts.size < 5) return -1f

            val user = parts[1].toLongOrNull() ?: 0
            val nice = parts[2].toLongOrNull() ?: 0
            val system = parts[3].toLongOrNull() ?: 0
            val idle = parts[4].toLongOrNull() ?: 0

            val total = user + nice + system + idle
            val now = System.currentTimeMillis()

            val last = lastCpuStats
            lastCpuStats = CpuStats(total, idle, now)

            if (last == null) {
                // First read, can't calculate usage yet
                return 0f
            }

            val totalDelta = total - last.total
            val idleDelta = idle - last.idle

            if (totalDelta == 0L) return 0f

            val usage = ((totalDelta - idleDelta).toFloat() / totalDelta.toFloat()) * 100f
            usage.coerceIn(0f, 100f)

        } catch (e: Exception) {
            Timber.tag(LogContext.SYSTEM.label).e(e, "Error reading CPU usage")
            -1f
        }
    }

    /**
     * Get total system memory in MB
     *
     * Method: Parse /proc/meminfo MemTotal
     */
    private fun getMemoryTotalMb(): Int {
        return try {
            val reader = BufferedReader(FileReader("/proc/meminfo"))
            val line = reader.readLine()  // First line is MemTotal
            reader.close()

            // Parse: MemTotal:        2048000 kB
            val parts = line.split("\\s+".toRegex())
            if (parts.size < 2) return -1

            val kb = parts[1].toLongOrNull() ?: return -1
            (kb / 1024).toInt()  // Convert kB to MB

        } catch (e: Exception) {
            Timber.tag(LogContext.SYSTEM.label).e(e, "Error reading total memory")
            -1
        }
    }

    /**
     * Get available system memory in MB
     *
     * Method: Parse /proc/meminfo MemAvailable
     */
    private fun getMemoryAvailableMb(): Int {
        return try {
            val reader = BufferedReader(FileReader("/proc/meminfo"))
            var availableKb: Long? = null

            // Read lines until we find MemAvailable
            reader.use {
                it.lineSequence().forEach { line ->
                    if (line.startsWith("MemAvailable:")) {
                        val parts = line.split("\\s+".toRegex())
                        if (parts.size >= 2) {
                            availableKb = parts[1].toLongOrNull()
                            return@forEach
                        }
                    }
                }
            }

            if (availableKb != null) {
                (availableKb!! / 1024).toInt()  // Convert kB to MB
            } else {
                -1
            }

        } catch (e: Exception) {
            Timber.tag(LogContext.SYSTEM.label).e(e, "Error reading available memory")
            -1
        }
    }

    /**
     * Get used system memory in MB
     *
     * Calculation: total_mb - available_mb
     */
    private fun getMemoryUsedMb(): Int {
        val total = getMemoryTotalMb()
        val available = getMemoryAvailableMb()
        return if (total > 0 && available > 0) {
            total - available
        } else {
            -1
        }
    }

    /**
     * Get total storage in GB
     *
     * API: StatFs.getTotalBytes() for /data partition
     */
    private fun getStorageTotalGb(): Float {
        return try {
            val stat = StatFs("/data")
            val totalBytes = stat.totalBytes
            (totalBytes / (1024.0 * 1024.0 * 1024.0)).toFloat()
        } catch (e: Exception) {
            Timber.tag(LogContext.SYSTEM.label).e(e, "Error reading total storage")
            -1f
        }
    }

    /**
     * Get available storage in GB
     *
     * API: StatFs.getAvailableBytes() for /data partition
     */
    private fun getStorageAvailableGb(): Float {
        return try {
            val stat = StatFs("/data")
            val availableBytes = stat.availableBytes
            (availableBytes / (1024.0 * 1024.0 * 1024.0)).toFloat()
        } catch (e: Exception) {
            Timber.tag(LogContext.SYSTEM.label).e(e, "Error reading available storage")
            -1f
        }
    }

    /**
     * Get used storage in GB
     *
     * Calculation: total_gb - available_gb
     */
    private fun getStorageUsedGb(): Float {
        val total = getStorageTotalGb()
        val available = getStorageAvailableGb()
        return if (total > 0 && available > 0) {
            total - available
        } else {
            -1f
        }
    }

    /**
     * Get CPU temperature in Celsius
     *
     * Method: Read /sys/class/thermal/thermal_zone[N]/temp
     * Note: May not be available on all devices
     */
    private fun getCpuTemperature(): Float {
        return try {
            val thermalDir = File("/sys/class/thermal")
            if (!thermalDir.exists()) return -1f

            // Find first thermal zone with valid temperature
            thermalDir.listFiles()?.forEach { zone ->
                if (zone.name.startsWith("thermal_zone")) {
                    val tempFile = File(zone, "temp")
                    if (tempFile.exists()) {
                        val temp = tempFile.readText().trim().toIntOrNull()
                        if (temp != null && temp > 0) {
                            return temp / 1000f  // Convert millidegrees to degrees
                        }
                    }
                }
            }

            -1f  // No valid temperature found

        } catch (e: Exception) {
            Timber.tag(LogContext.SYSTEM.label).w(e, "CPU temperature not available")
            -1f
        }
    }

    /**
     * Get system uptime in seconds
     *
     * Method: Parse /proc/uptime
     */
    private fun getUptimeSeconds(): Long {
        return try {
            val reader = BufferedReader(FileReader("/proc/uptime"))
            val line = reader.readLine()
            reader.close()

            // Parse: uptime_seconds idle_seconds
            val parts = line.split(" ")
            if (parts.isEmpty()) return -1

            val uptimeSeconds = parts[0].toDoubleOrNull() ?: return -1
            uptimeSeconds.toLong()

        } catch (e: Exception) {
            Timber.tag(LogContext.SYSTEM.label).e(e, "Error reading uptime")
            -1
        }
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
     * Get Android version
     *
     * API: Build.VERSION.RELEASE
     */
    private fun getAndroidVersion(): String {
        return Build.VERSION.RELEASE
    }

    /**
     * Get kernel version
     *
     * Method: Parse /proc/version
     */
    private fun getKernelVersion(): String {
        return try {
            val reader = BufferedReader(FileReader("/proc/version"))
            val version = reader.readLine()
            reader.close()

            // Extract version number from: Linux version 5.4.0-...
            val parts = version.split(" ")
            if (parts.size >= 3) {
                parts[2]  // Version is third token
            } else {
                version.take(50)  // Fallback: first 50 chars
            }

        } catch (e: Exception) {
            Timber.tag(LogContext.SYSTEM.label).e(e, "Error reading kernel version")
            "unknown"
        }
    }
}
