package uk.unmannedsystems.dpm_android.diagnostics

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import uk.unmannedsystems.dpm_android.eventlog.EventLevel
import uk.unmannedsystems.dpm_android.eventlog.EventLogViewModel
import uk.unmannedsystems.dpm_android.network.NetworkManager

/**
 * ViewModel for Quick Diagnostics Screen
 * Provides real-time health status of H16↔SBC connection, camera, and errors
 */
class DiagnosticsViewModel : ViewModel() {

    private val _uiState = MutableStateFlow(DiagnosticsUiState())
    val uiState: StateFlow<DiagnosticsUiState> = _uiState.asStateFlow()

    private var refreshJob: Job? = null

    init {
        startAutoRefresh()
    }

    private fun startAutoRefresh() {
        refreshJob?.cancel()
        refreshJob = viewModelScope.launch {
            while (true) {
                refresh()
                delay(2000) // Refresh every 2 seconds
            }
        }
    }

    fun refresh() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isRefreshing = true)

            val networkManager = NetworkManager
            val isConnected = networkManager.isConnected()
            val lastStatus = networkManager.lastStatusMessage.value

            // Calculate metrics
            val latency = calculateLatency()
            val packetLoss = calculatePacketLoss()
            val lastHeartbeat = System.currentTimeMillis() // TODO: Get actual heartbeat time

            // Get camera status
            val isCameraConnected = lastStatus?.payload?.camera?.connected ?: false
            val cameraModel = lastStatus?.payload?.camera?.model ?: "Unknown"
            val cameraDetails = if (isCameraConnected) {
                "Model: $cameraModel"
            } else {
                "Check USB connection to Air-Side"
            }

            // Get connection details
            val connectionDetails = if (isConnected) {
                val settings = uk.unmannedsystems.dpm_android.network.NetworkSettings
                "Connected to ${settings.ipAddress}:${settings.tcpPort}"
            } else {
                "Not connected to Air-Side"
            }

            // Get recent errors from EventLog
            val recentErrors = EventLogViewModel.events.value
                .filter { it.level == EventLevel.ERROR || it.level == EventLevel.WARNING }
                .takeLast(10)
                .map {
                    ErrorEntry(
                        timestamp = it.timestamp,
                        severity = when (it.level) {
                            EventLevel.ERROR -> ErrorSeverity.ERROR
                            EventLevel.WARNING -> ErrorSeverity.WARNING
                            else -> ErrorSeverity.INFO
                        },
                        message = it.message
                    )
                }

            // Determine overall health
            val hasErrors = recentErrors.any { it.severity == ErrorSeverity.ERROR }
            val isOverallHealthy = isConnected && isCameraConnected && !hasErrors

            val statusMessage = when {
                !isConnected -> "H16 not connected to Air-Side"
                !isCameraConnected -> "Camera not detected by Air-Side"
                hasErrors -> "${recentErrors.count { it.severity == ErrorSeverity.ERROR }} critical errors detected"
                else -> "All systems operational"
            }

            _uiState.value = _uiState.value.copy(
                isRefreshing = false,
                isSbcConnected = isConnected,
                isCameraConnected = isCameraConnected,
                connectionDetails = connectionDetails,
                cameraDetails = cameraDetails,
                latencyMs = latency,
                packetLossPercent = packetLoss,
                lastHeartbeatTime = if (isConnected) lastHeartbeat else null,
                recentErrors = recentErrors,
                isOverallHealthy = isOverallHealthy,
                overallStatusMessage = statusMessage
            )
        }
    }

    private fun calculateLatency(): Int? {
        // TODO: Implement actual latency calculation from network stats
        // For now, return a placeholder
        return if (NetworkManager.isConnected()) {
            (50..150).random() // Simulated latency
        } else null
    }

    private fun calculatePacketLoss(): Float? {
        // TODO: Implement actual packet loss calculation from network stats
        // For now, return a placeholder
        return if (NetworkManager.isConnected()) {
            (0.0f..2.0f).random() // Simulated packet loss
        } else null
    }

    fun reconnect() {
        viewModelScope.launch {
            NetworkManager.connect()
            delay(1000)
            refresh()
        }
    }

    fun clearErrors() {
        EventLogViewModel.clearLog()
        refresh()
    }

    override fun onCleared() {
        super.onCleared()
        refreshJob?.cancel()
    }
}

data class DiagnosticsUiState(
    val isRefreshing: Boolean = false,
    val isSbcConnected: Boolean = false,
    val isCameraConnected: Boolean = false,
    val connectionDetails: String = "",
    val cameraDetails: String = "",
    val latencyMs: Int? = null,
    val packetLossPercent: Float? = null,
    val lastHeartbeatTime: Long? = null,
    val recentErrors: List<ErrorEntry> = emptyList(),
    val isOverallHealthy: Boolean = false,
    val overallStatusMessage: String = "Initializing..."
)
