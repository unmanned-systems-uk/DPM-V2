Ground-Side RTSP Video Stream - Instructions for Claude Code (Android)
📋 Document Purpose
This document provides complete instructions for Claude Code (Android Studio) to implement RTSP video streaming display in the DPM Android app.

🎯 Mission Statement
Objective: Display RTSP video stream from R16 Air Unit as full-screen background on Camera screen with semi-transparent overlay controls.
RTSP URL: rtsp://192.168.1.10:8554/H264Video (R16 default, will be configurable)
Air-Side Status: ✅ Already working - R16 Air Unit provides RTSP stream via hardware encoder (Camera HDMI → R16)

🏗️ Architecture Overview
┌────────────────────────────────────────────────────────────┐
│                     GROUND SIDE (H16)                      │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │           Android App (DPM)                          │ │
│  │                                                      │ │
│  │  ┌────────────────────────────────────────────────┐ │ │
│  │  │         Camera Screen (Composable)             │ │ │
│  │  │                                                │ │ │
│  │  │  ┌──────────────────────────────────────────┐ │ │ │
│  │  │  │ Layer 1: Full-Screen Video (Background) │ │ │ │
│  │  │  │                                          │ │ │ │
│  │  │  │  ExoPlayer (RTSP Client)                 │ │ │ │
│  │  │  │  - Hardware accelerated decoding         │ │ │ │
│  │  │  │  - Auto aspect ratio                     │ │ │ │
│  │  │  │  - Fills entire screen                   │ │ │ │
│  │  │  │                                          │ │ │ │
│  │  │  └──────────────────────────────────────────┘ │ │ │
│  │  │                                                │ │ │
│  │  │  ┌──────────────────────────────────────────┐ │ │ │
│  │  │  │ Layer 2: Controls Overlay (Foreground)  │ │ │ │
│  │  │  │                                          │ │ │ │
│  │  │  │  ┌────────────┐   "Camera Live View"    │ │ │ │
│  │  │  │  │ Settings   │                          │ │ │ │
│  │  │  │  │ Panel      │   [Capture Button]      │ │ │ │
│  │  │  │  │ • Shutter  │                          │ │ │ │
│  │  │  │  │ • ISO      │   [AWB] [JPEG]  🔋 Menu │ │ │ │
│  │  │  │  └────────────┘                          │ │ │ │
│  │  │  │                                          │ │ │ │
│  │  │  │  Semi-transparent background (alpha)    │ │ │ │
│  │  │  └──────────────────────────────────────────┘ │ │ │
│  │  │                                                │ │ │
│  │  └────────────────────────────────────────────────┘ │ │
│  │                                                      │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
└────────────────────────────────────────────────────────────┘
                            ▲
                            │
                            │ RTSP Stream
                            │ rtsp://192.168.1.10:8554/H264Video
                            │
                ┌───────────┴──────────┐
                │   R16 Air Unit       │
                │   (Hardware Encoder) │
                │   Already Working ✅ │
                └──────────────────────┘
```

---

## 📱 UI Design Reference

Based on uploaded mockup `Camera_UI.jpg`:
```
┌─────────────────────────────────────────┐
│  [Full-Screen RTSP Video Background]    │
│                                         │
│  ┌──────────────┐                       │
│  │ ● Air-Side   │  "Camera Live View"   │
│  │   Connected  │                       │
│  │              │                       │
│  │ ▶  1/125     │                       │
│  │ ƒ  4.0       │                       │
│  │ ISO 800      │                       │
│  └──────────────┘                       │
│                                         │
│                                         │
│                    ⭕                   │
│                 [Capture]               │
│                                         │
│  [AWB]  [JPEG]            🔋 100%  ☰   │
└─────────────────────────────────────────┘
Key UI Elements:

Full-screen video - fills entire screen, always visible
Settings panel (top-left) - camera parameters with status indicator
Title (top-center) - "Camera Live View"
Capture button (center-bottom) - large circular button
File format buttons (bottom-left) - AWB, JPEG toggles
Status indicators (bottom-right) - battery, menu


