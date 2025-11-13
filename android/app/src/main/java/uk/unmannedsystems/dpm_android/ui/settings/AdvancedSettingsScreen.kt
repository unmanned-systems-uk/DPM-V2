package uk.unmannedsystems.dpm_android.ui.settings

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import uk.unmannedsystems.dpm_android.model.*

/**
 * Advanced Settings Screen
 *
 * Allows viewing and editing Air-Side configuration
 * Part of Issue #73 - Phase 1: Foundation Infrastructure (Gap 3)
 *
 * Features:
 * - Network settings (ports, IP)
 * - Timing settings (intervals, timeouts)
 * - Logging settings (level, file size, network logging)
 * - Health monitoring settings (broadcast interval, history duration)
 * - Input validation with error messages
 * - Save/Discard/Reset functionality
 * - Export/Import configuration
 * - Restart required indicators
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AdvancedSettingsScreen(
    modifier: Modifier = Modifier,
    viewModel: AdvancedSettingsViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsState()

    // Show snackbar for success/error messages
    val snackbarHostState = remember { SnackbarHostState() }

    LaunchedEffect(uiState.successMessage) {
        uiState.successMessage?.let { message ->
            snackbarHostState.showSnackbar(
                message = message,
                duration = SnackbarDuration.Short
            )
            viewModel.clearSuccessMessage()
        }
    }

    LaunchedEffect(uiState.error) {
        uiState.error?.let { message ->
            snackbarHostState.showSnackbar(
                message = message,
                duration = SnackbarDuration.Long
            )
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Advanced Settings") },
                actions = {
                    // Connection status
                    if (uiState.isConnectedToAirSide) {
                        Icon(
                            imageVector = Icons.Default.CheckCircle,
                            contentDescription = "Connected",
                            tint = Color(0xFF10B981),
                            modifier = Modifier.padding(end = 8.dp)
                        )
                    } else {
                        Icon(
                            imageVector = Icons.Default.Error,
                            contentDescription = "Disconnected",
                            tint = Color(0xFFDC2626),
                            modifier = Modifier.padding(end = 8.dp)
                        )
                    }

                    // Refresh button
                    IconButton(
                        onClick = { viewModel.fetchConfig() },
                        enabled = uiState.isConnectedToAirSide && !uiState.isLoading
                    ) {
                        Icon(
                            imageVector = Icons.Default.Refresh,
                            contentDescription = "Fetch config"
                        )
                    }

                    // Export button
                    IconButton(
                        onClick = { /* TODO: Export to file */ },
                        enabled = uiState.hasConfig
                    ) {
                        Icon(
                            imageVector = Icons.Default.FileDownload,
                            contentDescription = "Export config"
                        )
                    }

                    // Import button
                    IconButton(
                        onClick = { /* TODO: Import from file */ }
                    ) {
                        Icon(
                            imageVector = Icons.Default.FileUpload,
                            contentDescription = "Import config"
                        )
                    }
                }
            )
        },
        snackbarHost = { SnackbarHost(snackbarHostState) },
        bottomBar = {
            if (uiState.hasConfig) {
                BottomAppBar {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(horizontal = 16.dp),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        // Discard button
                        OutlinedButton(
                            onClick = { viewModel.discardChanges() },
                            enabled = uiState.hasUnsavedChanges
                        ) {
                            Icon(
                                imageVector = Icons.Default.Close,
                                contentDescription = null,
                                modifier = Modifier.size(18.dp)
                            )
                            Spacer(modifier = Modifier.width(4.dp))
                            Text("Discard")
                        }

                        // Reset to defaults button
                        OutlinedButton(
                            onClick = { viewModel.resetToDefaults() }
                        ) {
                            Icon(
                                imageVector = Icons.Default.RestartAlt,
                                contentDescription = null,
                                modifier = Modifier.size(18.dp)
                            )
                            Spacer(modifier = Modifier.width(4.dp))
                            Text("Reset")
                        }

                        // Save button
                        Button(
                            onClick = { viewModel.saveConfig() },
                            enabled = uiState.hasUnsavedChanges && !uiState.isSaving && uiState.isConnectedToAirSide
                        ) {
                            if (uiState.isSaving) {
                                CircularProgressIndicator(
                                    modifier = Modifier.size(18.dp),
                                    color = MaterialTheme.colorScheme.onPrimary
                                )
                            } else {
                                Icon(
                                    imageVector = Icons.Default.Save,
                                    contentDescription = null,
                                    modifier = Modifier.size(18.dp)
                                )
                            }
                            Spacer(modifier = Modifier.width(4.dp))
                            Text("Save")
                        }
                    }
                }
            }
        }
    ) { paddingValues ->
        if (uiState.isLoading) {
            // Loading state
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues),
                contentAlignment = Alignment.Center
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    CircularProgressIndicator()
                    Spacer(modifier = Modifier.height(16.dp))
                    Text("Loading configuration...")
                }
            }
        } else if (!uiState.hasConfig) {
            // No config loaded
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues),
                contentAlignment = Alignment.Center
            ) {
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally,
                    modifier = Modifier.padding(24.dp)
                ) {
                    Icon(
                        imageVector = if (uiState.isConnectedToAirSide) Icons.Default.Settings else Icons.Default.SignalWifiOff,
                        contentDescription = null,
                        modifier = Modifier.size(64.dp),
                        tint = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Spacer(modifier = Modifier.height(16.dp))
                    Text(
                        text = if (uiState.isConnectedToAirSide) "Click refresh to load configuration" else "Connect to Air-Side to load configuration",
                        style = MaterialTheme.typography.titleMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
        } else {
            // Settings content
            Column(
                modifier = modifier
                    .fillMaxSize()
                    .padding(paddingValues)
                    .verticalScroll(rememberScrollState())
                    .padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                val config = uiState.displayConfig

                // Network Settings
                NetworkSettingsSection(
                    network = config.network,
                    onUpdate = { viewModel.updateNetworkConfig(it) },
                    validationErrors = uiState.validationErrors.filter { it.startsWith("Network:") }
                )

                // Timing Settings
                TimingSettingsSection(
                    timing = config.timing,
                    onUpdate = { viewModel.updateTimingConfig(it) },
                    validationErrors = uiState.validationErrors.filter { it.startsWith("Timing:") }
                )

                // Logging Settings
                LoggingSettingsSection(
                    logging = config.logging,
                    onUpdate = { viewModel.updateLoggingConfig(it) },
                    validationErrors = uiState.validationErrors.filter { it.startsWith("Logging:") }
                )

                // Health Settings
                HealthSettingsSection(
                    health = config.health,
                    onUpdate = { viewModel.updateHealthConfig(it) },
                    validationErrors = uiState.validationErrors.filter { it.startsWith("Health:") }
                )

                // Spacer for bottom bar
                Spacer(modifier = Modifier.height(80.dp))
            }
        }
    }
}

