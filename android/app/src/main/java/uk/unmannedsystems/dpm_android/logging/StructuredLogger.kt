package uk.unmannedsystems.dpm_android.logging

import com.google.gson.Gson
import com.google.gson.GsonBuilder
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import timber.log.Timber
import uk.unmannedsystems.dpm_android.logging.sinks.LogSink
import java.text.SimpleDateFormat
import java.util.*
import java.util.concurrent.ConcurrentLinkedQueue

/**
 * Log level enum matching Air-Side specification
 */
enum class LogLevel(val value: Int, val label: String) {
    DEBUG(0, "DEBUG"),
    INFO(1, "INFO"),
    WARNING(2, "WARNING"),
    ERROR(3, "ERROR");

    companion object {
        fun fromString(level: String): LogLevel {
            return entries.find { it.label == level.uppercase() } ?: INFO
        }
    }
}

/**
 * Log context enum for categorizing logs
 *
 * NOTE: Must stay synchronized with protocol/log_contexts.json
 * Issue #164: Added HEALTH, CONFIG, DISCOVERY for protocol compliance
 */
enum class LogContext(val label: String) {
    CAMERA("CAMERA"),
    NETWORK("NETWORK"),
    COMMAND("COMMAND"),
    CONFIG("CONFIG"),           // Added for Issue #164 protocol compliance
    DISCOVERY("DISCOVERY"),     // Added for Issue #164 protocol compliance
    SYSTEM("SYSTEM"),
    STORAGE("STORAGE"),
    HEALTH("HEALTH"),           // Added for Issue #164 protocol compliance
    SYNC("SYNC"),
    UI("UI");

    companion object {
        fun fromString(context: String): LogContext {
            return entries.find { it.label == context.uppercase() } ?: SYSTEM
        }
    }
}

/**
 * Log domain for identifying source (Air-Side vs Ground-Side)
 */
enum class LogDomain(val label: String) {
    AIR("AIR"),
    GROUND("GROUND");
}

/**
 * Structured log entry data class
 */
data class LogEntry(
    val timestamp: String,
    val level: LogLevel,
    val context: LogContext,
    val domain: LogDomain,
    val threadName: String,
    val message: String,
    val fields: Map<String, Any> = emptyMap()
) {
    /**
     * Convert to JSON string for network/file output
     */
    fun toJson(): String {
        val map = mutableMapOf<String, Any>(
            "timestamp" to timestamp,
            "level" to level.label,
            "context" to context.label,
            "domain" to domain.label,
            "thread" to threadName,
            "message" to message
        )
        // Add structured fields
        map.putAll(fields)
        return gson.toJson(map)
    }

    /**
     * Convert to human-readable string for console/UI
     */
    fun toDisplayString(): String {
        val sb = StringBuilder()
        sb.append("$timestamp [${domain.label}][${level.label}][${context.label}] $message")
        if (fields.isNotEmpty()) {
            sb.append("\n  └─ ")
            sb.append(fields.entries.joinToString(", ") { "${it.key}: ${it.value}" })
        }
        return sb.toString()
    }

    companion object {
        private val gson: Gson = GsonBuilder().create()
    }
}

/**
 * Structured Logger - Main logging class
 *
 * Features:
 * - Thread-safe logging with coroutines
 * - Multiple sinks (Console, File, Network, Memory)
 * - Structured fields (key-value pairs)
 * - JSON output format
 * - Integration with Timber for Android Logcat
 */
object StructuredLogger {
    private const val TAG = "StructuredLogger"

    // Sinks
    private val sinks = mutableListOf<LogSink>()
    private val logQueue = ConcurrentLinkedQueue<LogEntry>()

    // Coroutine scope for background logging
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    private var processingJob: Job? = null

    // Configuration
    private var minLogLevel = LogLevel.DEBUG
    private var isInitialized = false

