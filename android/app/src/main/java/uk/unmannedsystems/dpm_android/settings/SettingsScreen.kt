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
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarDuration
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
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
import uk.unmannedsystems.dpm_android.network.ConnectionLogEntry
import uk.unmannedsystems.dpm_android.network.ConnectionState
import uk.unmannedsystems.dpm_android.network.LogLevel
import uk.unmannedsystems.dpm_android.network.NetworkSettings
import uk.unmannedsystems.dpm_android.network.NetworkStatus
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
    val snackbarHostState = remember { SnackbarHostState() }
    val coroutineScope = rememberCoroutineScope()

    Scaffold(
        snackbarHost = { SnackbarHost(snackbarHostState) },
        modifier = modifier
    ) { padding ->
        SettingsContent(
            networkStatus = networkStatus,
            currentSettings = currentSettings,
            onSaveSettings = { newSettings ->
                viewModel.updateSettings(newSettings)
                coroutineScope.launch {
                    snackbarHostState.showSnackbar(
                        message = "Settings saved: ${newSettings.targetIp}:${newSettings.commandPort}",
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

@Composable
private fun SettingsContent(
    networkStatus: NetworkStatus,
    currentSettings: NetworkSettings,
    onSaveSettings: (NetworkSettings) -> Unit,
    onConnect: () -> Unit,
    onDisconnect: () -> Unit,
    onResetToDefaults: () -> Unit,
    modifier: Modifier = Modifier
) {
    var targetIp by rememberSaveable { mutableStateOf(currentSettings.targetIp) }
    var commandPort by rememberSaveable { mutableStateOf(currentSettings.commandPort.toString()) }
    var statusPort by rememberSaveable { mutableStateOf(currentSettings.statusListenPort.toString()) }
    var heartbeatPort by rememberSaveable { mutableStateOf(currentSettings.heartbeatPort.toString()) }

    // Update text fields when currentSettings changes (e.g., when defaults are loaded)
    androidx.compose.runtime.LaunchedEffect(currentSettings) {
        targetIp = currentSettings.targetIp
        commandPort = currentSettings.commandPort.toString()
        statusPort = currentSettings.statusListenPort.toString()
        heartbeatPort = currentSettings.heartbeatPort.toString()
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

        Spacer(modifier = Modifier.height(16.dp))
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
