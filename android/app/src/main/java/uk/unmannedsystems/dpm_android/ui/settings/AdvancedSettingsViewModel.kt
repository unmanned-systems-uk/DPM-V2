package uk.unmannedsystems.dpm_android.ui.settings

import android.util.Log
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.google.gson.Gson
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import uk.unmannedsystems.dpm_android.model.*
import uk.unmannedsystems.dpm_android.network.NetworkManager

/**
 * ViewModel for Advanced Settings UI
 *
 * Manages Air-Side configuration synchronization via get_config/update_config commands
 * Part of Issue #73 - Phase 1: Foundation Infrastructure (Gap 3)
 *
 * Features:
 * - Configuration fetching from Air-Side
 * - Configuration validation
 * - Configuration updates to Air-Side
 * - Export/import configuration to/from JSON files
 * - Reset to defaults
 * - Change tracking
 */
class AdvancedSettingsViewModel : ViewModel() {

    companion object {
        private const val TAG = "AdvancedSettingsVM"
    }

    private val gson = Gson()

    // UI State
    private val _uiState = MutableStateFlow(AdvancedSettingsUiState())
    val uiState: StateFlow<AdvancedSettingsUiState> = _uiState.asStateFlow()

    init {
        Log.i(TAG, "AdvancedSettingsViewModel initialized")
        observeConnectionStatus()
    }

    /**
     * Observe network connection status
     */
    private fun observeConnectionStatus() {
        viewModelScope.launch {
            NetworkManager.connectionStatus.collect { status ->
                val isConnected = status.state == uk.unmannedsystems.dpm_android.network.ConnectionState.OPERATIONAL
                _uiState.update { it.copy(isConnectedToAirSide = isConnected) }

                if (isConnected && _uiState.value.config == null) {
                    // Auto-fetch config when connected
                    fetchConfig()
                }
            }
        }
    }

    /**
     * Fetch configuration from Air-Side
     */
    fun fetchConfig() {
        Log.i(TAG, "Fetching configuration from Air-Side")
        _uiState.update { it.copy(isLoading = true, error = null) }

        viewModelScope.launch {
            try {
                // Send get_config command to Air-Side
                val result = NetworkManager.sendCommand("get_config", emptyMap())

                result.fold(
                    onSuccess = { response ->
                        val resultMap = response.result
                        if (resultMap?.containsKey("config") == true) {
                            // Parse config from response
                            val configJson = gson.toJson(resultMap["config"])
                            val config = gson.fromJson(configJson, AirSideConfig::class.java)

                            _uiState.update {
                                it.copy(
                                    config = config,
                                    originalConfig = config,
                                    isLoading = false,
                                    hasUnsavedChanges = false,
                                    error = null
                                )
                            }
                            Log.i(TAG, "Configuration fetched successfully")
                        } else {
                            throw Exception("Invalid response: missing 'config' field")
                        }
                    },
                    onFailure = { error ->
                        throw error
                    }
                )

            } catch (e: Exception) {
                Log.e(TAG, "Failed to fetch configuration: ${e.message}", e)
                _uiState.update {
                    it.copy(
                        isLoading = false,
                        error = "Failed to fetch config: ${e.message}"
                    )
                }
            }
        }
    }

    /**
     * Update network configuration
     */
    fun updateNetworkConfig(network: NetworkConfig) {
        _uiState.update {
            val newConfig = it.config?.copy(network = network)
            it.copy(
                config = newConfig,
                hasUnsavedChanges = newConfig != it.originalConfig
            )
        }
    }

    /**
     * Update timing configuration
     */
    fun updateTimingConfig(timing: TimingConfig) {
        _uiState.update {
            val newConfig = it.config?.copy(timing = timing)
            it.copy(
                config = newConfig,
                hasUnsavedChanges = newConfig != it.originalConfig
            )
        }
    }

    /**
     * Update logging configuration
     */
    fun updateLoggingConfig(logging: LoggingConfig) {
        _uiState.update {
            val newConfig = it.config?.copy(logging = logging)
            it.copy(
                config = newConfig,
                hasUnsavedChanges = newConfig != it.originalConfig
            )
        }
    }

    /**
     * Update health configuration
     */
    fun updateHealthConfig(health: HealthConfig) {
        _uiState.update {
            val newConfig = it.config?.copy(health = health)
            it.copy(
                config = newConfig,
                hasUnsavedChanges = newConfig != it.originalConfig
            )
        }
    }

