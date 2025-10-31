package uk.unmannedsystems.dpm_android.camera

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlin.math.ln
import kotlin.math.min

/**
 * Focus Distance Overlay
 * Displays current camera focus distance as a progress bar with text
 *
 * @param focalDistanceM Current focal distance in meters
 *   - Positive number (e.g., 5.5) = distance in meters
 *   - -1f = infinity (∞)
 *   - null = no data / not available
 */
@Composable
fun FocusDistanceOverlay(
    focalDistanceM: Float?,
    modifier: Modifier = Modifier
) {
    // Only show overlay if we have data
    focalDistanceM?.let { distance ->
        Box(
            modifier = modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp, vertical = 8.dp)
        ) {
            Surface(
                color = Color.Black.copy(alpha = 0.6f),
                shape = RoundedCornerShape(12.dp),
                shadowElevation = 4.dp
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(12.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    // Distance text display
                    Text(
                        text = formatDistance(distance),
                        color = Color.White,
                        fontSize = 20.sp,
                        fontWeight = FontWeight.Bold
                    )

                    Spacer(modifier = Modifier.height(8.dp))

                    // Progress bar visualization
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(12.dp)
                    ) {
                        // Background track (gray)
                        LinearProgressIndicator(
                            progress = 1.0f,
                            modifier = Modifier.fillMaxSize(),
                            color = Color.Gray.copy(alpha = 0.3f),
                            trackColor = Color.Transparent
                        )

                        // Foreground indicator (cyan)
                        LinearProgressIndicator(
                            progress = calculateFocusPosition(distance),
                            modifier = Modifier.fillMaxSize(),
                            color = Color.Cyan,
                            trackColor = Color.Transparent
                        )
                    }

                    Spacer(modifier = Modifier.height(4.dp))

                    // Scale markers
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        ScaleMarker("0.5m")
                        ScaleMarker("1m")
                        ScaleMarker("5m")
                        ScaleMarker("10m")
                        ScaleMarker("∞")
                    }
                }
            }
        }
    }
}

/**
 * Format distance for display
 */
private fun formatDistance(distance: Float): String {
    return when {
        distance < 0 -> "∞"  // Infinity
        distance < 1.0f -> "${(distance * 100).toInt()}cm"  // Less than 1m, show in cm
        else -> String.format("%.1fm", distance)  // 1m or more, show in meters
    }
}

/**
 * Calculate progress bar position (0.0 to 1.0) based on focus distance
 * Uses logarithmic scale for better visualization across range
 *
 * Scale:
 * - 0-1m: 0-30% of bar (macro/close-up range)
 * - 1-10m: 30-70% of bar (portrait/landscape)
 * - 10m-∞: 70-100% of bar (distant/infinity)
 */
private fun calculateFocusPosition(distance: Float): Float {
    if (distance < 0) return 1.0f  // Infinity = 100%

    return when {
        distance < 1.0f -> {
            // 0-1m range: linear mapping to 0-30%
            (distance / 1.0f) * 0.3f
        }
        distance < 10.0f -> {
            // 1-10m range: logarithmic mapping to 30-70%
            val normalized = (ln(distance) - ln(1.0f)) / (ln(10.0f) - ln(1.0f))
            0.3f + (normalized.toFloat() * 0.4f)
        }
        else -> {
            // 10m+ range: asymptotic approach to 100%
            val normalized = (ln(distance) - ln(10.0f)) / (ln(50.0f) - ln(10.0f))
            0.7f + min(normalized.toFloat() * 0.3f, 0.3f)
        }
    }
}

/**
 * Scale marker text
 */
@Composable
private fun ScaleMarker(text: String) {
    Text(
        text = text,
        color = Color.White.copy(alpha = 0.6f),
        fontSize = 10.sp
    )
}
