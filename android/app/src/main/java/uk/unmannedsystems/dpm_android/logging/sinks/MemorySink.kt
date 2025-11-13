package uk.unmannedsystems.dpm_android.logging.sinks

import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import uk.unmannedsystems.dpm_android.logging.LogEntry
import java.util.LinkedList

/**
 * Memory Sink - Stores logs in memory for UI display
 *
 * Features:
 * - Ring buffer (fixed capacity)
 * - StateFlow for reactive UI updates
 * - Thread-safe
 * - Stores both Air-Side and Ground-Side logs
 * - Sorted by timestamp for merged timeline
 */
class MemorySink(
    private val maxEntries: Int = 1000
) : LogSink {
    private val buffer = LinkedList<LogEntry>()

    // StateFlow for UI observation
    private val _logs = MutableStateFlow<List<LogEntry>>(emptyList())
    val logs: StateFlow<List<LogEntry>> = _logs

    /**
     * Write a log entry to memory
     */
    @Synchronized
    override fun write(entry: LogEntry) {
        // Add to buffer
        buffer.add(entry)

        // Remove oldest if over capacity
        if (buffer.size > maxEntries) {
            buffer.removeFirst()
        }

        // Update StateFlow (sort by timestamp for merged timeline)
        _logs.value = buffer.toList().sortedBy { it.timestamp }
    }

    /**
     * Flush (no-op for memory sink)
     */
    override fun flush() {
        // No-op for memory
    }

    /**
     * Close (clear buffer)
     */
    @Synchronized
    override fun close() {
        buffer.clear()
        _logs.value = emptyList()
    }

    /**
     * Clear all logs
     */
    @Synchronized
    fun clear() {
        buffer.clear()
        _logs.value = emptyList()
    }

    /**
     * Get current log count
     */
    @Synchronized
    fun getCount(): Int {
        return buffer.size
    }

    /**
     * Get logs filtered by level/context/domain
     */
    @Synchronized
    fun getFiltered(
        minLevel: uk.unmannedsystems.dpm_android.logging.LogLevel? = null,
        context: uk.unmannedsystems.dpm_android.logging.LogContext? = null,
        domain: uk.unmannedsystems.dpm_android.logging.LogDomain? = null,
        searchText: String? = null
    ): List<LogEntry> {
        return buffer.filter { entry ->
            val levelMatch = minLevel == null || entry.level.value >= minLevel.value
            val contextMatch = context == null || entry.context == context
            val domainMatch = domain == null || entry.domain == domain
            val textMatch = searchText.isNullOrBlank() ||
                    entry.message.contains(searchText, ignoreCase = true) ||
                    entry.fields.values.any { it.toString().contains(searchText, ignoreCase = true) }

            levelMatch && contextMatch && domainMatch && textMatch
        }.sortedBy { it.timestamp }
    }
}
