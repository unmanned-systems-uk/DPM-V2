package uk.unmannedsystems.dpm_android.logging

import kotlinx.coroutines.*
import org.json.JSONObject
import timber.log.Timber
import uk.unmannedsystems.dpm_android.DPMApplication
import java.net.DatagramPacket
import java.net.DatagramSocket
import java.net.SocketException

/**
 * UDP Log Receiver
 *
 * Listens for Air-Side log entries on UDP port 5005 and adds them to MemorySink
 * Part of Issue #73 - Phase 1: Foundation Infrastructure (Gap 1)
 *
 * Features:
 * - UDP socket listener on port 5005
 * - JSON parsing of Air-Side log entries
 * - Automatic addition to MemorySink for display in Log Viewer
 * - Thread-safe operation
 * - Graceful shutdown
 */
class UdpLogReceiver(
    private val port: Int = 5005
) {
    private val TAG = "UdpLogReceiver"

    private var socket: DatagramSocket? = null
    private var isRunning = false
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())

    /**
     * Start listening for UDP log packets
     */
    fun start() {
        if (isRunning) {
            StructuredLogger.warning(LogContext.NETWORK, "UDP log receiver already running")
            return
        }

        scope.launch {
            try {
                socket = DatagramSocket(port)
                isRunning = true
                StructuredLogger.info(LogContext.NETWORK, "UDP log receiver started on port $port")

                val buffer = ByteArray(65536) // Max UDP packet size
                val packet = DatagramPacket(buffer, buffer.size)

                while (isRunning && !Thread.currentThread().isInterrupted) {
                    try {
                        // Receive UDP packet (blocking)
                        socket?.receive(packet)

                        // Parse JSON log entry
                        val json = String(packet.data, 0, packet.length)
                        parseAndAddLog(json)

                    } catch (e: SocketException) {
                        if (isRunning) {
                            StructuredLogger.error(LogContext.NETWORK, "Socket error receiving UDP packet: ${e.message}")
                        }
                        // Socket closed, exit loop
                        break
                    } catch (e: Exception) {
                        StructuredLogger.error(LogContext.NETWORK, "Error processing UDP log packet: ${e.message}")
                        // Continue listening for next packet
                    }
                }

            } catch (e: Exception) {
                StructuredLogger.error(LogContext.NETWORK, "Error starting UDP log receiver: ${e.message}")
            } finally {
                isRunning = false
                socket?.close()
                socket = null
                StructuredLogger.info(LogContext.NETWORK, "UDP log receiver stopped")
            }
        }
    }

    /**
     * Stop listening for UDP log packets
     */
    fun stop() {
        if (!isRunning) {
            return
        }

        StructuredLogger.info(LogContext.NETWORK, "Stopping UDP log receiver...")
        isRunning = false
        socket?.close()
        scope.cancel()
    }

    /**
     * Parse JSON log entry and add to MemorySink
     */
    private fun parseAndAddLog(json: String) {
        try {
            val obj = JSONObject(json)

            // Parse fields
            val timestamp = obj.optString("timestamp", "")
            val levelStr = obj.optString("level", "INFO")
            val contextStr = obj.optString("context", "SYSTEM")
            val domainStr = obj.optString("domain", "AIR")
            val threadName = obj.optString("thread", "")
            val message = obj.optString("message", "")

            // Parse additional fields
            val fields = mutableMapOf<String, Any>()
            val fieldsObj = obj.optJSONObject("fields")
            if (fieldsObj != null) {
                val keys = fieldsObj.keys()
                while (keys.hasNext()) {
                    val key = keys.next()
                    fields[key] = fieldsObj.get(key)
                }
            }

            // Convert strings to enums
            val level = try {
                LogLevel.valueOf(levelStr.uppercase())
            } catch (e: IllegalArgumentException) {
                LogLevel.INFO
            }

            val context = try {
                LogContext.valueOf(contextStr.uppercase())
            } catch (e: IllegalArgumentException) {
                LogContext.SYSTEM
            }

            val domain = try {
                LogDomain.valueOf(domainStr.uppercase())
            } catch (e: IllegalArgumentException) {
                LogDomain.AIR
            }

            // Create LogEntry
            val logEntry = LogEntry(
                timestamp = timestamp,
                level = level,
                context = context,
                domain = domain,
                threadName = threadName,
                message = message,
                fields = fields
            )

            // Add to MemorySink (for local Log Viewer)
            DPMApplication.memorySink.write(logEntry)

            // Also log via Timber for SystemTools relay (Issue #99, #113)
            // This ensures Air-Side logs flow through StructuredLogger → NetworkSink → SystemTools
            when (level) {
                LogLevel.DEBUG -> Timber.tag("AIR-SIDE").d(message)
                LogLevel.INFO -> Timber.tag("AIR-SIDE").i(message)
                LogLevel.WARNING -> Timber.tag("AIR-SIDE").w(message)
                LogLevel.ERROR -> Timber.tag("AIR-SIDE").e(message)
                else -> Timber.tag("AIR-SIDE").i(message)
            }

            // Log successfully received (verbose level not needed for protocol compliance)

        } catch (e: Exception) {
            StructuredLogger.error(LogContext.NETWORK, "Error parsing log JSON: ${e.message}")
        }
    }

    /**
     * Check if receiver is running
     */
    fun isRunning(): Boolean = isRunning

    companion object {
        const val DEFAULT_PORT = 5005
    }
}
