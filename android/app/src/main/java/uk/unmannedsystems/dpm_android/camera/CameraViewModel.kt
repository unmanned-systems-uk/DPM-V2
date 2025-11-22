package uk.unmannedsystems.dpm_android.camera

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import timber.log.Timber
import uk.unmannedsystems.dpm_android.logging.LogContext
import uk.unmannedsystems.dpm_android.network.ConnectionState
import uk.unmannedsystems.dpm_android.network.NetworkManager
import uk.unmannedsystems.dpm_android.settings.SettingsManager

/**
 * ViewModel for managing camera state and controls
 */
class CameraViewModel : ViewModel() {
    private val _cameraState = MutableStateFlow(CameraState())
    val cameraState: StateFlow<CameraState> = _cameraState.asStateFlow()

    // Focus distance state (from camera.focus responses)
    private val _focusDistanceM = MutableStateFlow<Float?>(null)
    val focusDistanceM: StateFlow<Float?> = _focusDistanceM.asStateFlow()

    private var propertyPollingJob: Job? = null
    private var isCurrentlyOperational = false // Track operational state to prevent unnecessary restarts

    companion object {
        private const val DEFAULT_QUERY_FREQUENCY_HZ = 0.5f // 0.5Hz = every 2 seconds
    }

    init {
        // Monitor network connection status from shared NetworkManager
        viewModelScope.launch {
            NetworkManager.connectionStatus.collect { networkStatus ->
                val isConnected = networkStatus.state == ConnectionState.CONNECTED ||
                                 networkStatus.state == ConnectionState.OPERATIONAL

                _cameraState.update { state ->
                    state.copy(isConnected = isConnected)
                }

                // Only start property polling when OPERATIONAL (heartbeat received)
                // This prevents querying when connection is established but no heartbeat yet
                val isOperational = networkStatus.state == ConnectionState.OPERATIONAL

                // Only start/stop polling if the operational state actually changed
                if (isOperational != isCurrentlyOperational) {
                    isCurrentlyOperational = isOperational
                    if (isOperational) {
                        startPropertyPolling()
                    } else {
                        stopPropertyPolling()
                    }
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
                Timber.tag(LogContext.CAMERA.label).d("Auto-connect skipped - already connected/connecting (state: $currentState)")
                return@launch
            }

            // Check if NetworkManager is initialized
            if (!NetworkManager.isInitialized()) {
                Timber.tag(LogContext.CAMERA.label).w("Auto-connect skipped - NetworkManager not initialized")
                return@launch
            }

            Timber.tag(LogContext.CAMERA.label).d("Starting auto-connect to Air-Side...")
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
            WhiteBalance.SHADE -> "shade"
            WhiteBalance.CLOUDY -> "cloudy"
            WhiteBalance.TUNGSTEN -> "tungsten"
            WhiteBalance.FLUORESCENT_WARM -> "fluorescent_warm"
            WhiteBalance.FLUORESCENT_COOL -> "fluorescent_cool"
            WhiteBalance.FLUORESCENT_DAY -> "fluorescent_day"
            WhiteBalance.FLUORESCENT_DAYLIGHT -> "fluorescent_daylight"
            WhiteBalance.FLASH -> "flash"
            WhiteBalance.UNDERWATER -> "underwater"
            WhiteBalance.CUSTOM -> "custom"
            WhiteBalance.TEMPERATURE -> "temperature"
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
     * Set shutter speed directly
     */
    fun setShutterSpeed(shutterSpeed: ShutterSpeed) {
        _cameraState.update { state ->
            // Send command to air-side
            sendPropertyCommand("shutter_speed", shutterSpeedToProtocol(shutterSpeed))

            state.copy(shutterSpeed = shutterSpeed)
        }
    }

    /**
     * Set aperture directly
     */
    fun setAperture(aperture: Aperture) {
        _cameraState.update { state ->
            // Send command to air-side
            sendPropertyCommand("aperture", apertureToProtocol(aperture))

            state.copy(aperture = aperture)
        }
    }

    /**
     * Set ISO directly
     */
    fun setISO(iso: ISO) {
        _cameraState.update { state ->
            // Send command to air-side
            sendPropertyCommand("iso", isoToProtocol(iso))

            state.copy(iso = iso)
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
                Timber.tag(LogContext.CAMERA.label).d("Triggering camera capture...")
                val result = NetworkManager.getClient()?.captureImage()
                result?.fold(
                    onSuccess = { response ->
                        Timber.tag(LogContext.CAMERA.label).d("Capture successful: ${response.status} - ${response.result}")
                    },
                    onFailure = { error ->
                        Timber.tag(LogContext.CAMERA.label).e(error, "Capture failed")
                    }
                )
            } catch (e: Exception) {
                Timber.tag(LogContext.CAMERA.label).e(e, "Error sending capture command")
            }
        }
    }

    /**
     * Focus camera toward near (closer objects)
     * @param speed Focus speed: 1 (slow), 2 (medium), 3 (fast)
     */
    fun focusNear(speed: Int = 3) {
        viewModelScope.launch {
            try {
                Timber.tag(LogContext.CAMERA.label).d("Focusing NEAR at speed $speed")
                val result = NetworkManager.getClient()?.focusCamera("near", speed)
                result?.fold(
                    onSuccess = { response ->
                        Timber.tag(LogContext.CAMERA.label).d("Focus NEAR successful: ${response.result}")
                        parseFocusDistance(response.result)
                    },
                    onFailure = { error ->
                        Timber.tag(LogContext.CAMERA.label).e(error, "Focus NEAR failed")
                    }
                )
            } catch (e: Exception) {
                Timber.tag(LogContext.CAMERA.label).e(e, "Error sending focus NEAR command")
            }
        }
    }

    /**
     * Focus camera toward far (distant objects / infinity)
     * @param speed Focus speed: 1 (slow), 2 (medium), 3 (fast)
     */
    fun focusFar(speed: Int = 3) {
        viewModelScope.launch {
            try {
                Timber.tag(LogContext.CAMERA.label).d("Focusing FAR at speed $speed")
                val result = NetworkManager.getClient()?.focusCamera("far", speed)
                result?.fold(
                    onSuccess = { response ->
                        Timber.tag(LogContext.CAMERA.label).d("Focus FAR successful: ${response.result}")
                        parseFocusDistance(response.result)
                    },
                    onFailure = { error ->
                        Timber.tag(LogContext.CAMERA.label).e(error, "Focus FAR failed")
                    }
                )
            } catch (e: Exception) {
                Timber.tag(LogContext.CAMERA.label).e(e, "Error sending focus FAR command")
            }
        }
    }

    /**
     * Stop focus movement
     */
    fun focusStop() {
        viewModelScope.launch {
            try {
                Timber.tag(LogContext.CAMERA.label).d("Stopping focus")
                val result = NetworkManager.getClient()?.focusCamera("stop")
                result?.fold(
                    onSuccess = { response ->
                        Timber.tag(LogContext.CAMERA.label).d("Focus STOP successful")
                        parseFocusDistance(response.result)
                    },
                    onFailure = { error ->
                        Timber.tag(LogContext.CAMERA.label).e(error, "Focus STOP failed")
                    }
                )
            } catch (e: Exception) {
                Timber.tag(LogContext.CAMERA.label).e(e, "Error sending focus STOP command")
            }
        }
    }

    /**
     * Auto-focus hold (AF-ON button simulation)
     * @param state "press" or "release"
     */
    fun setAutoFocusHold(state: String) {
        viewModelScope.launch {
            try {
                Timber.tag(LogContext.CAMERA.label).d("Auto-focus hold: $state")
                val result = NetworkManager.getClient()?.setAutoFocusHold(state)
                result?.fold(
                    onSuccess = { response ->
                        Timber.tag(LogContext.CAMERA.label).d("Auto-focus hold $state successful")
                    },
                    onFailure = { error ->
                        Timber.tag(LogContext.CAMERA.label).e(error, "Auto-focus hold $state failed")
                    }
                )
            } catch (e: Exception) {
                Timber.tag(LogContext.CAMERA.label).e(e, "Error sending auto-focus hold command")
            }
        }
    }

    /**
     * Parse focus distance from response result
     * Updates _focusDistanceM StateFlow
     */
    private fun parseFocusDistance(result: Map<String, Any>?) {
        result?.get("focus_distance_m")?.let { distance ->
            when (distance) {
                is Number -> {
                    val distanceM = distance.toFloat()
                    _focusDistanceM.value = distanceM
                    Timber.tag(LogContext.CAMERA.label).d("Focus distance: ${distanceM}m")
                }
                "infinity" -> {
                    _focusDistanceM.value = -1f  // -1 represents infinity
                    Timber.tag(LogContext.CAMERA.label).d("Focus distance: infinity")
                }
                else -> {
                    Timber.tag(LogContext.CAMERA.label).w("Unknown focus_distance_m value: $distance")
                }
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
     * Validates property values against JSON specification before sending
     */
    private fun sendPropertyCommand(property: String, value: String) {
        viewModelScope.launch {
            try {
                // Validate property value against JSON specification
                if (!PropertyLoader.isValidValue(property, value)) {
                    Timber.tag(LogContext.CAMERA.label).e("Invalid $property value '$value' - not in specification (camera_properties.json)")
                    Timber.tag(LogContext.CAMERA.label).e("Valid values are defined in assets/camera_properties.json")
                    // TODO: Notify user via UI about invalid property value
                    return@launch
                }

                Timber.tag(LogContext.CAMERA.label).d("Setting camera property: $property = $value")
                val result = NetworkManager.getClient()?.setCameraProperty(property, value)
                result?.fold(
                    onSuccess = { response ->
                        Timber.tag(LogContext.CAMERA.label).d("Property set successfully: $property = $value")
                    },
                    onFailure = { error ->
                        Timber.tag(LogContext.CAMERA.label).e(error, "Failed to set property: $property = $value")
                    }
                )
            } catch (e: Exception) {
                Timber.tag(LogContext.CAMERA.label).e(e, "Error sending property command: $property = $value")
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
                    Timber.tag(LogContext.CAMERA.label).d("Syncing shutter speed: ${settings.shutterSpeed}")
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
                    Timber.tag(LogContext.CAMERA.label).d("Syncing aperture: ${settings.aperture}")
                    newState = newState.copy(aperture = aperture)
                }
            }

            // Sync ISO (if not empty)
            if (settings.iso.isNotEmpty()) {
                val iso = ISO.entries.find {
                    it.displayValue == settings.iso
                }
                if (iso != null && iso != state.iso) {
                    Timber.tag(LogContext.CAMERA.label).d("Syncing ISO: ${settings.iso}")
                    newState = newState.copy(iso = iso)
                }
            }

            // Sync white balance (if not empty)
            if (settings.whiteBalance.isNotEmpty()) {
                val whiteBalance = when (settings.whiteBalance) {
                    "auto" -> WhiteBalance.AUTO
                    "daylight" -> WhiteBalance.DAYLIGHT
                    "shade" -> WhiteBalance.SHADE
                    "cloudy" -> WhiteBalance.CLOUDY
                    "tungsten" -> WhiteBalance.TUNGSTEN
                    "fluorescent_warm" -> WhiteBalance.FLUORESCENT_WARM
                    "fluorescent_cool" -> WhiteBalance.FLUORESCENT_COOL
                    "fluorescent_day" -> WhiteBalance.FLUORESCENT_DAY
                    "fluorescent_daylight" -> WhiteBalance.FLUORESCENT_DAYLIGHT
                    "flash" -> WhiteBalance.FLASH
                    "underwater" -> WhiteBalance.UNDERWATER
                    "custom" -> WhiteBalance.CUSTOM
                    "temperature" -> WhiteBalance.TEMPERATURE
                    else -> null
                }
                if (whiteBalance != null && whiteBalance != state.whiteBalance) {
                    Timber.tag(LogContext.CAMERA.label).d("Syncing white balance: ${settings.whiteBalance}")
                    newState = newState.copy(whiteBalance = whiteBalance)
                }
            }

            // Sync focus mode (if not empty)
            if (settings.focusMode.isNotEmpty()) {
                val focusMode = when (settings.focusMode) {
                    "af_s" -> FocusMode.AUTO
                    "af_c" -> FocusMode.CONTINUOUS
                    "manual" -> FocusMode.MANUAL
                    else -> null
                }
                if (focusMode != null && focusMode != state.focusMode) {
                    Timber.tag(LogContext.CAMERA.label).d("Syncing focus mode: ${settings.focusMode}")
                    newState = newState.copy(focusMode = focusMode)
                }
            }

            // Sync file format (if not empty)
            if (settings.fileFormat.isNotEmpty()) {
                val fileFormat = when (settings.fileFormat) {
                    "jpeg" -> FileFormat.JPEG
                    "raw" -> FileFormat.RAW
                    "jpeg_raw" -> FileFormat.JPEG_PLUS_RAW
                    else -> null
                }
                if (fileFormat != null && fileFormat != state.fileFormat) {
                    Timber.tag(LogContext.CAMERA.label).d("Syncing file format: ${settings.fileFormat}")
                    newState = newState.copy(fileFormat = fileFormat)
                }
            }

            // Sync focal distance (if available)
            settings.focalDistanceMeters?.let { distance ->
                // Update focal distance StateFlow for FocusDistanceOverlay
                _focusDistanceM.value = distance

                // Log for debugging
                val distanceStr = when {
                    distance < 0 -> "infinity"
                    distance == 0.0f -> "unknown"
                    distance < 1.0f -> "${(distance * 100).toInt()}cm"
                    else -> String.format("%.1fm", distance)
                }
                Timber.tag(LogContext.CAMERA.label).d("Syncing focal distance: $distanceStr (raw: $distance)")
            }

            newState
        }
    }

    /**
     * Start periodic property polling from Air-Side
     * Queries all 6 Phase 1 camera properties at configured frequency:
     * shutter_speed, aperture, iso, white_balance, focus_mode, file_format
     */
    fun startPropertyPolling() {
        // Stop any existing polling
        stopPropertyPolling()

        // Check if property querying is enabled
        val isEnabled = SettingsManager.getPropertyQueryEnabled()
        if (!isEnabled) {
            Timber.tag(LogContext.CAMERA.label).d("Property polling disabled in settings")
            return
        }

        // Get query frequency from settings (default 0.5Hz = 2000ms)
        val frequencyHz = SettingsManager.getPropertyQueryFrequency() ?: DEFAULT_QUERY_FREQUENCY_HZ
        val intervalMs = (1000 / frequencyHz).toLong()

        Timber.tag(LogContext.CAMERA.label).d("Starting property polling at ${frequencyHz}Hz (every ${intervalMs}ms)")

        propertyPollingJob = viewModelScope.launch {
            while (isActive) {
                // Only query if connected and enabled
                if (_cameraState.value.isConnected && SettingsManager.getPropertyQueryEnabled()) {
                    queryAndUpdateProperties()
                }
                delay(intervalMs)
            }
        }
    }

    /**
     * Stop property polling
     */
    fun stopPropertyPolling() {
        propertyPollingJob?.cancel()
        propertyPollingJob = null
        Timber.tag(LogContext.CAMERA.label).d("Property polling stopped")
    }

    /**
     * Query camera properties from Air-Side and update state
     * Queries all 6 Phase 1 camera properties
     */
    private suspend fun queryAndUpdateProperties() {
        try {
            val properties = listOf(
                "shutter_speed",
                "aperture",
                "iso",
                "white_balance",
                "focus_mode",
                "file_format"
            )
            val result = NetworkManager.getClient()?.getCameraProperties(properties)

            result?.fold(
                onSuccess = { response ->
                    // Check if response contains an error (e.g., camera not connected)
                    response.error?.let { error ->
                        // Use the error message from the protocol
                        val errorMessage = when (error.code) {
                            5005 -> "Camera not connected"
                            else -> error.message
                        }
                        Timber.tag(LogContext.CAMERA.label).w("Camera error: $errorMessage (code: ${error.code})")

                        // Update state with error message
                        _cameraState.update { state ->
                            state.copy(cameraError = errorMessage)
                        }
                        return@fold
                    }

                    // Clear any previous error
                    _cameraState.update { state ->
                        if (state.cameraError != null) {
                            state.copy(cameraError = null)
                        } else {
                            state
                        }
                    }

                    // Parse successful response
                    response.result?.let { resultMap ->
                        Timber.tag(LogContext.CAMERA.label).d("Property query response: $resultMap")
                        parseAndUpdateProperties(resultMap)
                    }
                },
                onFailure = { error ->
                    Timber.tag(LogContext.CAMERA.label).e(error, "Property query failed")
                    _cameraState.update { state ->
                        state.copy(cameraError = "Communication error: ${error.message}")
                    }
                }
            )
        } catch (e: Exception) {
            Timber.tag(LogContext.CAMERA.label).e(e, "Error querying properties")
            _cameraState.update { state ->
                state.copy(cameraError = "Query error: ${e.message}")
            }
        }
    }

    /**
     * Parse property values from Air-Side response and update camera state
     */
    @Suppress("UNCHECKED_CAST")
    private fun parseAndUpdateProperties(resultMap: Map<String, Any>) {
        _cameraState.update { state ->
            var newState = state

            // Parse shutter speed
            (resultMap["shutter_speed"] as? String)?.let { shutterSpeedStr ->
                if (shutterSpeedStr.isNotEmpty()) {
                    val shutterSpeed = ShutterSpeed.entries.find {
                        it.displayValue == shutterSpeedStr
                    }
                    if (shutterSpeed != null && shutterSpeed != state.shutterSpeed) {
                        Timber.tag(LogContext.CAMERA.label).d("Updating shutter speed from query: $shutterSpeedStr")
                        newState = newState.copy(shutterSpeed = shutterSpeed)
                    }
                }
            }

            // Parse aperture
            (resultMap["aperture"] as? String)?.let { apertureStr ->
                if (apertureStr.isNotEmpty()) {
                    // Remove "f/" prefix if present
                    val apertureValue = apertureStr.removePrefix("f/")
                    val aperture = Aperture.entries.find {
                        it.displayValue == apertureValue
                    }
                    if (aperture != null && aperture != state.aperture) {
                        Timber.tag(LogContext.CAMERA.label).d("Updating aperture from query: $apertureStr")
                        newState = newState.copy(aperture = aperture)
                    }
                }
            }

            // Parse ISO
            (resultMap["iso"] as? String)?.let { isoStr ->
                if (isoStr.isNotEmpty()) {
                    val iso = ISO.entries.find {
                        it.displayValue == isoStr
                    }
                    if (iso != null && iso != state.iso) {
                        Timber.tag(LogContext.CAMERA.label).d("Updating ISO from query: $isoStr")
                        newState = newState.copy(iso = iso)
                    }
                }
            }

            // Parse white balance
            (resultMap["white_balance"] as? String)?.let { wbStr ->
                if (wbStr.isNotEmpty()) {
                    val whiteBalance = when (wbStr) {
                        "auto" -> WhiteBalance.AUTO
                        "daylight" -> WhiteBalance.DAYLIGHT
                        "shade" -> WhiteBalance.SHADE
                        "cloudy" -> WhiteBalance.CLOUDY
                        "tungsten" -> WhiteBalance.TUNGSTEN
                        "fluorescent_warm" -> WhiteBalance.FLUORESCENT_WARM
                        "fluorescent_cool" -> WhiteBalance.FLUORESCENT_COOL
                        "fluorescent_day" -> WhiteBalance.FLUORESCENT_DAY
                        "fluorescent_daylight" -> WhiteBalance.FLUORESCENT_DAYLIGHT
                        "flash" -> WhiteBalance.FLASH
                        "underwater" -> WhiteBalance.UNDERWATER
                        "custom" -> WhiteBalance.CUSTOM
                        "temperature" -> WhiteBalance.TEMPERATURE
                        else -> null
                    }
                    if (whiteBalance != null && whiteBalance != state.whiteBalance) {
                        Timber.tag(LogContext.CAMERA.label).d("Updating white balance from query: $wbStr")
                        newState = newState.copy(whiteBalance = whiteBalance)
                    }
                }
            }

            // Parse focus mode
            (resultMap["focus_mode"] as? String)?.let { focusStr ->
                if (focusStr.isNotEmpty()) {
                    val focusMode = when (focusStr) {
                        "af_s" -> FocusMode.AUTO
                        "af_c" -> FocusMode.CONTINUOUS
                        "manual" -> FocusMode.MANUAL
                        else -> null
                    }
                    if (focusMode != null && focusMode != state.focusMode) {
                        Timber.tag(LogContext.CAMERA.label).d("Updating focus mode from query: $focusStr")
                        newState = newState.copy(focusMode = focusMode)
                    }
                }
            }

            // Parse file format
            (resultMap["file_format"] as? String)?.let { formatStr ->
                if (formatStr.isNotEmpty()) {
                    val fileFormat = when (formatStr) {
                        "jpeg" -> FileFormat.JPEG
                        "raw" -> FileFormat.RAW
                        "jpeg_raw" -> FileFormat.JPEG_PLUS_RAW
                        else -> null
                    }
                    if (fileFormat != null && fileFormat != state.fileFormat) {
                        Timber.tag(LogContext.CAMERA.label).d("Updating file format from query: $formatStr")
                        newState = newState.copy(fileFormat = fileFormat)
                    }
                }
            }

            newState
        }
    }
}
