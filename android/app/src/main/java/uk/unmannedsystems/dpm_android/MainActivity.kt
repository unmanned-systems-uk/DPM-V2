package uk.unmannedsystems.dpm_android

import android.os.Build
import android.os.Bundle
import android.view.View
import android.view.WindowInsets
import android.view.WindowInsetsController
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.WindowInsetsControllerCompat
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CameraAlt
import androidx.compose.material.icons.filled.ChevronRight
import androidx.compose.material.icons.filled.Download
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.List
import androidx.compose.material.icons.filled.Menu
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.FloatingActionButton
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationDrawerItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.ModalNavigationDrawer
import androidx.compose.material3.DrawerValue
import androidx.compose.material3.ModalDrawerSheet
import androidx.compose.material3.rememberDrawerState
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import kotlinx.coroutines.launch
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.tooling.preview.PreviewScreenSizes
import uk.unmannedsystems.dpm_android.camera.CameraControlScreen
import uk.unmannedsystems.dpm_android.eventlog.EventLogScreen
import uk.unmannedsystems.dpm_android.settings.SettingsScreen
import uk.unmannedsystems.dpm_android.system.SystemStatusScreen
import uk.unmannedsystems.dpm_android.ui.theme.DPMAndroidTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Enable immersive fullscreen mode - hide system navigation bar
        enableImmersiveMode()

        enableEdgeToEdge()
        setContent {
            DPMAndroidTheme {
                DPMAndroidApp()
            }
        }
    }

    override fun onWindowFocusChanged(hasFocus: Boolean) {
        super.onWindowFocusChanged(hasFocus)
        // Re-enable immersive mode when user swipes to temporarily show system bars
        if (hasFocus) {
            enableImmersiveMode()
        }
    }

    private fun enableImmersiveMode() {
        // Use WindowInsetsControllerCompat for compatibility across Android versions
        val windowInsetsController = WindowCompat.getInsetsController(window, window.decorView)

        // Configure immersive mode behavior
        windowInsetsController.systemBarsBehavior =
            WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE

        // Hide both status bar and navigation bar
        windowInsetsController.hide(WindowInsetsCompat.Type.systemBars())

        // Make content draw behind system bars
        WindowCompat.setDecorFitsSystemWindows(window, false)
    }
}

@PreviewScreenSizes
@Composable
fun DPMAndroidApp() {
    var currentDestination by rememberSaveable { mutableStateOf(AppDestinations.CAMERA) }
    var showFloatingMenu by rememberSaveable { mutableStateOf(true) }
    val drawerState = rememberDrawerState(initialValue = DrawerValue.Closed)
    val scope = rememberCoroutineScope()

    ModalNavigationDrawer(
        drawerState = drawerState,
        drawerContent = {
            ModalDrawerSheet {
                Column(
                    modifier = Modifier
                        .padding(16.dp)
                        .verticalScroll(rememberScrollState())
                ) {
                    Text(
                        "DPM Android",
                        style = androidx.compose.material3.MaterialTheme.typography.headlineMedium,
                        modifier = Modifier.padding(bottom = 16.dp)
                    )
                    AppDestinations.entries.forEach { destination ->
                        NavigationDrawerItem(
                            icon = {
                                Icon(
                                    destination.icon,
                                    contentDescription = destination.label
                                )
                            },
                            label = { Text(destination.label) },
                            selected = destination == currentDestination,
                            onClick = {
                                currentDestination = destination
                                scope.launch { drawerState.close() }
                            },
                            modifier = Modifier.padding(vertical = 4.dp)
                        )
                    }
                }
            }
        }
    ) {
        Scaffold(
            modifier = Modifier.fillMaxSize()
        ) { innerPadding ->
            Box(modifier = Modifier.fillMaxSize()) {
                // Content
            when (currentDestination) {
                AppDestinations.CAMERA -> {
                    CameraControlScreen(
                        onMenuVisibilityChange = { visible -> showFloatingMenu = visible },
                        modifier = Modifier.padding(innerPadding)
                    )
                }
                AppDestinations.ADVANCED_CAMERA -> {
                    uk.unmannedsystems.dpm_android.camera.SonyRemoteControlScreen(
                        onClose = { currentDestination = AppDestinations.CAMERA },
                        modifier = Modifier.padding(innerPadding)
                    )
                }
                AppDestinations.DOWNLOADS -> {
                    PlaceholderScreen(
                        text = "Downloads\n\nContent download management will be implemented here.",
                        modifier = Modifier.padding(innerPadding)
                    )
                }
                AppDestinations.SYSTEM_STATUS -> {
                    SystemStatusScreen(
                        modifier = Modifier.padding(innerPadding)
                    )
                }
                AppDestinations.EVENT_LOG -> {
                    EventLogScreen(
                        modifier = Modifier.padding(innerPadding)
                    )
                }
                AppDestinations.SETTINGS -> {
                    SettingsScreen(
                        modifier = Modifier.padding(innerPadding)
                    )
                }
            }

                // Elegant left-side menu button
                if (showFloatingMenu) {
                    LeftMenuButton(
                        onClick = { scope.launch { drawerState.open() } },
                        modifier = Modifier
                            .align(Alignment.CenterStart)
                            .padding(start = 16.dp)
                    )
                }
            }
        }
    }
}

/**
 * Elegant left-side menu button
 * Appears as a rounded tab on the left edge of the screen
 */
@Composable
private fun LeftMenuButton(
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Surface(
        modifier = modifier
            .size(width = 40.dp, height = 60.dp)
            .clickable(onClick = onClick),
        shape = androidx.compose.foundation.shape.RoundedCornerShape(
            topEnd = 30.dp,
            bottomEnd = 30.dp
        ),
        color = Color.Black.copy(alpha = 0.6f),
        shadowElevation = 4.dp
    ) {
        Box(
            contentAlignment = Alignment.Center,
            modifier = Modifier.fillMaxSize()
        ) {
            Icon(
                imageVector = Icons.Default.ChevronRight,
                contentDescription = "Open Menu",
                tint = Color.White,
                modifier = Modifier.size(24.dp)
            )
        }
    }
}

enum class AppDestinations(
    val label: String,
    val icon: ImageVector,
) {
    CAMERA("Camera", Icons.Default.CameraAlt),
    ADVANCED_CAMERA("Advanced Camera Controls", Icons.Default.Settings),
    DOWNLOADS("Downloads", Icons.Default.Download),
    SYSTEM_STATUS("System Status", Icons.Default.Info),
    EVENT_LOG("Event Log", Icons.Default.List),
    SETTINGS("Settings", Icons.Default.Settings),
}

@Composable
fun PlaceholderScreen(text: String, modifier: Modifier = Modifier) {
    Box(
        modifier = modifier.fillMaxSize(),
        contentAlignment = Alignment.Center
    ) {
        Text(
            text = text,
            style = androidx.compose.material3.MaterialTheme.typography.bodyLarge
        )
    }
}