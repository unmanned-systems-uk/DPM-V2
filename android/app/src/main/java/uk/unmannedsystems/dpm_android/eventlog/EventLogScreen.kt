package uk.unmannedsystems.dpm_android.eventlog

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

@Composable
fun EventLogScreen(
    modifier: Modifier = Modifier
) {
    val events by EventLogViewModel.events.collectAsState()
    val listState = rememberLazyListState()
    var filterCategory by remember { mutableStateOf<EventCategory?>(null) }
    var filterLevel by remember { mutableStateOf<EventLevel?>(null) }

    // Auto-scroll to bottom when new events arrive
    LaunchedEffect(events.size) {
        if (events.isNotEmpty()) {
            listState.animateScrollToItem(events.size - 1)
        }
    }

    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        // Header
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "Event Log",
                style = MaterialTheme.typography.headlineMedium,
                fontWeight = FontWeight.Bold
            )

            OutlinedButton(
                onClick = { EventLogViewModel.clearLog() }
            ) {
                Icon(Icons.Default.Delete, contentDescription = null)
                Spacer(modifier = Modifier.width(4.dp))
                Text("Clear")
            }
        }

        Spacer(modifier = Modifier.height(8.dp))

        // Stats
        Text(
            text = "Total events: ${events.size}",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )

        Spacer(modifier = Modifier.height(16.dp))

        // Filter buttons
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            FilterChip(
                label = "All",
                selected = filterCategory == null && filterLevel == null,
                onClick = {
                    filterCategory = null
                    filterLevel = null
                }
            )

            FilterChip(
                label = "Network",
                selected = filterCategory == EventCategory.NETWORK,
                onClick = {
                    filterCategory = if (filterCategory == EventCategory.NETWORK) null else EventCategory.NETWORK
                }
            )

            FilterChip(
                label = "Errors",
                selected = filterLevel == EventLevel.ERROR,
                onClick = {
                    filterLevel = if (filterLevel == EventLevel.ERROR) null else EventLevel.ERROR
                }
            )
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Event list
        val filteredEvents = events.filter { event ->
            (filterCategory == null || event.category == filterCategory) &&
            (filterLevel == null || event.level == filterLevel)
        }

        if (filteredEvents.isEmpty()) {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.surfaceVariant
                )
            ) {
                Column(
                    modifier = Modifier.padding(32.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        text = if (events.isEmpty()) "No events logged yet" else "No events match the filter",
                        style = MaterialTheme.typography.bodyLarge,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
        } else {
            LazyColumn(
                state = listState,
                modifier = Modifier.fillMaxSize(),
                verticalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                items(filteredEvents) { event ->
                    EventLogItem(event = event)
                }
            }
        }
    }
}

@Composable
private fun FilterChip(
    label: String,
    selected: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Button(
        onClick = onClick,
        modifier = modifier
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.labelMedium
        )
    }
}

@Composable
private fun EventLogItem(
    event: EventLogEntry,
    modifier: Modifier = Modifier
) {
    val timeFormat = remember { SimpleDateFormat("HH:mm:ss.SSS", Locale.getDefault()) }

    val backgroundColor = when (event.level) {
        EventLevel.ERROR -> MaterialTheme.colorScheme.errorContainer
        EventLevel.WARNING -> MaterialTheme.colorScheme.tertiaryContainer
        EventLevel.INFO -> MaterialTheme.colorScheme.primaryContainer
        EventLevel.DEBUG -> MaterialTheme.colorScheme.surfaceVariant
    }

    val textColor = when (event.level) {
        EventLevel.ERROR -> MaterialTheme.colorScheme.onErrorContainer
        EventLevel.WARNING -> MaterialTheme.colorScheme.onTertiaryContainer
        EventLevel.INFO -> MaterialTheme.colorScheme.onPrimaryContainer
        EventLevel.DEBUG -> MaterialTheme.colorScheme.onSurfaceVariant
    }

    Card(
        modifier = modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = backgroundColor
        )
    ) {
        Column(modifier = Modifier.padding(12.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = timeFormat.format(Date(event.timestamp)),
                    style = MaterialTheme.typography.labelSmall,
                    fontFamily = FontFamily.Monospace,
                    color = textColor
                )

                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text(
                        text = event.category.name,
                        style = MaterialTheme.typography.labelSmall,
                        fontWeight = FontWeight.Bold,
                        color = textColor
                    )
                    Text(
                        text = event.level.name,
                        style = MaterialTheme.typography.labelSmall,
                        color = textColor
                    )
                }
            }

            Spacer(modifier = Modifier.height(4.dp))

            Text(
                text = event.message,
                style = MaterialTheme.typography.bodyMedium,
                color = textColor
            )

            event.details?.let { details ->
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = details,
                    style = MaterialTheme.typography.bodySmall,
                    fontFamily = FontFamily.Monospace,
                    color = textColor.copy(alpha = 0.8f)
                )
            }
        }
    }
}