@Composable
fun NetworkSettingsSection(
    network: NetworkConfig,
    onUpdate: (NetworkConfig) -> Unit,
    validationErrors: List<String>
) {
    SettingsCard(title = "Network Settings", hasErrors = validationErrors.isNotEmpty()) {
        var tcpPort by remember(network) { mutableStateOf(network.tcpPort.toString()) }
        var udpStatusPort by remember(network) { mutableStateOf(network.udpStatusPort.toString()) }
        var udpHeartbeatPort by remember(network) { mutableStateOf(network.udpHeartbeatPort.toString()) }
        var groundIp by remember(network) { mutableStateOf(network.groundIp) }

        OutlinedTextField(
            value = tcpPort,
            onValueChange = {
                tcpPort = it
                it.toIntOrNull()?.let { port ->
                    onUpdate(network.copy(tcpPort = port))
                }
            },
            label = { Text("TCP Port") },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            modifier = Modifier.fillMaxWidth(),
            supportingText = { Text("1024-65535") }
        )

        OutlinedTextField(
            value = udpStatusPort,
            onValueChange = {
                udpStatusPort = it
                it.toIntOrNull()?.let { port ->
                    onUpdate(network.copy(udpStatusPort = port))
                }
            },
            label = { Text("UDP Status Port") },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            modifier = Modifier.fillMaxWidth(),
            supportingText = { Text("1024-65535") }
        )

        OutlinedTextField(
            value = udpHeartbeatPort,
            onValueChange = {
                udpHeartbeatPort = it
                it.toIntOrNull()?.let { port ->
                    onUpdate(network.copy(udpHeartbeatPort = port))
                }
            },
            label = { Text("UDP Heartbeat Port") },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            modifier = Modifier.fillMaxWidth(),
            supportingText = { Text("1024-65535") }
        )

        OutlinedTextField(
            value = groundIp,
            onValueChange = {
                groundIp = it
                onUpdate(network.copy(groundIp = it))
            },
            label = { Text("Ground IP Address") },
            modifier = Modifier.fillMaxWidth(),
            supportingText = { Text("IPv4 address (e.g., 192.168.144.11)") }
        )

        if (validationErrors.isNotEmpty()) {
            validationErrors.forEach { error ->
                Text(
                    text = error.removePrefix("Network: "),
                    color = MaterialTheme.colorScheme.error,
                    style = MaterialTheme.typography.bodySmall,
                    modifier = Modifier.padding(top = 4.dp)
                )
            }
        }
    }
}

