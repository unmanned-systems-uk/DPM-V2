package uk.unmannedsystems.dpm_android.ui.theme

import android.app.Activity
import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.dynamicDarkColorScheme
import androidx.compose.material3.dynamicLightColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.platform.LocalContext

// Professional camera UI color scheme - always dark
private val CameraColorScheme = darkColorScheme(
    primary = CameraAccentBlue,
    secondary = CameraAccentOrange,
    tertiary = CameraAccentGreen,
    background = CameraBlack,
    surface = CameraDarkGray,
    surfaceVariant = CameraMediumGray,
    onPrimary = CameraTextPrimary,
    onSecondary = CameraTextPrimary,
    onTertiary = CameraTextPrimary,
    onBackground = CameraTextPrimary,
    onSurface = CameraTextPrimary,
    error = CameraAccentRed,
    onError = CameraTextPrimary
)

@Composable
fun DPMAndroidTheme(
    // Professional camera app - always use dark theme
    darkTheme: Boolean = true,
    content: @Composable () -> Unit
) {
    // Always use the camera color scheme for consistent professional look
    val colorScheme = CameraColorScheme

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}