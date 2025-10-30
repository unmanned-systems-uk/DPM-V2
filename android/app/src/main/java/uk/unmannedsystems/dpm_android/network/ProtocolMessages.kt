package uk.unmannedsystems.dpm_android.network

import com.google.gson.annotations.SerializedName

/**
 * Base message structure for all protocol messages
 */
data class BaseMessage<T>(
    @SerializedName("protocol_version") val protocolVersion: String = "1.0",
    @SerializedName("message_type") val messageType: String,
    @SerializedName("sequence_id") val sequenceId: Int,
    val timestamp: Long,
    val payload: T
)

/**
 * Command message payload
 */
data class CommandPayload(
    val command: String,
    val parameters: Map<String, Any>
)

/**
 * Response message payload
 */
data class ResponsePayload(
    val command: String,
    val status: String, // success, error, in_progress
    val result: Map<String, Any>? = null,
    val error: ErrorInfo? = null
)

/**
 * Error information
 */
data class ErrorInfo(
    val code: Int,
    val message: String,
    val details: Any? = null  // Can be String or Map, depending on Air-Side implementation
)

/**
 * Handshake message payload
 */
data class HandshakePayload(
    @SerializedName("client_id") val clientId: String,
    @SerializedName("client_version") val clientVersion: String,
    @SerializedName("requested_features") val requestedFeatures: List<String>
)

/**
 * Handshake response payload
 */
data class HandshakeResponsePayload(
    @SerializedName("server_id") val serverId: String,
    @SerializedName("server_version") val serverVersion: String,
    @SerializedName("supported_features") val supportedFeatures: List<String>,
    @SerializedName("camera_connected") val cameraConnected: Boolean,
    @SerializedName("camera_model") val cameraModel: String?,
    @SerializedName("gimbal_connected") val gimbalConnected: Boolean,
    @SerializedName("gimbal_type") val gimbalType: String?
)

/**
 * Status message payload
 */
data class StatusPayload(
    val system: SystemStatus,
    val camera: CameraStatusInfo,
    val gimbal: GimbalStatus? = null,
    val downloads: DownloadStatus? = null
)

/**
 * System status information
 * Matches air-side UDP status broadcast format
 */
data class SystemStatus(
    @SerializedName("uptime_seconds") val uptimeSeconds: Long,
    @SerializedName("cpu_percent") val cpuPercent: Float,
    @SerializedName("memory_mb") val memoryMb: Int,
    @SerializedName("memory_total_mb") val memoryTotalMb: Int,
    @SerializedName("disk_free_gb") val diskFreeGb: Float,
    @SerializedName("network_rx_mbps") val networkRxMbps: Float? = null,
    @SerializedName("network_tx_mbps") val networkTxMbps: Float? = null
) {
    // Computed property for memory usage percentage
    val memoryUsagePercent: Float
        get() = if (memoryTotalMb > 0) {
            (memoryMb.toFloat() / memoryTotalMb.toFloat()) * 100f
        } else 0f
}

/**
 * Simple camera settings synchronized from Air Side
 * Broadcast in every UDP status message (5 Hz)
 */
data class SimpleCameraSettings(
    @SerializedName("shutter_speed") val shutterSpeed: String = "",
    val aperture: String = "",
    val iso: String = "",
    @SerializedName("white_balance") val whiteBalance: String = "",
    @SerializedName("focus_mode") val focusMode: String = "",
    @SerializedName("file_format") val fileFormat: String = ""
)

/**
 * Camera status information from Pi
 */
data class CameraStatusInfo(
    val connected: Boolean,
    val model: String?,
    @SerializedName("firmware_version") val firmwareVersion: String?,
    @SerializedName("battery_percent") val batteryPercent: Int,
    @SerializedName("battery_minutes_remaining") val batteryMinutesRemaining: Int?,
    val recording: Boolean,
    val storage: StorageInfo?,
    @SerializedName("current_settings") val currentSettings: CurrentCameraSettings?,
    val settings: SimpleCameraSettings? = null,  // New field for synchronized settings
    @SerializedName("remaining_shots") val remainingShots: Int? = null
)

/**
 * Storage information
 */
data class StorageInfo(
    @SerializedName("total_mb") val totalMb: Long,
    @SerializedName("free_mb") val freeMb: Long,
    @SerializedName("remaining_images") val remainingImages: Int,
    @SerializedName("remaining_video_minutes") val remainingVideoMinutes: Int
)

/**
 * Current camera settings
 */
data class CurrentCameraSettings(
    val mode: String,
    @SerializedName("shutter_speed") val shutterSpeed: String,
    val aperture: String,
    val iso: Int,
    @SerializedName("white_balance") val whiteBalance: WhiteBalanceInfo,
    @SerializedName("focus_mode") val focusMode: String,
    @SerializedName("file_format") val fileFormat: FileFormatInfo
)

/**
 * White balance information
 */
data class WhiteBalanceInfo(
    val mode: String,
    @SerializedName("color_temp") val colorTemp: Int?
)

/**
 * File format information
 */
data class FileFormatInfo(
    val format: String,
    @SerializedName("jpeg_quality") val jpegQuality: String?,
    @SerializedName("image_size") val imageSize: String?
)

/**
 * Gimbal status information
 */
data class GimbalStatus(
    val connected: Boolean,
    val type: String?,
    val model: String?,
    val mode: String?,
    val attitude: GimbalAttitude?,
    val moving: Boolean
)

/**
 * Gimbal attitude
 */
data class GimbalAttitude(
    val pitch: Float,
    val yaw: Float,
    val roll: Float
)

/**
 * Download status information
 */
data class DownloadStatus(
    @SerializedName("queue_size") val queueSize: Int,
    @SerializedName("active_download") val activeDownload: ActiveDownloadInfo?
)

/**
 * Active download information
 */
data class ActiveDownloadInfo(
    @SerializedName("content_id") val contentId: String,
    @SerializedName("progress_percent") val progressPercent: Int,
    @SerializedName("speed_mbps") val speedMbps: Float,
    @SerializedName("estimated_time_remaining_seconds") val estimatedTimeRemainingSeconds: Int
)

/**
 * Heartbeat message payload
 * @param sender "ground" or "air"
 * @param clientId Unique identifier for the client instance (e.g., "H16", "WPC", "RPi-Air")
 * @param uptimeSeconds Number of seconds since the application started
 */
data class HeartbeatPayload(
    val sender: String,
    @SerializedName("client_id") val clientId: String,
    @SerializedName("uptime_seconds") val uptimeSeconds: Long
)
