package uk.unmannedsystems.dpm_android.camera.components

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.KeyboardArrowDown
import androidx.compose.material.icons.filled.KeyboardArrowUp
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import uk.unmannedsystems.dpm_android.ui.theme.CameraButtonBackground
import uk.unmannedsystems.dpm_android.ui.theme.CameraTextSecondary

/**
 * Exposure control component with label, value display, and increment/decrement buttons
 */
@Composable
fun ExposureControl(
    label: String,
    value: String,
    onIncrement: () -> Unit,
    onDecrement: () -> Unit,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // Label
        Text(
            text = label,
            style = MaterialTheme.typography.labelSmall,
            color = CameraTextSecondary,
            fontSize = 10.sp
        )

        Spacer(modifier = Modifier.height(4.dp))

        // Up arrow button
        Icon(
            imageVector = Icons.Default.KeyboardArrowUp,
            contentDescription = "Increase $label",
            modifier = Modifier
                .size(24.dp)
                .clickable { onIncrement() },
            tint = MaterialTheme.colorScheme.onSurface
        )

        // Value display
        Text(
            text = value,
            style = MaterialTheme.typography.headlineSmall,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.onSurface,
            fontSize = 28.sp,
            modifier = Modifier.padding(vertical = 8.dp)
        )

        // Down arrow button
        Icon(
            imageVector = Icons.Default.KeyboardArrowDown,
            contentDescription = "Decrease $label",
            modifier = Modifier
                .size(24.dp)
                .clickable { onDecrement() },
            tint = MaterialTheme.colorScheme.onSurface
        )
    }
}

/**
 * Compact exposure control with F-stop styling
 */
@Composable
fun ApertureControl(
    value: String,
    onIncrement: () -> Unit,
    onDecrement: () -> Unit,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // Label
        Text(
            text = "F",
            style = MaterialTheme.typography.labelSmall,
            color = CameraTextSecondary,
            fontSize = 14.sp,
            fontWeight = FontWeight.Bold
        )

        Spacer(modifier = Modifier.height(4.dp))

        // Up arrow button
        Icon(
            imageVector = Icons.Default.KeyboardArrowUp,
            contentDescription = "Decrease F-stop",
            modifier = Modifier
                .size(24.dp)
                .clickable { onIncrement() },
            tint = MaterialTheme.colorScheme.onSurface
        )

        // Value display
        Text(
            text = value,
            style = MaterialTheme.typography.headlineSmall,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.onSurface,
            fontSize = 28.sp,
            modifier = Modifier.padding(vertical = 8.dp)
        )

        // Down arrow button
        Icon(
            imageVector = Icons.Default.KeyboardArrowDown,
            contentDescription = "Increase F-stop",
            modifier = Modifier
                .size(24.dp)
                .clickable { onDecrement() },
            tint = MaterialTheme.colorScheme.onSurface
        )
    }
}

/**
 * Exposure compensation control with +/- indicator
 */
@Composable
fun ExposureCompensationControl(
    value: Float,
    onIncrement: () -> Unit,
    onDecrement: () -> Unit,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier
            .clip(RoundedCornerShape(8.dp))
            .background(CameraButtonBackground)
            .padding(horizontal = 12.dp, vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        // Label
        Text(
            text = "±",
            style = MaterialTheme.typography.bodyMedium,
            color = CameraTextSecondary,
            fontWeight = FontWeight.Bold
        )

        // Decrement button
        Icon(
            imageVector = Icons.Default.KeyboardArrowDown,
            contentDescription = "Decrease exposure compensation",
            modifier = Modifier
                .size(20.dp)
                .clickable { onDecrement() },
            tint = MaterialTheme.colorScheme.onSurface
        )

        // Value display
        Text(
            text = if (value >= 0) "+%.1f".format(value) else "%.1f".format(value),
            style = MaterialTheme.typography.bodyLarge,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.onSurface,
            modifier = Modifier.width(48.dp)
        )

        // Increment button
        Icon(
            imageVector = Icons.Default.KeyboardArrowUp,
            contentDescription = "Increase exposure compensation",
            modifier = Modifier
                .size(20.dp)
                .clickable { onIncrement() },
            tint = MaterialTheme.colorScheme.onSurface
        )
    }
}
