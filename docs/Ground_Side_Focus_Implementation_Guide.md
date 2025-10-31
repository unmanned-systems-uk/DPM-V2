# Ground-Side Focus Control Implementation Guide
**DPM-V2 Android GCS Camera Focus Features**

**Version:** 1.2.0
**Date:** 2025-10-31
**Status:** Air-Side Implementation Complete - Ready for Ground-Side Development
**Author:** DPM Development Team

---

## Table of Contents
1. [Overview](#overview)
2. [Feature Requirements](#feature-requirements)
3. [Protocol Specification](#protocol-specification)
4. [UI/UX Design](#uiux-design)
5. [Implementation Guide](#implementation-guide)
6. [Testing Strategy](#testing-strategy)
7. [Error Handling](#error-handling)

---

## Overview

This document provides complete implementation instructions for Android GCS developers to add manual focus control and auto-focus features to the DPM-V2 Ground Control Station.

### What's Already Done (Air-Side)
✅ `camera.focus` command - Manual focus control (near/far/stop)
✅ `camera.auto_focus_hold` command - AF-ON button simulation
✅ `CrDeviceProperty_PriorityKeySettings` - SDK commands override physical camera controls
✅ Protocol specification in `/protocol/commands.json`
✅ C++ implementation in payload-manager container

### What Needs To Be Built (Ground-Side)
❌ Android UI controls for manual focus
❌ Protocol client implementation for focus commands
❌ Touch gestures for focus control
❌ Visual feedback during focus operations
❌ Integration with existing camera controls

---

## Feature Requirements

### FR-1: Manual Focus Control
**Priority:** P0 (Critical for drone photography)

**User Story:**
*"As a drone pilot, I need to manually adjust camera focus during flight so that I can achieve sharp focus on subjects at varying distances."*

**Acceptance Criteria:**
- [ ] User can initiate focus movement toward near (closer objects)
- [ ] User can initiate focus movement toward far (distant objects)
- [ ] User can stop focus movement at any time
- [ ] User can select focus speed (slow/medium/fast)
- [ ] Focus controls are only enabled when camera is in manual focus mode
- [ ] Visual feedback shows current focus operation state

### FR-2: Auto-Focus Trigger
**Priority:** P1 (High - complements manual focus)

**User Story:**
*"As a drone pilot, I need a quick way to trigger auto-focus so that the camera can automatically focus on the current subject without switching modes."*

**Acceptance Criteria:**
- [ ] User can press-and-hold to engage auto-focus
- [ ] User can release to stop auto-focus operation
- [ ] Works in any auto-focus mode (AF-S, AF-C)
- [ ] Visual feedback shows AF active state
- [ ] Single-tap gesture for quick AF operation

---

## Protocol Specification

### Command 1: `camera.focus`

**Purpose:** Control manual focus direction and speed

**Request Format:**
```json
{
  "seq_id": 123,
  "command": "camera.focus",
  "payload": {
    "action": "near",    // Required: "near" | "far" | "stop"
    "speed": 3           // Optional: 1 (slow) | 2 (medium) | 3 (fast), default: 3
  }
}
```

**Success Response:**
```json
{
  "seq_id": 123,
  "command": "camera.focus",
  "status": "success",
  "result": {
    "action": "near",
    "speed": 3
  }
}
```

**Error Response:**
```json
{
  "seq_id": 123,
  "command": "camera.focus",
  "status": "error",
  "error": {
    "code": 3001,
    "message": "Camera not in manual focus mode"
  }
}
```

**Error Codes:**
- `1000` - Internal error (camera not connected)
- `3001` - Camera not in manual focus mode
- `3002` - Invalid action parameter
- `3003` - Invalid speed parameter
- `3004` - Focus operation failed

---

### Command 2: `camera.auto_focus_hold`

**Purpose:** Trigger auto-focus (AF-ON button simulation)

**Request Format:**
```json
{
  "seq_id": 124,
  "command": "camera.auto_focus_hold",
  "payload": {
    "state": "press"     // Required: "press" | "release"
  }
}
```

**Success Response:**
```json
{
  "seq_id": 124,
  "command": "camera.auto_focus_hold",
  "status": "success",
  "result": {
    "state": "press"
  }
}
```

**Error Response:**
```json
{
  "seq_id": 124,
  "command": "camera.auto_focus_hold",
  "status": "error",
  "error": {
    "code": 3005,
    "message": "Auto-focus operation failed"
  }
}
```

**Error Codes:**
- `1000` - Internal error (camera not connected)
- `3005` - Auto-focus hold failed
- `3006` - Invalid state parameter

---

## UI/UX Design

### Location in UI Hierarchy
```
CameraControlFragment
├── ExposureControls (existing)
├── WhiteBalanceControls (existing)
└── FocusControls (NEW)
    ├── ManualFocusPanel
    │   ├── NearButton (<<<)
    │   ├── FarButton (>>>)
    │   ├── SpeedSelector
    │   └── StopButton
    └── AutoFocusButton (AF-ON)
```

### UI Components

#### 1. Manual Focus Panel
**Layout:** Horizontal button strip with speed selector

**Visual Design:**
```
┌─────────────────────────────────────────┐
│  FOCUS MODE: MANUAL                     │
│                                         │
│  ┌────┐  ┌────┐  ┌────┐  ┌──────────┐ │
│  │ <<< │  │STOP│  │ >>> │  │Speed: ▼ │ │
│  │NEAR│  │    │  │ FAR │  │   3     │ │
│  └────┘  └────┘  └────┘  └──────────┘ │
│                                         │
│  [  Active: Focusing FAR at speed 3  ] │
└─────────────────────────────────────────┘
```

**Button Behavior:**
- **NEAR Button** - Press and hold to focus closer, release to stop
- **FAR Button** - Press and hold to focus further, release to stop
- **STOP Button** - Tap to immediately halt any focus operation
- **Speed Dropdown** - Select 1 (slow), 2 (medium), or 3 (fast)

**State Management:**
```kotlin
enum class FocusState {
    IDLE,              // No focus operation
    FOCUSING_NEAR,     // Moving focus closer
    FOCUSING_FAR,      // Moving focus further
    STOPPING           // Stop command sent
}
```

---

#### 2. Auto-Focus Button
**Layout:** Floating action button in camera view

**Visual Design:**
```
Camera Preview
┌─────────────────────────────────────┐
│                                     │
│                                     │
│          [Subject Framing]          │
│                                     │
│                      ┌──────┐       │
│                      │ AF-ON│       │
│                      └──────┘       │
└─────────────────────────────────────┘
```

**Button States:**
- **Idle** - White circle with "AF" text
- **Pressed** - Green circle with ripple animation
- **Focusing** - Pulsing green animation
- **Locked** - Solid green (if camera achieves focus lock)

**Interaction:**
- **Press** - Sends `camera.auto_focus_hold` with `state: "press"`
- **Release** - Sends `camera.auto_focus_hold` with `state: "release"`
- **Single Tap** - Press → 1 second delay → Release

---

### Touch Gestures (Advanced)

**Optional Enhancement:** Two-finger swipe for focus control

```
┌─────────────────────────────────────┐
│  Swipe Up (↑)                       │
│  = Focus Near (closer)              │
│                                     │
│  Swipe Down (↓)                     │
│  = Focus Far (distant)              │
└─────────────────────────────────────┘
```

**Implementation:**
```kotlin
override fun onScaleBegin(detector: ScaleGestureDetector): Boolean {
    if (detector.pointerCount == 2) {
        // Two-finger gesture detected
        return true
    }
    return false
}

override fun onScale(detector: ScaleGestureDetector): Boolean {
    val deltaY = detector.currentSpanY - detector.previousSpanY

    when {
        deltaY > FOCUS_THRESHOLD -> sendFocusCommand("near", currentSpeed)
        deltaY < -FOCUS_THRESHOLD -> sendFocusCommand("far", currentSpeed)
    }
    return true
}

override fun onScaleEnd(detector: ScaleGestureDetector) {
    sendFocusCommand("stop", 0)
}
```

---

## Implementation Guide

### Step 1: Protocol Client Extension

**File:** `app/src/main/java/com/dpm/gcs/protocol/DPMProtocolClient.kt`

Add focus command methods:

```kotlin
/**
 * Send manual focus command to camera
 *
 * @param action Focus direction: "near", "far", or "stop"
 * @param speed Focus speed: 1 (slow), 2 (medium), 3 (fast)
 * @return Command sequence ID
 */
suspend fun sendFocusCommand(
    action: String,
    speed: Int = 3
): Result<CommandResponse> {
    require(action in listOf("near", "far", "stop")) {
        "Invalid focus action: $action"
    }
    require(speed in 1..3) {
        "Invalid focus speed: $speed (must be 1-3)"
    }

    val payload = buildJsonObject {
        put("action", action)
        if (action != "stop") {
            put("speed", speed)
        }
    }

    return sendCommand("camera.focus", payload)
}

/**
 * Send auto-focus hold command (AF-ON button simulation)
 *
 * @param state Button state: "press" or "release"
 * @return Command sequence ID
 */
suspend fun sendAutoFocusHold(
    state: String
): Result<CommandResponse> {
    require(state in listOf("press", "release")) {
        "Invalid AF state: $state"
    }

    val payload = buildJsonObject {
        put("state", state)
    }

    return sendCommand("camera.auto_focus_hold", payload)
}
```

---

### Step 2: Focus Control ViewModel

**File:** `app/src/main/java/com/dpm/gcs/ui/camera/FocusControlViewModel.kt`

```kotlin
class FocusControlViewModel(
    private val protocolClient: DPMProtocolClient
) : ViewModel() {

    // Observable state
    private val _focusState = MutableStateFlow(FocusState.IDLE)
    val focusState: StateFlow<FocusState> = _focusState.asStateFlow()

    private val _currentSpeed = MutableStateFlow(3)
    val currentSpeed: StateFlow<Int> = _currentSpeed.asStateFlow()

    private val _errorMessage = MutableSharedFlow<String>()
    val errorMessage: SharedFlow<String> = _errorMessage.asSharedFlow()

    // Manual focus operations
    fun startFocusNear(speed: Int = _currentSpeed.value) {
        viewModelScope.launch {
            _focusState.value = FocusState.FOCUSING_NEAR

            protocolClient.sendFocusCommand("near", speed)
                .onSuccess {
                    Timber.d("Focus NEAR started at speed $speed")
                }
                .onFailure { error ->
                    _focusState.value = FocusState.IDLE
                    _errorMessage.emit("Focus failed: ${error.message}")
                    Timber.e(error, "Failed to start focus near")
                }
        }
    }

    fun startFocusFar(speed: Int = _currentSpeed.value) {
        viewModelScope.launch {
            _focusState.value = FocusState.FOCUSING_FAR

            protocolClient.sendFocusCommand("far", speed)
                .onSuccess {
                    Timber.d("Focus FAR started at speed $speed")
                }
                .onFailure { error ->
                    _focusState.value = FocusState.IDLE
                    _errorMessage.emit("Focus failed: ${error.message}")
                    Timber.e(error, "Failed to start focus far")
                }
        }
    }

    fun stopFocus() {
        viewModelScope.launch {
            _focusState.value = FocusState.STOPPING

            protocolClient.sendFocusCommand("stop")
                .onSuccess {
                    _focusState.value = FocusState.IDLE
                    Timber.d("Focus stopped")
                }
                .onFailure { error ->
                    _focusState.value = FocusState.IDLE
                    _errorMessage.emit("Failed to stop focus: ${error.message}")
                    Timber.e(error, "Failed to stop focus")
                }
        }
    }

    fun setSpeed(speed: Int) {
        require(speed in 1..3) { "Speed must be 1-3" }
        _currentSpeed.value = speed
    }

    // Auto-focus operations
    fun pressAutoFocus() {
        viewModelScope.launch {
            protocolClient.sendAutoFocusHold("press")
                .onSuccess {
                    Timber.d("Auto-focus engaged")
                }
                .onFailure { error ->
                    _errorMessage.emit("Auto-focus failed: ${error.message}")
                    Timber.e(error, "Failed to engage auto-focus")
                }
        }
    }

    fun releaseAutoFocus() {
        viewModelScope.launch {
            protocolClient.sendAutoFocusHold("release")
                .onSuccess {
                    Timber.d("Auto-focus released")
                }
                .onFailure { error ->
                    _errorMessage.emit("Failed to release auto-focus: ${error.message}")
                    Timber.e(error, "Failed to release auto-focus")
                }
        }
    }

    // Quick AF: press, wait 1s, release
    fun quickAutoFocus() {
        viewModelScope.launch {
            pressAutoFocus()
            delay(1000)
            releaseAutoFocus()
        }
    }
}

enum class FocusState {
    IDLE,
    FOCUSING_NEAR,
    FOCUSING_FAR,
    STOPPING
}
```

---

### Step 3: Manual Focus UI Component

**File:** `app/src/main/java/com/dpm/gcs/ui/camera/ManualFocusPanel.kt`

```kotlin
@Composable
fun ManualFocusPanel(
    viewModel: FocusControlViewModel = hiltViewModel(),
    enabled: Boolean = true
) {
    val focusState by viewModel.focusState.collectAsState()
    val currentSpeed by viewModel.currentSpeed.collectAsState()
    val context = LocalContext.current

    // Collect error messages
    LaunchedEffect(Unit) {
        viewModel.errorMessage.collect { message ->
            Toast.makeText(context, message, Toast.LENGTH_SHORT).show()
        }
    }

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp)
    ) {
        // Header
        Text(
            text = "MANUAL FOCUS",
            style = MaterialTheme.typography.titleSmall,
            fontWeight = FontWeight.Bold
        )

        Spacer(modifier = Modifier.height(8.dp))

        // Control buttons
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            // NEAR button
            FocusButton(
                text = "<<<\nNEAR",
                onClick = { /* Handled by press/release */ },
                onPressStart = { viewModel.startFocusNear() },
                onPressEnd = { viewModel.stopFocus() },
                enabled = enabled && focusState != FocusState.FOCUSING_FAR,
                isActive = focusState == FocusState.FOCUSING_NEAR,
                modifier = Modifier.weight(1f)
            )

            Spacer(modifier = Modifier.width(8.dp))

            // STOP button
            Button(
                onClick = { viewModel.stopFocus() },
                enabled = enabled && focusState != FocusState.IDLE,
                colors = ButtonDefaults.buttonColors(
                    containerColor = MaterialTheme.colorScheme.error
                ),
                modifier = Modifier.weight(1f)
            ) {
                Text("STOP")
            }

            Spacer(modifier = Modifier.width(8.dp))

            // FAR button
            FocusButton(
                text = ">>>\nFAR",
                onClick = { /* Handled by press/release */ },
                onPressStart = { viewModel.startFocusFar() },
                onPressEnd = { viewModel.stopFocus() },
                enabled = enabled && focusState != FocusState.FOCUSING_NEAR,
                isActive = focusState == FocusState.FOCUSING_FAR,
                modifier = Modifier.weight(1f)
            )

            Spacer(modifier = Modifier.width(8.dp))

            // Speed selector
            SpeedSelector(
                currentSpeed = currentSpeed,
                onSpeedChanged = { viewModel.setSpeed(it) },
                enabled = enabled,
                modifier = Modifier.weight(1f)
            )
        }

        // Status indicator
        if (focusState != FocusState.IDLE) {
            Spacer(modifier = Modifier.height(8.dp))

            LinearProgressIndicator(
                modifier = Modifier.fillMaxWidth()
            )

            Text(
                text = when (focusState) {
                    FocusState.FOCUSING_NEAR -> "Focusing NEAR at speed $currentSpeed"
                    FocusState.FOCUSING_FAR -> "Focusing FAR at speed $currentSpeed"
                    FocusState.STOPPING -> "Stopping focus..."
                    else -> ""
                },
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.primary
            )
        }
    }
}

@Composable
fun FocusButton(
    text: String,
    onClick: () -> Unit,
    onPressStart: () -> Unit,
    onPressEnd: () -> Unit,
    enabled: Boolean,
    isActive: Boolean,
    modifier: Modifier = Modifier
) {
    Button(
        onClick = onClick,
        enabled = enabled,
        colors = ButtonDefaults.buttonColors(
            containerColor = if (isActive) {
                MaterialTheme.colorScheme.primary
            } else {
                MaterialTheme.colorScheme.secondary
            }
        ),
        modifier = modifier
            .pointerInput(Unit) {
                detectTapGestures(
                    onPress = {
                        onPressStart()
                        tryAwaitRelease()
                        onPressEnd()
                    }
                )
            }
    ) {
        Text(
            text = text,
            textAlign = TextAlign.Center,
            fontSize = 12.sp
        )
    }
}

@Composable
fun SpeedSelector(
    currentSpeed: Int,
    onSpeedChanged: (Int) -> Unit,
    enabled: Boolean,
    modifier: Modifier = Modifier
) {
    var expanded by remember { mutableStateOf(false) }

    Box(modifier = modifier) {
        OutlinedButton(
            onClick = { expanded = true },
            enabled = enabled
        ) {
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Text("Speed", fontSize = 10.sp)
                Text(
                    text = when (currentSpeed) {
                        1 -> "SLOW"
                        2 -> "MED"
                        3 -> "FAST"
                        else -> currentSpeed.toString()
                    },
                    fontSize = 12.sp,
                    fontWeight = FontWeight.Bold
                )
            }
        }

        DropdownMenu(
            expanded = expanded,
            onDismissRequest = { expanded = false }
        ) {
            DropdownMenuItem(
                text = { Text("1 - Slow") },
                onClick = {
                    onSpeedChanged(1)
                    expanded = false
                }
            )
            DropdownMenuItem(
                text = { Text("2 - Medium") },
                onClick = {
                    onSpeedChanged(2)
                    expanded = false
                }
            )
            DropdownMenuItem(
                text = { Text("3 - Fast") },
                onClick = {
                    onSpeedChanged(3)
                    expanded = false
                }
            )
        }
    }
}
```

---

### Step 4: Auto-Focus Button Component

**File:** `app/src/main/java/com/dpm/gcs/ui/camera/AutoFocusButton.kt`

```kotlin
@Composable
fun AutoFocusButton(
    viewModel: FocusControlViewModel = hiltViewModel(),
    modifier: Modifier = Modifier
) {
    var isPressed by remember { mutableStateOf(false) }
    val context = LocalContext.current

    // Collect error messages
    LaunchedEffect(Unit) {
        viewModel.errorMessage.collect { message ->
            Toast.makeText(context, message, Toast.LENGTH_SHORT).show()
        }
    }

    FloatingActionButton(
        onClick = { viewModel.quickAutoFocus() },
        containerColor = if (isPressed) {
            Color(0xFF4CAF50) // Green when active
        } else {
            MaterialTheme.colorScheme.surface
        },
        modifier = modifier
            .size(64.dp)
            .pointerInput(Unit) {
                detectTapGestures(
                    onPress = {
                        isPressed = true
                        viewModel.pressAutoFocus()
                        tryAwaitRelease()
                        isPressed = false
                        viewModel.releaseAutoFocus()
                    }
                )
            }
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Icon(
                imageVector = Icons.Default.CenterFocusStrong,
                contentDescription = "Auto Focus",
                tint = if (isPressed) Color.White else Color.Black
            )
            Text(
                text = "AF",
                fontSize = 10.sp,
                fontWeight = FontWeight.Bold,
                color = if (isPressed) Color.White else Color.Black
            )
        }
    }
}
```

---

### Step 5: Integration with Camera Control Fragment

**File:** `app/src/main/java/com/dpm/gcs/ui/camera/CameraControlFragment.kt`

```kotlin
@Composable
fun CameraControlScreen(
    cameraViewModel: CameraViewModel,
    focusViewModel: FocusControlViewModel
) {
    val cameraStatus by cameraViewModel.cameraStatus.collectAsState()
    val focusMode = cameraStatus?.focusMode ?: "auto"

    Scaffold(
        floatingActionButton = {
            // AF button always visible (works in any AF mode)
            AutoFocusButton(viewModel = focusViewModel)
        }
    ) { padding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            // Existing camera controls
            item {
                ExposureControls(viewModel = cameraViewModel)
            }

            item {
                WhiteBalanceControls(viewModel = cameraViewModel)
            }

            // Manual focus controls (only show when in manual mode)
            if (focusMode == "manual") {
                item {
                    Divider()
                    ManualFocusPanel(
                        viewModel = focusViewModel,
                        enabled = cameraStatus?.isConnected == true
                    )
                }
            }
        }
    }
}
```

---

## Testing Strategy

### Unit Tests

**File:** `app/src/test/java/com/dpm/gcs/ui/camera/FocusControlViewModelTest.kt`

```kotlin
@Test
fun `startFocusNear should send near command with current speed`() = runTest {
    // Arrange
    val viewModel = FocusControlViewModel(mockProtocolClient)
    viewModel.setSpeed(2)

    coEvery {
        mockProtocolClient.sendFocusCommand("near", 2)
    } returns Result.success(mockResponse)

    // Act
    viewModel.startFocusNear()

    // Assert
    assertEquals(FocusState.FOCUSING_NEAR, viewModel.focusState.value)
    coVerify { mockProtocolClient.sendFocusCommand("near", 2) }
}

@Test
fun `stopFocus should transition to IDLE state`() = runTest {
    // Arrange
    val viewModel = FocusControlViewModel(mockProtocolClient)

    coEvery {
        mockProtocolClient.sendFocusCommand("stop")
    } returns Result.success(mockResponse)

    // Act
    viewModel.stopFocus()
    advanceUntilIdle()

    // Assert
    assertEquals(FocusState.IDLE, viewModel.focusState.value)
}

@Test
fun `quickAutoFocus should press, wait, then release`() = runTest {
    // Arrange
    val viewModel = FocusControlViewModel(mockProtocolClient)

    coEvery {
        mockProtocolClient.sendAutoFocusHold(any())
    } returns Result.success(mockResponse)

    // Act
    viewModel.quickAutoFocus()
    advanceTimeBy(1100) // Wait for 1 second delay

    // Assert
    coVerify(exactly = 1) { mockProtocolClient.sendAutoFocusHold("press") }
    coVerify(exactly = 1) { mockProtocolClient.sendAutoFocusHold("release") }
}
```

### Integration Tests

**Test Scenarios:**

1. **Manual Focus Flow:**
   ```
   1. Switch camera to manual focus mode
   2. Tap and hold NEAR button
   3. Verify focus command sent with action="near"
   4. Release button
   5. Verify stop command sent
   6. Verify UI returns to idle state
   ```

2. **Speed Change:**
   ```
   1. Select speed = 1 (slow)
   2. Tap and hold FAR button
   3. Verify command includes speed=1
   4. Change speed to 3 while focusing
   5. Release and press again
   6. Verify new command includes speed=3
   ```

3. **Auto-Focus:**
   ```
   1. Tap AF button
   2. Verify press command sent
   3. Wait 1 second
   4. Verify release command sent
   5. Verify button returns to normal state
   ```

4. **Error Handling:**
   ```
   1. Disconnect camera
   2. Try to focus
   3. Verify error message displayed
   4. Verify UI returns to safe state
   ```

### Manual Testing Checklist

**Hardware Setup:**
- [ ] Sony camera connected via USB to Air-Side SBC
- [ ] Air-Side container running (payload-manager:latest)
- [ ] Android GCS connected to Air-Side via TCP (port 5000)
- [ ] Camera in manual focus mode for manual focus tests
- [ ] Camera in AF-S or AF-C mode for auto-focus tests

**Test Cases:**

**TC-001: Manual Focus Near**
1. Open camera controls
2. Verify "MANUAL FOCUS" panel visible (camera must be in manual mode)
3. Press and hold NEAR button for 2 seconds
4. Observe camera lens moving to focus closer
5. Release button
6. Verify lens stops moving
7. Result: PASS / FAIL

**TC-002: Manual Focus Far**
1. Press and hold FAR button for 2 seconds
2. Observe camera lens moving to focus further away
3. Release button
4. Verify lens stops moving
5. Result: PASS / FAIL

**TC-003: Focus Speed Control**
1. Select speed = 1 (slow)
2. Press NEAR button, observe slow movement
3. Release and select speed = 3 (fast)
4. Press NEAR button, observe faster movement
5. Result: PASS / FAIL

**TC-004: Emergency Stop**
1. Hold FAR button to start focusing
2. While focus is active, tap STOP button
3. Verify focus immediately stops
4. Result: PASS / FAIL

**TC-005: Auto-Focus Quick Tap**
1. Point camera at subject
2. Single-tap AF button
3. Observe camera attempting to focus
4. Verify AF button shows green indication
5. After ~1 second, verify button returns to normal
6. Result: PASS / FAIL

**TC-006: Auto-Focus Press & Hold**
1. Press and hold AF button
2. Observe continuous AF attempt
3. Release button
4. Verify AF stops
5. Result: PASS / FAIL

**TC-007: Error - Camera Not Connected**
1. Disconnect camera (power off or unplug USB)
2. Try to use focus controls
3. Verify error toast: "Focus failed: Camera not connected"
4. Verify controls return to safe state
5. Result: PASS / FAIL

**TC-008: Error - Wrong Focus Mode**
1. Set camera to auto-focus mode (AF-S or AF-C)
2. Try to use manual focus NEAR/FAR buttons
3. Verify error: "Camera not in manual focus mode"
4. Verify AF button still works
5. Result: PASS / FAIL

---

## Error Handling

### Client-Side Validation

**Before sending commands:**
```kotlin
fun validateFocusCommand(action: String, speed: Int): ValidationResult {
    return when {
        action !in listOf("near", "far", "stop") ->
            ValidationResult.Error("Invalid action: $action")

        speed !in 1..3 ->
            ValidationResult.Error("Speed must be 1-3, got: $speed")

        !isCameraConnected() ->
            ValidationResult.Error("Camera not connected")

        action != "stop" && !isManualFocusMode() ->
            ValidationResult.Error("Manual focus requires camera in MF mode")

        else ->
            ValidationResult.Valid
    }
}
```

### Error Code Mapping

```kotlin
object FocusErrorMessages {
    fun getMessage(errorCode: Int): String = when (errorCode) {
        1000 -> "Camera not connected. Please check connection."
        3001 -> "Camera must be in manual focus mode. Switch to MF first."
        3002 -> "Invalid focus action. Please try again."
        3003 -> "Invalid speed setting. Please select 1-3."
        3004 -> "Focus operation failed. Check camera status."
        3005 -> "Auto-focus failed. Ensure camera is ready."
        3006 -> "Invalid AF state. Please try again."
        else -> "Unknown error (code: $errorCode)"
    }
}
```

### Retry Strategy

```kotlin
suspend fun sendFocusCommandWithRetry(
    action: String,
    speed: Int,
    maxRetries: Int = 2
): Result<CommandResponse> {
    repeat(maxRetries) { attempt ->
        val result = protocolClient.sendFocusCommand(action, speed)

        if (result.isSuccess) {
            return result
        }

        val error = result.exceptionOrNull()

        // Don't retry validation errors
        if (error is ValidationException) {
            return result
        }

        // Retry on timeout or network errors
        if (attempt < maxRetries - 1) {
            Timber.w("Focus command failed (attempt ${attempt + 1}), retrying...")
            delay(500) // Wait before retry
        }
    }

    return Result.failure(Exception("Focus command failed after $maxRetries attempts"))
}
```

---

## Implementation Checklist

### Phase 1: Core Protocol (Week 1)
- [ ] Add `sendFocusCommand()` to DPMProtocolClient
- [ ] Add `sendAutoFocusHold()` to DPMProtocolClient
- [ ] Write unit tests for protocol methods
- [ ] Test with mock Air-Side responses

### Phase 2: ViewModel & State Management (Week 1-2)
- [ ] Create `FocusControlViewModel`
- [ ] Implement state management (FocusState enum)
- [ ] Add error handling and retry logic
- [ ] Write ViewModel unit tests

### Phase 3: UI Components (Week 2)
- [ ] Create `ManualFocusPanel` composable
- [ ] Create `AutoFocusButton` composable
- [ ] Implement `FocusButton` with press/hold detection
- [ ] Implement `SpeedSelector` dropdown
- [ ] Add UI tests

### Phase 4: Integration (Week 2-3)
- [ ] Integrate with `CameraControlFragment`
- [ ] Add focus mode detection logic
- [ ] Wire up enable/disable states
- [ ] Test with real hardware

### Phase 5: Polish & Testing (Week 3)
- [ ] Add visual feedback animations
- [ ] Implement touch gesture support (optional)
- [ ] Conduct integration testing
- [ ] Conduct field testing with drone
- [ ] Document any issues or limitations

### Phase 6: Documentation (Week 3)
- [ ] Update user manual with focus controls
- [ ] Create training video/screenshots
- [ ] Document known issues
- [ ] Prepare release notes

---

## Expected Limitations & Notes

### Known Limitations

1. **Focus Speed Parameter:**
   - Speed parameter (1-3) is accepted by Air-Side but not currently applied
   - Sony SDK v2.00 doesn't expose focus driving speed control
   - Future SDK updates may enable this feature
   - For now, camera uses default/hardware-controlled speed

2. **Focus Position Feedback:**
   - Current implementation doesn't return focus position
   - Future enhancement: read `CrDeviceProperty_FocusPositionCurrentValue`
   - This would enable focus position slider UI

3. **Manual Focus Mode Requirement:**
   - `camera.focus` (near/far/stop) only works when camera is in Manual Focus (MF) mode
   - AF-S and AF-C modes use `camera.auto_focus_hold` instead
   - GCS should detect current focus mode and show appropriate controls

### Performance Considerations

- **Command Rate Limiting:** Don't send more than 10 focus commands per second
- **Network Latency:** Expect 50-200ms round-trip time over WiFi
- **Continuous Focus:** For smooth focus, send near/far once and let it run until user releases
- **Battery Impact:** Continuous manual focus can drain camera battery faster

---

## Questions & Support

**Contact:** DPM Development Team
**Slack:** #dpm-development
**Issue Tracker:** https://github.com/your-org/DPM-V2/issues

**Common Questions:**

**Q: Can I test without physical camera hardware?**
A: Yes, you can use the Air-Side mock mode. Set `CAMERA_MODE=stub` in the Air-Side container environment.

**Q: What happens if I send "near" while already focusing "far"?**
A: The Air-Side will accept the new command and change direction immediately. The previous operation is cancelled.

**Q: Does auto-focus hold work in manual focus mode?**
A: Yes, but camera must briefly switch to AF internally. Results may vary by camera model.

**Q: How do I debug protocol issues?**
A: Enable protocol logging in DPMProtocolClient. Check Air-Side logs: `docker logs -f payload-manager`

---

## Appendix: Wire Protocol Examples

### Example 1: Full Manual Focus Session

```json
// 1. User presses NEAR button (speed=2)
→ {
  "seq_id": 100,
  "command": "camera.focus",
  "payload": {"action": "near", "speed": 2}
}

← {
  "seq_id": 100,
  "command": "camera.focus",
  "status": "success",
  "result": {"action": "near", "speed": 2}
}

// 2. User releases button after 2 seconds
→ {
  "seq_id": 101,
  "command": "camera.focus",
  "payload": {"action": "stop"}
}

← {
  "seq_id": 101,
  "command": "camera.focus",
  "status": "success",
  "result": {"action": "stop", "speed": 2}
}

// 3. User presses FAR button (speed=3)
→ {
  "seq_id": 102,
  "command": "camera.focus",
  "payload": {"action": "far", "speed": 3}
}

← {
  "seq_id": 102,
  "command": "camera.focus",
  "status": "success",
  "result": {"action": "far", "speed": 3}
}
```

### Example 2: Auto-Focus Quick Tap

```json
// 1. User taps AF button (press phase)
→ {
  "seq_id": 200,
  "command": "camera.auto_focus_hold",
  "payload": {"state": "press"}
}

← {
  "seq_id": 200,
  "command": "camera.auto_focus_hold",
  "status": "success",
  "result": {"state": "press"}
}

// 2. After 1 second (release phase)
→ {
  "seq_id": 201,
  "command": "camera.auto_focus_hold",
  "payload": {"state": "release"}
}

← {
  "seq_id": 201,
  "command": "camera.auto_focus_hold",
  "status": "success",
  "result": {"state": "release"}
}
```

### Example 3: Error Handling

```json
// Attempt manual focus when camera is in AF mode
→ {
  "seq_id": 300,
  "command": "camera.focus",
  "payload": {"action": "near", "speed": 3}
}

← {
  "seq_id": 300,
  "command": "camera.focus",
  "status": "error",
  "error": {
    "code": 3001,
    "message": "Camera not in manual focus mode"
  }
}
```

---

**End of Ground-Side Implementation Guide**

**Document Version:** 1.0
**Last Updated:** 2025-10-31
**Air-Side Version:** 1.2.0 (Implemented)
**Ground-Side Target Version:** 1.2.0 (To Be Implemented)
