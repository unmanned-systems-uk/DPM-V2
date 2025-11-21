package uk.unmannedsystems.dpm_android.ui.health

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
import uk.unmannedsystems.dpm_android.model.*

/**
 * Health Dashboard Screen
 *
 * Displays real-time health metrics from Air-Side via UDP broadcasts
 * Part of Issue #73 - Phase 1: Foundation Infrastructure
 *
 * Features:
 * - System metrics (CPU, Memory, Disk, Network)
 * - Camera health (connection, latency, USB traffic, errors)
 * - Network health (TCP, UDP, command queue)
 * - Sync metrics (exposure, health, property reads)
 * - Color-coded status indicators (green/yellow/red)
 * - Connection status and stale data warnings
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HealthDashboardScreen(
    modifier: Modifier = Modifier,
    viewModel: HealthDashboardViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Health Dashboard") },
                actions = {
                    // Connection status indicator
                    ConnectionStatusChip(
                        isConnected = uiState.isConnected,
                        isStale = uiState.isStale,
                        timeSinceUpdate = uiState.getFormattedTimeSinceUpdate()
                    )

                    // Refresh button
                    IconButton(onClick = { viewModel.restartHealthMonitoring() }) {
                        Icon(
                            imageVector = Icons.Default.Refresh,
                            contentDescription = "Restart monitoring"
                        )
                    }
                }
            )
        }
    ) { paddingValues ->
        if (!uiState.hasData) {
            // No data available
            NoDataView(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues),
                isConnected = uiState.isConnected,
                errorCount = uiState.errorCount
            )
        } else {
            // Display health data
            Column(
                modifier = modifier
                    .fillMaxSize()
                    .padding(paddingValues)
                    .verticalScroll(rememberScrollState())
                    .padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                uiState.latestHealth?.let { health ->
                    // Overall Status
                    OverallStatusCard(status = uiState.overallStatus)

                    // System Health
                    SystemHealthCard(system = health.system)

                    // Camera Health
                    CameraHealthCard(camera = health.camera)

                    // Network Health
                    NetworkHealthCard(network = health.network)

                    // Sync Metrics
                    SyncMetricsCard(sync = health.sync)
                }
            }
        }
    }
}

/**
 * Connection status chip in top bar
 */
@Composable
fun ConnectionStatusChip(
    isConnected: Boolean,
    isStale: Boolean,
    timeSinceUpdate: String
) {
    val (color, text) = when {
        !isConnected -> Color(0xFFDC2626) to "Disconnected"
        isStale -> Color(0xFFF59E0B) to "Stale"
        else -> Color(0xFF10B981) to timeSinceUpdate
    }

    Surface(
        shape = CircleShape,
        color = color,
        modifier = Modifier.padding(end = 8.dp)
    ) {
        Text(
            text = text,
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp),
            style = MaterialTheme.typography.labelSmall,
            color = Color.White,
            fontWeight = FontWeight.Bold
        )
    }
}

/**
 * No data available view
 */
@Composable
fun NoDataView(
    modifier: Modifier = Modifier,
    isConnected: Boolean,
    errorCount: Int
) {
    Column(
        modifier = modifier.padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Icon(
            imageVector = if (isConnected) Icons.Default.HourglassEmpty else Icons.Default.SignalWifiOff,
            contentDescription = null,
            modifier = Modifier.size(64.dp),
            tint = MaterialTheme.colorScheme.onSurfaceVariant
        )

        Spacer(modifier = Modifier.height(16.dp))

        Text(
            text = if (isConnected) "Waiting for health data..." else "Not receiving health broadcasts",
            style = MaterialTheme.typography.titleMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )

        Spacer(modifier = Modifier.height(8.dp))

        Text(
            text = "UDP port 5004 • 5 Hz broadcasts",
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )

        if (errorCount > 0) {
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = "Errors: $errorCount",
                style = MaterialTheme.typography.bodySmall,
                color = Color(0xFFDC2626)
            )
        }
    }
}

/**
 * Overall status card
 */
@Composable
fun OverallStatusCard(status: HealthStatus) {
    val (color, icon, text) = when (status) {
        HealthStatus.NORMAL -> Triple(Color(0xFF10B981), Icons.Default.CheckCircle, "All Systems Normal")
        HealthStatus.WARNING -> Triple(Color(0xFFF59E0B), Icons.Default.Warning, "Warning: Check Metrics")
        HealthStatus.CRITICAL -> Triple(Color(0xFFDC2626), Icons.Default.Error, "Critical: Action Required")
    }

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = color.copy(alpha = 0.1f))
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.spacedBy(12.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                modifier = Modifier.size(32.dp),
                tint = color
            )
            Text(
                text = text,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = color
            )
        }
    }
}

/**
 * System health card
 */
@Composable
fun SystemHealthCard(system: SystemHealth) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = "SYSTEM",
                style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.Bold
            )

            Spacer(modifier = Modifier.height(12.dp))

            // CPU
            MetricRow(
                label = "CPU",
                value = "${system.cpuPercent.toInt()}%",
                status = system.getCpuStatus(),
                progress = system.cpuPercent / 100f
            )

            // Memory
            MetricRow(
                label = "Memory",
                value = "${system.memoryUsedMb} MB / ${system.memoryTotalMb} MB",
                status = system.getMemoryStatus(),
                progress = system.memoryPercent / 100f
            )

            // Disk (Protocol v2.0: Display in MB, converted from disk_used_mb)
            MetricRow(
                label = "Disk",
                value = "${system.diskUsedMb} MB / ${system.diskTotalMb} MB",
                status = system.getDiskStatus(),
                progress = system.diskUsagePercent / 100f
            )

            // Network
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                SimpleMetric("RX", "${system.networkRxMbps} Mbps")
                SimpleMetric("TX", "${system.networkTxMbps} Mbps")
                SimpleMetric("Uptime", formatUptime(system.uptimeSeconds ?: 0))
            }
        }
    }
}

