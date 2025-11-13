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
 * Features:
 * - TCP connection to SystemTools (via ADB port forward)
 * - JSON Lines format
 * - Automatic reconnection on disconnect
 * - Buffered writes
 * - Non-blocking (uses coroutines)
 *
 * Usage:
 * - SystemTools listens on port 5008
 * - ADB port forward: adb forward tcp:5008 tcp:5008
 * - Ground-Side connects to localhost:5008
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
            // Start connection attempt
            reconnectJob = scope.launch {
                attemptConnection()
            }

            // Start send worker
            sendJob = scope.launch {
                processSendQueue()
            }
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
        while (scope.isActive) {
            try {
                if (!isConnected) {
                    Log.d(TAG, "Attempting connection to $host:$port")

                    socket = Socket(host, port)
                    socket?.soTimeout = 5000  // 5 second read timeout
                    writer = BufferedWriter(OutputStreamWriter(socket?.getOutputStream()))

                    isConnected = true
                    Log.i(TAG, "Connected to SystemTools at $host:$port")
                }

                // Wait before next check
                delay(5000)
            } catch (e: Exception) {
                isConnected = false
                Log.w(TAG, "Connection failed, will retry: ${e.message}")

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
        while (scope.isActive) {
            try {
                if (isConnected && writer != null) {
                    val json = sendQueue.poll()
                    if (json != null) {
                        writer?.write(json)
                        writer?.newLine()
                        writer?.flush()
                    } else {
                        // Queue empty, wait briefly
                        delay(10)
                    }
                } else {
                    // Not connected, wait
                    delay(100)
                }
            } catch (e: Exception) {
                Log.e(TAG, "Error sending log to SystemTools", e)
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
