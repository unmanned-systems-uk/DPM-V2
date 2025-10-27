package uk.unmannedsystems.dpm_android.camera

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.expandVertically
import androidx.compose.animation.shrinkVertically
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowDropDown
import androidx.compose.material.icons.filled.Camera
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.FiberManualRecord
import androidx.compose.material.icons.filled.MoreVert
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.rotate
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import uk.unmannedsystems.dpm_android.camera.components.CaptureButton
import uk.unmannedsystems.dpm_android.settings.SettingsViewModel
import uk.unmannedsystems.dpm_android.video.FullScreenVideoPlayer
import uk.unmannedsystems.dpm_android.video.VideoPlayerViewModel

/**
 * Sony Remote-style control screen with comprehensive parameter access
 * Mimics the Sony Remote Camera Control app interface
 */
@Composable
fun SonyRemoteControlScreen(
    viewModel: CameraViewModel = viewModel(),
    videoPlayerViewModel: VideoPlayerViewModel = viewModel(),
    settingsViewModel: SettingsViewModel = viewModel(),
    onClose: () -> Unit,
    modifier: Modifier = Modifier
) {
    val cameraState by viewModel.cameraState.collectAsState()
    val videoSettings by settingsViewModel.videoSettings.collectAsState()
    val networkStatus by uk.unmannedsystems.dpm_android.network.NetworkManager.connectionStatus.collectAsState()
    val videoState by videoPlayerViewModel.videoState.collectAsState()

    Row(
        modifier = modifier
            .fillMaxSize()
            .background(Color.Black)
    ) {
        // Video feed on the left
        Box(
            modifier = Modifier
                .weight(1f)
                .fillMaxHeight()
        ) {
            FullScreenVideoPlayer(
                videoSettings = videoSettings,
                videoPlayerViewModel = videoPlayerViewModel,
                modifier = Modifier.fillMaxSize()
            )

            // Close button overlay on video
            IconButton(
                onClick = onClose,
                modifier = Modifier
                    .align(Alignment.TopStart)
                    .padding(16.dp)
                    .background(Color.Black.copy(alpha = 0.6f), shape = CircleShape)
            ) {
                Icon(
                    imageVector = Icons.Default.Close,
                    contentDescription = "Close advanced controls",
                    tint = Color.White
                )
            }
        }

        // Control sidebar on the right
        SonyRemoteSidebar(
            cameraState = cameraState,
            networkStatus = networkStatus,
            onCapture = viewModel::captureImage,
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
            modifier = Modifier
                .width(320.dp)
                .fillMaxHeight()
        )
    }
}

/**
 * Sidebar with collapsible sections matching Sony Remote interface
 */
@Composable
private fun SonyRemoteSidebar(
    cameraState: CameraState,
    networkStatus: uk.unmannedsystems.dpm_android.network.NetworkStatus,
    onCapture: () -> Unit,
    onIncrementShutter: () -> Unit,
    onDecrementShutter: () -> Unit,
    onIncrementAperture: () -> Unit,
    onDecrementAperture: () -> Unit,
    onIncrementISO: () -> Unit,
    onDecrementISO: () -> Unit,
    onIncrementExposureComp: () -> Unit,
    onDecrementExposureComp: () -> Unit,
    onModeSelected: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .background(Color(0xFF1C1C1C))
            .verticalScroll(rememberScrollState())
    ) {
        // Shooting section
        CollapsibleSection(
            title = "Shooting",
            initiallyExpanded = true
        ) {
            ShootingSection(onCapture = onCapture)
        }

        // Main Settings (Exposure Triangle)
        CollapsibleSection(
            title = "Main Settings",
            initiallyExpanded = true
        ) {
            MainSettingsSection(
                cameraState = cameraState,
                onIncrementShutter = onIncrementShutter,
                onDecrementShutter = onDecrementShutter,
                onIncrementAperture = onIncrementAperture,
                onDecrementAperture = onDecrementAperture,
                onIncrementISO = onIncrementISO,
                onDecrementISO = onDecrementISO,
                onIncrementExposureComp = onIncrementExposureComp,
                onDecrementExposureComp = onDecrementExposureComp
            )
        }

        // Sub Settings
        CollapsibleSection(
            title = "Sub Settings",
            initiallyExpanded = false
        ) {
            SubSettingsSection(cameraState = cameraState)
        }

        // Focus section
        CollapsibleSection(
            title = "Focus",
            initiallyExpanded = false
        ) {
            FocusSection(cameraState = cameraState)
        }

        Spacer(modifier = Modifier.height(16.dp))
    }
}

