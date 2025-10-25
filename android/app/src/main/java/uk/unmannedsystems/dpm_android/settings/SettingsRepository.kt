package uk.unmannedsystems.dpm_android.settings

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.booleanPreferencesKey
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.intPreferencesKey
import androidx.datastore.preferences.core.longPreferencesKey
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import uk.unmannedsystems.dpm_android.network.AspectRatioMode
import uk.unmannedsystems.dpm_android.network.NetworkSettings
import uk.unmannedsystems.dpm_android.network.VideoStreamSettings

/**
 * Repository for persisting network settings using DataStore
 */
class SettingsRepository(private val context: Context) {

    companion object {
        private val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "network_settings")

        // Network settings keys
        private val TARGET_IP = stringPreferencesKey("target_ip")
        private val COMMAND_PORT = intPreferencesKey("command_port")
        private val STATUS_LISTEN_PORT = intPreferencesKey("status_listen_port")
        private val HEARTBEAT_PORT = intPreferencesKey("heartbeat_port")
        private val CONNECTION_TIMEOUT_MS = longPreferencesKey("connection_timeout_ms")
        private val HEARTBEAT_INTERVAL_MS = longPreferencesKey("heartbeat_interval_ms")
        private val STATUS_BROADCAST_INTERVAL_MS = longPreferencesKey("status_broadcast_interval_ms")

        // Video settings keys
        private val VIDEO_ENABLED = booleanPreferencesKey("video_enabled")
        private val VIDEO_RTSP_URL = stringPreferencesKey("video_rtsp_url")
        private val VIDEO_ASPECT_RATIO = stringPreferencesKey("video_aspect_ratio")
        private val VIDEO_BUFFER_DURATION = longPreferencesKey("video_buffer_duration")

        // Default values
        private val DEFAULT_SETTINGS = NetworkSettings()
        private val DEFAULT_VIDEO_SETTINGS = VideoStreamSettings()
    }

    /**
     * Flow of network settings
     */
    val networkSettingsFlow: Flow<NetworkSettings> = context.dataStore.data
        .map { preferences ->
            NetworkSettings(
                targetIp = preferences[TARGET_IP] ?: DEFAULT_SETTINGS.targetIp,
                commandPort = preferences[COMMAND_PORT] ?: DEFAULT_SETTINGS.commandPort,
                statusListenPort = preferences[STATUS_LISTEN_PORT] ?: DEFAULT_SETTINGS.statusListenPort,
                heartbeatPort = preferences[HEARTBEAT_PORT] ?: DEFAULT_SETTINGS.heartbeatPort,
                connectionTimeoutMs = preferences[CONNECTION_TIMEOUT_MS] ?: DEFAULT_SETTINGS.connectionTimeoutMs,
                heartbeatIntervalMs = preferences[HEARTBEAT_INTERVAL_MS] ?: DEFAULT_SETTINGS.heartbeatIntervalMs,
                statusBroadcastIntervalMs = preferences[STATUS_BROADCAST_INTERVAL_MS] ?: DEFAULT_SETTINGS.statusBroadcastIntervalMs
            )
        }

    /**
     * Save network settings
     */
    suspend fun saveNetworkSettings(settings: NetworkSettings) {
        context.dataStore.edit { preferences ->
            preferences[TARGET_IP] = settings.targetIp
            preferences[COMMAND_PORT] = settings.commandPort
            preferences[STATUS_LISTEN_PORT] = settings.statusListenPort
            preferences[HEARTBEAT_PORT] = settings.heartbeatPort
            preferences[CONNECTION_TIMEOUT_MS] = settings.connectionTimeoutMs
            preferences[HEARTBEAT_INTERVAL_MS] = settings.heartbeatIntervalMs
            preferences[STATUS_BROADCAST_INTERVAL_MS] = settings.statusBroadcastIntervalMs
        }
    }

    /**
     * Reset to default settings and save
     */
    suspend fun resetToDefaults() {
        saveNetworkSettings(DEFAULT_SETTINGS)
    }

    /**
     * Get default settings
     */
    fun getDefaultSettings(): NetworkSettings = DEFAULT_SETTINGS

    /**
     * Flow of video stream settings
     */
    val videoSettingsFlow: Flow<VideoStreamSettings> = context.dataStore.data
        .map { preferences ->
            VideoStreamSettings(
                enabled = preferences[VIDEO_ENABLED] ?: DEFAULT_VIDEO_SETTINGS.enabled,
                rtspUrl = preferences[VIDEO_RTSP_URL] ?: DEFAULT_VIDEO_SETTINGS.rtspUrl,
                aspectRatioMode = try {
                    AspectRatioMode.valueOf(
                        preferences[VIDEO_ASPECT_RATIO] ?: DEFAULT_VIDEO_SETTINGS.aspectRatioMode.name
                    )
                } catch (e: IllegalArgumentException) {
                    DEFAULT_VIDEO_SETTINGS.aspectRatioMode
                },
                bufferDurationMs = preferences[VIDEO_BUFFER_DURATION] ?: DEFAULT_VIDEO_SETTINGS.bufferDurationMs
            )
        }

    /**
     * Save video stream settings
     */
    suspend fun saveVideoSettings(settings: VideoStreamSettings) {
        context.dataStore.edit { preferences ->
            preferences[VIDEO_ENABLED] = settings.enabled
            preferences[VIDEO_RTSP_URL] = settings.rtspUrl
            preferences[VIDEO_ASPECT_RATIO] = settings.aspectRatioMode.name
            preferences[VIDEO_BUFFER_DURATION] = settings.bufferDurationMs
        }
    }

    /**
     * Get default video settings
     */
    fun getDefaultVideoSettings(): VideoStreamSettings = DEFAULT_VIDEO_SETTINGS
}
