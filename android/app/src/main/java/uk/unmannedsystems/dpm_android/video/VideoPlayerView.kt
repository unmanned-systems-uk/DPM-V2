package uk.unmannedsystems.dpm_android.video

import android.view.ViewGroup
import android.widget.FrameLayout
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.key
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.media3.ui.AspectRatioFrameLayout
import androidx.media3.ui.PlayerView
import uk.unmannedsystems.dpm_android.network.AspectRatioMode
import uk.unmannedsystems.dpm_android.network.VideoStreamSettings

/**
 * Full-screen video player composable for RTSP streaming
 *
 * Displays RTSP video stream using ExoPlayer with overlay states for
 * connecting, error, and disconnected states.
 *
 * @param videoSettings Video stream configuration
 * @param modifier Modifier for layout customization
 * @param videoPlayerViewModel ViewModel managing ExoPlayer lifecycle
 */
@Composable
fun FullScreenVideoPlayer(
    videoSettings: VideoStreamSettings,
    modifier: Modifier = Modifier,
    videoPlayerViewModel: VideoPlayerViewModel = viewModel()
) {
    val context = LocalContext.current
    val videoState by videoPlayerViewModel.videoState.collectAsState()
    val surfaceUpdateTrigger by videoPlayerViewModel.surfaceUpdateTrigger.collectAsState()

    // Initialize player when composable enters composition or settings change
    LaunchedEffect(videoSettings.rtspUrl, videoSettings.bufferDurationMs) {
        if (videoSettings.enabled) {
            videoPlayerViewModel.initializePlayer(
                context = context,
                rtspUrl = videoSettings.rtspUrl,
                bufferDurationMs = videoSettings.bufferDurationMs
            )
        }
    }

    // Release player when composable leaves composition
    DisposableEffect(Unit) {
        onDispose {
            videoPlayerViewModel.releasePlayer()
        }
    }

    Box(modifier = modifier.fillMaxSize()) {
        if (videoSettings.enabled) {
            // Video player view with key to force recreation on URL change
            key(videoSettings.rtspUrl) {
                AndroidView(
                    factory = { context ->
                        android.util.Log.d("VideoPlayerView", "Creating NEW PlayerView for URL: ${videoSettings.rtspUrl}")

                        PlayerView(context).apply {
                            // Explicitly use SurfaceView for better RTSP compatibility
                            setShowBuffering(PlayerView.SHOW_BUFFERING_NEVER)
                            useController = false

                            layoutParams = FrameLayout.LayoutParams(
                                ViewGroup.LayoutParams.MATCH_PARENT,
                                ViewGroup.LayoutParams.MATCH_PARENT
                            )

                            // Set resize mode
                            resizeMode = when (videoSettings.aspectRatioMode) {
                                AspectRatioMode.FILL -> AspectRatioFrameLayout.RESIZE_MODE_FILL
                                AspectRatioMode.FIT -> AspectRatioFrameLayout.RESIZE_MODE_FIT
                                AspectRatioMode.AUTO -> AspectRatioFrameLayout.RESIZE_MODE_FIT
                            }

                            // Configure visibility and screen settings
                            visibility = android.view.View.VISIBLE
                            keepScreenOn = true
                            setBackgroundColor(android.graphics.Color.BLACK)

                            // Bind player immediately if available
                            val currentPlayer = videoPlayerViewModel.getPlayer()
                            if (currentPlayer != null) {
                                player = currentPlayer
                                android.util.Log.d("VideoPlayerView", "Player bound in factory - Playing: ${currentPlayer.isPlaying}, Tracks: ${currentPlayer.currentTracks.groups.size}")
                            } else {
                                android.util.Log.w("VideoPlayerView", "No player available in factory!")
                            }
                        }
                    },
                    update = { playerView ->
                        val currentPlayer = videoPlayerViewModel.getPlayer()

                        android.util.Log.d("VideoPlayerView", "Update (trigger=$surfaceUpdateTrigger) - Player exists: ${currentPlayer != null}, Currently bound: ${playerView.player != null}, Playing: ${currentPlayer?.isPlaying}")

                        // Bind player if not already bound (don't rebind during playback)
                        if (currentPlayer != null && playerView.player != currentPlayer) {
                            playerView.player = currentPlayer
                            android.util.Log.d("VideoPlayerView", "Player bound - Tracks: ${currentPlayer.currentTracks.groups.size}")
                        }

                        // Update resize mode
                        playerView.resizeMode = when (videoSettings.aspectRatioMode) {
                            AspectRatioMode.FILL -> AspectRatioFrameLayout.RESIZE_MODE_FILL
                            AspectRatioMode.FIT -> AspectRatioFrameLayout.RESIZE_MODE_FIT
                            AspectRatioMode.AUTO -> AspectRatioFrameLayout.RESIZE_MODE_FIT
                        }

                        // Ensure visibility
                        playerView.visibility = android.view.View.VISIBLE
                        playerView.keepScreenOn = true
                    },
                    modifier = Modifier.fillMaxSize()
                )
            }

            // Show overlay states over video
            when (val state = videoState) {
                is VideoPlayerViewModel.VideoState.Disconnected -> {
                    DisconnectedOverlay()
                }
                is VideoPlayerViewModel.VideoState.Connecting -> {
                    ConnectingOverlay()
                }
                is VideoPlayerViewModel.VideoState.Error -> {
                    ErrorOverlay(errorMessage = state.message)
                }
                is VideoPlayerViewModel.VideoState.Connected -> {
                    // Video is playing - no overlay needed
                }
            }
        } else {
            // Video disabled in settings
            VideoDisabledOverlay()
        }
    }
}

/**
 * Overlay shown when video is disconnected
 */
@Composable
private fun DisconnectedOverlay() {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.Black),
        contentAlignment = Alignment.Center
    ) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Text(
                text = "Video Disconnected",
                color = Color.White,
                style = MaterialTheme.typography.titleMedium
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = "Waiting for stream...",
                color = Color.White.copy(alpha = 0.7f),
                style = MaterialTheme.typography.bodySmall
            )
        }
    }
}

/**
 * Overlay shown when video is connecting/buffering
 */
@Composable
private fun ConnectingOverlay() {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.Black.copy(alpha = 0.7f)),
        contentAlignment = Alignment.Center
    ) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            CircularProgressIndicator(color = Color.White)
            Spacer(modifier = Modifier.height(16.dp))
            Text(
                text = "Connecting to video stream...",
                color = Color.White,
                style = MaterialTheme.typography.bodyLarge
            )
        }
    }
}

/**
 * Overlay shown when video encounters an error
 */
@Composable
private fun ErrorOverlay(errorMessage: String) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.Black),
        contentAlignment = Alignment.Center
    ) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Text(
                text = "Video Error",
                color = Color.Red,
                style = MaterialTheme.typography.titleMedium
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = errorMessage,
                color = Color.White,
                style = MaterialTheme.typography.bodyMedium
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = "Check network connection and RTSP URL in settings",
                color = Color.White.copy(alpha = 0.7f),
                style = MaterialTheme.typography.bodySmall
            )
        }
    }
}

/**
 * Overlay shown when video is disabled in settings
 */
@Composable
private fun VideoDisabledOverlay() {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.Black),
        contentAlignment = Alignment.Center
    ) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Text(
                text = "Video Stream Disabled",
                color = Color.White,
                style = MaterialTheme.typography.titleMedium
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = "Enable video in Settings to view stream",
                color = Color.White.copy(alpha = 0.7f),
                style = MaterialTheme.typography.bodySmall
            )
        }
    }
}