/**
 * Camera health card
 */
@Composable
fun CameraHealthCard(camera: CameraHealth) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = "CAMERA",
                style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.Bold
            )

            Spacer(modifier = Modifier.height(12.dp))

            // Connection status
            StatusRow(
                label = "Status",
                isGood = camera.connected,
                goodText = "Connected",
                badText = "Disconnected"
            )

            if (camera.connected) {
                // Latency
                MetricRow(
                    label = "SDK Latency",
                    value = "${camera.sdkLatencyMs} ms",
                    status = camera.getLatencyStatus(),
                    showProgress = false
                )

                // USB Traffic
                SimpleMetric(
                    label = "USB Traffic",
                    value = "${camera.usbTrafficMbps} Mbps"
                )

                // Error count
                SimpleMetric(
                    label = "Errors",
                    value = camera.errorCount.toString(),
                    valueColor = if (camera.errorCount > 0) Color(0xFFDC2626) else Color(0xFF10B981)
                )
            }
        }
    }
}

/**
 * Network health card
 */
@Composable
fun NetworkHealthCard(network: NetworkHealth) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = "NETWORK",
                style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.Bold
            )

            Spacer(modifier = Modifier.height(12.dp))

            // TCP status
            StatusRow(
                label = "TCP",
                isGood = network.tcpConnected,
                goodText = "Connected",
                badText = "Disconnected"
            )

            if (network.tcpConnected) {
                // TCP Latency
                MetricRow(
                    label = "TCP Latency",
                    value = "${network.tcpLatencyMs} ms",
                    status = network.getTcpLatencyStatus(),
                    showProgress = false
                )
            }

            // UDP Loss
            MetricRow(
                label = "UDP Loss",
                value = "${network.udpLossPercent}%",
                status = network.getUdpLossStatus(),
                showProgress = false
            )

            // Command Queue
            MetricRow(
                label = "Queue Depth",
                value = network.commandQueueDepth.toString(),
                status = network.getQueueStatus(),
                showProgress = false
            )
        }
    }
}

/**
 * Sync metrics card
 */
@Composable
fun SyncMetricsCard(sync: SyncMetrics) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = "SYNC METRICS",
                style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.Bold
            )

            Spacer(modifier = Modifier.height(12.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                SimpleMetric("Exposure", "${sync.exposureRateHz} Hz")
                SimpleMetric("Health", "${sync.healthRateHz} Hz")
                SimpleMetric("Properties", "${sync.propertyReadsSec}/sec")
            }
        }
    }
}

/**
 * Metric row with progress bar
 */
@Composable
fun MetricRow(
    label: String,
    value: String,
    status: HealthStatus,
    progress: Float? = null,
    showProgress: Boolean = true
) {
    val color = when (status) {
        HealthStatus.NORMAL -> Color(0xFF10B981)
        HealthStatus.WARNING -> Color(0xFFF59E0B)
        HealthStatus.CRITICAL -> Color(0xFFDC2626)
    }

    Column(modifier = Modifier.padding(vertical = 4.dp)) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = label,
                style = MaterialTheme.typography.bodyMedium
            )

            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    text = value,
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = FontWeight.Bold,
                    fontFamily = FontFamily.Monospace,
                    color = color
                )

                Spacer(modifier = Modifier.width(8.dp))

                StatusIndicator(status)
            }
        }

        if (showProgress && progress != null) {
            Spacer(modifier = Modifier.height(4.dp))
            LinearProgressIndicator(
                progress = progress.coerceIn(0f, 1f),
                modifier = Modifier
                    .fillMaxWidth()
                    .height(8.dp),
                color = color,
                trackColor = color.copy(alpha = 0.2f)
            )
        }
    }
}

/**
 * Status row (Connected/Disconnected)
 */
@Composable
fun StatusRow(
    label: String,
    isGood: Boolean,
    goodText: String,
    badText: String
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.bodyMedium
        )

        Row(verticalAlignment = Alignment.CenterVertically) {
            Text(
                text = if (isGood) goodText else badText,
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.Bold,
                color = if (isGood) Color(0xFF10B981) else Color(0xFFDC2626)
            )

            Spacer(modifier = Modifier.width(8.dp))

            StatusIndicator(if (isGood) HealthStatus.NORMAL else HealthStatus.CRITICAL)
        }
    }
}

/**
 * Simple metric (label + value)
 */
@Composable
fun SimpleMetric(
    label: String,
    value: String,
    valueColor: Color = MaterialTheme.colorScheme.onSurface
) {
    Column {
        Text(
            text = label,
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Text(
            text = value,
            style = MaterialTheme.typography.bodyMedium,
            fontWeight = FontWeight.Bold,
            fontFamily = FontFamily.Monospace,
            color = valueColor
        )
    }
}

/**
 * Status indicator circle
 */
@Composable
fun StatusIndicator(status: HealthStatus) {
    val color = when (status) {
        HealthStatus.NORMAL -> Color(0xFF10B981)
        HealthStatus.WARNING -> Color(0xFFF59E0B)
        HealthStatus.CRITICAL -> Color(0xFFDC2626)
    }

    Box(
        modifier = Modifier
            .size(12.dp)
            .background(color, CircleShape)
    )
}

/**
 * Format uptime in human-readable format
 */
fun formatUptime(seconds: Long): String {
    val days = seconds / 86400
    val hours = (seconds % 86400) / 3600
    val minutes = (seconds % 3600) / 60

    return when {
        days > 0 -> "${days}d ${hours}h"
        hours > 0 -> "${hours}h ${minutes}m"
        else -> "${minutes}m"
    }
}