@Composable
fun TimingSettingsSection(
    timing: TimingConfig,
    onUpdate: (TimingConfig) -> Unit,
    validationErrors: List<String>
) {
    SettingsCard(title = "Timing Settings", hasErrors = validationErrors.isNotEmpty()) {
        var statusInterval by remember(timing) { mutableStateOf(timing.statusIntervalMs.toString()) }
        var heartbeatInterval by remember(timing) { mutableStateOf(timing.heartbeatIntervalMs.toString()) }
        var heartbeatTimeout by remember(timing) { mutableStateOf(timing.heartbeatTimeoutSec.toString()) }
        var reconnectInterval by remember(timing) { mutableStateOf(timing.reconnectIntervalMs.toString()) }

        OutlinedTextField(
            value = statusInterval,
            onValueChange = {
                statusInterval = it
                it.toIntOrNull()?.let { interval ->
                    onUpdate(timing.copy(statusIntervalMs = interval))
                }
            },
            label = { Text("Status Interval (ms)") },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            modifier = Modifier.fillMaxWidth(),
            supportingText = { Text("50-5000 ms") }
        )

        OutlinedTextField(
            value = heartbeatInterval,
            onValueChange = {
                heartbeatInterval = it
                it.toIntOrNull()?.let { interval ->
                    onUpdate(timing.copy(heartbeatIntervalMs = interval))
                }
            },
            label = { Text("Heartbeat Interval (ms)") },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            modifier = Modifier.fillMaxWidth(),
            supportingText = { Text("500-5000 ms") }
        )

        OutlinedTextField(
            value = heartbeatTimeout,
            onValueChange = {
                heartbeatTimeout = it
                it.toIntOrNull()?.let { timeout ->
                    onUpdate(timing.copy(heartbeatTimeoutSec = timeout))
                }
            },
            label = { Text("Heartbeat Timeout (sec)") },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            modifier = Modifier.fillMaxWidth(),
            supportingText = { Text("1-60 seconds") }
        )

        OutlinedTextField(
            value = reconnectInterval,
            onValueChange = {
                reconnectInterval = it
                it.toIntOrNull()?.let { interval ->
                    onUpdate(timing.copy(reconnectIntervalMs = interval))
                }
            },
            label = { Text("Reconnect Interval (ms)") },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            modifier = Modifier.fillMaxWidth(),
            supportingText = { Text("500-5000 ms") }
        )

        if (validationErrors.isNotEmpty()) {
            validationErrors.forEach { error ->
                Text(
                    text = error.removePrefix("Timing: "),
                    color = MaterialTheme.colorScheme.error,
                    style = MaterialTheme.typography.bodySmall,
                    modifier = Modifier.padding(top = 4.dp)
                )
            }
        }
    }
}

