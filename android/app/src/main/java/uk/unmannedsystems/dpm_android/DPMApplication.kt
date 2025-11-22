package uk.unmannedsystems.dpm_android

import android.app.Application
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch
import timber.log.Timber
import uk.unmannedsystems.dpm_android.camera.PropertyLoader
import uk.unmannedsystems.dpm_android.logging.LogContext
import uk.unmannedsystems.dpm_android.logging.LogLevel
import uk.unmannedsystems.dpm_android.logging.StructuredLogger
import uk.unmannedsystems.dpm_android.logging.UdpLogReceiver
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
        // MemorySink for Log Viewer UI access
        lateinit var memorySink: MemorySink
            private set

        // UDP log receiver for Air-Side logs
        private var udpLogReceiver: UdpLogReceiver? = null
    }

    override fun onCreate() {
        super.onCreate()
        Timber.tag(LogContext.SYSTEM.label).i("═══════════════════════════════════════════════════")
        Timber.tag(LogContext.SYSTEM.label).i("DPM Application Starting - Build: ${BuildConfig.BUILD_DATE}")
        Timber.tag(LogContext.SYSTEM.label).i("Platform: SkyDroid H16 (Ground-Side)")
        Timber.tag(LogContext.SYSTEM.label).i("═══════════════════════════════════════════════════")

        // Initialize SettingsManager
        SettingsManager.initialize(this)
        Timber.tag(LogContext.SYSTEM.label).d("✅ SettingsManager initialized")

        // Plant Timber tree for Android Logcat integration (before StructuredLogger)
        if (Timber.treeCount == 0) {
            Timber.plant(Timber.DebugTree())  // Default Android logging for now
        }

        // Initialize PropertyLoader (specification-first architecture)
        Timber.tag(LogContext.SYSTEM.label).d("Loading camera property specifications from camera_properties.json...")
        if (!PropertyLoader.initialize(this)) {
            Timber.tag(LogContext.SYSTEM.label).e("❌ Failed to initialize PropertyLoader - camera property validation unavailable")
            // Continue anyway - app can still function, but property validation will fail
        } else {
            Timber.tag(LogContext.SYSTEM.label).d("✅ PropertyLoader initialized successfully")
            Timber.tag(LogContext.SYSTEM.label).d("   Loaded properties: ISO=${PropertyLoader.getValueCount("iso")}, " +
                    "Shutter=${PropertyLoader.getValueCount("shutter_speed")}, " +
                    "Aperture=${PropertyLoader.getValueCount("aperture")}")
        }

        // Initialize logger and network on app startup
        applicationScope.launch {
            try {
                // Load saved settings
                val settingsRepository = SettingsRepository(this@DPMApplication)
                val savedSettings = settingsRepository.networkSettingsFlow.first()
                val autoConnectEnabled = settingsRepository.autoConnectEnabledFlow.first()
                val autoReconnectEnabled = settingsRepository.autoReconnectEnabledFlow.first()
                val autoReconnectInterval = settingsRepository.autoReconnectIntervalFlow.first()
                val clientId = settingsRepository.clientIdFlow.first()

                // Load SystemTools logging settings (Issue #99)
                val systemToolsLogHost = settingsRepository.systemToolsLogHostFlow.first()
                val systemToolsLogPort = settingsRepository.systemToolsLogPortFlow.first()
                val systemToolsLogEnabled = settingsRepository.systemToolsLogEnabledFlow.first()

                Timber.tag(LogContext.SYSTEM.label).i("───────────────────────────────────────────────────")
                Timber.tag(LogContext.SYSTEM.label).i("Settings Loaded:")
                Timber.tag(LogContext.SYSTEM.label).i("  Air-Side: ${savedSettings.targetIp}:${savedSettings.commandPort}")
                Timber.tag(LogContext.SYSTEM.label).i("  Client ID: $clientId")
                Timber.tag(LogContext.SYSTEM.label).i("  Auto-connect: $autoConnectEnabled")
                Timber.tag(LogContext.SYSTEM.label).i("  Auto-reconnect: $autoReconnectEnabled (${autoReconnectInterval}s)")
                Timber.tag(LogContext.SYSTEM.label).i("  SystemTools: $systemToolsLogHost:$systemToolsLogPort (enabled: $systemToolsLogEnabled)")
                Timber.tag(LogContext.SYSTEM.label).i("───────────────────────────────────────────────────")

                // Initialize StructuredLogger with dynamic SystemTools settings (Issue #99)
                Timber.tag(LogContext.SYSTEM.label).d("Initializing StructuredLogger...")
                initializeStructuredLogger(systemToolsLogHost, systemToolsLogPort, systemToolsLogEnabled && BuildConfig.DEBUG)
                Timber.tag(LogContext.SYSTEM.label).d("✅ StructuredLogger initialized")

                // Plant StructuredLogger Timber tree
                if (Timber.treeCount == 1) {  // Only DebugTree is planted
                    Timber.plant(StructuredLogger.TimberTree())
                    Timber.tag(LogContext.SYSTEM.label).d("✅ StructuredLogger Timber tree planted")
                }

                // Log app startup with structured logger
                Timber.i("═══ DPM H16 Ground-Side Application Ready ═══")
                Timber.i("Build: ${BuildConfig.BUILD_DATE}")
                Timber.i("SystemTools logging: $systemToolsLogHost:$systemToolsLogPort")

                // Initialize NetworkManager with context, saved settings and client ID
                Timber.tag(LogContext.SYSTEM.label).d("Initializing NetworkManager...")
                NetworkManager.initialize(this@DPMApplication, savedSettings, clientId)
                Timber.tag(LogContext.SYSTEM.label).d("✅ NetworkManager initialized")

                // Configure auto-reconnect
                NetworkManager.configureAutoReconnect(autoReconnectEnabled, autoReconnectInterval)
                Timber.i("Auto-reconnect configured: enabled=$autoReconnectEnabled, interval=${autoReconnectInterval}s")

                // Auto-connect on startup if enabled
                if (autoConnectEnabled) {
                    Timber.tag(LogContext.SYSTEM.label).i("🔄 Auto-connecting to Air-Side on app startup...")
                    Timber.i("Auto-connect enabled - connecting to ${savedSettings.targetIp}:${savedSettings.commandPort}")
                    NetworkManager.connect()
                } else {
                    Timber.tag(LogContext.SYSTEM.label).i("⏸️  Auto-connect disabled, skipping initial connection")
                    Timber.i("Auto-connect disabled - manual connection required")
                }

                Timber.tag(LogContext.SYSTEM.label).i("═══════════════════════════════════════════════════")
                Timber.tag(LogContext.SYSTEM.label).i("DPM Application Initialization Complete")
                Timber.tag(LogContext.SYSTEM.label).i("═══════════════════════════════════════════════════")

            } catch (e: Exception) {
                Timber.tag(LogContext.SYSTEM.label).e(e, "❌ Error initializing application")
                Timber.e(e, "Application initialization failed")
            }
        }
    }

    /**
     * Initialize StructuredLogger with all sinks
     *
     * Issue #99: Dynamic SystemTools IP configuration
     * - Default: "localhost" with ADB reverse port forwarding (adb reverse tcp:5008 tcp:5008)
     * - Fallback: User-configurable IP in settings (for when ADB reverse fails)
     *
     * @param systemToolsHost SystemTools host (default: "localhost")
     * @param systemToolsPort SystemTools port (default: 5008)
     * @param networkSinkEnabled Enable NetworkSink (only in DEBUG builds)
     */
    private fun initializeStructuredLogger(
        systemToolsHost: String = "localhost",
        systemToolsPort: Int = 5008,
        networkSinkEnabled: Boolean = false
    ) {
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

            // NetworkSink for SystemTools (Issue #99: Dynamic IP)
            // Uses settings-configured host (default: "localhost" with ADB reverse)
            // Setup ADB reverse: adb reverse tcp:5008 tcp:5008
            val networkSink = NetworkSink(
                host = systemToolsHost,
                port = systemToolsPort,
                enabled = networkSinkEnabled
            )

            Timber.tag(LogContext.SYSTEM.label).i("NetworkSink configuration: host=$systemToolsHost, port=$systemToolsPort, enabled=$networkSinkEnabled")

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

            Timber.tag(LogContext.SYSTEM.label).i("✅ StructuredLogger initialized with ${sinks.size} sinks")
            Timber.tag(LogContext.SYSTEM.label).i("   - FileSink: ${logDir.absolutePath}")
            Timber.tag(LogContext.SYSTEM.label).i("   - MemorySink: 1000 entries max")
            if (networkSinkEnabled) {
                Timber.tag(LogContext.SYSTEM.label).i("   - NetworkSink: $systemToolsHost:$systemToolsPort ✅ ENABLED")
            } else {
                Timber.tag(LogContext.SYSTEM.label).i("   - NetworkSink: ❌ DISABLED (not a DEBUG build or disabled in settings)")
            }

            // Start UDP log receiver for Air-Side logs
            udpLogReceiver = UdpLogReceiver(port = 5005)
            udpLogReceiver?.start()
            Timber.tag(LogContext.SYSTEM.label).i("✅ UDP log receiver started on port 5005 (Air-Side logs)")

        } catch (e: Exception) {
            Timber.tag(LogContext.SYSTEM.label).e(e, "❌ Failed to initialize StructuredLogger")
        }
    }
}
