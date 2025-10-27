package uk.unmannedsystems.dpm_android.camera

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Warning
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import uk.unmannedsystems.dpm_android.camera.components.ApertureControl
import uk.unmannedsystems.dpm_android.camera.components.CaptureButton
import uk.unmannedsystems.dpm_android.camera.components.ControlButton
import uk.unmannedsystems.dpm_android.camera.components.ExposureCompensationControl
import uk.unmannedsystems.dpm_android.camera.components.ExposureControl
import uk.unmannedsystems.dpm_android.camera.components.ModeSelector
import uk.unmannedsystems.dpm_android.camera.components.StatusIndicator
import uk.unmannedsystems.dpm_android.settings.SettingsViewModel
import uk.unmannedsystems.dpm_android.ui.theme.CameraTextSecondary
import uk.unmannedsystems.dpm_android.ui.theme.DPMAndroidTheme
import uk.unmannedsystems.dpm_android.video.FullScreenVideoPlayer
import uk.unmannedsystems.dpm_android.video.VideoPlayerViewModel

/**
 * Represents which setting is currently expanded
 */
enum class ExpandedSetting {
    NONE, SHUTTER, APERTURE, ISO
}

/**
 * Main camera control screen with full-screen video background
 */
@Composable
fun CameraControlScreen(
    viewModel: CameraViewModel = viewModel(),
    videoPlayerViewModel: VideoPlayerViewModel = viewModel(),
    settingsViewModel: SettingsViewModel = viewModel(),
    onMenuVisibilityChange: (Boolean) -> Unit = {},
    modifier: Modifier = Modifier
) {
    val cameraState by viewModel.cameraState.collectAsState()
    val videoSettings by settingsViewModel.videoSettings.collectAsState()
    var expandedSetting by rememberSaveable { mutableStateOf(ExpandedSetting.NONE) }
    var showAdvancedControls by rememberSaveable { mutableStateOf(false) }

    // Get connection state from NetworkManager
    val networkStatus by uk.unmannedsystems.dpm_android.network.NetworkManager.connectionStatus.collectAsState()

    // Auto-connect when screen appears
    androidx.compose.runtime.LaunchedEffect(Unit) {
        viewModel.startAutoConnect()
    }

    // Hide menu button when in advanced mode
    androidx.compose.runtime.LaunchedEffect(showAdvancedControls) {
        onMenuVisibilityChange(!showAdvancedControls)
    }

    // Show either the minimalist overlay screen or the Sony Remote advanced screen
    if (showAdvancedControls) {
        SonyRemoteControlScreen(
            viewModel = viewModel,
            videoPlayerViewModel = videoPlayerViewModel,
            settingsViewModel = settingsViewModel,
            onClose = { showAdvancedControls = false },
            modifier = modifier
        )
    } else {
        CameraControlContent(
            cameraState = cameraState,
            videoSettings = videoSettings,
            videoPlayerViewModel = videoPlayerViewModel,
            networkStatus = networkStatus,
            expandedSetting = expandedSetting,
            onExpandSetting = { expandedSetting = it },
            onIncrementShutter = viewModel::incrementShutterSpeed,
            onDecrementShutter = viewModel::decrementShutterSpeed,
            onIncrementAperture = viewModel::incrementAperture,
            onDecrementAperture = viewModel::decrementAperture,
            onIncrementISO = viewModel::incrementISO,
            onDecrementISO = viewModel::decrementISO,
            onIncrementExposureComp = { viewModel.adjustExposureCompensation(0.3f) },
            onDecrementExposureComp = { viewModel.adjustExposureCompensation(-0.3f) },
            onModeSelected = { modeName ->
                val mode = CameraMode.entries.find { it.displayName == modeName }
                mode?.let { viewModel.setMode(it) }
            },
            onWhiteBalanceClick = {
                // TODO: Show white balance selector
            },
            onFileFormatClick = {
                // TODO: Show file format selector
            },
            onCaptureClick = viewModel::captureImage,
            onMenuClick = {
                // TODO: Show settings menu
            },
            onConnectionClick = {
                if (cameraState.isConnected) {
                    viewModel.disconnect()
                } else {
                    viewModel.connect()
                }
            },
            onAdvancedControlsClick = { showAdvancedControls = true },
            modifier = modifier
        )
    }
}

