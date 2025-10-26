package uk.unmannedsystems.dpm_android.camera

import android.util.Log
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import uk.unmannedsystems.dpm_android.network.ConnectionState
import uk.unmannedsystems.dpm_android.network.NetworkManager

/**
 * ViewModel for managing camera state and controls
 */
class CameraViewModel : ViewModel() {
    private val _cameraState = MutableStateFlow(CameraState())
    val cameraState: StateFlow<CameraState> = _cameraState.asStateFlow()

    companion object {
        private const val TAG = "CameraViewModel"
    }

    init {
        // Monitor network connection status from shared NetworkManager
        viewModelScope.launch {
            NetworkManager.connectionStatus.collect { networkStatus ->
                _cameraState.update { state ->
                    state.copy(
                        isConnected = networkStatus.state == ConnectionState.CONNECTED ||
                                     networkStatus.state == ConnectionState.OPERATIONAL
                    )
                }
            }
        }

        // Monitor camera status for settings synchronization
        viewModelScope.launch {
            NetworkManager.cameraStatus.collect { cameraStatus ->
                cameraStatus?.let { status ->
                    // Sync battery level and remaining shots
                    _cameraState.update { state ->
                        state.copy(
                            batteryLevel = status.batteryPercent,
                            remainingShots = status.remainingShots ?: state.remainingShots
                        )
                    }

                    // Sync camera settings if available
                    status.settings?.let { settings ->
                        syncCameraSettings(settings)
                    }
                }
            }
        }
    }

    /**
     * Start auto-connect to Air-Side
     * Should be called when the camera screen appears
     */
    fun startAutoConnect() {
        viewModelScope.launch {
            // Check if already connected or connecting
            val currentState = NetworkManager.connectionStatus.value.state
            if (currentState == ConnectionState.CONNECTED ||
                currentState == ConnectionState.OPERATIONAL ||
                currentState == ConnectionState.CONNECTING) {
                Log.d(TAG, "Auto-connect skipped - already connected/connecting (state: $currentState)")
                return@launch
            }

            // Check if NetworkManager is initialized
            if (!NetworkManager.isInitialized()) {
                Log.w(TAG, "Auto-connect skipped - NetworkManager not initialized")
                return@launch
            }

            Log.d(TAG, "Starting auto-connect to Air-Side...")
            NetworkManager.connect()
        }
    }

    // ========== Protocol Conversion Helpers ==========

    /**
     * Convert ShutterSpeed enum to protocol value (e.g., "1/8000")
     */
    private fun shutterSpeedToProtocol(shutter: ShutterSpeed): String {
        return shutter.displayValue
    }

    /**
     * Convert Aperture enum to protocol value (e.g., "f/2.8")
     */
    private fun apertureToProtocol(aperture: Aperture): String {
        return "f/${aperture.displayValue}"
    }

    /**
     * Convert ISO enum to protocol value (e.g., "800")
     */
    private fun isoToProtocol(iso: ISO): String {
        return iso.displayValue
    }

    /**
     * Convert WhiteBalance enum to protocol value (e.g., "daylight")
     */
    private fun whiteBalanceToProtocol(wb: WhiteBalance): String {
        return when (wb) {
            WhiteBalance.AUTO -> "auto"
            WhiteBalance.DAYLIGHT -> "daylight"
            WhiteBalance.CLOUDY -> "cloudy"
            WhiteBalance.TUNGSTEN -> "tungsten"
            WhiteBalance.FLUORESCENT -> "fluorescent_warm"
            WhiteBalance.FLASH -> "flash"
            WhiteBalance.CUSTOM -> "custom"
        }
    }

    /**
     * Convert FocusMode enum to protocol value (e.g., "af_s")
     */
    private fun focusModeToProtocol(mode: FocusMode): String {
        return when (mode) {
            FocusMode.AUTO -> "af_s"
            FocusMode.CONTINUOUS -> "af_c"
            FocusMode.MANUAL -> "manual"
        }
    }

