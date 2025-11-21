package uk.unmannedsystems.dpm_android.model

import com.google.gson.annotations.SerializedName

/**
 * Health snapshot data model matching Air-Side health broadcast structure
 *
 * Receives UDP broadcasts from Air-Side (port 5004) at 5 Hz (200ms interval)
 * Part of Issue #73 - Phase 1: Foundation Infrastructure
 */
data class HealthSnapshot(
    val timestamp: String,
    val system: SystemHealth,
    val camera: CameraHealth,
    val network: NetworkHealth,
    val sync: SyncMetrics
) {
    /**
     * Check if this health snapshot is stale (older than 15 seconds)
     */
    fun isStale(currentTimeMillis: Long): Boolean {
        // Parse ISO 8601 timestamp and compare
        try {
            val snapshotTime = parseIso8601(timestamp)
            return (currentTimeMillis - snapshotTime) > 15_000
        } catch (e: Exception) {
            return true // Consider invalid timestamps as stale
        }
    }

    private fun parseIso8601(timestamp: String): Long {
        // Simple ISO 8601 parser for format: 2025-11-13T03:00:00.000Z
        return java.time.Instant.parse(timestamp).toEpochMilli()
    }
}

/**
 * System health metrics
 * Protocol v2.0: All disk metrics in MB (not GB)
 */
data class SystemHealth(
    @SerializedName("cpu_percent") val cpuPercent: Float,
    @SerializedName("memory_used_mb") val memoryUsedMb: Int,
    @SerializedName("memory_total_mb") val memoryTotalMb: Int,
    @SerializedName("disk_used_mb") val diskUsedMb: Int,
    @SerializedName("disk_total_mb") val diskTotalMb: Int,
    @SerializedName("network_rx_mbps") val networkRxMbps: Float,
    @SerializedName("network_tx_mbps") val networkTxMbps: Float,
    @SerializedName("uptime_seconds") val uptimeSeconds: Long? = null
) {
    /**
     * Calculate memory usage percentage
     */
    val memoryPercent: Float
        get() = (memoryUsedMb.toFloat() / memoryTotalMb.toFloat()) * 100f

    /**
     * Calculate disk usage percentage
     * Protocol v2.0: Use disk_used_mb directly (not calculated from free)
     */
    val diskUsagePercent: Float
        get() = (diskUsedMb.toFloat() / diskTotalMb.toFloat()) * 100f

    /**
     * Get CPU health status
     */
    fun getCpuStatus(): HealthStatus {
        return when {
            cpuPercent >= 90f -> HealthStatus.CRITICAL
            cpuPercent >= 70f -> HealthStatus.WARNING
            else -> HealthStatus.NORMAL
        }
    }

    /**
     * Get memory health status
     */
    fun getMemoryStatus(): HealthStatus {
        return when {
            memoryPercent >= 90f -> HealthStatus.CRITICAL
            memoryPercent >= 75f -> HealthStatus.WARNING
            else -> HealthStatus.NORMAL
        }
    }

    /**
     * Get disk health status
     */
    fun getDiskStatus(): HealthStatus {
        return when {
            diskUsagePercent >= 95f -> HealthStatus.CRITICAL
            diskUsagePercent >= 85f -> HealthStatus.WARNING
            else -> HealthStatus.NORMAL
        }
    }
}

/**
 * Camera health metrics
 */
data class CameraHealth(
    val connected: Boolean,
    @SerializedName("sdk_latency_ms") val sdkLatencyMs: Float,
    @SerializedName("usb_traffic_mbps") val usbTrafficMbps: Float,
    @SerializedName("error_count") val errorCount: Int
) {
    /**
     * Get camera latency health status
     */
    fun getLatencyStatus(): HealthStatus {
        if (!connected) return HealthStatus.CRITICAL
        return when {
            sdkLatencyMs >= 100f -> HealthStatus.CRITICAL
            sdkLatencyMs >= 40f -> HealthStatus.WARNING
            else -> HealthStatus.NORMAL
        }
    }

    /**
     * Get overall camera health status
     */
    fun getOverallStatus(): HealthStatus {
        if (!connected) return HealthStatus.CRITICAL
        if (errorCount > 0) return HealthStatus.WARNING
        return getLatencyStatus()
    }
}

/**
 * Network health metrics
 */
data class NetworkHealth(
    @SerializedName("tcp_connected") val tcpConnected: Boolean,
    @SerializedName("tcp_latency_ms") val tcpLatencyMs: Float,
    @SerializedName("udp_loss_percent") val udpLossPercent: Float,
    @SerializedName("command_queue_depth") val commandQueueDepth: Int
) {
    /**
     * Get TCP latency health status
     */
    fun getTcpLatencyStatus(): HealthStatus {
        if (!tcpConnected) return HealthStatus.CRITICAL
        return when {
            tcpLatencyMs >= 100f -> HealthStatus.CRITICAL
            tcpLatencyMs >= 50f -> HealthStatus.WARNING
            else -> HealthStatus.NORMAL
        }
    }

    /**
     * Get UDP loss health status
     */
    fun getUdpLossStatus(): HealthStatus {
        return when {
            udpLossPercent >= 10f -> HealthStatus.CRITICAL
            udpLossPercent >= 2f -> HealthStatus.WARNING
            else -> HealthStatus.NORMAL
        }
    }

    /**
     * Get command queue health status
     */
    fun getQueueStatus(): HealthStatus {
        return when {
            commandQueueDepth >= 50 -> HealthStatus.CRITICAL
            commandQueueDepth >= 10 -> HealthStatus.WARNING
            else -> HealthStatus.NORMAL
        }
    }

    /**
     * Get overall network health status
     */
    fun getOverallStatus(): HealthStatus {
        if (!tcpConnected) return HealthStatus.CRITICAL
        val statuses = listOf(
            getTcpLatencyStatus(),
            getUdpLossStatus(),
            getQueueStatus()
        )
        return when {
            statuses.any { it == HealthStatus.CRITICAL } -> HealthStatus.CRITICAL
            statuses.any { it == HealthStatus.WARNING } -> HealthStatus.WARNING
            else -> HealthStatus.NORMAL
        }
    }
}

/**
 * Sync metrics
 * Protocol v2.0: property_reads_sec is integer (per second count)
 */
data class SyncMetrics(
    @SerializedName("exposure_rate_hz") val exposureRateHz: Float,
    @SerializedName("health_rate_hz") val healthRateHz: Float,
    @SerializedName("property_reads_sec") val propertyReadsSec: Int
) {
    /**
     * Get exposure sync health status
     */
    fun getExposureSyncStatus(): HealthStatus {
        return when {
            exposureRateHz < 1f -> HealthStatus.CRITICAL
            exposureRateHz < 3f -> HealthStatus.WARNING
            else -> HealthStatus.NORMAL
        }
    }

    /**
     * Get health sync health status
     */
    fun getHealthSyncStatus(): HealthStatus {
        return when {
            healthRateHz < 1f -> HealthStatus.CRITICAL
            healthRateHz < 3f -> HealthStatus.WARNING
            else -> HealthStatus.NORMAL
        }
    }
}

/**
 * Health status enum with color coding
 */
enum class HealthStatus {
    NORMAL,    // Green - All good
    WARNING,   // Yellow - Attention needed
    CRITICAL   // Red - Immediate action required
}
