package uk.unmannedsystems.dpm_android.eventlog

import androidx.lifecycle.ViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

/**
 * Event log entry for development diagnostics
 */
data class EventLogEntry(
    val timestamp: Long = System.currentTimeMillis(),
    val category: EventCategory,
    val level: EventLevel,
    val message: String,
    val details: String? = null
)

enum class EventCategory {
    NETWORK,
    CAMERA,
    UI,
    SYSTEM,
    ERROR
}

enum class EventLevel {
    DEBUG,
    INFO,
    WARNING,
    ERROR
}

/**
 * ViewModel for managing application event log
 * Singleton pattern to allow logging from anywhere in the app
 */
object EventLogViewModel : ViewModel() {
    private val _events = MutableStateFlow<List<EventLogEntry>>(emptyList())
    val events: StateFlow<List<EventLogEntry>> = _events.asStateFlow()

    private val maxEvents = 1000 // Keep last 1000 events

    /**
     * Add an event to the log
     */
    fun logEvent(
        category: EventCategory,
        level: EventLevel,
        message: String,
        details: String? = null
    ) {
        val event = EventLogEntry(
            timestamp = System.currentTimeMillis(),
            category = category,
            level = level,
            message = message,
            details = details
        )

        _events.value = (_events.value + event).takeLast(maxEvents)
    }

    /**
     * Clear all events
     */
    fun clearLog() {
        _events.value = emptyList()
    }

    /**
     * Get events filtered by category
     */
    fun getEventsByCategory(category: EventCategory): List<EventLogEntry> {
        return _events.value.filter { it.category == category }
    }

    /**
     * Get events filtered by level
     */
    fun getEventsByLevel(level: EventLevel): List<EventLogEntry> {
        return _events.value.filter { it.level == level }
    }

    // Convenience logging functions
    fun logDebug(category: EventCategory, message: String, details: String? = null) {
        logEvent(category, EventLevel.DEBUG, message, details)
    }

    fun logInfo(category: EventCategory, message: String, details: String? = null) {
        logEvent(category, EventLevel.INFO, message, details)
    }

    fun logWarning(category: EventCategory, message: String, details: String? = null) {
        logEvent(category, EventLevel.WARNING, message, details)
    }

    fun logError(category: EventCategory, message: String, details: String? = null) {
        logEvent(category, EventLevel.ERROR, message, details)
    }
}
