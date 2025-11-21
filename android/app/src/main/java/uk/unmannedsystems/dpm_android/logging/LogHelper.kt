package uk.unmannedsystems.dpm_android.logging

import timber.log.Timber

/**
 * Unified logging helper that wraps both Android logcat (Log.d) and Timber/StructuredLogger
 *
 * Allows dynamic control of both logging systems via Advanced Settings:
 * - Android Logcat: Safe, always available via ADB
 * - Structured Logging: Timber → FileSink, MemorySink, NetworkSink → SystemTools
 *
 * Both can run in parallel during testing. Disable Log.d() only after Timber is proven reliable.
 *
 * Usage:
 * ```
 * // Instead of:
 * Log.d("MyTag", "message")
 * Timber.d("message")
 *
 * // Use:
 * LogHelper.d("MyTag", "message")
 * ```
 *
 * @see uk.unmannedsystems.dpm_android.settings.SettingsRepository
 */
object LogHelper {
    private var androidLogcatEnabled = true
    private var structuredLoggingEnabled = true

    /**
     * Update logging settings from SettingsRepository
     * Should be called when settings change or on app startup
     */
    fun updateSettings(androidEnabled: Boolean, structuredEnabled: Boolean) {
        androidLogcatEnabled = androidEnabled
        structuredLoggingEnabled = structuredEnabled

        // Log the configuration change itself using protocol-compliant logging
        StructuredLogger.info("CONFIG", "Logging configuration updated: Android=$androidEnabled, Structured=$structuredEnabled")
    }

    /**
     * Debug log
     */
    fun d(tag: String, message: String) {
        if (structuredLoggingEnabled) {
            Timber.tag(tag).d(message)
        }
    }

    /**
     * Info log
     */
    fun i(tag: String, message: String) {
        if (structuredLoggingEnabled) {
            Timber.tag(tag).i(message)
        }
    }

    /**
     * Warning log
     */
    fun w(tag: String, message: String, throwable: Throwable? = null) {
        if (structuredLoggingEnabled) {
            if (throwable != null) {
                Timber.tag(tag).w(throwable, message)
            } else {
                Timber.tag(tag).w(message)
            }
        }
    }

    /**
     * Error log
     */
    fun e(tag: String, message: String, throwable: Throwable? = null) {
        if (structuredLoggingEnabled) {
            if (throwable != null) {
                Timber.tag(tag).e(throwable, message)
            } else {
                Timber.tag(tag).e(message)
            }
        }
    }

    /**
     * Verbose log
     */
    fun v(tag: String, message: String) {
        if (structuredLoggingEnabled) {
            Timber.tag(tag).v(message)
        }
    }

    /**
     * Get current Android logcat enabled state
     */
    fun isAndroidLogcatEnabled(): Boolean = androidLogcatEnabled

    /**
     * Get current structured logging enabled state
     */
    fun isStructuredLoggingEnabled(): Boolean = structuredLoggingEnabled
}
