package uk.unmannedsystems.dpm_android.settings

import android.content.Context
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.runBlocking

/**
 * Global singleton for accessing settings throughout the app
 * Provides convenient access to SettingsRepository
 */
object SettingsManager {
    private var repository: SettingsRepository? = null

    /**
     * Initialize SettingsManager with application context
     * Should be called once during app startup
     */
    fun initialize(context: Context) {
        repository = SettingsRepository(context)
    }

    /**
     * Get property query frequency (Hz)
     * Returns default value if not initialized
     */
    fun getPropertyQueryFrequency(): Float {
        return repository?.let {
            // Use runBlocking to get the first value synchronously
            // This is acceptable for settings access
            runBlocking {
                it.propertyQueryFrequencyFlow.first()
            }
        } ?: 0.5f // Default fallback
    }

    /**
     * Get property query frequency flow for reactive updates
     */
    fun getPropertyQueryFrequencyFlow(): Flow<Float>? {
        return repository?.propertyQueryFrequencyFlow
    }

    /**
     * Save property query frequency
     */
    suspend fun savePropertyQueryFrequency(frequencyHz: Float) {
        repository?.savePropertyQueryFrequency(frequencyHz)
    }

    /**
     * Get property query enabled state
     * Returns default value if not initialized
     */
    fun getPropertyQueryEnabled(): Boolean {
        return repository?.let {
            runBlocking {
                it.propertyQueryEnabledFlow.first()
            }
        } ?: true // Default enabled
    }

    /**
     * Get property query enabled flow for reactive updates
     */
    fun getPropertyQueryEnabledFlow(): Flow<Boolean>? {
        return repository?.propertyQueryEnabledFlow
    }

    /**
     * Save property query enabled state
     */
    suspend fun savePropertyQueryEnabled(enabled: Boolean) {
        repository?.savePropertyQueryEnabled(enabled)
    }
}