    /**
     * Save configuration to Air-Side
     */
    fun saveConfig() {
        val config = _uiState.value.config ?: run {
            Log.w(TAG, "No configuration to save")
            return
        }

        // Validate configuration
        val validationResult = config.validate()
        if (!validationResult.isValid) {
            Log.w(TAG, "Configuration validation failed: ${validationResult.errorMessage}")
            _uiState.update {
                it.copy(
                    error = "Validation failed:\n${validationResult.errorMessage}",
                    validationErrors = validationResult.errors
                )
            }
            return
        }

        Log.i(TAG, "Saving configuration to Air-Side")
        _uiState.update { it.copy(isSaving = true, error = null, validationErrors = emptyList()) }

        viewModelScope.launch {
            try {
                // Convert config to map for command payload
                val configJson = gson.toJson(config)
                val configMap = gson.fromJson(configJson, Map::class.java) as Map<String, Any>

                // Send update_config command to Air-Side
                val result = NetworkManager.sendCommand("update_config", mapOf("config" to configMap))

                result.fold(
                    onSuccess = { response ->
                        if (response.status == "success") {
                            _uiState.update {
                                it.copy(
                                    originalConfig = config,
                                    isSaving = false,
                                    hasUnsavedChanges = false,
                                    error = null,
                                    successMessage = "Configuration saved successfully"
                                )
                            }
                            Log.i(TAG, "Configuration saved successfully")

                            // Check if restart is required
                            if (requiresRestart(config)) {
                                _uiState.update {
                                    it.copy(
                                        successMessage = "Configuration saved. Air-Side restart required for changes to take effect."
                                    )
                                }
                            }
                        } else {
                            throw Exception("Save failed: ${response.error?.message ?: "Unknown error"}")
                        }
                    },
                    onFailure = { error ->
                        throw error
                    }
                )

            } catch (e: Exception) {
                Log.e(TAG, "Failed to save configuration: ${e.message}", e)
                _uiState.update {
                    it.copy(
                        isSaving = false,
                        error = "Failed to save config: ${e.message}"
                    )
                }
            }
        }
    }

    /**
     * Reset configuration to defaults
     */
    fun resetToDefaults() {
        Log.i(TAG, "Resetting configuration to defaults")
        val defaultConfig = AirSideConfig.createDefault()
        _uiState.update {
            it.copy(
                config = defaultConfig,
                hasUnsavedChanges = defaultConfig != it.originalConfig,
                error = null
            )
        }
    }

    /**
     * Discard unsaved changes
     */
    fun discardChanges() {
        Log.i(TAG, "Discarding unsaved changes")
        _uiState.update {
            it.copy(
                config = it.originalConfig,
                hasUnsavedChanges = false,
                error = null,
                validationErrors = emptyList()
            )
        }
    }

    /**
     * Export configuration to JSON string
     */
    fun exportConfig(): String {
        val config = _uiState.value.config ?: AirSideConfig.createDefault()
        return gson.toJson(config)
    }

    /**
     * Import configuration from JSON string
     */
    fun importConfig(json: String): Boolean {
        return try {
            val config = gson.fromJson(json, AirSideConfig::class.java)
            val validationResult = config.validate()

            if (validationResult.isValid) {
                _uiState.update {
                    it.copy(
                        config = config,
                        hasUnsavedChanges = config != it.originalConfig,
                        error = null,
                        validationErrors = emptyList()
                    )
                }
                Log.i(TAG, "Configuration imported successfully")
                true
            } else {
                Log.w(TAG, "Imported configuration is invalid: ${validationResult.errorMessage}")
                _uiState.update {
                    it.copy(
                        error = "Invalid configuration:\n${validationResult.errorMessage}",
                        validationErrors = validationResult.errors
                    )
                }
                false
            }

        } catch (e: Exception) {
            Log.e(TAG, "Failed to import configuration: ${e.message}", e)
            _uiState.update {
                it.copy(error = "Failed to import config: ${e.message}")
            }
            false
        }
    }

    /**
     * Clear success message
     */
    fun clearSuccessMessage() {
        _uiState.update { it.copy(successMessage = null) }
    }

    /**
     * Clear error message
     */
    fun clearError() {
        _uiState.update { it.copy(error = null, validationErrors = emptyList()) }
    }

    /**
     * Check if configuration changes require Air-Side restart
     */
    private fun requiresRestart(newConfig: AirSideConfig): Boolean {
        val original = _uiState.value.originalConfig ?: return false

        // Network changes require restart
        if (newConfig.network != original.network) return true

        // Timing changes require restart
        if (newConfig.timing != original.timing) return true

        // Some logging changes require restart
        if (newConfig.logging.logLevel != original.logging.logLevel) return true
        if (newConfig.logging.fileLoggingEnabled != original.logging.fileLoggingEnabled) return true

        return false
    }
}

/**
 * UI State for Advanced Settings
 */
data class AdvancedSettingsUiState(
    val config: AirSideConfig? = null,
    val originalConfig: AirSideConfig? = null,
    val isConnectedToAirSide: Boolean = false,
    val isLoading: Boolean = false,
    val isSaving: Boolean = false,
    val hasUnsavedChanges: Boolean = false,
    val error: String? = null,
    val successMessage: String? = null,
    val validationErrors: List<String> = emptyList()
) {
    /**
     * Check if config is loaded
     */
    val hasConfig: Boolean
        get() = config != null

    /**
     * Get display config or default
     */
    val displayConfig: AirSideConfig
        get() = config ?: AirSideConfig.createDefault()
}
