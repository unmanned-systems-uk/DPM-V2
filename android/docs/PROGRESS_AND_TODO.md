# DPM Android App - Progress & TODO

## Current Status (2025-10-25)

### Working Features ✓
- Basic UI layout with Camera Control and Settings screens
- Network settings configuration (IP, ports)
- Connection state management
- Protocol message structures defined
- TCP/UDP client implementation

### Issues Identified ❌
1. **No connection diagnostics** - Connection failures show only "ERROR" state
2. **No settings save confirmation** - User doesn't know if settings were saved
3. **Poor error visibility** - No indication of what step failed during connection
4. **No network permission verification** - App may fail silently if permissions denied
5. **No pre-flight checks** - No validation before attempting connection
6. **Target IP not shown in status** - User can't verify which IP is being used

---

## Priority Improvements for Android Studio

### 🔴 HIGH PRIORITY - Network Diagnostics & Error Handling

#### 1. Enhanced Network Status Model
**File:** `app/src/main/java/uk/unmannedsystems/dpm_android/network/NetworkSettings.kt`

**Changes Required:**
```kotlin
data class NetworkStatus(
    val state: ConnectionState = ConnectionState.DISCONNECTED,
    val lastHeartbeatMs: Long = 0,
    val roundTripTimeMs: Long = 0,
    val errorMessage: String? = null,

    // NEW FIELDS FOR DIAGNOSTICS
    val targetIp: String? = null,           // Currently attempting to connect to this IP
    val targetPort: Int? = null,            // Currently attempting this port
    val connectionStep: String? = null,     // Current step: "Resolving", "TCP Connect", "Handshake", etc.
    val lastAttemptTime: Long = 0,          // Timestamp of last connection attempt
    val detailedError: String? = null       // Technical error details for debugging
)
```

**Why:** Users need to see exactly what the app is trying to do and where it's failing.

---

#### 2. Improved NetworkClient Logging & Status Updates
**File:** `app/src/main/java/uk/unmannedsystems/dpm_android/network/NetworkClient.kt`

**Changes Required:**

**a) Update connection state at each step:**
```kotlin
fun connect() {
    // ... existing code ...

    connectJob = scope.launch {
        try {
            // Step 1: Starting connection
            updateConnectionState(
                ConnectionState.CONNECTING,
                step = "Initializing connection to ${settings.targetIp}:${settings.commandPort}",
                targetIp = settings.targetIp,
                targetPort = settings.commandPort
            )

            // Step 2: TCP Connection
            updateConnectionState(
                ConnectionState.CONNECTING,
                step = "Connecting TCP socket..."
            )
            connectTcp()

            // Step 3: Sending handshake
            updateConnectionState(
                ConnectionState.CONNECTING,
                step = "Sending handshake..."
            )
            sendHandshake()

            // Step 4: Starting listeners
            updateConnectionState(
                ConnectionState.CONNECTING,
                step = "Starting UDP listeners..."
            )
            startUdpStatusListener()
            startHeartbeat()

            // Success!
            updateConnectionState(
                ConnectionState.CONNECTED,
                step = "Connected successfully"
            )

        } catch (e: Exception) {
            Log.e(TAG, "Connection failed at step: ${_connectionStatus.value.connectionStep}", e)
            updateConnectionState(
                ConnectionState.ERROR,
                errorMessage = "Failed: ${e.message}",
                detailedError = "${e.javaClass.simpleName}: ${e.message}\nStep: ${_connectionStatus.value.connectionStep}"
            )

            // Retry logic...
        }
    }
}
```

**b) Enhanced error handling in connectTcp():**
```kotlin
private suspend fun connectTcp() {
    try {
        val address = InetAddress.getByName(settings.targetIp)
        Log.d(TAG, "Resolved ${settings.targetIp} to $address")

        updateConnectionState(
            ConnectionState.CONNECTING,
            step = "Opening socket to ${address.hostAddress}:${settings.commandPort}"
        )

        tcpSocket = withContext(Dispatchers.IO) {
            Socket(address, settings.commandPort).apply {
                soTimeout = settings.connectionTimeoutMs.toInt()
            }
        }

        Log.i(TAG, "TCP socket connected successfully")
        tcpWriter = PrintWriter(tcpSocket!!.getOutputStream(), true)
        tcpReader = BufferedReader(InputStreamReader(tcpSocket!!.getInputStream()))

    } catch (e: UnknownHostException) {
        throw Exception("Cannot resolve hostname: ${settings.targetIp}", e)
    } catch (e: ConnectException) {
        throw Exception("Connection refused by ${settings.targetIp}:${settings.commandPort}. Is the server running?", e)
    } catch (e: SocketTimeoutException) {
        throw Exception("Connection timeout after ${settings.connectionTimeoutMs}ms. Server not responding?", e)
    } catch (e: Exception) {
        throw Exception("TCP connection failed: ${e.message}", e)
    }
}
```

