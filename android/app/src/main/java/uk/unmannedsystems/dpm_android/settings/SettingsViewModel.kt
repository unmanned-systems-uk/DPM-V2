package uk.unmannedsystems.dpm_android.settings

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch
import uk.unmannedsystems.dpm_android.network.NetworkManager
import uk.unmannedsystems.dpm_android.network.NetworkSettings
import uk.unmannedsystems.dpm_android.network.NetworkStatus
import uk.unmannedsystems.dpm_android.network.VideoStreamSettings

/**
 * ViewModel for managing network settings and connection
 */
class SettingsViewModel(application: Application) : AndroidViewModel(application) {
    private val settingsRepository = SettingsRepository(application)

    val networkSettings: StateFlow<NetworkSettings> = settingsRepository.networkSettingsFlow
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = NetworkSettings()
        )

    val videoSettings: StateFlow<VideoStreamSettings> = settingsRepository.videoSettingsFlow
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = VideoStreamSettings()
        )

    val propertyQueryFrequency: StateFlow<Float> = settingsRepository.propertyQueryFrequencyFlow
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = settingsRepository.getDefaultPropertyQueryFrequency()
        )

    val propertyQueryEnabled: StateFlow<Boolean> = settingsRepository.propertyQueryEnabledFlow
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = settingsRepository.getDefaultPropertyQueryEnabled()
        )

    val autoConnectEnabled: StateFlow<Boolean> = settingsRepository.autoConnectEnabledFlow
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = settingsRepository.getDefaultAutoConnectEnabled()
        )

    val autoReconnectEnabled: StateFlow<Boolean> = settingsRepository.autoReconnectEnabledFlow
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = settingsRepository.getDefaultAutoReconnectEnabled()
        )

    val autoReconnectInterval: StateFlow<Int> = settingsRepository.autoReconnectIntervalFlow
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = settingsRepository.getDefaultAutoReconnectInterval()
        )

    val clientId: StateFlow<String> = settingsRepository.clientIdFlow
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = settingsRepository.getDefaultClientId()
        )

    // Use NetworkManager's stable StateFlow
    val networkStatus: StateFlow<NetworkStatus> = NetworkManager.connectionStatus

    init {
        // Monitor settings changes and reinitialize NetworkManager when settings change
        // Note: Auto-connect happens in DPMApplication.onCreate(), not here
        viewModelScope.launch {
            settingsRepository.networkSettingsFlow.combine(settingsRepository.clientIdFlow) { savedSettings, savedClientId ->
                Pair(savedSettings, savedClientId)
            }.collect { (savedSettings, savedClientId) ->
                // Reinitialize NetworkManager when settings change
                // (This happens after user saves new settings or client ID)
                NetworkManager.initialize(savedSettings, savedClientId)
            }
        }
    }

    /**
     * Update network settings and persist them
     */
    fun updateSettings(settings: NetworkSettings) {
        viewModelScope.launch {
            // Disconnect if currently connected
            NetworkManager.disconnect()

            // Save settings to DataStore (will trigger flow and reinitialize)
            settingsRepository.saveNetworkSettings(settings)
        }
    }

    /**
     * Reset to default settings
     */
    fun resetToDefaults() {
        viewModelScope.launch {
            settingsRepository.resetToDefaults()
            // Settings will be updated via the flow which will reinitialize NetworkManager
        }
    }

    /**
     * Connect to Raspberry Pi
     */
    fun connect() {
        NetworkManager.connect()
    }

    /**
     * Disconnect from Raspberry Pi
     */
    fun disconnect() {
        NetworkManager.disconnect()
    }

    /**
     * Update video stream settings and persist them
     */
    fun updateVideoSettings(settings: VideoStreamSettings) {
        viewModelScope.launch {
            settingsRepository.saveVideoSettings(settings)
        }
    }

    /**
     * Update property query frequency and persist it
     */
    fun updatePropertyQueryFrequency(frequencyHz: Float) {
        viewModelScope.launch {
            settingsRepository.savePropertyQueryFrequency(frequencyHz)
        }
    }

    /**
     * Update property query enabled state and persist it
     */
    fun updatePropertyQueryEnabled(enabled: Boolean) {
        viewModelScope.launch {
            settingsRepository.savePropertyQueryEnabled(enabled)
        }
    }

    /**
     * Update auto-connect enabled state and persist it
     */
    fun updateAutoConnectEnabled(enabled: Boolean) {
        viewModelScope.launch {
            settingsRepository.saveAutoConnectEnabled(enabled)
        }
    }

    /**
     * Update auto-reconnect enabled state and persist it
     */
    fun updateAutoReconnectEnabled(enabled: Boolean) {
        viewModelScope.launch {
            settingsRepository.saveAutoReconnectEnabled(enabled)
            // Update NetworkManager configuration
            NetworkManager.configureAutoReconnect(enabled, autoReconnectInterval.value)
        }
    }

    /**
     * Update auto-reconnect interval and persist it
     */
    fun updateAutoReconnectInterval(intervalSeconds: Int) {
        viewModelScope.launch {
            settingsRepository.saveAutoReconnectInterval(intervalSeconds)
            // Update NetworkManager configuration
            NetworkManager.configureAutoReconnect(autoReconnectEnabled.value, intervalSeconds)
        }
    }

    /**
     * Update client ID and persist it
     * Note: Requires reconnection to take effect
     */
    fun updateClientId(clientId: String) {
        viewModelScope.launch {
            settingsRepository.saveClientId(clientId)
        }
    }
}