/**
 * Collapsible section header with expand/collapse animation
 */
@Composable
private fun CollapsibleSection(
    title: String,
    initiallyExpanded: Boolean = false,
    content: @Composable () -> Unit
) {
    var expanded by rememberSaveable { mutableStateOf(initiallyExpanded) }

    Column {
        // Section header
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .clickable { expanded = !expanded }
                .background(Color(0xFF2A2A2A))
                .padding(horizontal = 12.dp, vertical = 10.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = title,
                color = Color.White,
                fontSize = 14.sp,
                fontWeight = FontWeight.Medium
            )
            Row(
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    imageVector = Icons.Default.ArrowDropDown,
                    contentDescription = if (expanded) "Collapse" else "Expand",
                    tint = Color.White,
                    modifier = Modifier
                        .size(20.dp)
                        .rotate(if (expanded) 0f else -90f)
                )
                Icon(
                    imageVector = Icons.Default.MoreVert,
                    contentDescription = "More options",
                    tint = Color.White,
                    modifier = Modifier.size(16.dp)
                )
            }
        }

        // Section content
        AnimatedVisibility(
            visible = expanded,
            enter = expandVertically(),
            exit = shrinkVertically()
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(Color(0xFF1C1C1C))
                    .padding(12.dp)
            ) {
                content()
            }
        }
    }
}

/**
 * Shooting section - AF, Capture, Record, Settings buttons
 */
@Composable
private fun ShootingSection(onCapture: () -> Unit) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Column(
            verticalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            Text(
                text = "AEL",
                color = Color.White.copy(alpha = 0.5f),
                fontSize = 10.sp
            )
            Text(
                text = "FEL",
                color = Color.White.copy(alpha = 0.5f),
                fontSize = 10.sp
            )
            Text(
                text = "AWBL",
                color = Color.White.copy(alpha = 0.5f),
                fontSize = 10.sp
            )
        }

        Row(
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            // AF Button
            CircularControlButton(
                text = "AF",
                enabled = true,
                onClick = { /* TODO: AF trigger */ }
            )

            // Capture button
            CircularControlButton(
                icon = Icons.Default.Camera,
                enabled = true,
                onClick = onCapture
            )

            // Record button
            CircularControlButton(
                icon = Icons.Default.FiberManualRecord,
                enabled = true,
                onClick = { /* TODO: Video record */ },
                tint = Color.Red
            )

            // Settings button
            CircularControlButton(
                icon = Icons.Default.MoreVert,
                enabled = true,
                onClick = { /* TODO: More settings */ }
            )
        }
    }
}

/**
 * Circular control button matching Sony style
 */
@Composable
private fun CircularControlButton(
    text: String? = null,
    icon: ImageVector? = null,
    enabled: Boolean,
    onClick: () -> Unit,
    tint: Color = Color.White,
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier
            .size(48.dp)
            .border(
                width = 2.dp,
                color = if (enabled) tint else Color.Gray,
                shape = CircleShape
            )
            .clickable(enabled = enabled, onClick = onClick)
            .padding(4.dp),
        contentAlignment = Alignment.Center
    ) {
        if (text != null) {
            Text(
                text = text,
                color = if (enabled) tint else Color.Gray,
                fontSize = 12.sp,
                fontWeight = FontWeight.Bold
            )
        } else if (icon != null) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = if (enabled) tint else Color.Gray,
                modifier = Modifier.size(24.dp)
            )
        }
    }
}