🔧 Implementation Tasks
Task 1: Add ExoPlayer Dependencies (5 min)
File: android/app/build.gradle.kts
Action: Add ExoPlayer libraries
kotlindependencies {
    // Existing dependencies...
    
    // ExoPlayer for RTSP video streaming
    implementation("androidx.media3:media3-exoplayer:1.2.0")
    implementation("androidx.media3:media3-ui:1.2.0")
    implementation("androidx.media3:media3-exoplayer-rtsp:1.2.0")
}
Verification: Sync Gradle successfully

Task 2: Create Video Stream Settings (10 min)
File: android/app/src/main/java/com/dpm/data/VideoStreamSettings.kt (NEW)
kotlinpackage com.dpm.data

data class VideoStreamSettings(
    val rtspUrl: String = "rtsp://192.168.1.10:8554/H264Video",
    val autoConnect: Boolean = true,
    val aspectRatioMode: AspectRatioMode = AspectRatioMode.AUTO,
    val lowLatencyMode: Boolean = true
)

enum class AspectRatioMode {
    AUTO,   // Detect from stream
    FILL,   // Fill entire screen
    FIT     // Fit to screen maintaining aspect
}

Task 3: Add Video Settings to DataStore (15 min)
File: android/app/src/main/java/com/dpm/data/SettingsRepository.kt
Action: Extend existing repository
kotlin// Add to existing SettingsRepository.kt

// Add DataStore keys
private val VIDEO_RTSP_URL = stringPreferencesKey("video_rtsp_url")
private val VIDEO_AUTO_CONNECT = booleanPreferencesKey("video_auto_connect")
private val VIDEO_ASPECT_RATIO = stringPreferencesKey("video_aspect_ratio")
private val VIDEO_LOW_LATENCY = booleanPreferencesKey("video_low_latency")

// Add to existing Settings data class
data class Settings(
    // ... existing fields ...
    val videoStreamSettings: VideoStreamSettings = VideoStreamSettings()
)

// Add save function
suspend fun saveVideoStreamSettings(settings: VideoStreamSettings) {
    dataStore.edit { preferences ->
        preferences[VIDEO_RTSP_URL] = settings.rtspUrl
        preferences[VIDEO_AUTO_CONNECT] = settings.autoConnect
        preferences[VIDEO_ASPECT_RATIO] = settings.aspectRatioMode.name
        preferences[VIDEO_LOW_LATENCY] = settings.lowLatencyMode
    }
}

// Update getSettings() flow to include video settings
val getSettings: Flow<Settings> = dataStore.data
    .catch { exception ->
        if (exception is IOException) {
            emit(emptyPreferences())
        } else {
            throw exception
        }
    }
    .map { preferences ->
        Settings(
            // ... existing fields ...
            videoStreamSettings = VideoStreamSettings(
                rtspUrl = preferences[VIDEO_RTSP_URL] 
                    ?: "rtsp://192.168.1.10:8554/H264Video",
                autoConnect = preferences[VIDEO_AUTO_CONNECT] ?: true,
                aspectRatioMode = AspectRatioMode.valueOf(
                    preferences[VIDEO_ASPECT_RATIO] ?: "AUTO"
                ),
                lowLatencyMode = preferences[VIDEO_LOW_LATENCY] ?: true
            )
        )
    }

Task 4: Create VideoPlayerViewModel (30 min)
File: android/app/src/main/java/com/dpm/viewmodel/VideoPlayerViewModel.kt (NEW)
kotlinpackage com.dpm.viewmodel

