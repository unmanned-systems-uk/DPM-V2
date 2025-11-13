package uk.unmannedsystems.dpm_android.ui.debug

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import uk.unmannedsystems.dpm_android.logging.LogContext
import uk.unmannedsystems.dpm_android.logging.LogDomain
import uk.unmannedsystems.dpm_android.logging.LogEntry
import uk.unmannedsystems.dpm_android.logging.LogLevel
import kotlinx.coroutines.launch

/**
 * Log Viewer Screen
 *
 * Displays merged Air-Side + Ground-Side log timeline with color coding
 * Part of Issue #73 - Phase 1: Foundation Infrastructure (Gap 1)
 *
 * Features:
 * - Merged chronological timeline (Air-Side + Ground-Side)
 * - Color-coded by domain (Blue=Air, Purple=Ground)
 * - Filtering by level, context, domain
 * - Text search across messages and fields
 * - Start/Stop Air-Side log streaming controls
 * - Auto-scroll toggle
 * - Clear logs button
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun LogViewerScreen(
    modifier: Modifier = Modifier,
    viewModel: LogViewerViewModel = viewModel()
) {
    val filteredLogs by viewModel.filteredLogs.collectAsState()
    val selectedMinLevel by viewModel.selectedMinLevel.collectAsState()
    val selectedContext by viewModel.selectedContext.collectAsState()
    val selectedDomain by viewModel.selectedDomain.collectAsState()
    val searchText by viewModel.searchText.collectAsState()
    val autoScroll by viewModel.autoScroll.collectAsState()
    val airLogStreamingEnabled by viewModel.airLogStreamingEnabled.collectAsState()
    val errorMessage by viewModel.errorMessage.collectAsState()

    var showFiltersDialog by remember { mutableStateOf(false) }
    var showAirStreamDialog by remember { mutableStateOf(false) }

    val listState = rememberLazyListState()
    val coroutineScope = rememberCoroutineScope()

    // Auto-scroll to bottom when new logs arrive
    LaunchedEffect(filteredLogs.size) {
        if (autoScroll && filteredLogs.isNotEmpty()) {
            coroutineScope.launch {
                listState.animateScrollToItem(filteredLogs.size - 1)
            }
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Log Viewer") },
                actions = {
                    // Air-Side streaming indicator
                    if (airLogStreamingEnabled) {
                        AssistChip(
                            onClick = { viewModel.stopAirLogStreaming() },
                            label = { Text("Air Streaming ON", fontSize = 12.sp) },
                            leadingIcon = {
                                Icon(
                                    Icons.Default.Stop,
                                    contentDescription = "Stop",
                                    modifier = Modifier.size(16.dp)
                                )
                            },
                            colors = AssistChipDefaults.assistChipColors(
                                containerColor = MaterialTheme.colorScheme.primaryContainer
                            ),
                            modifier = Modifier.padding(end = 8.dp)
                        )
                    } else {
                        IconButton(onClick = { showAirStreamDialog = true }) {
                            Icon(
                                Icons.Default.PlayArrow,
                                contentDescription = "Start Air-Side streaming"
                            )
                        }
                    }

                    // Auto-scroll toggle
                    IconButton(onClick = { viewModel.toggleAutoScroll() }) {
                        Icon(
                            if (autoScroll) Icons.Default.ArrowDownward else Icons.Default.PauseCircleOutline,
                            contentDescription = "Toggle auto-scroll",
                            tint = if (autoScroll) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }

                    // Filters
                    IconButton(onClick = { showFiltersDialog = true }) {
                        Icon(
                            Icons.Default.FilterList,
                            contentDescription = "Filters",
                            tint = if (selectedMinLevel != null || selectedContext != null || selectedDomain != null)
                                MaterialTheme.colorScheme.primary
                            else
                                MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }

                    // Clear logs
                    IconButton(onClick = { viewModel.clearLogs() }) {
                        Icon(
                            Icons.Default.Delete,
                            contentDescription = "Clear logs"
                        )
                    }
                }
            )
        }
    ) { paddingValues ->
        Column(
            modifier = modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            // Search bar
            OutlinedTextField(
                value = searchText,
                onValueChange = { viewModel.setSearchText(it) },
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 8.dp),
                placeholder = { Text("Search logs...") },
                leadingIcon = {
                    Icon(Icons.Default.Search, contentDescription = "Search")
                },
                trailingIcon = {
                    if (searchText.isNotEmpty()) {
                        IconButton(onClick = { viewModel.setSearchText("") }) {
                            Icon(Icons.Default.Clear, contentDescription = "Clear search")
                        }
                    }
                },
                singleLine = true
            )

            // Active filters display
            if (selectedMinLevel != null || selectedContext != null || selectedDomain != null) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp, vertical = 4.dp),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    selectedMinLevel?.let { level ->
                        FilterChip(
                            selected = true,
                            onClick = { viewModel.setMinLevel(null) },
                            label = { Text(level.label, fontSize = 12.sp) },
                            trailingIcon = {
                                Icon(
                                    Icons.Default.Close,
                                    contentDescription = "Remove",
                                    modifier = Modifier.size(16.dp)
                                )
                            }
                        )
                    }
                    selectedContext?.let { context ->
                        FilterChip(
                            selected = true,
                            onClick = { viewModel.setContext(null) },
                            label = { Text(context.label, fontSize = 12.sp) },
                            trailingIcon = {
                                Icon(
                                    Icons.Default.Close,
                                    contentDescription = "Remove",
                                    modifier = Modifier.size(16.dp)
                                )
                            }
                        )
                    }
                    selectedDomain?.let { domain ->
                        FilterChip(
                            selected = true,
                            onClick = { viewModel.setDomain(null) },
                            label = { Text(domain.label, fontSize = 12.sp) },
                            trailingIcon = {
                                Icon(
                                    Icons.Default.Close,
                                    contentDescription = "Remove",
                                    modifier = Modifier.size(16.dp)
                                )
                            }
                        )
                    }
                }
            }

            // Error message
            errorMessage?.let { error ->
                Surface(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp, vertical = 8.dp),
                    color = MaterialTheme.colorScheme.errorContainer,
                    shape = MaterialTheme.shapes.small
                ) {
                    Row(
                        modifier = Modifier.padding(12.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            Icons.Default.Warning,
                            contentDescription = "Error",
                            tint = MaterialTheme.colorScheme.error,
                            modifier = Modifier.size(20.dp)
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            error,
                            color = MaterialTheme.colorScheme.onErrorContainer,
                            fontSize = 14.sp,
                            modifier = Modifier.weight(1f)
                        )
                        IconButton(
                            onClick = { viewModel.clearError() },
                            modifier = Modifier.size(24.dp)
                        ) {
                            Icon(
                                Icons.Default.Close,
                                contentDescription = "Dismiss",
                                modifier = Modifier.size(16.dp)
                            )
                        }
                    }
                }
            }

            // Log count and statistics
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 4.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    "${filteredLogs.size} logs",
                    fontSize = 12.sp,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )

                // Domain count breakdown
                Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    val airCount = filteredLogs.count { it.domain == LogDomain.AIR }
                    val groundCount = filteredLogs.count { it.domain == LogDomain.GROUND }

                    Text(
                        "Air: $airCount",
                        fontSize = 12.sp,
                        color = Color(0xFF2196F3),
                        fontWeight = FontWeight.Bold
                    )
                    Text(
                        "Ground: $groundCount",
                        fontSize = 12.sp,
                        color = Color(0xFF9C27B0),
                        fontWeight = FontWeight.Bold
                    )
                }
            }

            Divider()

            // Log list
            if (filteredLogs.isEmpty()) {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Icon(
                            Icons.Default.Info,
                            contentDescription = "No logs",
                            modifier = Modifier.size(48.dp),
                            tint = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                        Text(
                            "No logs to display",
                            style = MaterialTheme.typography.bodyLarge,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                        Text(
                            "Start Air-Side streaming or generate Ground-Side logs",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            } else {
                LazyColumn(
                    modifier = Modifier.fillMaxSize(),
                    state = listState,
                    contentPadding = PaddingValues(16.dp),
                    verticalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    items(filteredLogs, key = { "${it.timestamp}-${it.domain.label}-${it.message.hashCode()}" }) { logEntry ->
                        LogEntryCard(entry = logEntry)
                    }
                }
            }
        }
    }

    // Filters dialog
    if (showFiltersDialog) {
        FiltersDialog(
            selectedMinLevel = selectedMinLevel,
            selectedContext = selectedContext,
            selectedDomain = selectedDomain,
            onMinLevelChange = { viewModel.setMinLevel(it) },
            onContextChange = { viewModel.setContext(it) },
            onDomainChange = { viewModel.setDomain(it) },
            onDismiss = { showFiltersDialog = false }
        )
    }

    // Air-Side streaming dialog
    if (showAirStreamDialog) {
        AirStreamingDialog(
            onStart = { durationSeconds ->
                viewModel.startAirLogStreaming(durationSeconds)
                showAirStreamDialog = false
            },
            onDismiss = { showAirStreamDialog = false }
        )
    }
}

/**
 * Log entry card component
 */