/**
 * Mode selection section
 */
@Composable
private fun ModeSection(
    currentMode: CameraMode,
    onModeSelected: (String) -> Unit
) {
    Column(
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        CameraMode.entries.forEach { mode ->
            SonyRadioButton(
                text = mode.displayName,
                selected = mode == currentMode,
                onClick = { onModeSelected(mode.displayName) }
            )
        }
    }
}

/**
 * Sony-style radio button
 */
@Composable
private fun SonyRadioButton(
    text: String,
    selected: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier
            .fillMaxWidth()
            .clickable(onClick = onClick)
            .padding(vertical = 4.dp),
        horizontalArrangement = Arrangement.spacedBy(12.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        // Radio circle
        Box(
            modifier = Modifier
                .size(16.dp)
                .border(
                    width = 2.dp,
                    color = if (selected) Color(0xFFFF5722) else Color.Gray,
                    shape = CircleShape
                ),
            contentAlignment = Alignment.Center
        ) {
            if (selected) {
                Box(
                    modifier = Modifier
                        .size(8.dp)
                        .background(Color(0xFFFF5722), CircleShape)
                )
            }
        }

        Text(
            text = text,
            color = if (selected) Color.White else Color.Gray,
            fontSize = 14.sp
        )
    }
}

/**
 * Main Settings section - Exposure triangle controls
 */
@Composable
private fun MainSettingsSection(
    cameraState: CameraState,
    onIncrementShutter: () -> Unit,
    onDecrementShutter: () -> Unit,
    onIncrementAperture: () -> Unit,
    onDecrementAperture: () -> Unit,
    onIncrementISO: () -> Unit,
    onDecrementISO: () -> Unit,
    onIncrementExposureComp: () -> Unit,
    onDecrementExposureComp: () -> Unit
) {
    Column(
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // Row 1: Shutter, Aperture
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Shutter Speed
            SonyParameterControl(
                label = "Shutter Speed",
                value = cameraState.shutterSpeed.displayValue,
                onIncrement = onIncrementShutter,
                onDecrement = onDecrementShutter,
                highlighted = true
            )

            // Aperture
            SonyParameterControl(
                label = "F",
                value = cameraState.aperture.displayValue,
                onIncrement = onIncrementAperture,
                onDecrement = onDecrementAperture
            )
        }

        // Row 2: ISO, EV, Flash
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            // ISO
            SonyParameterControl(
                label = "ISO",
                value = cameraState.iso.displayValue,
                onIncrement = onIncrementISO,
                onDecrement = onDecrementISO
            )

            // Exposure Compensation
            val expComp = cameraState.exposureCompensation
            SonyParameterControl(
                label = "EV",
                value = if (expComp >= 0) "+$expComp" else "$expComp",
                onIncrement = onIncrementExposureComp,
                onDecrement = onDecrementExposureComp
            )

            // Flash
            SonyParameterControl(
                label = "Flash",
                value = "±0.0",
                onIncrement = { /* TODO */ },
                onDecrement = { /* TODO */ }
            )
        }
    }
}

/**
 * Sony-style parameter control with increment/decrement buttons
 */
@Composable
private fun SonyParameterControl(
    label: String,
    value: String,
    onIncrement: () -> Unit,
    onDecrement: () -> Unit,
    highlighted: Boolean = false,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier,
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(4.dp)
    ) {
        // Label
        Text(
            text = label,
            color = Color.White.copy(alpha = 0.6f),
            fontSize = 10.sp
        )

        // Value with background
        Box(
            modifier = Modifier
                .background(
                    color = if (highlighted) Color(0xFFFF5722) else Color(0xFF3A3A3A),
                    shape = RoundedCornerShape(4.dp)
                )
                .padding(horizontal = 12.dp, vertical = 8.dp),
            contentAlignment = Alignment.Center
        ) {
            Text(
                text = value,
                color = Color.White,
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold,
                textAlign = TextAlign.Center
            )
        }

        // Increment/Decrement buttons
        Row(
            horizontalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            SmallArrowButton(
                direction = "down",
                onClick = onDecrement
            )
            SmallArrowButton(
                direction = "up",
                onClick = onIncrement
            )
        }
    }
}

