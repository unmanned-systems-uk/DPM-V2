package uk.unmannedsystems.dpm_android.ui.debug

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import uk.unmannedsystems.dpm_android.DPMApplication
import uk.unmannedsystems.dpm_android.logging.LogContext
import uk.unmannedsystems.dpm_android.logging.LogDomain
import uk.unmannedsystems.dpm_android.logging.LogEntry
import uk.unmannedsystems.dpm_android.logging.LogLevel
import uk.unmannedsystems.dpm_android.network.NetworkManager
import java.text.SimpleDateFormat
import java.util.*

/**
 * ViewModel for Log Viewer Screen
 *
 * Features:
 * - Merged Air-Side + Ground-Side log timeline
 * - Filtering by level/context/domain
 * - Text search across messages and fields
 * - Controls for enabling/disabling Air-Side log streaming
 */
class LogViewerViewModel : ViewModel() {
    private val memorySink = DPMApplication.memorySink

    // Filter states
    private val _selectedMinLevel = MutableStateFlow<LogLevel?>(null)
    val selectedMinLevel: StateFlow<LogLevel?> = _selectedMinLevel

    private val _selectedContext = MutableStateFlow<LogContext?>(null)
    val selectedContext: StateFlow<LogContext?> = _selectedContext

    private val _selectedDomain = MutableStateFlow<LogDomain?>(null)
    val selectedDomain: StateFlow<LogDomain?> = _selectedDomain

    private val _searchText = MutableStateFlow("")
    val searchText: StateFlow<String> = _searchText

    // Auto-scroll toggle
    private val _autoScroll = MutableStateFlow(true)
    val autoScroll: StateFlow<Boolean> = _autoScroll

    // Air-Side log streaming state
    private val _airLogStreamingEnabled = MutableStateFlow(false)
    val airLogStreamingEnabled: StateFlow<Boolean> = _airLogStreamingEnabled

    private val _airLogStreamingExpiry = MutableStateFlow<Date?>(null)
    val airLogStreamingExpiry: StateFlow<Date?> = _airLogStreamingExpiry

    // Error state
    private val _errorMessage = MutableStateFlow<String?>(null)
    val errorMessage: StateFlow<String?> = _errorMessage

    // Filtered logs (reactively updated)
    val filteredLogs: StateFlow<List<LogEntry>> = combine(
        memorySink.logs,
        selectedMinLevel,
        selectedContext,
        selectedDomain,
        searchText
    ) { logs, minLevel, context, domain, search ->
        logs.filter { entry ->
            val levelMatch = minLevel == null || entry.level.value >= minLevel.value
            val contextMatch = context == null || entry.context == context
            val domainMatch = domain == null || entry.domain == domain
            val textMatch = search.isBlank() ||
                    entry.message.contains(search, ignoreCase = true) ||
                    entry.fields.values.any { it.toString().contains(search, ignoreCase = true) }

            levelMatch && contextMatch && domainMatch && textMatch
        }.sortedBy { it.timestamp }
    }.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = emptyList()
    )

    /**
     * Set minimum log level filter
     */
    fun setMinLevel(level: LogLevel?) {
        _selectedMinLevel.value = level
    }

    /**
     * Set context filter
     */
    fun setContext(context: LogContext?) {
        _selectedContext.value = context
    }

    /**
     * Set domain filter
     */
    fun setDomain(domain: LogDomain?) {
        _selectedDomain.value = domain
    }

    /**
     * Set search text
     */
    fun setSearchText(text: String) {
        _searchText.value = text
    }

    /**
     * Toggle auto-scroll
     */
    fun toggleAutoScroll() {
        _autoScroll.value = !_autoScroll.value
    }

    /**
     * Clear all logs from memory
     */
    fun clearLogs() {
        memorySink.clear()
    }

    /**
     * Start Air-Side log streaming
     *
     * Sends enable_log_streaming command to Air-Side with specified duration.
     * Air-Side will stream logs via UDP for the duration, then auto-disable.
     */
    fun startAirLogStreaming(durationSeconds: Int = 300) {
        viewModelScope.launch {
            try {
                // Send command to Air-Side
                val result = NetworkManager.sendCommand(
                    command = "enable_log_streaming",
                    parameters = mapOf("duration" to durationSeconds)
                )

                result.onSuccess {
                    _airLogStreamingEnabled.value = true

                    // Calculate expiry time
                    val expiry = Calendar.getInstance().apply {
                        add(Calendar.SECOND, durationSeconds)
                    }.time
                    _airLogStreamingExpiry.value = expiry

                    _errorMessage.value = null

                    // Auto-disable after duration
                    kotlinx.coroutines.delay(durationSeconds * 1000L)
                    _airLogStreamingEnabled.value = false
                    _airLogStreamingExpiry.value = null
                }.onFailure { error ->
                    _errorMessage.value = "Failed to enable Air-Side log streaming: ${error.message}"
                }
            } catch (e: Exception) {
                _errorMessage.value = "Error enabling Air-Side log streaming: ${e.message}"
            }
        }
    }

    /**
     * Stop Air-Side log streaming
     */
    fun stopAirLogStreaming() {
        viewModelScope.launch {
            try {
                // Send command to Air-Side
                val result = NetworkManager.sendCommand(
                    command = "disable_log_streaming",
                    parameters = emptyMap()
                )

                result.onSuccess {
                    _airLogStreamingEnabled.value = false
                    _airLogStreamingExpiry.value = null
                    _errorMessage.value = null
                }.onFailure { error ->
                    _errorMessage.value = "Failed to disable Air-Side log streaming: ${error.message}"
                }
            } catch (e: Exception) {
                _errorMessage.value = "Error disabling Air-Side log streaming: ${e.message}"
            }
        }
    }

    /**
     * Clear error message
     */
    fun clearError() {
        _errorMessage.value = null
    }

    /**
     * Format expiry time as "Expires in X min Y sec"
     */
    fun getExpiryString(): String {
        val expiry = _airLogStreamingExpiry.value ?: return ""
        val now = Date()
        val diff = expiry.time - now.time
        if (diff <= 0) return "Expired"

        val minutes = (diff / 1000 / 60).toInt()
        val seconds = ((diff / 1000) % 60).toInt()

        return "Expires in ${minutes}m ${seconds}s"
    }
}