import android.content.Context
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import androidx.media3.common.MediaItem
import androidx.media3.common.PlaybackException
import androidx.media3.common.Player
import androidx.media3.exoplayer.ExoPlayer
import androidx.media3.exoplayer.rtsp.RtspMediaSource
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class VideoPlayerViewModel : ViewModel() {

    private val _videoState = MutableStateFlow<VideoState>(VideoState.Disconnected)
    val videoState: StateFlow<VideoState> = _videoState.asStateFlow()

    private var exoPlayer: ExoPlayer? = null

    sealed class VideoState {
        object Disconnected : VideoState()
        object Connecting : VideoState()
        data class Connected(val resolution: String = "Unknown") : VideoState()
        data class Error(val message: String) : VideoState()
    }

    fun initializePlayer(context: Context, rtspUrl: String) {
        viewModelScope.launch {
            try {
                _videoState.value = VideoState.Connecting

                exoPlayer = ExoPlayer.Builder(context)
                    .build()
                    .apply {
                        val mediaItem = MediaItem.fromUri(rtspUrl)
                        setMediaItem(mediaItem)
                        
                        // Add player listener
                        addListener(object : Player.Listener {
                            override fun onPlaybackStateChanged(playbackState: Int) {
                                when (playbackState) {
                                    Player.STATE_READY -> {
                                        val videoFormat = videoFormat
                                        val resolution = if (videoFormat != null) {
                                            "${videoFormat.width}x${videoFormat.height}"
                                        } else {
                                            "Unknown"
                                        }
                                        _videoState.value = VideoState.Connected(resolution)
                                    }
                                    Player.STATE_BUFFERING -> {
                                        _videoState.value = VideoState.Connecting
                                    }
                                }
                            }

                            override fun onPlayerError(error: PlaybackException) {
                                _videoState.value = VideoState.Error(
                                    error.message ?: "Unknown playback error"
                                )
                            }
                        })
                        
                        prepare()
                        play()
                    }
            } catch (e: Exception) {
                _videoState.value = VideoState.Error(e.message ?: "Failed to initialize player")
            }
        }
    }

    fun releasePlayer() {
        exoPlayer?.release()
        exoPlayer = null
        _videoState.value = VideoState.Disconnected
    }

    fun getPlayer(): ExoPlayer? = exoPlayer

    override fun onCleared() {
        super.onCleared()
        releasePlayer()
    }
}

Task 5: Create FullScreenVideoPlayer Composable
File: android/app/src/main/java/com/dpm/ui/components/VideoPlayer.kt (NEW)
kotlinpackage com.dpm.ui.components

import android.view.ViewGroup
import android.widget.FrameLayout
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.media3.ui.PlayerView
import com.dpm.viewmodel.VideoPlayerViewModel

@Composable
fun FullScreenVideoPlayer(
    rtspUrl: String,
    modifier: Modifier = Modifier,
    videoPlayerViewModel: VideoPlayerViewModel = viewModel()
) {
    val context = LocalContext.current
    val videoState by videoPlayerViewModel.videoState.collectAsState()

    // Initialize player when composable enters composition
    LaunchedEffect(rtspUrl) {
        videoPlayerViewModel.initializePlayer(context, rtspUrl)
    }

    // Release player when composable leaves composition
    DisposableEffect(Unit) {
        onDispose {
            videoPlayerViewModel.releasePlayer()
        }
    }

    Box(modifier = modifier.fillMaxSize()) {
        // Video player view
        AndroidView(
            factory = { context ->
                PlayerView(context).apply {
                    player = videoPlayerViewModel.getPlayer()
                    useController = false // Hide default controls
                    layoutParams = FrameLayout.LayoutParams(
                        ViewGroup.LayoutParams.MATCH_PARENT,
                        ViewGroup.LayoutParams.MATCH_PARENT
                    )
                    // Set resize mode to fill
                    resizeMode = androidx.media3.ui.AspectRatioFrameLayout.RESIZE_MODE_FILL
                }
            },
            update = { playerView ->
                playerView.player = videoPlayerViewModel.getPlayer()
            },
            modifier = Modifier.fillMaxSize()
        )

        // Show loading/error states over video
        when (val state = videoState) {
            is VideoPlayerViewModel.VideoState.Disconnected -> {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .background(Color.Black),
                    contentAlignment = Alignment.Center
                ) {
                    Text("Video Disconnected", color = Color.White)
                }
            }
            is VideoPlayerViewModel.VideoState.Connecting -> {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .background(Color.Black.copy(alpha = 0.7f)),
                    contentAlignment = Alignment.Center
                ) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        CircularProgressIndicator(color = Color.White)
                        Spacer(modifier = Modifier.height(16.dp))
                        Text("Connecting to video stream...", color = Color.White)
                    }
                }
            }
            is VideoPlayerViewModel.VideoState.Error -> {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .background(Color.Black),
                    contentAlignment = Alignment.Center
                ) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("Video Error", color = Color.Red)
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(state.message, color = Color.White)
                    }
                }
            }
            is VideoPlayerViewModel.VideoState.Connected -> {
                // Video is playing - no overlay needed
            }
        }
    }
}