@Composable
private fun CameraControlContent(
    cameraState: CameraState,
    videoSettings: uk.unmannedsystems.dpm_android.network.VideoStreamSettings,
    videoPlayerViewModel: VideoPlayerViewModel,
    networkStatus: uk.unmannedsystems.dpm_android.network.NetworkStatus,
    expandedSetting: ExpandedSetting,
    onExpandSetting: (ExpandedSetting) -> Unit,
    onIncrementShutter: () -> Unit,
    onDecrementShutter: () -> Unit,
    onIncrementAperture: () -> Unit,
    onDecrementAperture: () -> Unit,
    onIncrementISO: () -> Unit,
    onDecrementISO: () -> Unit,
    onIncrementExposureComp: () -> Unit,
    onDecrementExposureComp: () -> Unit,
    onModeSelected: (String) -> Unit,
    onWhiteBalanceClick: () -> Unit,
    onFileFormatClick: () -> Unit,
    onCaptureClick: () -> Unit,
    onMenuClick: () -> Unit,
    onConnectionClick: () -> Unit,
    onAdvancedControlsClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    val videoState by videoPlayerViewModel.videoState.collectAsState()

    Box(
        modifier = modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
    ) {
        // Full-screen video background
        FullScreenVideoPlayer(
            videoSettings = videoSettings,
            videoPlayerViewModel = videoPlayerViewModel,
            modifier = Modifier.fillMaxSize()
        )

        // Camera error banner (e.g., "Camera not connected")
        cameraState.cameraError?.let { errorMessage ->
            Card(
                modifier = Modifier
                    .align(Alignment.TopCenter)
                    .padding(top = 16.dp, start = 16.dp, end = 16.dp)
                    .fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.errorContainer
                ),
                elevation = CardDefaults.cardElevation(defaultElevation = 4.dp),
                shape = RoundedCornerShape(12.dp)
            ) {
                Row(
                    modifier = Modifier
                        .padding(16.dp)
                        .fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.Warning,
                        contentDescription = "Error",
                        tint = MaterialTheme.colorScheme.error,
                        modifier = Modifier.size(32.dp)
                    )
                    Column(modifier = Modifier.weight(1f)) {
                        Text(
                            text = errorMessage,
                            style = MaterialTheme.typography.titleMedium,
                            color = MaterialTheme.colorScheme.onErrorContainer,
                            fontWeight = FontWeight.Bold
                        )
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(
                            text = "Please check camera connectivity",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onErrorContainer.copy(alpha = 0.8f)
                        )
                    }
                }
            }
        }

        // Sony-style camera parameter overlay (auto-hides after inactivity)
        if (expandedSetting == ExpandedSetting.NONE) {
            SonyCameraOverlay(
                cameraState = cameraState,
                videoState = videoState,
                networkStatus = networkStatus,
                onParameterClick = { parameter ->
                    when (parameter) {
                        "shutter" -> onExpandSetting(ExpandedSetting.SHUTTER)
                        "aperture" -> onExpandSetting(ExpandedSetting.APERTURE)
                        "iso" -> onExpandSetting(ExpandedSetting.ISO)
                        "wb" -> onWhiteBalanceClick()
                        "format" -> onFileFormatClick()
                        "mode" -> { /* TODO: Mode selector */ }
                        "focus" -> { /* TODO: Focus mode toggle */ }
                        "shutter_type" -> { /* TODO: Shutter type */ }
                        "exp_comp" -> { /* TODO: Exposure compensation */ }
                        "advanced" -> onAdvancedControlsClick()
                    }
                },
                onConnectionClick = onConnectionClick,
                modifier = Modifier.fillMaxSize()
            )
        }

        // Expanded setting in center
        if (expandedSetting != ExpandedSetting.NONE) {
            ExpandedSettingDialog(
                cameraState = cameraState,
                expandedSetting = expandedSetting,
                onDismiss = { onExpandSetting(ExpandedSetting.NONE) },
                onIncrementShutter = onIncrementShutter,
                onDecrementShutter = onDecrementShutter,
                onIncrementAperture = onIncrementAperture,
                onDecrementAperture = onDecrementAperture,
                onIncrementISO = onIncrementISO,
                onDecrementISO = onDecrementISO,
                modifier = Modifier.align(Alignment.Center)
            )
        }

        // Capture button - always visible in bottom center
        Box(
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .padding(bottom = 32.dp)
        ) {
            CaptureButton(
                onClick = onCaptureClick,
                isRecording = cameraState.isRecording
            )
        }
    }
}