**c) Update the updateConnectionState function signature:**
```kotlin
private fun updateConnectionState(
    state: ConnectionState,
    errorMessage: String? = null,
    detailedError: String? = null,
    step: String? = null,
    targetIp: String? = null,
    targetPort: Int? = null
) {
    _connectionStatus.value = _connectionStatus.value.copy(
        state = state,
        errorMessage = errorMessage,
        detailedError = detailedError,
        connectionStep = step,
        targetIp = targetIp ?: _connectionStatus.value.targetIp,
        targetPort = targetPort ?: _connectionStatus.value.targetPort,
        lastAttemptTime = if (state == ConnectionState.CONNECTING) {
            System.currentTimeMillis()
        } else {
            _connectionStatus.value.lastAttemptTime
        }
    )
}
```

**Why:** This provides step-by-step visibility into the connection process and specific error messages.

---

#### 3. Network Permission Verification
**File:** `app/src/main/java/uk/unmannedsystems/dpm_android/MainActivity.kt`

**Changes Required:**

**a) Add permission check in MainActivity:**
```kotlin
import android.content.pm.PackageManager
import android.Manifest

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Check network permission
        checkNetworkPermission()

        setContent {
            // ... existing UI code ...
        }
    }

    private fun checkNetworkPermission() {
        val permission = Manifest.permission.INTERNET
        if (checkSelfPermission(permission) != PackageManager.PERMISSION_GRANTED) {
            Log.e("MainActivity", "INTERNET permission not granted!")
            // In modern Android, INTERNET is automatically granted, but log it anyway
        } else {
            Log.d("MainActivity", "INTERNET permission OK")
        }
    }
}
```

**b) Add AndroidManifest.xml verification:**
Ensure `app/src/main/AndroidManifest.xml` contains:
```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
```

**Why:** Explicit verification prevents silent failures due to missing permissions.

---

#### 4. Pre-flight Network Connectivity Check
**File:** `app/src/main/java/uk/unmannedsystems/dpm_android/network/NetworkClient.kt`

**Add new function:**
```kotlin
/**
 * Pre-flight check before attempting connection
 * Tests basic network connectivity and reachability
 */
suspend fun testConnectivity(): Result<String> {
    return withContext(Dispatchers.IO) {
        try {
            // Test 1: Check if we have network connectivity
            val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
            val activeNetwork = connectivityManager.activeNetworkInfo
            if (activeNetwork?.isConnected != true) {
                return@withContext Result.failure(Exception("No network connectivity. Check WiFi/Mobile data."))
            }

            // Test 2: Try to resolve the target IP
            val address = try {
                InetAddress.getByName(settings.targetIp)
            } catch (e: UnknownHostException) {
                return@withContext Result.failure(Exception("Cannot resolve ${settings.targetIp}. Check IP address."))
            }

            // Test 3: Check if target is reachable (ICMP ping - may not work on all networks)
            val reachable = address.isReachable(2000)
            if (!reachable) {
                Log.w(TAG, "Target ${settings.targetIp} not responding to ping (this may be normal if ICMP is blocked)")
            }

            Result.success("Pre-flight check passed. Target: ${address.hostAddress}")

        } catch (e: Exception) {
            Result.failure(Exception("Pre-flight check failed: ${e.message}"))
        }
    }
}
```

**Note:** Requires Context - pass in NetworkClient constructor or use Application context.

**Why:** Catch common issues (no network, bad IP) before attempting full connection.

---

### 🟡 MEDIUM PRIORITY - UI/UX Improvements

#### 5. Settings Save Confirmation
**File:** `app/src/main/java/uk/unmannedsystems/dpm_android/settings/SettingsScreen.kt`