Task 6: Update CameraScreen with Video Background 
File: android/app/src/main/java/com/dpm/ui/screens/CameraScreen.kt
Action: Refactor to use Box layout with video background and overlay controls
kotlinpackage com.dpm.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Menu
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.dpm.data.SettingsRepository
import com.dpm.ui.components.FullScreenVideoPlayer
import com.dpm.viewmodel.CameraViewModel
import com.dpm.viewmodel.VideoPlayerViewModel

@Composable
fun CameraScreen(
    cameraViewModel: CameraViewModel = viewModel(),
    videoPlayerViewModel: VideoPlayerViewModel = viewModel(),
    settingsRepository: SettingsRepository,
    onMenuClick: () -> Unit = {}
) {
    // Get video settings from repository
    val settings by settingsRepository.getSettings.collectAsState(initial = null)
    val videoSettings = settings?.videoStreamSettings

    Box(modifier = Modifier.fillMaxSize()) {
        // Layer 1: Full-screen video background
        if (videoSettings?.autoConnect == true) {
            FullScreenVideoPlayer(
                rtspUrl = videoSettings.rtspUrl,
                modifier = Modifier.fillMaxSize(),
                videoPlayerViewModel = videoPlayerViewModel
            )
        } else {
            // Placeholder if video disabled
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(Color.Black),
                contentAlignment = Alignment.Center
            ) {
                Text("Video Disabled", color = Color.White)
            }
        }

        // Layer 2: Semi-transparent overlay with controls
        CameraControlsOverlay(
            cameraViewModel = cameraViewModel,
            onMenuClick = onMenuClick,
            modifier = Modifier.fillMaxSize()
        )
    }
}

