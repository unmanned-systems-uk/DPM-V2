package uk.unmannedsystems.dpm_android.ui.settings

import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
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
import androidx.compose.ui.platform.LocalFocusManager
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import kotlinx.coroutines.launch
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
    val focusManager = LocalFocusManager.current

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
        modifier = Modifier
            .fillMaxSize()
            .imePadding(),  // Issue #113: Adjust for keyboard
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
        // Always show Ground-Side settings, Air-Side config is optional
        if (!uiState.hasConfig) {
            // No Air-Side config loaded - but show Ground-Side settings
            Column(
                modifier = modifier
                    .fillMaxSize()
                    .padding(paddingValues)
                    .verticalScroll(rememberScrollState())
                    .clickable(  // Issue #113: Tap-outside-to-dismiss keyboard
                        interactionSource = remember { MutableInteractionSource() },
                        indication = null
                    ) {
                        focusManager.clearFocus()
                    }
                    .padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                // Info card about Air-Side config
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f)
                    )
                ) {
                    Row(
                        modifier = Modifier.padding(16.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        if (uiState.isLoading) {
                            CircularProgressIndicator(
                                modifier = Modifier.size(40.dp),
                                strokeWidth = 3.dp
                            )
                        } else {
                            Icon(
                                imageVector = if (uiState.isConnectedToAirSide) Icons.Default.Settings else Icons.Default.SignalWifiOff,
                                contentDescription = null,
                                modifier = Modifier.size(40.dp),
                                tint = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                        Spacer(modifier = Modifier.width(16.dp))
                        Column {
                            Text(
                                text = "Air-Side Configuration",
                                style = MaterialTheme.typography.titleMedium,
                                fontWeight = FontWeight.Bold
                            )
                            Text(
                                text = when {
                                    uiState.isLoading -> "Loading Air-Side configuration..."
                                    uiState.isConnectedToAirSide -> "Click refresh to load Air-Side configuration"
                                    else -> "Connect to Air-Side to load configuration"
                                },
                                style = MaterialTheme.typography.bodyMedium,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                    }
                }

                // Ground-Side settings (always available)
                Text(
                    text = "Ground-Side Settings",
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold
                )

                // SystemTools Logging Settings (Ground-Side only - Issue #99)
                SystemToolsLoggingSection()

                // Logging Control Settings (Ground-Side only - Issue #113)
                LoggingControlSection()

                // Spacer for bottom bar
                Spacer(modifier = Modifier.height(80.dp))
            }
        } else {
            // Settings content
            Column(
                modifier = modifier
                    .fillMaxSize()
                    .padding(paddingValues)
                    .verticalScroll(rememberScrollState())
                    .clickable(  // Issue #113: Tap-outside-to-dismiss keyboard
                        interactionSource = remember { MutableInteractionSource() },
                        indication = null
                    ) {
                        focusManager.clearFocus()
                    }
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

                // SystemTools Logging Settings (Ground-Side only - Issue #99)
                SystemToolsLoggingSection()

                // Logging Control Settings (Ground-Side only - Issue #113)
                LoggingControlSection()

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

@OptIn(ExperimentalMaterial3Api::class)
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

/**
 * SystemTools Logging Configuration Section (Ground-Side Only - Issue #99)
 *
 * Allows user to configure SystemTools connection:
 * - Host/IP: "localhost" (with ADB reverse) or direct IP (e.g., "10.0.1.83")
 * - Port: TCP port number (default: 5008)
 * - Enabled: Toggle SystemTools logging on/off
 *
 * This is Ground-Side specific configuration (not sent to Air-Side)
 */
@Composable
fun SystemToolsLoggingSection() {
    val context = androidx.compose.ui.platform.LocalContext.current
    val scope = rememberCoroutineScope()
    val settingsRepository = remember { uk.unmannedsystems.dpm_android.settings.SettingsRepository(context) }

    // Load current settings
    val systemToolsHost by settingsRepository.systemToolsLogHostFlow.collectAsState(initial = "localhost")
    val systemToolsPort by settingsRepository.systemToolsLogPortFlow.collectAsState(initial = 5008)
    val systemToolsEnabled by settingsRepository.systemToolsLogEnabledFlow.collectAsState(initial = true)

    // Local state for text fields
    var hostInput by remember(systemToolsHost) { mutableStateOf(systemToolsHost) }
    var portInput by remember(systemToolsPort) { mutableStateOf(systemToolsPort.toString()) }

    // Validation
    val hostError = hostInput.isBlank()
    val portError = portInput.toIntOrNull()?.let { it !in 1024..65535 } ?: true

    SettingsCard(
        title = "SystemTools Logging (Ground-Side)",
        hasErrors = hostError || portError
    ) {
        // Info text
        Text(
            text = "Configure log streaming to SystemTools development tool",
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.padding(bottom = 8.dp)
        )

        // Enable toggle
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text("Enable SystemTools Logging")
                Text(
                    text = "DEBUG builds only",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            Switch(
                checked = systemToolsEnabled,
                onCheckedChange = { enabled ->
                    scope.launch {
                        settingsRepository.saveSystemToolsLogEnabled(enabled)
                    }
                }
            )
        }

        Spacer(modifier = Modifier.height(8.dp))

        // Host field
        OutlinedTextField(
            value = hostInput,
            onValueChange = { hostInput = it },
            label = { Text("Host / IP Address") },
            placeholder = { Text("localhost or 10.0.1.83") },
            modifier = Modifier.fillMaxWidth(),
            supportingText = {
                if (hostInput == "localhost") {
                    Text("Using localhost requires ADB reverse", color = MaterialTheme.colorScheme.primary)
                } else {
                    Text("Direct IP connection (fallback mode)")
                }
            },
            isError = hostError,
            enabled = systemToolsEnabled,
            trailingIcon = {
                if (hostInput != systemToolsHost) {
                    IconButton(onClick = {
                        scope.launch {
                            settingsRepository.saveSystemToolsLogHost(hostInput)
                        }
                    }) {
                        Icon(Icons.Default.Check, "Save host")
                    }
                }
            }
        )

        // Port field
        OutlinedTextField(
            value = portInput,
            onValueChange = { portInput = it },
            label = { Text("Port") },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            modifier = Modifier.fillMaxWidth(),
            supportingText = { Text("1024-65535 (default: 5008)") },
            isError = portError,
            enabled = systemToolsEnabled,
            trailingIcon = {
                val portValue = portInput.toIntOrNull()
                if (portValue != null && portValue != systemToolsPort && !portError) {
                    IconButton(onClick = {
                        scope.launch {
                            settingsRepository.saveSystemToolsLogPort(portValue)
                        }
                    }) {
                        Icon(Icons.Default.Check, "Save port")
                    }
                }
            }
        )

        // ADB reverse instructions (show when using localhost)
        if (hostInput == "localhost") {
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = 8.dp),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.3f)
                )
            ) {
                Row(
                    modifier = Modifier.padding(12.dp),
                    verticalAlignment = Alignment.Top
                ) {
                    Icon(
                        imageVector = Icons.Default.Info,
                        contentDescription = null,
                        tint = MaterialTheme.colorScheme.primary,
                        modifier = Modifier.size(20.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Column {
                        Text(
                            text = "ADB Reverse Setup Required",
                            style = MaterialTheme.typography.labelMedium,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.primary
                        )
                        Text(
                            text = "Run on dev machine:\nadb reverse tcp:$systemToolsPort tcp:$systemToolsPort",
                            style = MaterialTheme.typography.bodySmall,
                            fontFamily = androidx.compose.ui.text.font.FontFamily.Monospace,
                            modifier = Modifier.padding(top = 4.dp)
                        )
                    }
                }
            }
        }

        // Validation errors
        if (hostError) {
            Text(
                text = "Host cannot be empty",
                color = MaterialTheme.colorScheme.error,
                style = MaterialTheme.typography.bodySmall,
                modifier = Modifier.padding(top = 4.dp)
            )
        }
        if (portError) {
            Text(
                text = "Port must be between 1024 and 65535",
                color = MaterialTheme.colorScheme.error,
                style = MaterialTheme.typography.bodySmall,
                modifier = Modifier.padding(top = 4.dp)
            )
        }

        // Restart notice
        if (hostInput != systemToolsHost || portInput.toIntOrNull() != systemToolsPort) {
            Text(
                text = "⚠️ App restart required for changes to take effect",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.tertiary,
                modifier = Modifier.padding(top = 8.dp)
            )
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

/**
 * Logging Control Section - Issue #113
 *
 * Controls which logging systems are active:
 * - Android Logcat (Log.d): Traditional Android logging (safe, always available via ADB)
 * - Structured Logging (Timber): StructuredLogger → SystemTools (new system being tested)
 *
 * Both can run in parallel. Disable Log.d() only after Timber is proven 100% reliable.
 */
@Composable
fun LoggingControlSection() {
    val context = androidx.compose.ui.platform.LocalContext.current
    val scope = rememberCoroutineScope()
    val settingsRepository = remember { uk.unmannedsystems.dpm_android.settings.SettingsRepository(context) }

    // Load current settings
    val androidLogcatEnabled by settingsRepository.androidLogcatEnabledFlow.collectAsState(
        initial = settingsRepository.getDefaultAndroidLogcatEnabled()
    )
    val structuredLoggingEnabled by settingsRepository.structuredLoggingEnabledFlow.collectAsState(
        initial = settingsRepository.getDefaultStructuredLoggingEnabled()
    )

    SettingsCard(
        title = "Logging Control (Debug)",
        hasErrors = !androidLogcatEnabled && !structuredLoggingEnabled
    ) {
        Column(
            modifier = Modifier.fillMaxWidth(),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            // Android Logcat Toggle
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = "Android Logcat (Log.d)",
                        style = MaterialTheme.typography.bodyLarge,
                        fontWeight = FontWeight.Medium
                    )
                    Text(
                        text = "Traditional Android logging (safe, always available via ADB)",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                Switch(
                    checked = androidLogcatEnabled,
                    onCheckedChange = { enabled ->
                        scope.launch {
                            settingsRepository.saveAndroidLogcatEnabled(enabled)
                            // Update LogHelper immediately
                            uk.unmannedsystems.dpm_android.logging.LogHelper.updateSettings(
                                androidEnabled = enabled,
                                structuredEnabled = structuredLoggingEnabled
                            )
                        }
                    }
                )
            }

            Divider()

            // Structured Logging Toggle
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = "Structured Logging (Timber)",
                        style = MaterialTheme.typography.bodyLarge,
                        fontWeight = FontWeight.Medium
                    )
                    Text(
                        text = "Timber → FileSink, MemorySink, NetworkSink → SystemTools",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                Switch(
                    checked = structuredLoggingEnabled,
                    onCheckedChange = { enabled ->
                        scope.launch {
                            settingsRepository.saveStructuredLoggingEnabled(enabled)
                            // Update LogHelper immediately
                            uk.unmannedsystems.dpm_android.logging.LogHelper.updateSettings(
                                androidEnabled = androidLogcatEnabled,
                                structuredEnabled = enabled
                            )
                        }
                    }
                )
            }

            // Warning if both disabled
            if (!androidLogcatEnabled && !structuredLoggingEnabled) {
                Divider()
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(8.dp),
                    horizontalArrangement = Arrangement.Start,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = Icons.Default.Warning,
                        contentDescription = "Warning",
                        tint = MaterialTheme.colorScheme.error,
                        modifier = Modifier.size(20.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "All logging disabled - no diagnostics available",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.error
                    )
                }
            }

            // Info message
            Text(
                text = "💡 Keep both enabled during testing. Disable Log.d() only after Timber is proven reliable.",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.padding(top = 4.dp)
            )
        }
    }
}