    // Timestamp formatter (ISO 8601)
    private val timestampFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'", Locale.US).apply {
        timeZone = TimeZone.getTimeZone("UTC")
    }

    // Gson for JSON serialization
    private val gson: Gson = GsonBuilder().setPrettyPrinting().create()

    /**
     * Initialize the logger with sinks
     */
    fun init(
        minLevel: LogLevel = LogLevel.DEBUG,
        sinks: List<LogSink> = emptyList()
    ) {
        if (isInitialized) {
            // Already initialized - skip duplicate init
            return
        }

        minLogLevel = minLevel
        this.sinks.addAll(sinks)

        // Start background processing
        startProcessing()

        isInitialized = true
        // StructuredLogger initialized (internal logging removed to prevent circular dependencies)
    }

    /**
     * Add a sink dynamically
     */
    fun addSink(sink: LogSink) {
        synchronized(sinks) {
            sinks.add(sink)
        }
        // Sink added (internal logging removed to prevent circular dependencies)
    }

    /**
     * Remove a sink
     */
    fun removeSink(sink: LogSink) {
        synchronized(sinks) {
            sinks.remove(sink)
        }
        // Sink removed (internal logging removed to prevent circular dependencies)
    }

    /**
     * Set minimum log level
     */
    fun setMinLogLevel(level: LogLevel) {
        minLogLevel = level
        // Min log level set (internal logging removed to prevent circular dependencies)
    }

    /**
     * Log a message with structured fields
     */
    fun log(
        level: LogLevel,
        context: LogContext,
        message: String,
        fields: Map<String, Any> = emptyMap()
    ) {
        // Filter by minimum log level
        if (level.value < minLogLevel.value) {
            return
        }

        val entry = LogEntry(
            timestamp = timestampFormat.format(Date()),
            level = level,
            context = context,
            domain = LogDomain.GROUND,
            threadName = Thread.currentThread().name,
            message = message,
            fields = fields
        )

        // Add to queue for background processing
        logQueue.offer(entry)
    }

    /**
     * Log from Air-Side (received via UDP or TCP)
     */
    fun logFromAirSide(
        level: LogLevel,
        context: LogContext,
        timestamp: String,
        threadName: String,
        message: String,
        fields: Map<String, Any> = emptyMap()
    ) {
        val entry = LogEntry(
            timestamp = timestamp,
            level = level,
            context = context,
            domain = LogDomain.AIR,
            threadName = threadName,
            message = message,
            fields = fields
        )

        // Add to queue for background processing
        logQueue.offer(entry)
    }

    /**
     * Convenience methods for different log levels
     */
    fun debug(context: LogContext, message: String, fields: Map<String, Any> = emptyMap()) {
        log(LogLevel.DEBUG, context, message, fields)
    }

    fun info(context: LogContext, message: String, fields: Map<String, Any> = emptyMap()) {
        log(LogLevel.INFO, context, message, fields)
    }

    fun warning(context: LogContext, message: String, fields: Map<String, Any> = emptyMap()) {
        log(LogLevel.WARNING, context, message, fields)
    }

    fun error(context: LogContext, message: String, fields: Map<String, Any> = emptyMap()) {
        log(LogLevel.ERROR, context, message, fields)
    }

    /**
     * Start background processing of log queue
     */
    private fun startProcessing() {
        processingJob = scope.launch {
            while (isActive) {
                try {
                    val entry = logQueue.poll()
                    if (entry != null) {
                        // Send to all sinks
                        synchronized(sinks) {
                            sinks.forEach { sink ->
                                try {
                                    sink.write(entry)
                                } catch (e: Exception) {
                                    // Silently drop sink write errors to prevent circular logging
                                }
                            }
                        }
                    } else {
                        // No logs to process, wait briefly
                        delay(10)
                    }
                } catch (e: Exception) {
                    // Silently drop queue processing errors to prevent circular logging
                }
            }
        }
    }

    /**
     * Flush all sinks
     */
    fun flush() {
        synchronized(sinks) {
            sinks.forEach { sink ->
                try {
                    sink.flush()
                } catch (e: Exception) {
                    // Silently drop flush errors to prevent circular logging
                }
            }
        }
    }

    /**
     * Shutdown the logger
     */
    fun shutdown() {
        processingJob?.cancel()
        flush()
        synchronized(sinks) {
            sinks.forEach { sink ->
                try {
                    sink.close()
                } catch (e: Exception) {
                    // Silently drop close errors to prevent circular logging
                }
            }
            sinks.clear()
        }
        isInitialized = false
        // StructuredLogger shut down (internal logging removed to prevent circular dependencies)
    }

    /**
     * Timber Tree for Android Logcat integration
     */
    class TimberTree : Timber.Tree() {
        override fun log(priority: Int, tag: String?, message: String, t: Throwable?) {
            val level = when (priority) {
                Log.VERBOSE, Log.DEBUG -> LogLevel.DEBUG
                Log.INFO -> LogLevel.INFO
                Log.WARN -> LogLevel.WARNING
                Log.ERROR, Log.ASSERT -> LogLevel.ERROR
                else -> LogLevel.INFO
            }

            // Determine context from tag
            val context = when {
                tag?.contains("Camera", ignoreCase = true) == true -> LogContext.CAMERA
                tag?.contains("Network", ignoreCase = true) == true -> LogContext.NETWORK
                tag?.contains("Sync", ignoreCase = true) == true -> LogContext.SYNC
                tag?.contains("Command", ignoreCase = true) == true -> LogContext.COMMAND
                tag?.contains("Storage", ignoreCase = true) == true -> LogContext.STORAGE
                tag?.contains("UI", ignoreCase = true) == true -> LogContext.UI
                else -> LogContext.SYSTEM
            }

            val fields = mutableMapOf<String, Any>()
            if (tag != null) {
                fields["tag"] = tag
            }
            if (t != null) {
                fields["exception"] = t.toString()
                fields["stacktrace"] = t.stackTraceToString()
            }

            log(level, context, message, fields)
        }
    }
}