@Composable
fun CameraControlsOverlay(
    cameraViewModel: CameraViewModel,
    onMenuClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Box(modifier = modifier) {
        // Optional: Subtle darkening for better text visibility
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(Color.Black.copy(alpha = 0.2f))
        )

        // Top-left: Settings panel
        CameraSettingsPanel(
            cameraViewModel = cameraViewModel,
            modifier = Modifier
                .align(Alignment.TopStart)
                .padding(16.dp)
        )

        // Top-center: Title
        Text(
            text = "Camera Live View",
            color = Color.White,
            fontSize = 24.sp,
            modifier = Modifier
                .align(Alignment.TopCenter)
                .padding(top = 16.dp)
        )

        // Center-bottom: Capture button
        FloatingActionButton(
            onClick = { cameraViewModel.captureImage() },
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .padding(bottom = 80.dp)
                .size(72.dp),
            shape = CircleShape,
            containerColor = Color.White.copy(alpha = 0.9f)
        ) {
            // Circle icon (camera shutter)
            Box(
                modifier = Modifier
                    .size(60.dp)
                    .background(Color.Transparent),
                contentAlignment = Alignment.Center
            ) {
                Box(
                    modifier = Modifier
                        .size(50.dp)
                        .background(Color.White, CircleShape)
                )
            }
        }

        // Bottom-left: File format buttons
        Row(
            modifier = Modifier
                .align(Alignment.BottomStart)
                .padding(16.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            FileFormatButton("AWB", onClick = { /* TODO */ })
            FileFormatButton("JPEG", onClick = { /* TODO */ })
        }

        // Bottom-right: Battery and menu
        Row(
            modifier = Modifier
                .align(Alignment.BottomEnd)
                .padding(16.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            BatteryIndicator(level = 100)
            IconButton(onClick = onMenuClick) {
                Icon(
                    imageVector = Icons.Default.Menu,
                    contentDescription = "Menu",
                    tint = Color.White
                )
            }
        }
    }
}

@Composable
fun CameraSettingsPanel(
    cameraViewModel: CameraViewModel,
    modifier: Modifier = Modifier
) {
    val cameraState by cameraViewModel.cameraState.collectAsState()
    val connectionState by cameraViewModel.connectionState.collectAsState()

    Column(
        modifier = modifier
            .background(
                Color.Black.copy(alpha = 0.6f),
                shape = MaterialTheme.shapes.medium
            )
            .padding(12.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        // Connection indicator
        Row(verticalAlignment = Alignment.CenterVertically) {
            Box(
                modifier = Modifier
                    .size(12.dp)
                    .background(
                        if (connectionState == CameraViewModel.ConnectionState.Connected)
                            Color.Green else Color.Red,
                        CircleShape
                    )
            )
            Spacer(modifier = Modifier.width(8.dp))
            Text(
                text = when (connectionState) {
                    CameraViewModel.ConnectionState.Connected -> "Air-Side Connected"
                    CameraViewModel.ConnectionState.Connecting -> "Connecting..."
                    else -> "Disconnected"
                },
                color = Color.White,
                fontSize = 12.sp
            )
        }

        Divider(color = Color.White.copy(alpha = 0.3f))

        // Camera settings
        SettingRow(label = "▶", value = cameraState.shutter)
        SettingRow(label = "ƒ", value = cameraState.aperture)
        SettingRow(label = "ISO", value = cameraState.iso.toString())
    }
}

@Composable
fun SettingRow(label: String, value: String) {
    Row(
        horizontalArrangement = Arrangement.spacedBy(8.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            text = label,
            color = Color.White,
            fontSize = 14.sp
        )
        Text(
            text = value,
            color = Color.White,
            fontSize = 14.sp
        )
    }
}

@Composable
fun FileFormatButton(text: String, onClick: () -> Unit = {}) {
    Button(
        onClick = onClick,
        colors = ButtonDefaults.buttonColors(
            containerColor = Color.White.copy(alpha = 0.8f)
        ),
        modifier = Modifier.height(36.dp)
    ) {
        Text(text = text, color = Color.Black, fontSize = 12.sp)
    }
}

@Composable
fun BatteryIndicator(level: Int) {
    Row(
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(4.dp)
    ) {
        Text(
            text = "🔋",
            fontSize = 18.sp
        )
        Text(
            text = "$level%",
            color = Color.White,
            fontSize = 14.sp
        )
    }
}

Task 7: Add Video Settings to SettingsScreen
File: android/app/src/main/java/com/dpm/ui/screens/SettingsScreen.kt
Action: Add video configuration section
kotlin// Add to existing SettingsScreen.kt

// Inside SettingsScreen composable, add new section:

// Video Stream Settings Section
Text(
    text = "Video Stream",
    style = MaterialTheme.typography.titleMedium,
    modifier = Modifier.padding(vertical = 8.dp)
)

OutlinedTextField(
    value = videoSettings.rtspUrl,
    onValueChange = { 
        viewModel.updateVideoSettings(
            videoSettings.copy(rtspUrl = it)
        )
    },
    label = { Text("RTSP URL") },
    modifier = Modifier.fillMaxWidth(),
    singleLine = true
)

Row(
    modifier = Modifier.fillMaxWidth(),
    horizontalArrangement = Arrangement.SpaceBetween,
    verticalAlignment = Alignment.CenterVertically
) {
    Text("Auto-connect on startup")
    Switch(
        checked = videoSettings.autoConnect,
        onCheckedChange = {
            viewModel.updateVideoSettings(
                videoSettings.copy(autoConnect = it)
            )
        }
    )
}

Row(
    modifier = Modifier.fillMaxWidth(),
    horizontalArrangement = Arrangement.SpaceBetween,
    verticalAlignment = Alignment.CenterVertically
) {
    Text("Low latency mode")
    Switch(
        checked = videoSettings.lowLatencyMode,
        onCheckedChange = {
            viewModel.updateVideoSettings(
                videoSettings.copy(lowLatencyMode = it)
            )
        }
    )
}

// Aspect ratio dropdown
ExposedDropdownMenuBox(
    expanded = aspectRatioExpanded,
    onExpandedChange = { aspectRatioExpanded = !aspectRatioExpanded }
) {
    OutlinedTextField(
        value = videoSettings.aspectRatioMode.name,
        onValueChange = {},
        readOnly = true,
        label = { Text("Aspect Ratio") },
        trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = aspectRatioExpanded) },
        modifier = Modifier
            .fillMaxWidth()
            .menuAnchor()
    )
    
    ExposedDropdownMenu(
        expanded = aspectRatioExpanded,
        onDismissRequest = { aspectRatioExpanded = false }
    ) {
        AspectRatioMode.values().forEach { mode ->
            DropdownMenuItem(
                text = { Text(mode.name) },
                onClick = {
                    viewModel.updateVideoSettings(
                        videoSettings.copy(aspectRatioMode = mode)
                    )
                    aspectRatioExpanded = false
                }
            )
        }
    }
}

