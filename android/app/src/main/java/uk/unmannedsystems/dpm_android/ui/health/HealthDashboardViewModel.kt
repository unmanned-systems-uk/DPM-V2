package uk.unmannedsystems.dpm_android.ui.health

import android.util.Log
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import uk.unmannedsystems.dpm_android.model.HealthSnapshot
import uk.unmannedsystems.dpm_android.model.HealthStatus
import uk.unmannedsystems.dpm_android.network.HealthListener

/**
 * ViewModel for Health Dashboard
 *
 * Manages health monitoring state and controls HealthListener lifecycle
 * Part of Issue #73 - Phase 1: Foundation Infrastructure
 *
 * Features:
 * - Automatic HealthListener lifecycle management
 * - Real-time health data updates
 * - Stale data detection
 * - Connection state tracking
 * - Overall system health assessment
 */
class HealthDashboardViewModel : ViewModel() {

    companion object {
        private const val TAG = "HealthDashboardVM"
    }

    private val healthListener = HealthListener()

    // UI State
    private val _uiState = MutableStateFlow(HealthDashboardUiState())
    val uiState: StateFlow<HealthDashboardUiState> = _uiState.asStateFlow()

    init {
        Log.i(TAG, "HealthDashboardViewModel initialized")
        startHealthMonitoring()
    }

    /**
     * Start health monitoring
     */
    private fun startHealthMonitoring() {
        Log.i(TAG, "Starting health monitoring")

        // Start the health listener
        healthListener.start()

        // Collect latest health data
        viewModelScope.launch {
            healthListener.latestHealth.collect { health ->
                _uiState.update { state ->
                    state.copy(
                        latestHealth = health,
                        overallStatus = health?.let { calculateOverallStatus(it) } ?: HealthStatus.CRITICAL
                    )
                }
                if (health != null) {
                    Log.v(TAG, "Health data updated: CPU=${health.system.cpuPercent}%, " +
                            "MEM=${health.system.memoryPercent.toInt()}%")
                }
            }
        }

        // Collect connection state
        viewModelScope.launch {
            healthListener.isConnected.collect { connected ->
                _uiState.update { it.copy(isConnected = connected) }
                Log.d(TAG, "Connection state: ${if (connected) "CONNECTED" else "DISCONNECTED"}")
            }
        }

        // Collect stale state
        viewModelScope.launch {
            healthListener.isStale.collect { stale ->
                _uiState.update { it.copy(isStale = stale) }
                if (stale) {
                    Log.w(TAG, "Health data is STALE")
                }
            }
        }

        // Collect error count
        viewModelScope.launch {
            healthListener.errorCount.collect { errors ->
                _uiState.update { it.copy(errorCount = errors) }
                if (errors > 0) {
                    Log.w(TAG, "Health listener error count: $errors")
                }
            }
        }

        // Collect last received time
        viewModelScope.launch {
            healthListener.lastReceivedTime.collect { time ->
                _uiState.update { it.copy(lastReceivedTime = time) }
            }
        }
    }

    /**
     * Calculate overall system health status
     */
    private fun calculateOverallStatus(health: HealthSnapshot): HealthStatus {
        val statuses = listOf(
            health.system.getCpuStatus(),
            health.system.getMemoryStatus(),
            health.system.getDiskStatus(),
            health.camera.getOverallStatus(),
            health.network.getOverallStatus(),
            health.sync.getExposureSyncStatus(),
            health.sync.getHealthSyncStatus()
        )

        return when {
            statuses.any { it == HealthStatus.CRITICAL } -> HealthStatus.CRITICAL
            statuses.any { it == HealthStatus.WARNING } -> HealthStatus.WARNING
            else -> HealthStatus.NORMAL
        }
    }

    /**
     * Get time since last health update (in seconds)
     */
    fun getTimeSinceLastUpdate(): Long {
        val lastTime = _uiState.value.lastReceivedTime
        if (lastTime == 0L) return Long.MAX_VALUE
        return (System.currentTimeMillis() - lastTime) / 1000
    }

    /**
     * Get listener statistics
     */
    fun getListenerStats() = healthListener.getStats()

    /**
     * Restart health monitoring (for troubleshooting)
     */
    fun restartHealthMonitoring() {
        Log.i(TAG, "Restarting health monitoring")
        healthListener.stop()
        healthListener.start()
    }

    override fun onCleared() {
        super.onCleared()
        Log.i(TAG, "HealthDashboardViewModel cleared - stopping health listener")
        healthListener.stop()
    }
}

/**
 * UI State for Health Dashboard
 */
data class HealthDashboardUiState(
    val latestHealth: HealthSnapshot? = null,
    val isConnected: Boolean = false,
    val isStale: Boolean = false,
    val errorCount: Int = 0,
    val lastReceivedTime: Long = 0,
    val overallStatus: HealthStatus = HealthStatus.CRITICAL
) {
    /**
     * Check if we have valid health data
     */
    val hasData: Boolean
        get() = latestHealth != null

    /**
     * Get connection status text
     */
    val connectionStatusText: String
        get() = when {
            !isConnected -> "Disconnected"
            isStale -> "Stale"
            hasData -> "Connected"
            else -> "Waiting for data..."
        }

    /**
     * Get formatted time since last update
     */
    fun getFormattedTimeSinceUpdate(): String {
        if (lastReceivedTime == 0L) return "Never"

        val seconds = (System.currentTimeMillis() - lastReceivedTime) / 1000
        return when {
            seconds < 60 -> "${seconds}s ago"
            seconds < 3600 -> "${seconds / 60}m ${seconds % 60}s ago"
            else -> "${seconds / 3600}h ${(seconds % 3600) / 60}m ago"
        }
    }
}