    /**
     * Convert FileFormat enum to protocol value (e.g., "jpeg")
     */
    private fun fileFormatToProtocol(format: FileFormat): String {
        return when (format) {
            FileFormat.JPEG -> "jpeg"
            FileFormat.RAW -> "raw"
            FileFormat.JPEG_PLUS_RAW -> "jpeg_raw"
        }
    }

    // ========== Property Setters (Send Commands) ==========

    /**
     * Increment shutter speed (faster)
     */
    fun incrementShutterSpeed() {
        _cameraState.update { state ->
            val currentOrdinal = state.shutterSpeed.ordinal
            val newOrdinal = (currentOrdinal - 1).coerceAtLeast(0)
            val newShutterSpeed = ShutterSpeed.fromOrdinal(newOrdinal)

            // Send command to air-side
            sendPropertyCommand("shutter_speed", shutterSpeedToProtocol(newShutterSpeed))

            state.copy(shutterSpeed = newShutterSpeed)
        }
    }

    /**
     * Decrement shutter speed (slower)
     */
    fun decrementShutterSpeed() {
        _cameraState.update { state ->
            val currentOrdinal = state.shutterSpeed.ordinal
            val newOrdinal = (currentOrdinal + 1).coerceAtMost(ShutterSpeed.entries.size - 1)
            val newShutterSpeed = ShutterSpeed.fromOrdinal(newOrdinal)

            // Send command to air-side
            sendPropertyCommand("shutter_speed", shutterSpeedToProtocol(newShutterSpeed))

            state.copy(shutterSpeed = newShutterSpeed)
        }
    }

    /**
     * Increment aperture (smaller f-number, wider aperture)
     */
    fun incrementAperture() {
        _cameraState.update { state ->
            val currentOrdinal = state.aperture.ordinal
            val newOrdinal = (currentOrdinal - 1).coerceAtLeast(0)
            val newAperture = Aperture.fromOrdinal(newOrdinal)

            // Send command to air-side
            sendPropertyCommand("aperture", apertureToProtocol(newAperture))

            state.copy(aperture = newAperture)
        }
    }

    /**
     * Decrement aperture (larger f-number, narrower aperture)
     */
    fun decrementAperture() {
        _cameraState.update { state ->
            val currentOrdinal = state.aperture.ordinal
            val newOrdinal = (currentOrdinal + 1).coerceAtMost(Aperture.entries.size - 1)
            val newAperture = Aperture.fromOrdinal(newOrdinal)

            // Send command to air-side
            sendPropertyCommand("aperture", apertureToProtocol(newAperture))

            state.copy(aperture = newAperture)
        }
    }

    /**
     * Increment ISO (more sensitive)
     */
    fun incrementISO() {
        _cameraState.update { state ->
            val currentOrdinal = state.iso.ordinal
            val newOrdinal = (currentOrdinal + 1).coerceAtMost(ISO.entries.size - 1)
            val newISO = ISO.fromOrdinal(newOrdinal)

            // Send command to air-side
            sendPropertyCommand("iso", isoToProtocol(newISO))

            state.copy(iso = newISO)
        }
    }

    /**
     * Decrement ISO (less sensitive)
     */
    fun decrementISO() {
        _cameraState.update { state ->
            val currentOrdinal = state.iso.ordinal
            val newOrdinal = (currentOrdinal - 1).coerceAtLeast(0)
            val newISO = ISO.fromOrdinal(newOrdinal)

            // Send command to air-side
            sendPropertyCommand("iso", isoToProtocol(newISO))

            state.copy(iso = newISO)
        }
    }

    /**
     * Set camera mode
     */
    fun setMode(mode: CameraMode) {
        _cameraState.update { it.copy(mode = mode) }
    }

    /**
     * Adjust exposure compensation
     */
    fun adjustExposureCompensation(delta: Float) {
        _cameraState.update { state ->
            val newValue = (state.exposureCompensation + delta).coerceIn(-3.0f, 3.0f)
            state.copy(exposureCompensation = newValue)
        }
    }

    /**
     * Set white balance mode
     */
    fun setWhiteBalance(whiteBalance: WhiteBalance) {
        _cameraState.update {
            // Send command to air-side
            sendPropertyCommand("white_balance", whiteBalanceToProtocol(whiteBalance))

            it.copy(whiteBalance = whiteBalance)
        }
    }

