package uk.unmannedsystems.dpm_android.logging.sinks

import android.util.Log
import kotlinx.coroutines.*
import uk.unmannedsystems.dpm_android.logging.LogEntry
import java.io.BufferedWriter
import java.io.OutputStreamWriter
import java.net.Socket
import java.util.concurrent.ConcurrentLinkedQueue

/**
 * Network Sink - Sends logs to SystemTools via TCP
 *
 * Issue #99: Dynamic IP Configuration
 * - Default: "localhost" with ADB reverse port forwarding
 *   Setup: adb reverse tcp:5008 tcp:5008
 *   This forwards H16's localhost:5008 to dev machine's port 5008
 * - Fallback: User-configured IP (e.g., "10.0.1.83") when ADB reverse fails
 *
 * Features:
 * - TCP connection to SystemTools
 * - JSON Lines format
 * - Automatic reconnection on disconnect
 * - Buffered writes with queue
 * - Non-blocking (uses coroutines)
 * - Enhanced logging for diagnostics
 */
class NetworkSink(
    private val host: String = "localhost",
    private val port: Int = 5008,
    private val enabled: Boolean = true
) : LogSink {
    private val TAG = "NetworkSink"

    private var socket: Socket? = null
    private var writer: BufferedWriter? = null
    private var isConnected = false

    // Queue for buffering logs when disconnected
    private val sendQueue = ConcurrentLinkedQueue<String>()
    private val maxQueueSize = 1000

    // Coroutine scope for background operations
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    private var sendJob: Job? = null
    private var reconnectJob: Job? = null

    init {
        if (enabled) {
            Log.i(TAG, "NetworkSink enabled: Connecting to SystemTools at $host:$port")
            Log.i(TAG, "If using 'localhost', ensure ADB reverse is set up: adb reverse tcp:$port tcp:$port")

            // Start connection attempt
            reconnectJob = scope.launch {
                attemptConnection()
            }

            // Start send worker
            sendJob = scope.launch {
                processSendQueue()
            }
        } else {
            Log.i(TAG, "NetworkSink disabled (not in DEBUG build or explicitly disabled in settings)")
        }
    }

    /**
     * Write a log entry to the network sink
     */
    override fun write(entry: LogEntry) {
        if (!enabled) {
            return
        }

        try {
            val json = entry.toJson()

            // Add to send queue
            if (sendQueue.size < maxQueueSize) {
                sendQueue.offer(json)
            } else {
                // Queue full, drop oldest
                sendQueue.poll()
                sendQueue.offer(json)
                Log.w(TAG, "Send queue full, dropped oldest log")
            }
        } catch (e: Exception) {
            Log.e(TAG, "Failed to queue log entry", e)
        }
    }

    /**
     * Flush buffered writes
     */
    override fun flush() {
        try {
            writer?.flush()
        } catch (e: Exception) {
            // Ignore flush errors
        }
    }

    /**
     * Close the network sink
     */
    override fun close() {
        sendJob?.cancel()
        reconnectJob?.cancel()

        try {
            writer?.flush()
            writer?.close()
            socket?.close()
        } catch (e: Exception) {
            Log.e(TAG, "Error closing network sink", e)
        }

        isConnected = false
        Log.i(TAG, "NetworkSink closed")
    }

    /**
     * Attempt to connect to SystemTools
     */
    private suspend fun attemptConnection() {
        var attemptCount = 0
        while (scope.isActive) {
            try {
                if (!isConnected) {
                    attemptCount++
                    Log.d(TAG, "Connection attempt #$attemptCount to $host:$port (queue size: ${sendQueue.size})")

                    socket = Socket(host, port)
                    socket?.soTimeout = 5000  // 5 second read timeout
                    writer = BufferedWriter(OutputStreamWriter(socket?.getOutputStream()))

                    isConnected = true
                    attemptCount = 0  // Reset counter on success
                    Log.i(TAG, "✅ Connected to SystemTools at $host:$port")

                    if (host == "localhost") {
                        Log.i(TAG, "Using ADB reverse - ensure 'adb reverse tcp:$port tcp:$port' is active")
                    }
                }

                // Wait before next check
                delay(5000)
            } catch (e: Exception) {
                isConnected = false

                if (attemptCount == 1) {
                    // First failure - provide helpful diagnostic
                    Log.w(TAG, "❌ Connection failed to $host:$port: ${e.javaClass.simpleName} - ${e.message}")
                    if (host == "localhost") {
                        Log.w(TAG, "💡 Troubleshooting: Run 'adb reverse tcp:$port tcp:$port' and ensure SystemTools is running")
                        Log.w(TAG, "💡 Alternative: Change host to dev machine IP (e.g., '10.0.1.83') in settings")
                    } else {
                        Log.w(TAG, "💡 Troubleshooting: Ensure SystemTools is running on $host and port $port is accessible")
                    }
                } else if (attemptCount % 6 == 0) {
                    // Log every 6th attempt (every ~60 seconds) to avoid spam
                    Log.w(TAG, "Still attempting connection to $host:$port (attempt #$attemptCount, queue: ${sendQueue.size} logs)")
                }

                // Clean up
                try {
                    writer?.close()
                    socket?.close()
                } catch (ignored: Exception) {
                }
                writer = null
                socket = null

                // Wait before retry
                delay(10000)  // 10 seconds
            }
        }
    }

    /**
     * Process send queue - sends buffered logs to SystemTools
     */
    private suspend fun processSendQueue() {
        var logsSentCount = 0
        var lastLogReportTime = System.currentTimeMillis()

        while (scope.isActive) {
            try {
                if (isConnected && writer != null) {
                    val json = sendQueue.poll()
                    if (json != null) {
                        writer?.write(json)
                        writer?.newLine()
                        writer?.flush()

                        logsSentCount++

                        // Report stats every 100 logs or every 30 seconds
                        val now = System.currentTimeMillis()
                        if (logsSentCount % 100 == 0 || (now - lastLogReportTime) > 30000) {
                            Log.d(TAG, "📤 Sent $logsSentCount logs to SystemTools (queue: ${sendQueue.size})")
                            lastLogReportTime = now
                        }
                    } else {
                        // Queue empty, wait briefly
                        delay(10)
                    }
                } else {
                    // Not connected, wait
                    delay(100)
                }
            } catch (e: Exception) {
                Log.e(TAG, "❌ Error sending log to SystemTools: ${e.javaClass.simpleName} - ${e.message}")
                isConnected = false

                // Clean up connection
                try {
                    writer?.close()
                    socket?.close()
                } catch (ignored: Exception) {
                }
                writer = null
                socket = null

                delay(1000)
            }
        }
    }
}