@Composable
fun LogEntryCard(entry: LogEntry) {
    val domainColor = when (entry.domain) {
        LogDomain.AIR -> Color(0xFF2196F3)      // Blue
        LogDomain.GROUND -> Color(0xFF9C27B0)   // Purple
    }

    val levelColor = when (entry.level) {
        LogLevel.DEBUG -> Color(0xFF757575)     // Gray
        LogLevel.INFO -> Color(0xFF4CAF50)      // Green
        LogLevel.WARNING -> Color(0xFFFFA726)   // Orange
        LogLevel.ERROR -> Color(0xFFE53935)     // Red
    }

    Surface(
        modifier = Modifier.fillMaxWidth(),
        color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.3f),
        shape = MaterialTheme.shapes.small
    ) {
        Column(
            modifier = Modifier.padding(8.dp)
        ) {
            // Header row: timestamp, domain, level, context
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Timestamp
                Text(
                    entry.timestamp.substringAfter("T").substringBefore(".") + "Z",
                    fontSize = 11.sp,
                    fontFamily = FontFamily.Monospace,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )

                Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                    // Domain chip
                    Surface(
                        color = domainColor.copy(alpha = 0.2f),
                        shape = MaterialTheme.shapes.extraSmall
                    ) {
                        Text(
                            entry.domain.label,
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Bold,
                            color = domainColor,
                            modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                        )
                    }

                    // Level chip
                    Surface(
                        color = levelColor.copy(alpha = 0.2f),
                        shape = MaterialTheme.shapes.extraSmall
                    ) {
                        Text(
                            entry.level.label,
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Bold,
                            color = levelColor,
                            modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                        )
                    }

                    // Context chip
                    Surface(
                        color = MaterialTheme.colorScheme.secondaryContainer.copy(alpha = 0.5f),
                        shape = MaterialTheme.shapes.extraSmall
                    ) {
                        Text(
                            entry.context.label,
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.onSecondaryContainer,
                            modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(4.dp))

            // Message
            Text(
                entry.message,
                fontSize = 13.sp,
                color = MaterialTheme.colorScheme.onSurface,
                fontFamily = FontFamily.Monospace
            )

            // Structured fields (if any)
            if (entry.fields.isNotEmpty()) {
                Spacer(modifier = Modifier.height(4.dp))
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(start = 8.dp)
                ) {
                    entry.fields.forEach { (key, value) ->
                        Row {
                            Text(
                                "$key: ",
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Bold,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                                fontFamily = FontFamily.Monospace
                            )
                            Text(
                                value.toString(),
                                fontSize = 11.sp,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                                fontFamily = FontFamily.Monospace
                            )
                        }
                    }
                }
            }
        }
    }
}

