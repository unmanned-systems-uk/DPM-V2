package uk.unmannedsystems.dpm_android.camera

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Visibility
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableLongStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Shadow
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.geometry.Offset
import kotlinx.coroutines.delay

/**
 * Sony-style camera parameter overlay that mimics the familiar Sony camera LCD layout
 *
 * Features:
 * - Parameters positioned around screen edges (Sony LCD style)
 * - Auto-hides after 5 seconds of inactivity
 * - Small eye icon to show overlay when hidden
 * - Interactive parameters (tap to adjust)
 */
@Composable
fun SonyCameraOverlay(
    cameraState: CameraState,
    videoState: uk.unmannedsystems.dpm_android.video.VideoPlayerViewModel.VideoState,
    connectionState: uk.unmannedsystems.dpm_android.network.ConnectionState,
    onParameterClick: (String) -> Unit,
    onConnectionClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    var lastInteractionTime by remember { mutableLongStateOf(System.currentTimeMillis()) }
    var isVisible by remember { mutableStateOf(true) }

    // Callback to reset inactivity timer
    val resetTimer = { lastInteractionTime = System.currentTimeMillis() }

    // Auto-hide after 5 seconds of inactivity
    LaunchedEffect(lastInteractionTime) {
        delay(5000)
        if (System.currentTimeMillis() - lastInteractionTime >= 5000) {
            isVisible = false
        }
    }

    Box(modifier = modifier.fillMaxSize()) {
        // Connection status indicator - always visible in top right
        ConnectionStatusIcon(
            connectionState = connectionState,
            onClick = {
                resetTimer()
                onConnectionClick()
            },
            modifier = Modifier
                .align(Alignment.TopEnd)
                .padding(16.dp)
        )

        // Show overlay toggle button when hidden (below connection icon)
        if (!isVisible) {
            Surface(
                modifier = Modifier
                    .align(Alignment.TopEnd)
                    .padding(top = 72.dp, end = 16.dp)
                    .size(40.dp)
                    .clickable {
                        isVisible = true
                        resetTimer()
                    },
                shape = CircleShape,
                color = Color.Black.copy(alpha = 0.5f)
            ) {
                Icon(
                    imageVector = Icons.Default.Visibility,
                    contentDescription = "Show camera parameters",
                    tint = Color.White,
                    modifier = Modifier.padding(8.dp)
                )
            }
        }

        // Sony-style parameter overlay
        AnimatedVisibility(
            visible = isVisible,
            enter = fadeIn(animationSpec = tween(300)),
            exit = fadeOut(animationSpec = tween(300))
        ) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .pointerInput(Unit) {
                        detectTapGestures(
                            onPress = {
                                // Reset timer on any touch (down)
                                resetTimer()
                                // Wait for touch release
                                tryAwaitRelease()
                            },
                            onTap = {
                                // Also reset on tap
                                resetTimer()
                            }
                        )
                    }
            ) {
                // Top bar - Mode, shot count, quality
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .align(Alignment.TopCenter)
                        .padding(horizontal = 16.dp, vertical = 12.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    // Mode indicator (left)
                    SonyParameter(
                        text = cameraState.mode.shortName,
                        onClick = { onParameterClick("mode") },
                        onInteraction = resetTimer,
                        large = true
                    )

                    // Center info - shot count, format, quality
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        SonyParameter(
                            text = "${cameraState.remainingShots}",
                            onClick = { },
                            onInteraction = resetTimer
                        )
                        SonyParameter(
                            text = cameraState.fileFormat.displayName,
                            onClick = { onParameterClick("format") },
                            onInteraction = resetTimer
                        )
                    }

                    // Battery indicator (right)
                    SonyParameter(
                        text = "${cameraState.batteryLevel}%",
                        onClick = { },
                        onInteraction = resetTimer
                    )
                }

                // Left side - Focus mode, settings
                Column(
                    modifier = Modifier
                        .align(Alignment.CenterStart)
                        .padding(start = 16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    SonyParameter(
                        text = when (cameraState.focusMode) {
                            FocusMode.AUTO -> "AF"
                            FocusMode.MANUAL -> "MF"
                            FocusMode.CONTINUOUS -> "AFC"
                        },
                        onClick = { onParameterClick("focus") },
                        onInteraction = resetTimer
                    )
                    SonyParameter(
                        text = "MECH",
                        onClick = { onParameterClick("shutter_type") },
                        onInteraction = resetTimer
                    )
                }

                // Right side - White balance, connection status
                Column(
                    modifier = Modifier
                        .align(Alignment.CenterEnd)
                        .padding(end = 16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp),
                    horizontalAlignment = Alignment.End
                ) {
                    SonyParameter(
                        text = cameraState.whiteBalance.shortName,
                        onClick = { onParameterClick("wb") },
                        onInteraction = resetTimer
                    )

                    // Video connection indicator (Sony style)
                    val videoStatus = when (videoState) {
                        is uk.unmannedsystems.dpm_android.video.VideoPlayerViewModel.VideoState.Connected -> "VID"
                        is uk.unmannedsystems.dpm_android.video.VideoPlayerViewModel.VideoState.Connecting -> "..."
                        else -> "---"
                    }
                    SonyParameter(
                        text = videoStatus,
                        onClick = { },
                        onInteraction = resetTimer
                    )
                }

                // Bottom bar - Exposure triangle (Shutter, Aperture, ISO)
                // Transparent backgrounds so user can see live video while adjusting exposure
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .align(Alignment.BottomCenter)
                        .padding(horizontal = 16.dp, vertical = 12.dp),
                    horizontalArrangement = Arrangement.SpaceEvenly,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    // Shutter speed
                    SonyParameter(
                        text = cameraState.shutterSpeed.displayValue,
                        onClick = { onParameterClick("shutter") },
                        onInteraction = resetTimer,
                        large = true,
                        transparent = true
                    )

                    // Aperture
                    SonyParameter(
                        text = cameraState.aperture.displayValue,
                        onClick = { onParameterClick("aperture") },
                        onInteraction = resetTimer,
                        large = true,
                        transparent = true
                    )

                    // Exposure compensation
                    val expComp = cameraState.exposureCompensation
                    SonyParameter(
                        text = if (expComp >= 0) "+$expComp" else "$expComp",
                        onClick = { onParameterClick("exp_comp") },
                        onInteraction = resetTimer,
                        large = true,
                        transparent = true
                    )

                    // ISO
                    SonyParameter(
                        text = cameraState.iso.displayValue,
                        onClick = { onParameterClick("iso") },
                        onInteraction = resetTimer,
                        large = true,
                        transparent = true
                    )
                }
            }
        }
    }
}

