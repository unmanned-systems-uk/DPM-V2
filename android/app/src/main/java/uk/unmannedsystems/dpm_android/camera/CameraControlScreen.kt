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
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
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
import uk.unmannedsystems.dpm_android.ui.theme.CameraTextSecondary
import uk.unmannedsystems.dpm_android.ui.theme.DPMAndroidTheme

/**
 * Represents which setting is currently expanded
 */
enum class ExpandedSetting {
    NONE, SHUTTER, APERTURE, ISO
}

/**
 * Main camera control screen
 */
@Composable
fun CameraControlScreen(
    viewModel: CameraViewModel = viewModel(),
    modifier: Modifier = Modifier
) {
    val cameraState by viewModel.cameraState.collectAsState()
    var expandedSetting by rememberSaveable { mutableStateOf(ExpandedSetting.NONE) }

    CameraControlContent(
        cameraState = cameraState,
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
        modifier = modifier
    )
}

@Composable
private fun CameraControlContent(
    cameraState: CameraState,
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
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
    ) {
        // Camera preview area (placeholder)
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(Color(0xFF1A1A1A)),
            contentAlignment = Alignment.Center
        ) {
            Text(
                text = "Camera Live View",
                style = MaterialTheme.typography.headlineLarge,
                color = Color.Gray
            )
        }

        // Connection status indicator - top-left corner
        ConnectionStatusIndicator(
            isConnected = cameraState.isConnected,
            modifier = Modifier
                .align(Alignment.TopStart)
                .padding(16.dp)
        )

        // Minimized settings below connection indicator
        if (expandedSetting == ExpandedSetting.NONE) {
            MinimizedSettings(
                cameraState = cameraState,
                onExpandSetting = onExpandSetting,
                modifier = Modifier
                    .align(Alignment.TopStart)
                    .padding(start = 16.dp, top = 80.dp, end = 16.dp)
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

        // Bottom controls
        Row(
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Left side - Quick controls
            Row(
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                ControlButton(
                    label = cameraState.whiteBalance.shortName,
                    onClick = onWhiteBalanceClick
                )
                ControlButton(
                    label = cameraState.fileFormat.displayName,
                    onClick = onFileFormatClick
                )
            }

            // Center - Capture button
            CaptureButton(
                onClick = onCaptureClick,
                isRecording = cameraState.isRecording
            )

            // Right side - Mode and status
            Row(
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Status indicators (removed connection status - now in top-left)
                StatusIndicator(
                    icon = "🔋",
                    value = "${cameraState.batteryLevel}%"
                )
                StatusIndicator(
                    icon = "📷",
                    value = cameraState.remainingShots.toString()
                )
            }
        }

        // Top-right status (mode indicator)
        Text(
            text = cameraState.mode.shortName,
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold,
            color = Color.White,
            modifier = Modifier
                .align(Alignment.TopEnd)
                .padding(16.dp)
        )
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
 * Expanded setting dialog in center of screen
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
    // Semi-transparent background to dismiss
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.Black.copy(alpha = 0.5f))
            .clickable(onClick = onDismiss)
    )

    // Setting control card
    Card(
        modifier = modifier.size(400.dp, 300.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 8.dp)
    ) {
        Box(
            modifier = Modifier.fillMaxSize(),
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
                            color = CameraTextSecondary
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
 */
@Composable
private fun ConnectionStatusIndicator(
    isConnected: Boolean,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier,
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        // Colored circle indicator
        Box(
            modifier = Modifier
                .size(24.dp)
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
        Text(
            text = if (isConnected) "Air-Side Connected" else "Air-Side Disconnected",
            style = MaterialTheme.typography.labelMedium,
            color = Color.White,
            fontWeight = FontWeight.Bold,
            modifier = Modifier
                .background(
                    color = Color.Black.copy(alpha = 0.7f),
                    shape = RoundedCornerShape(4.dp)
                )
                .padding(horizontal = 8.dp, vertical = 4.dp)
        )
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