/**
 * Filters dialog
 */
@Composable
fun FiltersDialog(
    selectedMinLevel: LogLevel?,
    selectedContext: LogContext?,
    selectedDomain: LogDomain?,
    onMinLevelChange: (LogLevel?) -> Unit,
    onContextChange: (LogContext?) -> Unit,
    onDomainChange: (LogDomain?) -> Unit,
    onDismiss: () -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Filter Logs") },
        text = {
            Column(
                modifier = Modifier.fillMaxWidth(),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                // Level filter
                Column {
                    Text("Minimum Level", style = MaterialTheme.typography.labelLarge)
                    Spacer(modifier = Modifier.height(8.dp))
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        FilterChip(
                            selected = selectedMinLevel == null,
                            onClick = { onMinLevelChange(null) },
                            label = { Text("All", fontSize = 12.sp) }
                        )
                        LogLevel.entries.forEach { level ->
                            FilterChip(
                                selected = selectedMinLevel == level,
                                onClick = { onMinLevelChange(level) },
                                label = { Text(level.label, fontSize = 12.sp) }
                            )
                        }
                    }
                }

                // Context filter
                Column {
                    Text("Context", style = MaterialTheme.typography.labelLarge)
                    Spacer(modifier = Modifier.height(8.dp))
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(4.dp),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        FilterChip(
                            selected = selectedContext == null,
                            onClick = { onContextChange(null) },
                            label = { Text("All", fontSize = 11.sp) }
                        )
                        LogContext.entries.take(4).forEach { context ->
                            FilterChip(
                                selected = selectedContext == context,
                                onClick = { onContextChange(context) },
                                label = { Text(context.label, fontSize = 11.sp) }
                            )
                        }
                    }
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(4.dp),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        LogContext.entries.drop(4).forEach { context ->
                            FilterChip(
                                selected = selectedContext == context,
                                onClick = { onContextChange(context) },
                                label = { Text(context.label, fontSize = 11.sp) }
                            )
                        }
                    }
                }

                // Domain filter
                Column {
                    Text("Domain", style = MaterialTheme.typography.labelLarge)
                    Spacer(modifier = Modifier.height(8.dp))
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        FilterChip(
                            selected = selectedDomain == null,
                            onClick = { onDomainChange(null) },
                            label = { Text("Both", fontSize = 12.sp) }
                        )
                        LogDomain.entries.forEach { domain ->
                            FilterChip(
                                selected = selectedDomain == domain,
                                onClick = { onDomainChange(domain) },
                                label = { Text(domain.label, fontSize = 12.sp) }
                            )
                        }
                    }
                }
            }
        },
        confirmButton = {
            TextButton(onClick = onDismiss) {
                Text("Done")
            }
        }
    )
}