/**
 * Minimized settings display in top-left corner
 */
@Composable
private fun MinimizedSettings(
    cameraState: CameraState,
    onExpandSetting: (ExpandedSetting) -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(
            containerColor = Color.Black.copy(alpha = 0.7f)
        ),
        shape = RoundedCornerShape(8.dp)
    ) {
        Column(
            modifier = Modifier.padding(12.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            // Shutter Speed
            CompactSettingItem(
                label = cameraState.mode.shortName,
                value = cameraState.shutterSpeed.displayValue,
                onClick = { onExpandSetting(ExpandedSetting.SHUTTER) }
            )

            // Aperture
            CompactSettingItem(
                label = "f/",
                value = cameraState.aperture.displayValue,
                onClick = { onExpandSetting(ExpandedSetting.APERTURE) }
            )

            // ISO
            CompactSettingItem(
                label = "ISO",
                value = cameraState.iso.displayValue,
                onClick = { onExpandSetting(ExpandedSetting.ISO) }
            )
        }
    }
}

/**
 * Compact setting item for minimized display
 */
@Composable
private fun CompactSettingItem(
    label: String,
    value: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier
            .clip(RoundedCornerShape(4.dp))
            .clickable(onClick = onClick)
            .padding(horizontal = 8.dp, vertical = 4.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.labelSmall,
            color = Color.White.copy(alpha = 0.7f),
            fontSize = 11.sp,
            modifier = Modifier.width(36.dp)
        )
        Text(
            text = value,
            style = MaterialTheme.typography.bodyMedium,
            color = Color.White,
            fontWeight = FontWeight.Bold,
            fontSize = 16.sp
        )
    }
}

/**
 * Expanded setting dialog in center of screen - minimal and transparent
 */
@Composable
private fun ExpandedSettingDialog(
    cameraState: CameraState,
    expandedSetting: ExpandedSetting,
    onDismiss: () -> Unit,
    onIncrementShutter: () -> Unit,
    onDecrementShutter: () -> Unit,
    onIncrementAperture: () -> Unit,
    onDecrementAperture: () -> Unit,
    onIncrementISO: () -> Unit,
    onDecrementISO: () -> Unit,
    modifier: Modifier = Modifier
) {
    // Very subtle background to dismiss - can still see video
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.Black.copy(alpha = 0.15f))
            .clickable(onClick = onDismiss)
    )

    // Minimal control with subtle background
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(
            containerColor = Color.Black.copy(alpha = 0.6f)
        ),
        shape = RoundedCornerShape(16.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 0.dp)
    ) {
        Box(
            modifier = Modifier.padding(24.dp),
            contentAlignment = Alignment.Center
        ) {
            when (expandedSetting) {
                ExpandedSetting.SHUTTER -> {
                    ExposureControl(
                        label = cameraState.mode.shortName,
                        value = cameraState.shutterSpeed.displayValue,
                        onIncrement = onIncrementShutter,
                        onDecrement = onDecrementShutter
                    )
                }
                ExpandedSetting.APERTURE -> {
                    ApertureControl(
                        value = cameraState.aperture.displayValue,
                        onIncrement = onIncrementAperture,
                        onDecrement = onDecrementAperture
                    )
                }
                ExpandedSetting.ISO -> {
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Text(
                            text = "ISO",
                            style = MaterialTheme.typography.labelMedium,
                            color = Color.White.copy(alpha = 0.8f)
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        ExposureControl(
                            label = "",
                            value = cameraState.iso.displayValue,
                            onIncrement = onIncrementISO,
                            onDecrement = onDecrementISO
                        )
                    }
                }
                ExpandedSetting.NONE -> { /* Should not happen */ }
            }
        }
    }
}

/**
 * Connection status indicator with RED/GREEN circle
 * Click to connect/disconnect
 * Pulses when heartbeats are received from Air-Side
 */
