package uk.unmannedsystems.dpm_android.settings

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import uk.unmannedsystems.dpm_android.network.NetworkClient
import uk.unmannedsystems.dpm_android.network.NetworkSettings
import uk.unmannedsystems.dpm_android.network.NetworkStatus

/**
 * ViewModel for managing network settings and connection
 */
class SettingsViewModel(application: Application) : AndroidViewModel(application) {
    private val settingsRepository = SettingsRepository(application)

    private val _networkSettings = MutableStateFlow(NetworkSettings())
    val networkSettings: StateFlow<NetworkSettings> = _networkSettings.asStateFlow()

    private var networkClient: NetworkClient? = null
    private var autoConnectAttempted = false

    val networkStatus: StateFlow<NetworkStatus>
        get() = networkClient?.connectionStatus ?: MutableStateFlow(NetworkStatus()).asStateFlow()

    init {
        // Load saved settings and initialize
        viewModelScope.launch {
            settingsRepository.networkSettingsFlow.collect { savedSettings ->
                _networkSettings.value = savedSettings

                // Reinitialize network client with loaded settings
                initializeNetworkClient(savedSettings)

                // Auto-connect on first load only
                if (!autoConnectAttempted) {
                    autoConnectAttempted = true
                    connect()
                }
            }
        }
    }

    /**
     * Update network settings and persist them
     */
    fun updateSettings(settings: NetworkSettings) {
        viewModelScope.launch {
            // Save settings to DataStore
            settingsRepository.saveNetworkSettings(settings)

            // Update state (will be updated by the flow, but set immediately for UI responsiveness)
            _networkSettings.value = settings

            // Disconnect if currently connected
            networkClient?.disconnect()

            // Reinitialize with new settings
            initializeNetworkClient(settings)
        }
    }

    /**
     * Reset to default settings
     */
    fun resetToDefaults() {
        viewModelScope.launch {
            settingsRepository.resetToDefaults()
            // Settings will be updated via the flow
        }
    }

    /**
     * Connect to Raspberry Pi
     */
    fun connect() {
        networkClient?.connect()
    }

    /**
     * Disconnect from Raspberry Pi
     */
    fun disconnect() {
        networkClient?.disconnect()
    }

    /**
     * Get the current network client instance
     */
    fun getNetworkClient(): NetworkClient? = networkClient

    private fun initializeNetworkClient(settings: NetworkSettings) {
        networkClient?.close()
        networkClient = NetworkClient(settings)
    }

    override fun onCleared() {
        super.onCleared()
        networkClient?.close()
    }
}
