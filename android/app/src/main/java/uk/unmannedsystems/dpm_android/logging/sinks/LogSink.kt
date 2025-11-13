package uk.unmannedsystems.dpm_android.logging.sinks

import uk.unmannedsystems.dpm_android.logging.LogEntry

/**
 * Log Sink interface
 *
 * All log sinks must implement this interface to receive log entries
 * from StructuredLogger.
 */
interface LogSink {
    /**
     * Write a log entry to the sink
     */
    fun write(entry: LogEntry)

    /**
     * Flush any buffered log entries
     */
    fun flush()

    /**
     * Close the sink and release resources
     */
    fun close()
}