@Composable
fun LoggingSettingsSection(
    logging: LoggingConfig,
    onUpdate: (LoggingConfig) -> Unit,
    validationErrors: List<String>
) {
    SettingsCard(title = "Logging Settings", hasErrors = validationErrors.isNotEmpty()) {
        var logLevel by remember(logging) { mutableStateOf(logging.logLevel) }
        var fileMaxSize by remember(logging) { mutableStateOf(logging.fileMaxSizeMb.toString()) }
        var expanded by remember { mutableStateOf(false) }

        // Log level dropdown
        ExposedDropdownMenuBox(
            expanded = expanded,
            onExpandedChange = { expanded = it }
        ) {
            OutlinedTextField(
                value = logLevel,
                onValueChange = {},
                readOnly = true,
                label = { Text("Log Level") },
                trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = expanded) },
                modifier = Modifier
                    .fillMaxWidth()
                    .menuAnchor()
            )

            ExposedDropdownMenu(
                expanded = expanded,
                onDismissRequest = { expanded = false }
            ) {
                listOf("DEBUG", "INFO", "WARNING", "ERROR").forEach { level ->
                    DropdownMenuItem(
                        text = { Text(level) },
                        onClick = {
                            logLevel = level
                            onUpdate(logging.copy(logLevel = level))
                            expanded = false
                        }
                    )
                }
            }
        }

        // File logging toggle
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text("File Logging Enabled")
            Switch(
                checked = logging.fileLoggingEnabled,
                onCheckedChange = { onUpdate(logging.copy(fileLoggingEnabled = it)) }
            )
        }

        OutlinedTextField(
            value = fileMaxSize,
            onValueChange = {
                fileMaxSize = it
                it.toIntOrNull()?.let { size ->
                    onUpdate(logging.copy(fileMaxSizeMb = size))
                }
            },
            label = { Text("File Max Size (MB)") },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            modifier = Modifier.fillMaxWidth(),
            supportingText = { Text("10-500 MB") }
        )

        // Network logging toggle
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text("Network Logging to SystemTools")
            Switch(
                checked = logging.networkLoggingEnabled,
                onCheckedChange = { onUpdate(logging.copy(networkLoggingEnabled = it)) }
            )
        }

        if (validationErrors.isNotEmpty()) {
            validationErrors.forEach { error ->
                Text(
                    text = error.removePrefix("Logging: "),
                    color = MaterialTheme.colorScheme.error,
                    style = MaterialTheme.typography.bodySmall,
                    modifier = Modifier.padding(top = 4.dp)
                )
            }
        }
    }
}

@Composable
fun HealthSettingsSection(
    health: HealthConfig,
    onUpdate: (HealthConfig) -> Unit,
    validationErrors: List<String>
) {
    SettingsCard(title = "Health Monitoring Settings", hasErrors = validationErrors.isNotEmpty()) {
        var broadcastInterval by remember(health) { mutableStateOf(health.broadcastIntervalSec.toString()) }
        var historyDuration by remember(health) { mutableStateOf(health.historyDurationMin.toString()) }

        // Broadcast enabled toggle
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text("Health Broadcast Enabled")
            Switch(
                checked = health.broadcastEnabled,
                onCheckedChange = { onUpdate(health.copy(broadcastEnabled = it)) }
            )
        }

        OutlinedTextField(
            value = broadcastInterval,
            onValueChange = {
                broadcastInterval = it
                it.toIntOrNull()?.let { interval ->
                    onUpdate(health.copy(broadcastIntervalSec = interval))
                }
            },
            label = { Text("Broadcast Interval (sec)") },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            modifier = Modifier.fillMaxWidth(),
            supportingText = { Text("1-60 seconds") }
        )

        OutlinedTextField(
            value = historyDuration,
            onValueChange = {
                historyDuration = it
                it.toIntOrNull()?.let { duration ->
                    onUpdate(health.copy(historyDurationMin = duration))
                }
            },
            label = { Text("History Duration (min)") },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            modifier = Modifier.fillMaxWidth(),
            supportingText = { Text("10-120 minutes") }
        )

        if (validationErrors.isNotEmpty()) {
            validationErrors.forEach { error ->
                Text(
                    text = error.removePrefix("Health: "),
                    color = MaterialTheme.colorScheme.error,
                    style = MaterialTheme.typography.bodySmall,
                    modifier = Modifier.padding(top = 4.dp)
                )
            }
        }
    }
}

@Composable
fun SettingsCard(
    title: String,
    hasErrors: Boolean = false,
    content: @Composable ColumnScope.() -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = if (hasErrors) MaterialTheme.colorScheme.errorContainer.copy(alpha = 0.1f)
            else MaterialTheme.colorScheme.surface
        )
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    text = title,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                if (hasErrors) {
                    Spacer(modifier = Modifier.width(8.dp))
                    Icon(
                        imageVector = Icons.Default.Error,
                        contentDescription = "Validation errors",
                        tint = MaterialTheme.colorScheme.error,
                        modifier = Modifier.size(20.dp)
                    )
                }
            }

            Spacer(modifier = Modifier.height(12.dp))

            content()
        }
    }
}