    /**
     * Set file format
     */
    fun setFileFormat(format: FileFormat) {
        _cameraState.update {
            // Send command to air-side
            sendPropertyCommand("file_format", fileFormatToProtocol(format))

            it.copy(fileFormat = format)
        }
    }

    /**
     * Set focus mode
     */
    fun setFocusMode(mode: FocusMode) {
        _cameraState.update {
            // Send command to air-side
            sendPropertyCommand("focus_mode", focusModeToProtocol(mode))

            it.copy(focusMode = mode)
        }
    }

    /**
     * Toggle recording
     */
    fun toggleRecording() {
        _cameraState.update { it.copy(isRecording = !it.isRecording) }
    }

    // ========== Camera Commands ==========

    /**
     * Capture still image
     */
    fun captureImage() {
        viewModelScope.launch {
            try {
                Log.d(TAG, "Triggering camera capture...")
                val result = NetworkManager.getClient()?.captureImage()
                result?.fold(
                    onSuccess = { response ->
                        Log.d(TAG, "Capture successful: ${response.status} - ${response.result}")
                    },
                    onFailure = { error ->
                        Log.e(TAG, "Capture failed", error)
                    }
                )
            } catch (e: Exception) {
                Log.e(TAG, "Error sending capture command", e)
            }
        }
    }

    /**
     * Connect to Air-Side
     */
    fun connect() {
        NetworkManager.connect()
    }

    /**
     * Disconnect from Air-Side
     */
    fun disconnect() {
        NetworkManager.disconnect()
    }

    // ========== Helper Functions ==========

    /**
     * Send property command to air-side
     */
    private fun sendPropertyCommand(property: String, value: String) {
        viewModelScope.launch {
            try {
                Log.d(TAG, "Setting camera property: $property = $value")
                val result = NetworkManager.getClient()?.setCameraProperty(property, value)
                result?.fold(
                    onSuccess = { response ->
                        Log.d(TAG, "Property set successfully: $property = $value")
                    },
                    onFailure = { error ->
                        Log.e(TAG, "Failed to set property: $property = $value", error)
                    }
                )
            } catch (e: Exception) {
                Log.e(TAG, "Error sending property command: $property = $value", e)
            }
        }
    }

    /**
     * Synchronize camera settings from Air Side status broadcasts
     * Updates UI to match actual camera state
     */
    private fun syncCameraSettings(settings: uk.unmannedsystems.dpm_android.network.SimpleCameraSettings) {
        _cameraState.update { state ->
            var newState = state

            // Sync shutter speed (if not empty)
            if (settings.shutterSpeed.isNotEmpty()) {
                val shutterSpeed = ShutterSpeed.entries.find {
                    it.displayValue == settings.shutterSpeed
                }
                if (shutterSpeed != null && shutterSpeed != state.shutterSpeed) {
                    Log.d(TAG, "Syncing shutter speed: ${settings.shutterSpeed}")
                    newState = newState.copy(shutterSpeed = shutterSpeed)
                }
            }

            // Sync aperture (if not empty)
            if (settings.aperture.isNotEmpty()) {
                // Remove "f/" prefix if present
                val apertureValue = settings.aperture.removePrefix("f/")
                val aperture = Aperture.entries.find {
                    it.displayValue == apertureValue
                }
                if (aperture != null && aperture != state.aperture) {
                    Log.d(TAG, "Syncing aperture: ${settings.aperture}")
                    newState = newState.copy(aperture = aperture)
                }
            }

            // Sync ISO (if not empty)
            if (settings.iso.isNotEmpty()) {
                val iso = ISO.entries.find {
                    it.displayValue == settings.iso
                }
                if (iso != null && iso != state.iso) {
                    Log.d(TAG, "Syncing ISO: ${settings.iso}")
                    newState = newState.copy(iso = iso)
                }
            }

            // TODO: Sync white balance when Air Side implements it
            // TODO: Sync focus mode when Air Side implements it
            // TODO: Sync file format when Air Side implements it

            newState
        }
    }
}
