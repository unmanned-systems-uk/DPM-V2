package uk.unmannedsystems.dpm_android.diagnostics

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import java.text.SimpleDateFormat
import java.util.*

/**
 * Quick Diagnostics Screen - Visual health status indicators
 * Shows H16↔SBC connection, camera status, recent errors with RED/GREEN indicators
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DiagnosticsScreen(
    modifier: Modifier = Modifier,
    viewModel: DiagnosticsViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Quick Diagnostics") },
                actions = {
                    IconButton(
                        onClick = { viewModel.refresh() },
                        enabled = !uiState.isRefreshing
                    ) {
                        Icon(
                            imageVector = Icons.Default.Refresh,
                            contentDescription = "Refresh"
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
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            // Overall Status Header
            OverallStatusCard(
                isHealthy = uiState.isOverallHealthy,
                statusMessage = uiState.overallStatusMessage
            )

            // H16 ↔ SBC Connection Status
            ConnectionStatusCard(
                title = "H16 ↔ Air-Side Connection",
                isConnected = uiState.isSbcConnected,
                details = uiState.connectionDetails,
                icon = Icons.Default.Wifi
            )

            // Camera Connection Status
            ConnectionStatusCard(
                title = "Camera Connection",
                isConnected = uiState.isCameraConnected,
                details = uiState.cameraDetails,
                icon = Icons.Default.CameraAlt
            )

            // Network Health Metrics
            if (uiState.isSbcConnected) {
                NetworkHealthCard(
                    latencyMs = uiState.latencyMs,
                    packetLossPercent = uiState.packetLossPercent,
                    lastHeartbeat = uiState.lastHeartbeatTime
                )
            }

            // Last 10 Errors
            RecentErrorsCard(
                errors = uiState.recentErrors
            )

            // Quick Actions
            QuickActionsCard(
                onReconnect = { viewModel.reconnect() },
                onClearErrors = { viewModel.clearErrors() },
                isConnected = uiState.isSbcConnected
            )
        }
    }
}

@Composable
private fun OverallStatusCard(
    isHealthy: Boolean,
    statusMessage: String,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = if (isHealthy) {
                Color(0xFF1B5E20).copy(alpha = 0.2f) // Dark green tint
            } else {
                Color(0xFFB71C1C).copy(alpha = 0.2f) // Dark red tint
            }
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(20.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Large status indicator
            Box(
                modifier = Modifier
                    .size(48.dp)
                    .background(
                        color = if (isHealthy) Color(0xFF00FF00) else Color(0xFFFF0000),
                        shape = CircleShape
                    )
            )

            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = if (isHealthy) "SYSTEM HEALTHY" else "ISSUES DETECTED",
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold,
                    color = if (isHealthy) Color(0xFF00FF00) else Color(0xFFFF0000)
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = statusMessage,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}

@Composable
private fun ConnectionStatusCard(
    title: String,
    isConnected: Boolean,
    details: String,
    icon: ImageVector,
    modifier: Modifier = Modifier
) {
    Card(modifier = modifier.fillMaxWidth()) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(
                    horizontalArrangement = Arrangement.spacedBy(12.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = icon,
                        contentDescription = null,
                        modifier = Modifier.size(24.dp),
                        tint = MaterialTheme.colorScheme.primary
                    )
                    Text(
                        text = title,
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                }

                // Status indicator
                Box(
                    modifier = Modifier
                        .size(32.dp)
                        .background(
                            color = if (isConnected) Color(0xFF00FF00) else Color(0xFFFF0000),
                            shape = CircleShape
                        )
                )
            }

            Spacer(modifier = Modifier.height(8.dp))

            Text(
                text = if (isConnected) "✓ Connected" else "✗ Disconnected",
                style = MaterialTheme.typography.bodyLarge,
                fontWeight = FontWeight.Medium,
                color = if (isConnected) Color(0xFF00C853) else Color(0xFFD32F2F)
            )

            if (details.isNotEmpty()) {
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = details,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}

@Composable
private fun NetworkHealthCard(
    latencyMs: Int?,
    packetLossPercent: Float?,
    lastHeartbeat: Long?,
    modifier: Modifier = Modifier
) {
    Card(modifier = modifier.fillMaxWidth()) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = "Network Health",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )

            Spacer(modifier = Modifier.height(12.dp))

            // Latency
            latencyMs?.let {
                MetricRow(
                    label = "Latency",
                    value = "${it}ms",
                    isGood = it < 100
                )
            }

            // Packet Loss
            packetLossPercent?.let {
                MetricRow(
                    label = "Packet Loss",
                    value = String.format("%.1f%%", it),
                    isGood = it < 1.0f
                )
            }

            // Last Heartbeat
            lastHeartbeat?.let {
                val timeAgo = System.currentTimeMillis() - it
                val secondsAgo = timeAgo / 1000
                MetricRow(
                    label = "Last Heartbeat",
                    value = "${secondsAgo}s ago",
                    isGood = secondsAgo < 5
                )
            }
        }
    }
}

@Composable
private fun MetricRow(
    label: String,
    value: String,
    isGood: Boolean,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Row(
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = value,
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.Medium
            )
            Box(
                modifier = Modifier
                    .size(12.dp)
                    .background(
                        color = if (isGood) Color(0xFF00FF00) else Color(0xFFFFFF00),
                        shape = CircleShape
                    )
            )
        }
    }
}

@Composable
private fun RecentErrorsCard(
    errors: List<ErrorEntry>,
    modifier: Modifier = Modifier
) {
    Card(modifier = modifier.fillMaxWidth()) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "Last 10 Errors",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = "${errors.size} total",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }

            Spacer(modifier = Modifier.height(12.dp))

            if (errors.isEmpty()) {
                Text(
                    text = "✓ No errors logged",
                    style = MaterialTheme.typography.bodyMedium,
                    color = Color(0xFF00C853)
                )
            } else {
                errors.forEach { error ->
                    ErrorItem(error = error)
                    Spacer(modifier = Modifier.height(8.dp))
                }
            }
        }
    }
}

@Composable
private fun ErrorItem(
    error: ErrorEntry,
    modifier: Modifier = Modifier
) {
    val timeFormat = SimpleDateFormat("HH:mm:ss", Locale.getDefault())

    Column(
        modifier = modifier
            .fillMaxWidth()
            .background(
                color = when (error.severity) {
                    ErrorSeverity.ERROR -> MaterialTheme.colorScheme.errorContainer.copy(alpha = 0.3f)
                    ErrorSeverity.WARNING -> MaterialTheme.colorScheme.tertiaryContainer.copy(alpha = 0.3f)
                    ErrorSeverity.INFO -> MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.3f)
                },
                shape = MaterialTheme.shapes.small
            )
            .padding(12.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Text(
                text = timeFormat.format(Date(error.timestamp)),
                style = MaterialTheme.typography.labelSmall,
                fontFamily = FontFamily.Monospace
            )
            Text(
                text = error.severity.name,
                style = MaterialTheme.typography.labelSmall,
                fontWeight = FontWeight.Bold,
                color = when (error.severity) {
                    ErrorSeverity.ERROR -> MaterialTheme.colorScheme.error
                    ErrorSeverity.WARNING -> MaterialTheme.colorScheme.tertiary
                    ErrorSeverity.INFO -> MaterialTheme.colorScheme.primary
                }
            )
        }
        Spacer(modifier = Modifier.height(4.dp))
        Text(
            text = error.message,
            style = MaterialTheme.typography.bodySmall
        )
    }
}

@Composable
private fun QuickActionsCard(
    onReconnect: () -> Unit,
    onClearErrors: () -> Unit,
    isConnected: Boolean,
    modifier: Modifier = Modifier
) {
    Card(modifier = modifier.fillMaxWidth()) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = "Quick Actions",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )

            Spacer(modifier = Modifier.height(12.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Button(
                    onClick = onReconnect,
                    modifier = Modifier.weight(1f),
                    enabled = !isConnected
                ) {
                    Icon(Icons.Default.Refresh, contentDescription = null)
                    Spacer(modifier = Modifier.width(4.dp))
                    Text("Reconnect")
                }

                OutlinedButton(
                    onClick = onClearErrors,
                    modifier = Modifier.weight(1f)
                ) {
                    Icon(Icons.Default.Delete, contentDescription = null)
                    Spacer(modifier = Modifier.width(4.dp))
                    Text("Clear Log")
                }
            }
        }
    }
}

data class ErrorEntry(
    val timestamp: Long,
    val severity: ErrorSeverity,
    val message: String
)

enum class ErrorSeverity {
    ERROR, WARNING, INFO
}