Button(
    onClick = { /* Test connection */ },
    modifier = Modifier.fillMaxWidth()
) {
    Text("Test Video Connection")
}

Divider(modifier = Modifier.padding(vertical = 16.dp))

📋 Complete Implementation Checklist
Session 1: Video Integration 
Setup )

 Open project in Android Studio
 Read existing code structure (CameraScreen.kt, SettingsScreen.kt)
 Read CC_READ_THIS_FIRST.md for Git workflow
 Create new branch: feature/video-streaming
 Git commit: [SETUP] Create video streaming feature branch

Dependencies 

 Add ExoPlayer dependencies to build.gradle.kts
 Sync Gradle
 Verify no conflicts
 Git commit: [VIDEO] Add ExoPlayer dependencies

Data Layer 

 Create VideoStreamSettings.kt data class
 Update SettingsRepository.kt with video settings
 Add DataStore keys for video settings
 Test settings persistence
 Git commit: [VIDEO] Add video stream settings data layer

ViewModel 

 Create VideoPlayerViewModel.kt
 Implement ExoPlayer initialization
 Add player lifecycle management
 Add connection state handling
 Test ViewModel in isolation (if possible)
 Git commit: [VIDEO] Add VideoPlayerViewModel with ExoPlayer

Video Player Component 

 Create VideoPlayer.kt composable
 Implement FullScreenVideoPlayer with AndroidView
 Add loading/error states overlay
 Test with placeholder URL
 Git commit: [VIDEO] Add FullScreenVideoPlayer composable

Camera Screen Refactor 

 Backup existing CameraScreen.kt
 Refactor to Box layout (video + overlay)
 Create CameraControlsOverlay composable
 Create CameraSettingsPanel composable
 Style with semi-transparent backgrounds
 Add all UI components (capture button, file format, battery)
 Test layout in preview/emulator
 Git commit: [VIDEO] Refactor CameraScreen with video background

Settings Screen )

 Add video settings section to SettingsScreen.kt
 Add RTSP URL input field
 Add auto-connect toggle
 Add aspect ratio dropdown
 Add test connection button (placeholder)
 Git commit: [VIDEO] Add video settings to SettingsScreen

Testing & Polish 

 Test with R16 hardware (if available)
 Test with test RTSP URL: rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mp4
 Verify overlay transparency
 Verify controls are readable over video
 Test settings persistence (restart app)
 Test video reconnection after network interruption
 Git commit: [VIDEO] Testing and UI polish

Documentation 

 Update PROGRESS_AND_TODO.md (Ground-Side)
 Add comments to complex code sections
 Document any known issues
 Git commit: [DOCS] Update progress documentation

Final Review 

 Code review (check for best practices)
 Verify all Git commits are descriptive
 Create pull request (if using PR workflow)
 Git commit: [VIDEO] Complete video streaming feature


🧪 Testing Instructions
Test 1: Test with Public RTSP Stream (No Hardware Required)
kotlin// In SettingsScreen or directly in CameraScreen for testing
val testRtspUrl = "rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mp4"

// Should see Big Buck Bunny video playing
Test 2: Test with R16 Hardware
kotlin// Default R16 URL (may need to adjust based on network)
val r16RtspUrl = "rtsp://192.168.1.10:8554/H264Video"

// Check:
// - Video appears within 2-3 seconds
// - Full screen display
// - Controls visible over video
// - No lag/stuttering
Test 3: Test Network Interruption

Start video streaming
Disable WiFi temporarily
Re-enable WiFi
Verify: Video should reconnect automatically

Test 4: Test Settings Persistence

Change RTSP URL in settings
Toggle auto-connect off
Close app completely
Reopen app
Verify: Settings should be preserved

Test 5: Test UI Overlay Visibility

Start video streaming
Check all controls are readable:

Settings panel (top-left)
Title (top-center)
Capture button (bottom-center)
File format buttons (bottom-left)
Battery indicator (bottom-right)


Verify semi-transparent backgrounds work


