package uk.unmannedsystems.dpm_android.system

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import uk.unmannedsystems.dpm_android.network.ConnectionState
import uk.unmannedsystems.dpm_android.network.NetworkManager
import uk.unmannedsystems.dpm_android.network.SystemStatus

/**
 * ViewModel for managing system status display and queries
 */
class SystemStatusViewModel : ViewModel() {
    private val _uiState = MutableStateFlow(SystemStatusUiState())
    val uiState: StateFlow<SystemStatusUiState> = _uiState.asStateFlow()

    init {
        // Monitor network connection status from shared NetworkManager
        viewModelScope.launch {
            NetworkManager.connectionStatus.collect { networkStatus ->
                _uiState.update { state ->
                    state.copy(
                        isConnected = networkStatus.state == ConnectionState.CONNECTED ||
                                     networkStatus.state == ConnectionState.OPERATIONAL
                    )
                }
            }
        }

        // Monitor system status updates from UDP broadcasts
        viewModelScope.launch {
            NetworkManager.systemStatus.collect { systemStatus ->
                _uiState.update { state ->
                    state.copy(systemStatus = systemStatus)
                }
            }
        }
    }

    /**
     * Request fresh system status from air-side
     */
    fun refreshSystemStatus() {
        viewModelScope.launch {
            _uiState.update { it.copy(isRefreshing = true, errorMessage = null) }

            val result = NetworkManager.getSystemStatus()

            result.fold(
                onSuccess = { response ->
                    _uiState.update { state ->
                        state.copy(
                            isRefreshing = false,
                            lastRefreshTime = System.currentTimeMillis()
                        )
                    }
                },
                onFailure = { error ->
                    _uiState.update { state ->
                        state.copy(
                            isRefreshing = false,
                            errorMessage = "Failed to refresh: ${error.message}"
                        )
                    }
                }
            )
        }
    }

    /**
     * Connect to Air-Side
     */
    fun connect() {
        NetworkManager.connect()
    }

    /**
     * Disconnect from Air-Side
     */
    fun disconnect() {
        NetworkManager.disconnect()
    }

    /**
     * Clear error message
     */
    fun clearError() {
        _uiState.update { it.copy(errorMessage = null) }
    }
}

/**
 * UI state for System Status screen
 */
data class SystemStatusUiState(
    val isConnected: Boolean = false,
    val systemStatus: SystemStatus? = null,
    val isRefreshing: Boolean = false,
    val lastRefreshTime: Long? = null,
    val errorMessage: String? = null
)
