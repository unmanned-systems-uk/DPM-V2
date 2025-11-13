package uk.unmannedsystems.dpm_android

import android.app.Application
import android.util.Log
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch
import timber.log.Timber
import uk.unmannedsystems.dpm_android.camera.PropertyLoader
import uk.unmannedsystems.dpm_android.logging.LogLevel
import uk.unmannedsystems.dpm_android.logging.StructuredLogger
import uk.unmannedsystems.dpm_android.logging.sinks.FileSink
import uk.unmannedsystems.dpm_android.logging.sinks.MemorySink
import uk.unmannedsystems.dpm_android.logging.sinks.NetworkSink
import uk.unmannedsystems.dpm_android.network.NetworkManager
import uk.unmannedsystems.dpm_android.settings.SettingsManager
import uk.unmannedsystems.dpm_android.settings.SettingsRepository
import java.io.File

/**
 * Custom Application class for DPM Android
 * Handles app-wide initialization including network setup
 */
class DPMApplication : Application() {
    private val applicationScope = CoroutineScope(SupervisorJob() + Dispatchers.Main)

    companion object {
        private const val TAG = "DPMApplication"

        // MemorySink for Log Viewer UI access
        lateinit var memorySink: MemorySink
            private set
    }

    override fun onCreate() {
        super.onCreate()
        Log.d(TAG, "DPM Application starting...")

        // Initialize SettingsManager
        SettingsManager.initialize(this)

        // Initialize StructuredLogger with sinks
        initializeStructuredLogger()

        // Plant Timber tree for Android Logcat integration
        if (Timber.treeCount == 0) {
            Timber.plant(StructuredLogger.TimberTree())
            Timber.plant(Timber.DebugTree())  // Also keep default Android logging
        }

        // Log app startup with structured logger
        Timber.i("DPM Application initialized - Build: ${BuildConfig.BUILD_DATE}")

        // Initialize PropertyLoader (specification-first architecture)
        Log.d(TAG, "Loading camera property specifications from camera_properties.json...")
        if (!PropertyLoader.initialize(this)) {
            Log.e(TAG, "Failed to initialize PropertyLoader - camera property validation unavailable")
            // Continue anyway - app can still function, but property validation will fail
        } else {
            Log.d(TAG, "PropertyLoader initialized successfully")
            Log.d(TAG, "Loaded properties: ISO=${PropertyLoader.getValueCount("iso")}, " +
                    "Shutter=${PropertyLoader.getValueCount("shutter_speed")}, " +
                    "Aperture=${PropertyLoader.getValueCount("aperture")}")
        }

        // Initialize network on app startup
        applicationScope.launch {
            try {
                // Load saved settings
                val settingsRepository = SettingsRepository(this@DPMApplication)
                val savedSettings = settingsRepository.networkSettingsFlow.first()
                val autoConnectEnabled = settingsRepository.autoConnectEnabledFlow.first()
                val autoReconnectEnabled = settingsRepository.autoReconnectEnabledFlow.first()
                val autoReconnectInterval = settingsRepository.autoReconnectIntervalFlow.first()
                val clientId = settingsRepository.clientIdFlow.first()

                Log.d(TAG, "Loaded settings: ${savedSettings.targetIp}:${savedSettings.commandPort}, clientId: $clientId")
                Log.d(TAG, "Auto-connect enabled: $autoConnectEnabled")
                Log.d(TAG, "Auto-reconnect enabled: $autoReconnectEnabled, interval: ${autoReconnectInterval}s")

                // Initialize NetworkManager with context, saved settings and client ID
                NetworkManager.initialize(this@DPMApplication, savedSettings, clientId)

                // Configure auto-reconnect
                NetworkManager.configureAutoReconnect(autoReconnectEnabled, autoReconnectInterval)

                // Auto-connect on startup if enabled
                if (autoConnectEnabled) {
                    Log.d(TAG, "Auto-connecting on app startup...")
                    NetworkManager.connect()
                } else {
                    Log.d(TAG, "Auto-connect disabled, skipping initial connection")
                }
            } catch (e: Exception) {
                Log.e(TAG, "Error initializing network on startup", e)
            }
        }
    }

    /**
     * Initialize StructuredLogger with all sinks
     */
    private fun initializeStructuredLogger() {
        try {
            // Create log directory
            val logDir = File(getExternalFilesDir(null), "logs")
            if (!logDir.exists()) {
                logDir.mkdirs()
            }

            // Create sinks
            val fileSink = FileSink(
                logDir = logDir,
                maxFileSizeMB = 50,
                maxRotatedFiles = 3
            )

            memorySink = MemorySink(maxEntries = 1000)

            // NetworkSink for SystemTools (disabled by default, enable in debug builds if needed)
            val networkSinkEnabled = BuildConfig.DEBUG  // Only in debug builds
            val networkSink = NetworkSink(
                host = "localhost",
                port = 5008,
                enabled = networkSinkEnabled
            )

            // Initialize StructuredLogger with sinks
            val sinks = buildList {
                add(fileSink)
                add(memorySink)
                if (networkSinkEnabled) {
                    add(networkSink)
                }
            }

            StructuredLogger.init(
                minLevel = if (BuildConfig.DEBUG) LogLevel.DEBUG else LogLevel.INFO,
                sinks = sinks
            )

            Log.i(TAG, "StructuredLogger initialized with ${sinks.size} sinks (log dir: ${logDir.absolutePath})")
        } catch (e: Exception) {
            Log.e(TAG, "Failed to initialize StructuredLogger", e)
        }
    }
}