⚠️ Known Issues & Solutions
Issue 1: RTSP Connection Timeout
Symptom: "Connecting..." for >10 seconds, then error
Solutions:

Check R16 is powered on and HDMI connected
Verify network connectivity (ping 192.168.1.10)
Check RTSP URL format is correct
Try test URL to isolate R16 vs. app issue

Issue 2: Video Stuttering/Lag
Symptom: Video plays but with frequent pauses
Solutions:

Enable low latency mode in settings
Check WiFi signal strength
Reduce bitrate on R16 (if configurable)
Verify H16 hardware acceleration is active

Issue 3: Controls Not Visible Over Bright Video
Symptom: White text hard to read on light video background
Solutions:

Increase alpha on overlay background (0.3 → 0.5)
Add text shadow/outline to white text
Use colored backgrounds for critical controls

Issue 4: ExoPlayer "Source Error"
Symptom: Error message: "Source error"
Solutions:

Verify RTSP URL is accessible (test with VLC on PC)
Check RTSP server supports the codec (H.264)
Enable all ExoPlayer extensions in dependencies

Issue 5: App Crashes on Rotation
Symptom: App crashes when rotating device
Solutions:

Ensure proper lifecycle handling in ViewModel
Use DisposableEffect for player cleanup
Test with android:configChanges="orientation|screenSize" in manifest


📝 Code Style Guidelines
Composable Naming

Use PascalCase: FullScreenVideoPlayer, CameraControlsOverlay
Descriptive names reflecting UI purpose

State Management

Use StateFlow for ViewModel state
Use collectAsState() in composables
Avoid passing mutable state

Error Handling

Always handle ExoPlayer errors gracefully
Show user-friendly error messages
Log detailed errors for debugging

Performance

Use LaunchedEffect for initialization
Use DisposableEffect for cleanup
Avoid recomposition of video player unnecessarily


🎯 Success Criteria
Minimum Viable Product (MVP)

 Video displays full-screen on Camera screen
 Controls overlay visible and functional
 RTSP connection to R16 works reliably
 Settings can configure RTSP URL
 No crashes during normal use
 Acceptable latency (< 1 second)

Stretch Goals

 Hardware-accelerated decoding confirmed active
 < 300ms latency
 Smooth 30fps playback
 Graceful handling of network interruptions
 Video quality indicators in UI


🚀 Getting Started Commands for Claude Code
Initial Setup
bash# 1. Ensure Android Studio is open with DPM project loaded
# 2. Check current Git status
git status

# 3. Create feature branch
git checkout -b feature/video-streaming

# 4. Start with Task 1: Add dependencies to build.gradle.kts
During Development
bash# Commit regularly (every 30-60 min)
git add .
git commit -m "[VIDEO] <descriptive message>"

# Example commits:
# git commit -m "[VIDEO] Add ExoPlayer dependencies"
# git commit -m "[VIDEO] Create VideoPlayerViewModel"
# git commit -m "[VIDEO] Refactor CameraScreen with overlay"
Testing
bash# Build and run on emulator/device
# Android Studio: Run > Run 'app'
# Or: ./gradlew installDebug

# View logs
adb logcat | grep -E "(ExoPlayer|VideoPlayer|DPM)"

📚 Reference Documentation
ExoPlayer

Official Guide: https://developer.android.com/guide/topics/media/exoplayer
RTSP Support: https://developer.android.com/guide/topics/media/exoplayer/rtsp
Jetpack Compose Integration: https://developer.android.com/jetpack/compose/interop/interop-apis#views-in-compose

RTSP Protocol

RFC 2326: RTSP Specification
Testing with VLC: Media > Open Network Stream > rtsp://...

Android Compose

Box Layout: https://developer.android.com/jetpack/compose/layouts/box
AndroidView: https://developer.android.com/jetpack/compose/interop/interop-apis


✅ Pre-Implementation Checklist
Before starting, verify:

 Android Studio open with DPM project
 Project builds successfully
 Git repository clean (no uncommitted changes)
 R16 hardware available for testing (optional but recommended)
 Network connectivity to R16 (can ping 192.168.1.10)
 Understand existing CameraScreen.kt structure
 Read CC_READ_THIS_FIRST.md Git workflow
 Ready to commit every 30-60 minutes