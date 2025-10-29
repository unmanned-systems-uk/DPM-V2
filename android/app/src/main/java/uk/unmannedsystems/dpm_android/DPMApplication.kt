package uk.unmannedsystems.dpm_android

import android.app.Application
import android.util.Log
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch
import uk.unmannedsystems.dpm_android.camera.PropertyLoader
import uk.unmannedsystems.dpm_android.network.NetworkManager
import uk.unmannedsystems.dpm_android.settings.SettingsManager
import uk.unmannedsystems.dpm_android.settings.SettingsRepository

/**
 * Custom Application class for DPM Android
 * Handles app-wide initialization including network setup
 */
class DPMApplication : Application() {
    private val applicationScope = CoroutineScope(SupervisorJob() + Dispatchers.Main)

    companion object {
        private const val TAG = "DPMApplication"
    }

    override fun onCreate() {
        super.onCreate()
        Log.d(TAG, "DPM Application starting...")

        // Initialize SettingsManager
        SettingsManager.initialize(this)

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

                // Initialize NetworkManager with saved settings and client ID
                NetworkManager.initialize(savedSettings, clientId)

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
}
