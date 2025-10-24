package uk.unmannedsystems.dpm_android.settings

import androidx.lifecycle.ViewModel
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
class SettingsViewModel : ViewModel() {
    private val _networkSettings = MutableStateFlow(NetworkSettings())
    val networkSettings: StateFlow<NetworkSettings> = _networkSettings.asStateFlow()

    private var networkClient: NetworkClient? = null

    val networkStatus: StateFlow<NetworkStatus>
        get() = networkClient?.connectionStatus ?: MutableStateFlow(NetworkStatus()).asStateFlow()

    init {
        // Initialize network client with default settings
        initializeNetworkClient(_networkSettings.value)
    }

    /**
     * Update network settings
     */
    fun updateSettings(settings: NetworkSettings) {
        _networkSettings.value = settings

        // Disconnect if currently connected
        networkClient?.disconnect()

        // Reinitialize with new settings
        initializeNetworkClient(settings)
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