/**
 * Small arrow button for parameter adjustment
 */
@Composable
private fun SmallArrowButton(
    direction: String,
    onClick: () -> Unit
) {
    Box(
        modifier = Modifier
            .size(24.dp)
            .background(Color(0xFF3A3A3A), RoundedCornerShape(4.dp))
            .clickable(onClick = onClick),
        contentAlignment = Alignment.Center
    ) {
        Text(
            text = if (direction == "up") "▲" else "▼",
            color = Color.White,
            fontSize = 10.sp
        )
    }
}

/**
 * Sub Settings section - Format, Type, Quality, Size
 */
@Composable
private fun SubSettingsSection(cameraState: CameraState) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        // Format
        SubSettingItem(
            label = "Format",
            value = cameraState.fileFormat.displayName
        )

        // Type
        SubSettingItem(
            label = "Type",
            value = "RAW"
        )

        // Quality
        SubSettingItem(
            label = "Quality",
            value = "X.FINE"
        )

        // Size
        SubSettingItem(
            label = "Size",
            value = "L"
        )
    }

    Spacer(modifier = Modifier.height(12.dp))

    // Additional settings row
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceEvenly
    ) {
        SubSettingSmall("16:9")
        SubSettingSmall("AWB")
        SubSettingSmall("DRO\nAUTO")
        SubSettingSmall("")
        SubSettingSmall("")
    }
}

/**
 * Sub setting item display
 */
@Composable
private fun SubSettingItem(
    label: String,
    value: String
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(4.dp)
    ) {
        Text(
            text = label,
            color = Color.White.copy(alpha = 0.6f),
            fontSize = 10.sp
        )
        Text(
            text = value,
            color = Color.White,
            fontSize = 14.sp,
            fontWeight = FontWeight.Bold
        )
    }
}

/**
 * Small sub setting display
 */
@Composable
private fun SubSettingSmall(text: String) {
    Box(
        modifier = Modifier
            .size(48.dp)
            .border(1.dp, Color.Gray, RoundedCornerShape(4.dp))
            .padding(4.dp),
        contentAlignment = Alignment.Center
    ) {
        Text(
            text = text,
            color = Color.White,
            fontSize = 10.sp,
            textAlign = TextAlign.Center,
            lineHeight = 12.sp
        )
    }
}

/**
 * Focus section - Manual focus controls
 */
@Composable
private fun FocusSection(cameraState: CameraState) {
    Column(
        modifier = Modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        // Focus mode display
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = when (cameraState.focusMode) {
                    FocusMode.AUTO -> "MF"
                    FocusMode.MANUAL -> "MF"
                    FocusMode.CONTINUOUS -> "AFC"
                },
                color = Color.White,
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold
            )
            Text(
                text = "AF",
                color = Color.White.copy(alpha = 0.6f),
                fontSize = 12.sp
            )
        }

        // Focus control buttons
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            FocusButton("≤", onClick = { /* Far */ })
            FocusButton("«", onClick = { /* Medium far */ })
            FocusButton("<", onClick = { /* Near */ })
            FocusButton(">", onClick = { /* Near */ })
            FocusButton("»", onClick = { /* Medium near */ })
            FocusButton("≥", onClick = { /* Near */ })
        }
    }
}

/**
 * Focus adjustment button
 */
@Composable
private fun FocusButton(
    symbol: String,
    onClick: () -> Unit
) {
    Box(
        modifier = Modifier
            .size(40.dp)
            .background(Color(0xFF3A3A3A), RoundedCornerShape(4.dp))
            .clickable(onClick = onClick),
        contentAlignment = Alignment.Center
    ) {
        Text(
            text = symbol,
            color = Color.White,
            fontSize = 16.sp,
            fontWeight = FontWeight.Bold
        )
    }
}
