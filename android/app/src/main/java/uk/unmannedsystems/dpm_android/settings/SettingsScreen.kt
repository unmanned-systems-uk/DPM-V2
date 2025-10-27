package uk.unmannedsystems.dpm_android.settings

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.ui.Alignment
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.ExposedDropdownMenuBox
import androidx.compose.material3.ExposedDropdownMenuDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Slider
import androidx.compose.material3.SnackbarDuration
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import kotlinx.coroutines.launch
import uk.unmannedsystems.dpm_android.network.AspectRatioMode
import uk.unmannedsystems.dpm_android.network.ConnectionLogEntry
import uk.unmannedsystems.dpm_android.network.ConnectionState
import uk.unmannedsystems.dpm_android.network.LogLevel
import uk.unmannedsystems.dpm_android.network.NetworkSettings
import uk.unmannedsystems.dpm_android.network.NetworkStatus
import uk.unmannedsystems.dpm_android.network.VideoStreamSettings
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

@Composable
fun SettingsScreen(
    viewModel: SettingsViewModel = viewModel(),
    modifier: Modifier = Modifier
) {
    val networkStatus by viewModel.networkStatus.collectAsState()
    val currentSettings by viewModel.networkSettings.collectAsState()
    val videoSettings by viewModel.videoSettings.collectAsState()
    val propertyQueryFrequency by viewModel.propertyQueryFrequency.collectAsState()
    val propertyQueryEnabled by viewModel.propertyQueryEnabled.collectAsState()
    val autoConnectEnabled by viewModel.autoConnectEnabled.collectAsState()
    val autoReconnectEnabled by viewModel.autoReconnectEnabled.collectAsState()
    val autoReconnectInterval by viewModel.autoReconnectInterval.collectAsState()
    val snackbarHostState = remember { SnackbarHostState() }
    val coroutineScope = rememberCoroutineScope()

    Scaffold(
        snackbarHost = { SnackbarHost(snackbarHostState) },
        modifier = modifier
    ) { padding ->
        SettingsContent(
            networkStatus = networkStatus,
            currentSettings = currentSettings,
            videoSettings = videoSettings,
            propertyQueryFrequency = propertyQueryFrequency,
            propertyQueryEnabled = propertyQueryEnabled,
            autoConnectEnabled = autoConnectEnabled,
            autoReconnectEnabled = autoReconnectEnabled,
            autoReconnectInterval = autoReconnectInterval,
            onSaveSettings = { newSettings ->
                viewModel.updateSettings(newSettings)
                coroutineScope.launch {
                    snackbarHostState.showSnackbar(
                        message = "Settings saved: ${newSettings.targetIp}:${newSettings.commandPort}",
                        duration = SnackbarDuration.Short
                    )
                }
            },
            onSaveVideoSettings = { newVideoSettings ->
                viewModel.updateVideoSettings(newVideoSettings)
                coroutineScope.launch {
                    snackbarHostState.showSnackbar(
                        message = "Video settings saved",
                        duration = SnackbarDuration.Short
                    )
                }
            },
            onSavePropertyQueryFrequency = { newFrequency ->
                viewModel.updatePropertyQueryFrequency(newFrequency)
                coroutineScope.launch {
                    snackbarHostState.showSnackbar(
                        message = "Camera query frequency updated: ${newFrequency}Hz",
                        duration = SnackbarDuration.Short
                    )
                }
            },
            onSavePropertyQueryEnabled = { enabled ->
                viewModel.updatePropertyQueryEnabled(enabled)
                coroutineScope.launch {
                    snackbarHostState.showSnackbar(
                        message = if (enabled) "Property querying enabled" else "Property querying disabled",
                        duration = SnackbarDuration.Short
                    )
                }
            },
            onSaveAutoConnectEnabled = { enabled ->
                viewModel.updateAutoConnectEnabled(enabled)
                coroutineScope.launch {
                    snackbarHostState.showSnackbar(
                        message = if (enabled) "Auto-connect enabled" else "Auto-connect disabled",
                        duration = SnackbarDuration.Short
                    )
                }
            },
            onSaveAutoReconnectEnabled = { enabled ->
                viewModel.updateAutoReconnectEnabled(enabled)
                coroutineScope.launch {
                    snackbarHostState.showSnackbar(
                        message = if (enabled) "Auto-reconnect enabled" else "Auto-reconnect disabled",
                        duration = SnackbarDuration.Short
                    )
                }
            },
            onSaveAutoReconnectInterval = { interval ->
                viewModel.updateAutoReconnectInterval(interval)
                coroutineScope.launch {
                    snackbarHostState.showSnackbar(
                        message = "Auto-reconnect interval updated: ${interval}s",
                        duration = SnackbarDuration.Short
                    )
                }
            },
            onConnect = viewModel::connect,
            onDisconnect = viewModel::disconnect,
            onResetToDefaults = {
                viewModel.resetToDefaults()
                coroutineScope.launch {
                    snackbarHostState.showSnackbar(
                        message = "Reset to default settings",
                        duration = SnackbarDuration.Short
                    )
                }
            },
            modifier = Modifier.padding(padding)
        )
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun SettingsContent(
    networkStatus: NetworkStatus,
    currentSettings: NetworkSettings,
    videoSettings: VideoStreamSettings,
    propertyQueryFrequency: Float,
    propertyQueryEnabled: Boolean,
    autoConnectEnabled: Boolean,
    autoReconnectEnabled: Boolean,
    autoReconnectInterval: Int,
    onSaveSettings: (NetworkSettings) -> Unit,
    onSaveVideoSettings: (VideoStreamSettings) -> Unit,
    onSavePropertyQueryFrequency: (Float) -> Unit,
    onSavePropertyQueryEnabled: (Boolean) -> Unit,
    onSaveAutoConnectEnabled: (Boolean) -> Unit,
    onSaveAutoReconnectEnabled: (Boolean) -> Unit,
    onSaveAutoReconnectInterval: (Int) -> Unit,
    onConnect: () -> Unit,
    onDisconnect: () -> Unit,
    onResetToDefaults: () -> Unit,
    modifier: Modifier = Modifier
) {
    var targetIp by rememberSaveable { mutableStateOf(currentSettings.targetIp) }
    var commandPort by rememberSaveable { mutableStateOf(currentSettings.commandPort.toString()) }
    var statusPort by rememberSaveable { mutableStateOf(currentSettings.statusListenPort.toString()) }
    var heartbeatPort by rememberSaveable { mutableStateOf(currentSettings.heartbeatPort.toString()) }

    // Video settings state
    var videoEnabled by rememberSaveable { mutableStateOf(videoSettings.enabled) }
    var rtspUrl by rememberSaveable { mutableStateOf(videoSettings.rtspUrl) }
    var aspectRatioMode by rememberSaveable { mutableStateOf(videoSettings.aspectRatioMode) }
    var aspectRatioExpanded by remember { mutableStateOf(false) }

    // Camera settings state
    var queryFrequency by rememberSaveable { mutableStateOf(propertyQueryFrequency) }
    var queryEnabled by rememberSaveable { mutableStateOf(propertyQueryEnabled) }

    // Update text fields when currentSettings changes (e.g., when defaults are loaded)
    androidx.compose.runtime.LaunchedEffect(currentSettings) {
        targetIp = currentSettings.targetIp
        commandPort = currentSettings.commandPort.toString()
        statusPort = currentSettings.statusListenPort.toString()
        heartbeatPort = currentSettings.heartbeatPort.toString()
    }

    // Update video settings when they change
    androidx.compose.runtime.LaunchedEffect(videoSettings) {
        videoEnabled = videoSettings.enabled
        rtspUrl = videoSettings.rtspUrl
        aspectRatioMode = videoSettings.aspectRatioMode
    }

    // Update camera settings when they change
    androidx.compose.runtime.LaunchedEffect(propertyQueryFrequency) {
        queryFrequency = propertyQueryFrequency
    }

    androidx.compose.runtime.LaunchedEffect(propertyQueryEnabled) {
        queryEnabled = propertyQueryEnabled
    }

    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp)
    ) {
        Text(
            text = "Settings",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold
        )

        Spacer(modifier = Modifier.height(24.dp))

        // Connection Status Card
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(
                containerColor = when (networkStatus.state) {
                    ConnectionState.CONNECTED, ConnectionState.OPERATIONAL -> MaterialTheme.colorScheme.primaryContainer
                    ConnectionState.CONNECTING -> MaterialTheme.colorScheme.secondaryContainer
                    ConnectionState.ERROR -> MaterialTheme.colorScheme.errorContainer
                    else -> MaterialTheme.colorScheme.surfaceVariant
                }
            )
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "Connection Status",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.height(8.dp))

                Row {
                    Column(modifier = Modifier.weight(1f)) {
                        Text(
                            text = networkStatus.state.name,
                            style = MaterialTheme.typography.bodyLarge,
                            fontWeight = FontWeight.Bold
                        )

                        networkStatus.targetIp?.let { ip ->
                            Spacer(modifier = Modifier.height(4.dp))
                            Text(
                                text = "Target: $ip:${networkStatus.targetPort ?: currentSettings.commandPort}",
                                style = MaterialTheme.typography.bodyMedium,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }

                        networkStatus.errorMessage?.let { error ->
                            Spacer(modifier = Modifier.height(4.dp))
                            Text(
                                text = "Error: $error",
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.error
                            )
                        }
                    }

                    // Connection Logs on the right side
                    if (networkStatus.connectionLogs.isNotEmpty()) {
                        Spacer(modifier = Modifier.width(8.dp))
                        ConnectionLogsList(
                            logs = networkStatus.connectionLogs.takeLast(5),
                            modifier = Modifier.weight(1f)
                        )
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Connection Controls
        if (networkStatus.state == ConnectionState.DISCONNECTED || networkStatus.state == ConnectionState.ERROR) {
            Button(
                onClick = onConnect,
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("Connect to Raspberry Pi")
            }
        } else {
            Button(
                onClick = onDisconnect,
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("Disconnect")
            }
        }

        Spacer(modifier = Modifier.height(32.dp))

        // Connection Settings Section
        Text(
            text = "Connection Settings",
            style = MaterialTheme.typography.titleLarge,
            fontWeight = FontWeight.Bold
        )

        Spacer(modifier = Modifier.height(16.dp))

        // Auto-connect on startup toggle
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(
                containerColor = if (autoConnectEnabled)
                    MaterialTheme.colorScheme.primaryContainer
                else
                    MaterialTheme.colorScheme.surfaceVariant
            )
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = "Auto-Connect on Startup",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = if (autoConnectEnabled)
                            "App will connect automatically when launched"
                        else
                            "Manual connection required",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                Switch(
                    checked = autoConnectEnabled,
                    onCheckedChange = { onSaveAutoConnectEnabled(it) }
                )
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Auto-reconnect toggle
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(
                containerColor = if (autoReconnectEnabled)
                    MaterialTheme.colorScheme.primaryContainer
                else
                    MaterialTheme.colorScheme.surfaceVariant
            )
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = "Enable Auto-Reconnect",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = if (autoReconnectEnabled)
                            "Automatically reconnect if connection is lost during flight"
                        else
                            "No automatic reconnection",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                Switch(
                    checked = autoReconnectEnabled,
                    onCheckedChange = { onSaveAutoReconnectEnabled(it) }
                )
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Auto-reconnect interval
        var reconnectInterval by rememberSaveable { mutableStateOf(autoReconnectInterval.toFloat()) }

        androidx.compose.runtime.LaunchedEffect(autoReconnectInterval) {
            reconnectInterval = autoReconnectInterval.toFloat()
        }

        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.surfaceVariant
            )
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text(
                            text = "Auto-Reconnect Interval",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold
                        )
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(
                            text = "${reconnectInterval.toInt()} seconds",
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.primary
                        )
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(
                            text = "Time to wait before attempting to reconnect",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }

                Spacer(modifier = Modifier.height(12.dp))

                // Slider for interval (1s to 30s)
                Slider(
                    value = reconnectInterval,
                    onValueChange = { reconnectInterval = it },
                    valueRange = 1f..30f,
                    steps = 28,  // 1, 2, 3, ..., 30
                    onValueChangeFinished = {
                        onSaveAutoReconnectInterval(reconnectInterval.toInt())
                    },
                    modifier = Modifier.fillMaxWidth(),
                    enabled = autoReconnectEnabled
                )

                // Interval presets
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceEvenly
                ) {
                    Button(
                        onClick = {
                            reconnectInterval = 3f
                            onSaveAutoReconnectInterval(3)
                        },
                        modifier = Modifier.weight(1f).padding(end = 4.dp),
                        enabled = autoReconnectEnabled
                    ) {
                        Text("3s", style = MaterialTheme.typography.labelSmall)
                    }
                    Button(
                        onClick = {
                            reconnectInterval = 5f
                            onSaveAutoReconnectInterval(5)
                        },
                        modifier = Modifier.weight(1f).padding(horizontal = 4.dp),
                        enabled = autoReconnectEnabled
                    ) {
                        Text("5s (default)", style = MaterialTheme.typography.labelSmall)
                    }
                    Button(
                        onClick = {
                            reconnectInterval = 10f
                            onSaveAutoReconnectInterval(10)
                        },
                        modifier = Modifier.weight(1f).padding(start = 4.dp),
                        enabled = autoReconnectEnabled
                    ) {
                        Text("10s", style = MaterialTheme.typography.labelSmall)
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(32.dp))

        // Advanced Network Settings
        Text(
            text = "Advanced Network Settings",
            style = MaterialTheme.typography.titleLarge,
            fontWeight = FontWeight.Bold
        )

        Spacer(modifier = Modifier.height(16.dp))

        Text(
            text = "Network Interface: H16 internal interface",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )

        Spacer(modifier = Modifier.height(16.dp))

        // Target IP
        OutlinedTextField(
            value = targetIp,
            onValueChange = { targetIp = it },
            label = { Text("Target IP Address") },
            placeholder = { Text("192.168.144.20") },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true
        )

        Spacer(modifier = Modifier.height(12.dp))

        // Command Port (TCP)
        OutlinedTextField(
            value = commandPort,
            onValueChange = { commandPort = it },
            label = { Text("Command Port (TCP)") },
            placeholder = { Text("5000") },
            modifier = Modifier.fillMaxWidth(),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            singleLine = true
        )

        Spacer(modifier = Modifier.height(12.dp))

        // Status Listen Port (UDP)
        OutlinedTextField(
            value = statusPort,
            onValueChange = { statusPort = it },
            label = { Text("Status Listen Port (UDP)") },
            placeholder = { Text("5001") },
            modifier = Modifier.fillMaxWidth(),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            singleLine = true
        )

        Spacer(modifier = Modifier.height(12.dp))

        // Heartbeat Port (UDP)
        OutlinedTextField(
            value = heartbeatPort,
            onValueChange = { heartbeatPort = it },
            label = { Text("Heartbeat Target/Listen Port (UDP)") },
            placeholder = { Text("5002") },
            modifier = Modifier.fillMaxWidth(),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            singleLine = true
        )

        Spacer(modifier = Modifier.height(24.dp))

        // Save Settings Button
        Button(
            onClick = {
                val newSettings = NetworkSettings(
                    targetIp = targetIp,
                    commandPort = commandPort.toIntOrNull() ?: 5000,
                    statusListenPort = statusPort.toIntOrNull() ?: 5001,
                    heartbeatPort = heartbeatPort.toIntOrNull() ?: 5002
                )
                onSaveSettings(newSettings)
            },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("Save Network Settings")
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Default Settings Button
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.secondaryContainer
            )
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text(
                            text = "Default Configuration",
                            style = MaterialTheme.typography.titleSmall,
                            fontWeight = FontWeight.Bold
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(
                            text = """
                                • Target: 192.168.144.20:5000
                                • Status Listen Port: 5001
                                • Heartbeat Port: 5002
                            """.trimIndent(),
                            style = MaterialTheme.typography.bodySmall
                        )
                    }
                    Spacer(modifier = Modifier.width(16.dp))
                    Button(
                        onClick = onResetToDefaults
                    ) {
                        Text("Reset to Defaults")
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(32.dp))

        // Video Stream Settings Section
        Text(
            text = "Video Stream Settings",
            style = MaterialTheme.typography.titleLarge,
            fontWeight = FontWeight.Bold
        )

        Spacer(modifier = Modifier.height(16.dp))

        // Enable video streaming toggle
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(
                containerColor = if (videoEnabled)
                    MaterialTheme.colorScheme.primaryContainer
                else
                    MaterialTheme.colorScheme.surfaceVariant
            )
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = "Enable Video Stream",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = if (videoEnabled) "Video will display on Camera screen" else "Video disabled",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                Switch(
                    checked = videoEnabled,
                    onCheckedChange = { videoEnabled = it }
                )
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // RTSP URL
        OutlinedTextField(
            value = rtspUrl,
            onValueChange = { rtspUrl = it },
            label = { Text("RTSP URL") },
            placeholder = { Text("rtsp://192.168.1.10:8554/H264Video") },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true,
            enabled = videoEnabled
        )

        Spacer(modifier = Modifier.height(12.dp))

        // Aspect Ratio Mode Dropdown
        ExposedDropdownMenuBox(
            expanded = aspectRatioExpanded,
            onExpandedChange = { aspectRatioExpanded = !aspectRatioExpanded }
        ) {
            OutlinedTextField(
                value = aspectRatioMode.name,
                onValueChange = {},
                readOnly = true,
                label = { Text("Aspect Ratio Mode") },
                trailingIcon = {
                    ExposedDropdownMenuDefaults.TrailingIcon(expanded = aspectRatioExpanded)
                },
                modifier = Modifier
                    .fillMaxWidth()
                    .menuAnchor(),
                enabled = videoEnabled
            )

            ExposedDropdownMenu(
                expanded = aspectRatioExpanded,
                onDismissRequest = { aspectRatioExpanded = false }
            ) {
                AspectRatioMode.entries.forEach { mode ->
                    DropdownMenuItem(
                        text = {
                            Column {
                                Text(mode.name, fontWeight = FontWeight.Bold)
                                Text(
                                    text = when (mode) {
                                        AspectRatioMode.AUTO -> "Detect from stream"
                                        AspectRatioMode.FILL -> "Fill entire screen"
                                        AspectRatioMode.FIT -> "Fit maintaining aspect ratio"
                                    },
                                    style = MaterialTheme.typography.bodySmall,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant
                                )
                            }
                        },
                        onClick = {
                            aspectRatioMode = mode
                            aspectRatioExpanded = false
                        }
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        // Save Video Settings Button
        Button(
            onClick = {
                val newVideoSettings = VideoStreamSettings(
                    enabled = videoEnabled,
                    rtspUrl = rtspUrl,
                    aspectRatioMode = aspectRatioMode,
                    bufferDurationMs = videoSettings.bufferDurationMs  // Keep existing buffer setting
                )
                onSaveVideoSettings(newVideoSettings)
            },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("Save Video Settings")
        }

        Spacer(modifier = Modifier.height(32.dp))

        // Camera Settings Section
        Text(
            text = "Camera Settings",
            style = MaterialTheme.typography.titleLarge,
            fontWeight = FontWeight.Bold
        )

        Spacer(modifier = Modifier.height(16.dp))

        // Enable Property Querying Toggle
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(
                containerColor = if (queryEnabled)
                    MaterialTheme.colorScheme.primaryContainer
                else
                    MaterialTheme.colorScheme.surfaceVariant
            )
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = "Enable Property Querying",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = if (queryEnabled)
                            "Querying camera properties from Air-Side"
                        else
                            "Disabled for diagnostics",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                Switch(
                    checked = queryEnabled,
                    onCheckedChange = {
                        queryEnabled = it
                        onSavePropertyQueryEnabled(it)
                    }
                )
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Property Query Frequency
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.surfaceVariant
            )
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text(
                            text = "Property Query Frequency",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold
                        )
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(
                            text = "${String.format("%.1f", queryFrequency)} Hz (${String.format("%.0f", 1000 / queryFrequency)}ms interval)",
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.primary
                        )
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(
                            text = "How often to query camera properties (shutter, ISO, aperture)",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }

                Spacer(modifier = Modifier.height(12.dp))

                // Slider for frequency (0.1Hz to 2Hz)
                Slider(
                    value = queryFrequency,
                    onValueChange = { queryFrequency = it },
                    valueRange = 0.1f..2.0f,
                    steps = 18,  // 0.1, 0.2, ..., 2.0
                    onValueChangeFinished = {
                        onSavePropertyQueryFrequency(queryFrequency)
                    },
                    modifier = Modifier.fillMaxWidth()
                )

                // Frequency presets
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceEvenly
                ) {
                    Button(
                        onClick = {
                            queryFrequency = 0.5f
                            onSavePropertyQueryFrequency(0.5f)
                        },
                        modifier = Modifier.weight(1f).padding(end = 4.dp)
                    ) {
                        Text("0.5Hz (default)", style = MaterialTheme.typography.labelSmall)
                    }
                    Button(
                        onClick = {
                            queryFrequency = 1.0f
                            onSavePropertyQueryFrequency(1.0f)
                        },
                        modifier = Modifier.weight(1f).padding(horizontal = 4.dp)
                    ) {
                        Text("1.0Hz", style = MaterialTheme.typography.labelSmall)
                    }
                    Button(
                        onClick = {
                            queryFrequency = 2.0f
                            onSavePropertyQueryFrequency(2.0f)
                        },
                        modifier = Modifier.weight(1f).padding(start = 4.dp)
                    ) {
                        Text("2.0Hz", style = MaterialTheme.typography.labelSmall)
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Extra bottom padding to ensure all content is scrollable
        Spacer(modifier = Modifier.height(100.dp))
    }
}

@Composable
private fun ConnectionLogsList(
    logs: List<ConnectionLogEntry>,
    modifier: Modifier = Modifier
) {
    val timeFormat = remember { SimpleDateFormat("HH:mm:ss", Locale.getDefault()) }

    Column(modifier = modifier) {
        Text(
            text = "Connection Log",
            style = MaterialTheme.typography.labelSmall,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Spacer(modifier = Modifier.height(4.dp))

        logs.forEach { log ->
            val logColor = when (log.level) {
                LogLevel.INFO -> MaterialTheme.colorScheme.primary
                LogLevel.SUCCESS -> MaterialTheme.colorScheme.tertiary
                LogLevel.WARNING -> MaterialTheme.colorScheme.secondary
                LogLevel.ERROR -> MaterialTheme.colorScheme.error
            }

            Text(
                text = "${timeFormat.format(Date(log.timestamp))} ${log.message}",
                style = MaterialTheme.typography.bodySmall,
                fontFamily = FontFamily.Monospace,
                color = logColor,
                modifier = Modifier.padding(vertical = 1.dp)
            )
        }
    }
}