/**
 * Individual Sony-style parameter display
 */
@Composable
private fun SonyParameter(
    text: String,
    onClick: () -> Unit,
    onInteraction: () -> Unit = {},
    large: Boolean = false,
    transparent: Boolean = false,
    modifier: Modifier = Modifier
) {
    val baseModifier = if (transparent) {
        // Transparent mode: just clickable with padding
        modifier
            .clickable {
                onInteraction()
                onClick()
            }
            .padding(horizontal = 8.dp, vertical = 4.dp)
    } else {
        // Normal mode: background, clickable, padding
        modifier
            .background(
                color = Color.Black.copy(alpha = 0.4f),
                shape = androidx.compose.foundation.shape.RoundedCornerShape(4.dp)
            )
            .clickable {
                onInteraction()
                onClick()
            }
            .padding(horizontal = 8.dp, vertical = 4.dp)
    }

    Text(
        text = text,
        color = Color.White,
        fontSize = if (large) 22.sp else 14.sp,
        fontWeight = if (large) FontWeight.Bold else FontWeight.Normal,
        textAlign = TextAlign.Center,
        style = if (transparent) {
            // Transparent mode: Text with shadow for readability over video
            TextStyle(
                shadow = Shadow(
                    color = Color.Black.copy(alpha = 0.8f),
                    offset = Offset(2f, 2f),
                    blurRadius = 4f
                )
            )
        } else {
            TextStyle.Default
        },
        modifier = baseModifier
    )
}

/**
 * Connection status icon indicator
 * Shows Air-Side connection state with colored circle
 */
@Composable
private fun ConnectionStatusIcon(
    connectionState: uk.unmannedsystems.dpm_android.network.ConnectionState,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    val (statusColor, statusText) = when (connectionState) {
        uk.unmannedsystems.dpm_android.network.ConnectionState.DISCONNECTED -> Pair(
            Color(0xFFFF0000), // Red
            "Disconnected"
        )
        uk.unmannedsystems.dpm_android.network.ConnectionState.CONNECTING -> Pair(
            Color(0xFFFFAA00), // Yellow
            "Connecting"
        )
        uk.unmannedsystems.dpm_android.network.ConnectionState.CONNECTED,
        uk.unmannedsystems.dpm_android.network.ConnectionState.OPERATIONAL -> Pair(
            Color(0xFF00FF00), // Green
            "Connected"
        )
        uk.unmannedsystems.dpm_android.network.ConnectionState.ERROR -> Pair(
            Color(0xFFFF0000), // Red
            "Error"
        )
    }

    Surface(
        modifier = modifier
            .size(40.dp)
            .clickable(onClick = onClick),
        shape = CircleShape,
        color = Color.Black.copy(alpha = 0.6f)
    ) {
        Box(
            contentAlignment = Alignment.Center,
            modifier = Modifier.fillMaxSize()
        ) {
            // Colored status circle
            Box(
                modifier = Modifier
                    .size(16.dp)
                    .background(
                        color = statusColor,
                        shape = CircleShape
                    )
            )
        }
    }
}
