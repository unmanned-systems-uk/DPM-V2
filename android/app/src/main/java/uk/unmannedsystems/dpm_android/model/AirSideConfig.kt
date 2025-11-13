package uk.unmannedsystems.dpm_android.model

import com.google.gson.annotations.SerializedName

/**
 * Air-Side configuration data model
 *
 * Synchronized between Ground-Side and Air-Side via get_config/update_config commands
 * Part of Issue #73 - Phase 1: Foundation Infrastructure (Gap 3)
 */
data class AirSideConfig(
    val network: NetworkConfig,
    val timing: TimingConfig,
    val logging: LoggingConfig,
    val health: HealthConfig
) {
    /**
     * Validate entire configuration
     */
    fun validate(): ConfigValidationResult {
        val errors = mutableListOf<String>()

        // Validate each section
        network.validate().errors.forEach { errors.add("Network: $it") }
        timing.validate().errors.forEach { errors.add("Timing: $it") }
        logging.validate().errors.forEach { errors.add("Logging: $it") }
        health.validate().errors.forEach { errors.add("Health: $it") }

        return ConfigValidationResult(
            isValid = errors.isEmpty(),
            errors = errors
        )
    }

    companion object {
        /**
         * Create default configuration
         */
        fun createDefault(): AirSideConfig {
            return AirSideConfig(
                network = NetworkConfig.createDefault(),
                timing = TimingConfig.createDefault(),
                logging = LoggingConfig.createDefault(),
                health = HealthConfig.createDefault()
            )
        }
    }
}

/**
 * Network configuration
 */
data class NetworkConfig(
    @SerializedName("tcp_port") val tcpPort: Int,
    @SerializedName("udp_status_port") val udpStatusPort: Int,
    @SerializedName("udp_heartbeat_port") val udpHeartbeatPort: Int,
    @SerializedName("ground_ip") val groundIp: String
) {
    fun validate(): ConfigValidationResult {
        val errors = mutableListOf<String>()

        // Validate TCP port
        if (tcpPort !in 1024..65535) {
            errors.add("TCP port must be between 1024 and 65535 (got $tcpPort)")
        }

        // Validate UDP status port
        if (udpStatusPort !in 1024..65535) {
            errors.add("UDP status port must be between 1024 and 65535 (got $udpStatusPort)")
        }

        // Validate UDP heartbeat port
        if (udpHeartbeatPort !in 1024..65535) {
            errors.add("UDP heartbeat port must be between 1024 and 65535 (got $udpHeartbeatPort)")
        }

        // Validate IP address format
        if (!isValidIpv4(groundIp)) {
            errors.add("Ground IP must be a valid IPv4 address (got $groundIp)")
        }

        return ConfigValidationResult(
            isValid = errors.isEmpty(),
            errors = errors
        )
    }

    private fun isValidIpv4(ip: String): Boolean {
        val parts = ip.split(".")
        if (parts.size != 4) return false

        return parts.all { part ->
            part.toIntOrNull()?.let { it in 0..255 } ?: false
        }
    }

    companion object {
        fun createDefault() = NetworkConfig(
            tcpPort = 9001,
            udpStatusPort = 9002,
            udpHeartbeatPort = 9003,
            groundIp = "192.168.144.11"
        )
    }
}

/**
 * Timing configuration
 */
data class TimingConfig(
    @SerializedName("status_interval_ms") val statusIntervalMs: Int,
    @SerializedName("heartbeat_interval_ms") val heartbeatIntervalMs: Int,
    @SerializedName("heartbeat_timeout_sec") val heartbeatTimeoutSec: Int,
    @SerializedName("reconnect_interval_ms") val reconnectIntervalMs: Int
) {
    fun validate(): ConfigValidationResult {
        val errors = mutableListOf<String>()

        // Validate status interval
        if (statusIntervalMs !in 50..5000) {
            errors.add("Status interval must be between 50 and 5000 ms (got $statusIntervalMs)")
        }

        // Validate heartbeat interval
        if (heartbeatIntervalMs !in 500..5000) {
            errors.add("Heartbeat interval must be between 500 and 5000 ms (got $heartbeatIntervalMs)")
        }

        // Validate heartbeat timeout
        if (heartbeatTimeoutSec !in 1..60) {
            errors.add("Heartbeat timeout must be between 1 and 60 seconds (got $heartbeatTimeoutSec)")
        }

        // Validate reconnect interval
        if (reconnectIntervalMs !in 500..5000) {
            errors.add("Reconnect interval must be between 500 and 5000 ms (got $reconnectIntervalMs)")
        }

        return ConfigValidationResult(
            isValid = errors.isEmpty(),
            errors = errors
        )
    }

    companion object {
        fun createDefault() = TimingConfig(
            statusIntervalMs = 200,
            heartbeatIntervalMs = 1000,
            heartbeatTimeoutSec = 5,
            reconnectIntervalMs = 1000
        )
    }
}

/**
 * Logging configuration
 */
data class LoggingConfig(
    @SerializedName("log_level") val logLevel: String,
    @SerializedName("file_logging_enabled") val fileLoggingEnabled: Boolean,
    @SerializedName("file_max_size_mb") val fileMaxSizeMb: Int,
    @SerializedName("network_logging_enabled") val networkLoggingEnabled: Boolean
) {
    fun validate(): ConfigValidationResult {
        val errors = mutableListOf<String>()

        // Validate log level
        val validLevels = listOf("DEBUG", "INFO", "WARNING", "ERROR")
        if (logLevel !in validLevels) {
            errors.add("Log level must be one of: ${validLevels.joinToString(", ")} (got $logLevel)")
        }

        // Validate file max size
        if (fileMaxSizeMb !in 10..500) {
            errors.add("File max size must be between 10 and 500 MB (got $fileMaxSizeMb)")
        }

        return ConfigValidationResult(
            isValid = errors.isEmpty(),
            errors = errors
        )
    }

    companion object {
        fun createDefault() = LoggingConfig(
            logLevel = "INFO",
            fileLoggingEnabled = true,
            fileMaxSizeMb = 50,
            networkLoggingEnabled = true
        )
    }
}

/**
 * Health monitoring configuration
 */
data class HealthConfig(
    @SerializedName("broadcast_enabled") val broadcastEnabled: Boolean,
    @SerializedName("broadcast_interval_sec") val broadcastIntervalSec: Int,
    @SerializedName("history_duration_min") val historyDurationMin: Int
) {
    fun validate(): ConfigValidationResult {
        val errors = mutableListOf<String>()

        // Validate broadcast interval
        if (broadcastIntervalSec !in 1..60) {
            errors.add("Broadcast interval must be between 1 and 60 seconds (got $broadcastIntervalSec)")
        }

        // Validate history duration
        if (historyDurationMin !in 10..120) {
            errors.add("History duration must be between 10 and 120 minutes (got $historyDurationMin)")
        }

        return ConfigValidationResult(
            isValid = errors.isEmpty(),
            errors = errors
        )
    }

    companion object {
        fun createDefault() = HealthConfig(
            broadcastEnabled = true,
            broadcastIntervalSec = 5,
            historyDurationMin = 60
        )
    }
}

/**
 * Configuration validation result
 */
data class ConfigValidationResult(
    val isValid: Boolean,
    val errors: List<String>
) {
    val errorMessage: String
        get() = errors.joinToString("\n")
}