@Composable
private fun ConnectionStatusIndicator(
    isConnected: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    lastHeartbeatMs: Long = 0L
) {
    // Pulse animation - triggers when lastHeartbeatMs changes
    var pulseKey by remember { mutableStateOf(0) }

    // Detect heartbeat changes and trigger pulse
    LaunchedEffect(lastHeartbeatMs) {
        if (lastHeartbeatMs > 0L && isConnected) {
            pulseKey++
        }
    }

    // Animated scale for pulse effect
    val scale by animateFloatAsState(
        targetValue = if (pulseKey % 2 == 0) 1f else 1.3f,
        animationSpec = tween(durationMillis = 200),
        label = "heartbeat_pulse"
    )

    Row(
        modifier = modifier
            .clip(RoundedCornerShape(8.dp))
            .clickable(onClick = onClick)
            .background(
                color = Color.Black.copy(alpha = 0.7f),
                shape = RoundedCornerShape(8.dp)
            )
            .padding(8.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        // Colored circle indicator with heartbeat pulse
        Box(
            modifier = Modifier
                .size(24.dp)
                .scale(scale)
                .background(
                    color = if (isConnected) Color(0xFF00FF00) else Color(0xFFFF0000),
                    shape = CircleShape
                )
                .border(
                    width = 2.dp,
                    color = Color.White.copy(alpha = 0.8f),
                    shape = CircleShape
                )
        )

        // Status text
        Column {
            Text(
                text = if (isConnected) "Air-Side Connected" else "Air-Side Disconnected",
                style = MaterialTheme.typography.labelMedium,
                color = Color.White,
                fontWeight = FontWeight.Bold
            )
            Text(
                text = if (isConnected) "Tap to disconnect" else "Tap to connect",
                style = MaterialTheme.typography.labelSmall,
                color = Color.White.copy(alpha = 0.6f),
                fontSize = 10.sp
            )
        }
    }
}

/**
 * Video connection status indicator with colored circle
 * Shows video streaming state
 */
@Composable
private fun VideoConnectionIndicator(
    videoState: VideoPlayerViewModel.VideoState,
    videoEnabled: Boolean,
    modifier: Modifier = Modifier
) {
    val (statusColor, statusText, detailText) = when {
        !videoEnabled -> Triple(
            Color(0xFF888888), // Gray
            "Video Disabled",
            "Enable in Settings"
        )
        videoState is VideoPlayerViewModel.VideoState.Disconnected -> Triple(
            Color(0xFFFF0000), // Red
            "Video Disconnected",
            "Waiting for stream"
        )
        videoState is VideoPlayerViewModel.VideoState.Connecting -> Triple(
            Color(0xFFFFAA00), // Yellow
            "Video Connecting",
            "Buffering..."
        )
        videoState is VideoPlayerViewModel.VideoState.Connected -> Triple(
            Color(0xFF00FF00), // Green
            "Video Connected",
            videoState.resolution
        )
        videoState is VideoPlayerViewModel.VideoState.Error -> Triple(
            Color(0xFFFF0000), // Red
            "Video Error",
            videoState.message.take(30)
        )
        else -> Triple(
            Color(0xFF888888),
            "Unknown",
            ""
        )
    }

    Row(
        modifier = modifier
            .clip(RoundedCornerShape(8.dp))
            .background(
                color = Color.Black.copy(alpha = 0.7f),
                shape = RoundedCornerShape(8.dp)
            )
            .padding(8.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        // Colored circle indicator
        Box(
            modifier = Modifier
                .size(24.dp)
                .background(
                    color = statusColor,
                    shape = CircleShape
                )
                .border(
                    width = 2.dp,
                    color = Color.White.copy(alpha = 0.8f),
                    shape = CircleShape
                )
        )

        // Status text
        Column {
            Text(
                text = statusText,
                style = MaterialTheme.typography.labelMedium,
                color = Color.White,
                fontWeight = FontWeight.Bold
            )
            Text(
                text = detailText,
                style = MaterialTheme.typography.labelSmall,
                color = Color.White.copy(alpha = 0.6f),
                fontSize = 10.sp
            )
        }
    }
}

@Preview(showBackground = true, widthDp = 800, heightDp = 480)
@Composable
fun CameraControlScreenPreview() {
    DPMAndroidTheme {
        Surface {
            CameraControlScreen()
        }
    }
}
