package uk.unmannedsystems.dpm_android.logging.sinks

import uk.unmannedsystems.dpm_android.logging.LogEntry
import uk.unmannedsystems.dpm_android.logging.StructuredLogger
import java.io.BufferedWriter
import java.io.File
import java.io.FileWriter
import java.io.IOException

/**
 * File Sink - Writes logs to JSON Lines files with size-based rotation
 *
 * Features:
 * - JSON Lines format (.jsonl)
 * - Size-based rotation (default 50 MB)
 * - Keeps N rotated files (default 3)
 * - Thread-safe writes
 *
 * File naming:
 * - Current: ground-side.jsonl
 * - Rotated: ground-side.1.jsonl, ground-side.2.jsonl, ground-side.3.jsonl
 */
class FileSink(
    private val logDir: File,
    private val maxFileSizeMB: Int = 50,
    private val maxRotatedFiles: Int = 3
) : LogSink {
    private val TAG = "FileSink"

    private val baseFileName = "ground-side.jsonl"
    private val maxFileSizeBytes = maxFileSizeMB * 1024 * 1024L

    private var currentFile: File = File(logDir, baseFileName)
    private var writer: BufferedWriter? = null

    init {
        // Ensure log directory exists
        if (!logDir.exists()) {
            logDir.mkdirs()
            StructuredLogger.info("STORAGE", "Created log directory: ${logDir.absolutePath}")
        }

        // Open the current log file
        try {
            writer = BufferedWriter(FileWriter(currentFile, true))
            StructuredLogger.info("STORAGE", "FileSink initialized: ${currentFile.absolutePath}")
        } catch (e: IOException) {
            StructuredLogger.error("STORAGE", "Failed to open log file: ${e.message}")
        }
    }

    /**
     * Write a log entry to the file
     */
    @Synchronized
    override fun write(entry: LogEntry) {
        try {
            // Check if rotation is needed
            if (currentFile.length() >= maxFileSizeBytes) {
                rotate()
            }

            // Write JSON line
            writer?.write(entry.toJson())
            writer?.newLine()
        } catch (e: IOException) {
            StructuredLogger.error("STORAGE", "Failed to write log entry: ${e.message}")
        }
    }

    /**
     * Flush buffered writes to disk
     */
    @Synchronized
    override fun flush() {
        try {
            writer?.flush()
        } catch (e: IOException) {
            StructuredLogger.error("STORAGE", "Failed to flush log file: ${e.message}")
        }
    }

    /**
     * Close the file sink
     */
    @Synchronized
    override fun close() {
        try {
            writer?.flush()
            writer?.close()
            StructuredLogger.info("STORAGE", "FileSink closed")
        } catch (e: IOException) {
            StructuredLogger.error("STORAGE", "Failed to close log file: ${e.message}")
        }
    }

    /**
     * Rotate log files
     *
     * Process:
     * 1. Close current writer
     * 2. Delete oldest rotated file (if exists)
     * 3. Rename all rotated files (increment number)
     * 4. Rename current file to .1.jsonl
     * 5. Create new current file
     * 6. Open new writer
     */
    private fun rotate() {
        StructuredLogger.info("STORAGE", "Rotating log files (current size: ${currentFile.length() / 1024 / 1024} MB)")

        try {
            // Close current writer
            writer?.flush()
            writer?.close()

            // Delete oldest file (e.g., ground-side.3.jsonl)
            val oldestFile = File(logDir, "$baseFileName.$maxRotatedFiles.jsonl")
            if (oldestFile.exists()) {
                oldestFile.delete()
                StructuredLogger.debug("STORAGE", "Deleted oldest log file: ${oldestFile.name}")
            }

            // Rename existing rotated files (increment number)
            for (i in (maxRotatedFiles - 1) downTo 1) {
                val sourceFile = File(logDir, "$baseFileName.$i.jsonl")
                val destFile = File(logDir, "$baseFileName.${i + 1}.jsonl")
                if (sourceFile.exists()) {
                    sourceFile.renameTo(destFile)
                    StructuredLogger.debug("STORAGE", "Renamed ${sourceFile.name} -> ${destFile.name}")
                }
            }

            // Rename current file to .1.jsonl
            val rotatedFile = File(logDir, "$baseFileName.1.jsonl")
            currentFile.renameTo(rotatedFile)
            StructuredLogger.debug("STORAGE", "Renamed ${currentFile.name} -> ${rotatedFile.name}")

            // Create new current file
            currentFile = File(logDir, baseFileName)
            writer = BufferedWriter(FileWriter(currentFile, true))
            StructuredLogger.info("STORAGE", "Created new log file: ${currentFile.name}")
        } catch (e: IOException) {
            StructuredLogger.error("STORAGE", "Failed to rotate log files: ${e.message}")
        }
    }
}
