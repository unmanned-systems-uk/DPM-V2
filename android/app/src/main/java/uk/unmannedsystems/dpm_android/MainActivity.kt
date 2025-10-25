package uk.unmannedsystems.dpm_android

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CameraAlt
import androidx.compose.material.icons.filled.Download
import androidx.compose.material.icons.filled.List
import androidx.compose.material.icons.filled.Menu
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.FloatingActionButton
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationDrawerItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.ModalNavigationDrawer
import androidx.compose.material3.DrawerValue
import androidx.compose.material3.ModalDrawerSheet
import androidx.compose.material3.rememberDrawerState
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
import uk.unmannedsystems.dpm_android.ui.theme.DPMAndroidTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            DPMAndroidTheme {
                DPMAndroidApp()
            }
        }
    }
}

@PreviewScreenSizes
@Composable
fun DPMAndroidApp() {
    var currentDestination by rememberSaveable { mutableStateOf(AppDestinations.CAMERA) }
    val drawerState = rememberDrawerState(initialValue = DrawerValue.Closed)
    val scope = rememberCoroutineScope()

    ModalNavigationDrawer(
        drawerState = drawerState,
        drawerContent = {
            ModalDrawerSheet {
                Column(
                    modifier = Modifier.padding(16.dp)
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
            modifier = Modifier.fillMaxSize(),
            floatingActionButton = {
                FloatingActionButton(
                    onClick = { scope.launch { drawerState.open() } }
                ) {
                    Icon(Icons.Default.Menu, contentDescription = "Menu")
                }
            }
        ) { innerPadding ->
            when (currentDestination) {
                AppDestinations.CAMERA -> {
                    CameraControlScreen(
                        modifier = Modifier.padding(innerPadding)
                    )
                }
                AppDestinations.DOWNLOADS -> {
                    PlaceholderScreen(
                        text = "Downloads\n\nContent download management will be implemented here.",
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
        }
    }
}

enum class AppDestinations(
    val label: String,
    val icon: ImageVector,
) {
    CAMERA("Camera", Icons.Default.CameraAlt),
    DOWNLOADS("Downloads", Icons.Default.Download),
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