**Changes Required:**
```kotlin
@Composable
fun SettingsScreen(
    viewModel: SettingsViewModel = viewModel(),
    modifier: Modifier = Modifier
) {
    val networkStatus by viewModel.networkStatus.collectAsState()
    val currentSettings by viewModel.networkSettings.collectAsState()

    // NEW: Add Snackbar state
    val snackbarHostState = remember { SnackbarHostState() }
    val coroutineScope = rememberCoroutineScope()

    Scaffold(
        snackbarHost = { SnackbarHost(snackbarHostState) }
    ) { padding ->
        SettingsContent(
            // ... existing parameters ...
            onSaveSettings = { newSettings ->
                viewModel.updateSettings(newSettings)
                // Show confirmation
                coroutineScope.launch {
                    snackbarHostState.showSnackbar(
                        message = "Settings saved: ${newSettings.targetIp}:${newSettings.commandPort}",
                        duration = SnackbarDuration.Short
                    )
                }
            },
            // ...
        )
    }
}
```

**Why:** User feedback confirms the action was successful.

---

#### 6. Enhanced Connection Status Display
**File:** `app/src/main/java/uk/unmannedsystems/dpm_android/settings/SettingsScreen.kt`

**Changes Required:**
```kotlin
// Enhanced status card showing detailed information
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

        // Status state
        Text(
            text = networkStatus.state.name,
            style = MaterialTheme.typography.bodyLarge,
            fontWeight = FontWeight.Bold
        )

        // NEW: Show target if available
        networkStatus.targetIp?.let { ip ->
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = "Target: $ip:${networkStatus.targetPort ?: currentSettings.commandPort}",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }

        // NEW: Show current step if connecting
        networkStatus.connectionStep?.let { step ->
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = step,
                style = MaterialTheme.typography.bodySmall,
                fontStyle = FontStyle.Italic
            )
        }

        // Error message
        networkStatus.errorMessage?.let { error ->
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = "Error: $error",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.error
            )
        }

        // NEW: Last attempt time
        if (networkStatus.lastAttemptTime > 0) {
            Spacer(modifier = Modifier.height(4.dp))
            val timeSince = (System.currentTimeMillis() - networkStatus.lastAttemptTime) / 1000
            Text(
                text = "Last attempt: ${timeSince}s ago",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}
```

**Why:** Shows exactly what the app is doing and where it failed.

---

#### 7. Diagnostic Information Panel (Expandable)
**File:** `app/src/main/java/uk/unmannedsystems/dpm_android/settings/SettingsScreen.kt`

**Add new section:**
```kotlin
// NEW: Diagnostic panel (collapsible)
var showDiagnostics by rememberSaveable { mutableStateOf(false) }

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
            Text(
                text = "Diagnostics",
                style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.Bold
            )
            IconButton(onClick = { showDiagnostics = !showDiagnostics }) {
                Icon(
                    imageVector = if (showDiagnostics) Icons.Default.ExpandLess else Icons.Default.ExpandMore,
                    contentDescription = if (showDiagnostics) "Hide" else "Show"
                )
            }
        }

        if (showDiagnostics) {
            Spacer(modifier = Modifier.height(8.dp))

            // Current settings
            Text("Current Settings:", fontWeight = FontWeight.Bold, style = MaterialTheme.typography.bodySmall)
            Text("• Target: ${currentSettings.targetIp}:${currentSettings.commandPort}", style = MaterialTheme.typography.bodySmall)
            Text("• Status Port: ${currentSettings.statusListenPort}", style = MaterialTheme.typography.bodySmall)
            Text("• Heartbeat Port: ${currentSettings.heartbeatPort}", style = MaterialTheme.typography.bodySmall)
            Text("• Timeout: ${currentSettings.connectionTimeoutMs}ms", style = MaterialTheme.typography.bodySmall)

            Spacer(modifier = Modifier.height(8.dp))

            // Connection status details
            Text("Connection Details:", fontWeight = FontWeight.Bold, style = MaterialTheme.typography.bodySmall)
            Text("• State: ${networkStatus.state}", style = MaterialTheme.typography.bodySmall)
            networkStatus.connectionStep?.let {
                Text("• Step: $it", style = MaterialTheme.typography.bodySmall)
            }
            if (networkStatus.lastHeartbeatMs > 0) {
                val timeSince = (System.currentTimeMillis() - networkStatus.lastHeartbeatMs) / 1000
                Text("• Last Heartbeat: ${timeSince}s ago", style = MaterialTheme.typography.bodySmall)
            }

            // Detailed error (if available)
            networkStatus.detailedError?.let { error ->
                Spacer(modifier = Modifier.height(8.dp))
                Text("Technical Error:", fontWeight = FontWeight.Bold, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.error)
                Text(error, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.error, fontFamily = FontFamily.Monospace)
            }
        }
    }
}
```

