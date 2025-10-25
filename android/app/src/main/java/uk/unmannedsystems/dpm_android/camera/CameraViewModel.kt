package uk.unmannedsystems.dpm_android.camera

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import uk.unmannedsystems.dpm_android.network.ConnectionState
import uk.unmannedsystems.dpm_android.network.NetworkClient
import uk.unmannedsystems.dpm_android.network.NetworkSettings

/**
 * ViewModel for managing camera state and controls
 */
class CameraViewModel : ViewModel() {
    private val _cameraState = MutableStateFlow(CameraState())
    val cameraState: StateFlow<CameraState> = _cameraState.asStateFlow()

    // Network client for monitoring connection status
    private val networkClient = NetworkClient(NetworkSettings())

    init {
        // Monitor network connection status
        viewModelScope.launch {
            networkClient.connectionStatus.collect { networkStatus ->
                _cameraState.update { state ->
                    state.copy(
                        isConnected = networkStatus.state == ConnectionState.CONNECTED ||
                                     networkStatus.state == ConnectionState.OPERATIONAL
                    )
                }
            }
        }
    }

    /**
     * Increment shutter speed (faster)
     */
    fun incrementShutterSpeed() {
        _cameraState.update { state ->
            val currentOrdinal = state.shutterSpeed.ordinal
            val newOrdinal = (currentOrdinal - 1).coerceAtLeast(0)
            state.copy(shutterSpeed = ShutterSpeed.fromOrdinal(newOrdinal))
        }
    }

    /**
     * Decrement shutter speed (slower)
     */
    fun decrementShutterSpeed() {
        _cameraState.update { state ->
            val currentOrdinal = state.shutterSpeed.ordinal
            val newOrdinal = (currentOrdinal + 1).coerceAtMost(ShutterSpeed.entries.size - 1)
            state.copy(shutterSpeed = ShutterSpeed.fromOrdinal(newOrdinal))
        }
    }

    /**
     * Increment aperture (smaller f-number, wider aperture)
     */
    fun incrementAperture() {
        _cameraState.update { state ->
            val currentOrdinal = state.aperture.ordinal
            val newOrdinal = (currentOrdinal - 1).coerceAtLeast(0)
            state.copy(aperture = Aperture.fromOrdinal(newOrdinal))
        }
    }

    /**
     * Decrement aperture (larger f-number, narrower aperture)
     */
    fun decrementAperture() {
        _cameraState.update { state ->
            val currentOrdinal = state.aperture.ordinal
            val newOrdinal = (currentOrdinal + 1).coerceAtMost(Aperture.entries.size - 1)
            state.copy(aperture = Aperture.fromOrdinal(newOrdinal))
        }
    }

    /**
     * Increment ISO (more sensitive)
     */
    fun incrementISO() {
        _cameraState.update { state ->
            val currentOrdinal = state.iso.ordinal
            val newOrdinal = (currentOrdinal + 1).coerceAtMost(ISO.entries.size - 1)
            state.copy(iso = ISO.fromOrdinal(newOrdinal))
        }
    }

    /**
     * Decrement ISO (less sensitive)
     */
    fun decrementISO() {
        _cameraState.update { state ->
            val currentOrdinal = state.iso.ordinal
            val newOrdinal = (currentOrdinal - 1).coerceAtLeast(0)
            state.copy(iso = ISO.fromOrdinal(newOrdinal))
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
        _cameraState.update { it.copy(whiteBalance = whiteBalance) }
    }

    /**
     * Toggle recording
     */
    fun toggleRecording() {
        _cameraState.update { it.copy(isRecording = !it.isRecording) }
    }

    /**
     * Capture still image
     */
    fun captureImage() {
        // TODO: Send capture command to Pi
        // For now, just simulate
    }

    /**
     * Connect to Air-Side
     */
    fun connect() {
        networkClient.connect()
    }

    /**
     * Disconnect from Air-Side
     */
    fun disconnect() {
        networkClient.disconnect()
    }

    /**
     * Set file format
     */
    fun setFileFormat(format: FileFormat) {
        _cameraState.update { it.copy(fileFormat = format) }
    }

    /**
     * Set focus mode
     */
    fun setFocusMode(mode: FocusMode) {
        _cameraState.update { it.copy(focusMode = mode) }
    }

    override fun onCleared() {
        super.onCleared()
        networkClient.close()
    }
}