/**
 * Air-Side streaming dialog
 */
@Composable
fun AirStreamingDialog(
    onStart: (Int) -> Unit,
    onDismiss: () -> Unit
) {
    var selectedDuration by remember { mutableStateOf(300) } // Default 5 minutes

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Start Air-Side Log Streaming") },
        text = {
            Column(
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                Text(
                    "Enable real-time log streaming from Air-Side via UDP.",
                    style = MaterialTheme.typography.bodyMedium
                )
                Text(
                    "Select duration (streaming will auto-stop after timeout):",
                    style = MaterialTheme.typography.labelLarge
                )
                Row(
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    FilterChip(
                        selected = selectedDuration == 60,
                        onClick = { selectedDuration = 60 },
                        label = { Text("1 min") }
                    )
                    FilterChip(
                        selected = selectedDuration == 300,
                        onClick = { selectedDuration = 300 },
                        label = { Text("5 min") }
                    )
                    FilterChip(
                        selected = selectedDuration == 600,
                        onClick = { selectedDuration = 600 },
                        label = { Text("10 min") }
                    )
                    FilterChip(
                        selected = selectedDuration == 1800,
                        onClick = { selectedDuration = 1800 },
                        label = { Text("30 min") }
                    )
                }
            }
        },
        confirmButton = {
            Button(onClick = { onStart(selectedDuration) }) {
                Text("Start Streaming")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Cancel")
            }
        }
    )
}
