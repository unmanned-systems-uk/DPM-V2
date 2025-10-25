package uk.unmannedsystems.dpm_android.settings

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch
import uk.unmannedsystems.dpm_android.network.NetworkManager
import uk.unmannedsystems.dpm_android.network.NetworkSettings
import uk.unmannedsystems.dpm_android.network.NetworkStatus

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

    // Use NetworkManager's stable StateFlow
    val networkStatus: StateFlow<NetworkStatus> = NetworkManager.connectionStatus

    init {
        // Monitor settings changes and reinitialize NetworkManager when settings change
        // Note: Auto-connect happens in DPMApplication.onCreate(), not here
        viewModelScope.launch {
            settingsRepository.networkSettingsFlow.collect { savedSettings ->
                // Reinitialize NetworkManager when settings change
                // (This happens after user saves new settings)
                NetworkManager.initialize(savedSettings)
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
}