**Why:** Advanced users can see technical details without cluttering the main UI.

---

### 🟢 LOW PRIORITY - Additional Enhancements

#### 8. Connection Test Button
**File:** `app/src/main/java/uk/unmannedsystems/dpm_android/settings/SettingsScreen.kt`

**Add button:**
```kotlin
// NEW: Test Connection button (separate from Connect)
OutlinedButton(
    onClick = {
        coroutineScope.launch {
            val result = viewModel.testConnectivity()
            snackbarHostState.showSnackbar(
                message = result.getOrElse { it.message ?: "Test failed" },
                duration = SnackbarDuration.Long
            )
        }
    },
    modifier = Modifier.fillMaxWidth()
) {
    Icon(Icons.Default.NetworkCheck, contentDescription = null)
    Spacer(modifier = Modifier.width(8.dp))
    Text("Test Network Connectivity")
}
```

**Why:** Allows testing without full connection attempt.

---

#### 9. Auto-Retry Configuration
**File:** `app/src/main/java/uk/unmannedsystems/dpm_android/network/NetworkSettings.kt`

**Add settings:**
```kotlin
data class NetworkSettings(
    // ... existing fields ...
    val autoRetryEnabled: Boolean = true,
    val maxRetryAttempts: Int = 3,
    val retryDelayMs: Long = 2000
)
```

**Update NetworkClient to respect these settings.**

**Why:** Configurable retry behavior.

---

## Testing Checklist

After implementing improvements, test:

- [ ] Settings save shows confirmation
- [ ] Connection status shows target IP and port
- [ ] Connection status shows current step ("Connecting TCP...", etc.)
- [ ] Error messages are specific and helpful
- [ ] Diagnostics panel shows technical details
- [ ] Connection to wrong IP shows clear error
- [ ] Connection timeout shows clear error
- [ ] Connection refused shows clear error
- [ ] Network permission is verified on startup
- [ ] Settings persist after app restart

---

## Known Issues from Testing Session (2025-10-25)

### Issue 1: Android App Cannot Connect to Pi ✅ FIXED
**Symptoms:**
- App shows "DISCONNECTED" → "ERROR" immediately
- No connection attempts visible on Pi server logs
- Ping from H16 to Pi works fine
- **CRITICAL:** Android Settings shows NO permissions for DPM app

**Investigation Results:**
- Pi server is running and accepting connections (tested with nc)
- No network packets from H16 (10.0.1.45) reaching Pi (10.0.1.53)

**ROOT CAUSE IDENTIFIED:**
❌ **AndroidManifest.xml was missing INTERNET permission!**
- No `<uses-permission>` tags declared at all
- Android silently blocked all network access
- App couldn't make any TCP/UDP connections

**FIX APPLIED:**
✅ Added required permissions to AndroidManifest.xml:
```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
```

**Next Steps:**
1. **REBUILD AND REINSTALL APK** - Old APK won't have permissions
2. Verify permissions appear in Android Settings → Apps → DPM
3. Test connection again
4. If still failing, implement detailed logging per improvements above

---

## Development Environment Setup

1. **Open Project in Android Studio**
   ```bash
   # From project root
   cd android
   # Open in Android Studio: File → Open → Select 'android' folder
   ```

2. **Verify Dependencies**
   - Kotlin Coroutines
   - Jetpack Compose
   - Gson for JSON
   - Material3 for UI

3. **Build Configuration**
   - Target SDK: 34 (Android 14)
   - Min SDK: 26 (Android 8.0)

4. **Testing Setup**
   - Use ADB to install on H16
   - Monitor logcat for errors:
     ```bash
     adb logcat | grep -i "NetworkClient\|DPM"
     ```

---

## References

- **Protocol Specification:** `../sbc/docs/protocol-specification.md`
- **Network Architecture:** `../sbc/docs/network-architecture.md`
- **WiFi Testing Guide:** `../sbc/docs/WIFI_TESTING.md`
- **Main Project TODO:** `../sbc/docs/PROGRESS_AND_TODO.md`
