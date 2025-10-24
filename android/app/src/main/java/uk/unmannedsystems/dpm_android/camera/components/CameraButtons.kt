package uk.unmannedsystems.dpm_android.camera.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import uk.unmannedsystems.dpm_android.ui.theme.CameraAccentRed
import uk.unmannedsystems.dpm_android.ui.theme.CameraButtonBackground
import uk.unmannedsystems.dpm_android.ui.theme.CameraButtonSelected
import uk.unmannedsystems.dpm_android.ui.theme.CameraTextSecondary

/**
 * Large circular capture button
 */
@Composable
fun CaptureButton(
    onClick: () -> Unit,
    isRecording: Boolean = false,
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier
            .size(80.dp)
            .clip(CircleShape)
            .background(Color.Transparent)
            .border(4.dp, MaterialTheme.colorScheme.onSurface, CircleShape)
            .clickable { onClick() },
        contentAlignment = Alignment.Center
    ) {
        Box(
            modifier = Modifier
                .size(64.dp)
                .clip(if (isRecording) RoundedCornerShape(8.dp) else CircleShape)
                .background(if (isRecording) CameraAccentRed else MaterialTheme.colorScheme.onSurface)
        )
    }
}

/**
 * Mode selector button (M, Av, Tv, P, Auto)
 */
@Composable
fun ModeButton(
    label: String,
    isSelected: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier
            .clip(RoundedCornerShape(8.dp))
            .background(if (isSelected) CameraButtonSelected else CameraButtonBackground)
            .clickable { onClick() }
            .padding(horizontal = 16.dp, vertical = 12.dp),
        contentAlignment = Alignment.Center
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.titleMedium,
            fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal,
            color = if (isSelected) MaterialTheme.colorScheme.onSurface else CameraTextSecondary,
            fontSize = 18.sp
        )
    }
}

/**
 * Compact control button (AWB, etc.)
 */
@Composable
fun ControlButton(
    label: String,
    value: String? = null,
    isActive: Boolean = false,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier
            .clip(RoundedCornerShape(8.dp))
            .background(if (isActive) CameraButtonSelected else CameraButtonBackground)
            .clickable { onClick() }
            .padding(horizontal = 12.dp, vertical = 8.dp)
    ) {
        if (value != null) {
            Column(
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text(
                    text = label,
                    style = MaterialTheme.typography.labelSmall,
                    color = CameraTextSecondary,
                    fontSize = 10.sp
                )
                Text(
                    text = value,
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onSurface,
                    fontSize = 14.sp
                )
            }
        } else {
            Text(
                text = label,
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.Bold,
                color = if (isActive) MaterialTheme.colorScheme.onSurface else CameraTextSecondary,
                fontSize = 14.sp
            )
        }
    }
}

/**
 * Status indicator (battery, shots remaining, etc.)
 */
@Composable
fun StatusIndicator(
    icon: String,
    value: String,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier
            .clip(RoundedCornerShape(4.dp))
            .background(CameraButtonBackground)
            .padding(horizontal = 8.dp, vertical = 4.dp),
        horizontalArrangement = Arrangement.spacedBy(4.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            text = icon,
            style = MaterialTheme.typography.labelSmall,
            color = CameraTextSecondary,
            fontSize = 12.sp
        )
        Text(
            text = value,
            style = MaterialTheme.typography.labelSmall,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.onSurface,
            fontSize = 12.sp
        )
    }
}

/**
 * Mode selector row
 */
@Composable
fun ModeSelector(
    currentMode: String,
    modes: List<Pair<String, String>>, // (label, shortName)
    onModeSelected: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier,
        horizontalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        modes.forEach { (label, shortName) ->
            ModeButton(
                label = shortName,
                isSelected = currentMode == shortName,
                onClick = { onModeSelected(label) }
            )
        }
    }
}
