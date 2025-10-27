package uk.unmannedsystems.dpm_android.video

import android.content.Context
import android.util.Log
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import androidx.media3.common.MediaItem
import androidx.media3.common.PlaybackException
import androidx.media3.common.Player
import androidx.media3.common.C
import androidx.media3.exoplayer.ExoPlayer
import androidx.media3.exoplayer.DefaultLoadControl
import androidx.media3.exoplayer.trackselection.DefaultTrackSelector
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive

/**
 * ViewModel for managing RTSP video stream playback using ExoPlayer
 */
class VideoPlayerViewModel : ViewModel() {

    private val _videoState = MutableStateFlow<VideoState>(VideoState.Disconnected)
    val videoState: StateFlow<VideoState> = _videoState.asStateFlow()

    // Trigger for forcing PlayerView updates when video becomes ready
    private val _surfaceUpdateTrigger = MutableStateFlow(0)
    val surfaceUpdateTrigger: StateFlow<Int> = _surfaceUpdateTrigger.asStateFlow()

    private var exoPlayer: ExoPlayer? = null
    private var hasRenderedFirstFrame = false

    // Auto-reconnection state
    private var lastContext: Context? = null
    private var lastRtspUrl: String? = null
    private var lastBufferDurationMs: Long = 500
    private var reconnectionAttempts = 0
    private val maxReconnectionAttempts = 3

    // Latency optimization - periodic monitoring and correction
    private var latencyMonitorJob: Job? = null
    private var periodicReconnectJob: Job? = null
    private var connectionStartTime: Long = 0

    companion object {
        private const val TAG = "VideoPlayerViewModel"
        private const val RECONNECTION_DELAY_MS = 2000L

        // Latency optimization constants
        private const val LATENCY_CHECK_INTERVAL_MS = 10000L    // Check latency every 10s
        private const val MAX_ACCEPTABLE_LATENCY_MS = 3000L     // Max 3s lag before correction (increased threshold)
        private const val PERIODIC_RECONNECT_INTERVAL_MS = 1200000L  // Full reconnect every 20 mins
    }

    /**
     * Video playback state
     */
    sealed class VideoState {
        object Disconnected : VideoState()
        object Connecting : VideoState()
        data class Connected(val resolution: String = "Unknown") : VideoState()
        data class Error(val message: String) : VideoState()
    }

    /**
     * Initialize ExoPlayer and connect to RTSP stream
     *
     * @param context Android context for ExoPlayer initialization
     * @param rtspUrl RTSP stream URL (e.g., rtsp://192.168.1.10:8554/H264Video)
     * @param bufferDurationMs Buffer duration in milliseconds for low-latency tuning
     */
    fun initializePlayer(context: Context, rtspUrl: String, bufferDurationMs: Long = 500) {
        viewModelScope.launch {
            try {
                Log.d(TAG, "========================================")
                Log.d(TAG, "Initializing player for URL: $rtspUrl")
                Log.d(TAG, "Buffer duration: ${bufferDurationMs}ms")
                Log.d(TAG, "========================================")

                // Save connection parameters for auto-reconnection
                lastContext = context
                lastRtspUrl = rtspUrl
                lastBufferDurationMs = bufferDurationMs

                // Reset first frame flag for new connection
                hasRenderedFirstFrame = false

                _videoState.value = VideoState.Connecting

                // Configure aggressive low-latency load control
                val loadControl = DefaultLoadControl.Builder()
                    .setBufferDurationsMs(
                        bufferDurationMs.toInt(),  // Min buffer
                        (bufferDurationMs * 2).toInt(),  // Max buffer
                        (bufferDurationMs / 2).toInt(),  // Buffer for playback
                        bufferDurationMs.toInt()   // Buffer for rebuffer
                    )
                    .setPrioritizeTimeOverSizeThresholds(true)  // Low-latency mode
                    .setBackBuffer(0, false)  // Don't keep back buffer
                    .build()

                // Track selector optimized for low latency
                val trackSelector = DefaultTrackSelector(context)

                exoPlayer = ExoPlayer.Builder(context)
                    .setLoadControl(loadControl)
                    .setTrackSelector(trackSelector)
                    .build()
                    .apply {
                        val mediaItem = MediaItem.fromUri(rtspUrl)
                        setMediaItem(mediaItem)

                        // Add player listener for state changes
                        addListener(object : Player.Listener {
                            override fun onPlaybackStateChanged(playbackState: Int) {
                                when (playbackState) {
                                    Player.STATE_READY -> {
                                        val videoFormat = this@apply.videoFormat
                                        val resolution = if (videoFormat != null) {
                                            "${videoFormat.width}x${videoFormat.height}"
                                        } else {
                                            "Unknown"
                                        }
                                        Log.d(TAG, "Video ready: $resolution - Playing: ${this@apply.isPlaying}")
                                        _videoState.value = VideoState.Connected(resolution)
                                        // Reset reconnection attempts on successful connection
                                        reconnectionAttempts = 0
                                    }
                                    Player.STATE_BUFFERING -> {
                                        Log.d(TAG, "Video buffering...")
                                        _videoState.value = VideoState.Connecting
                                    }
                                    Player.STATE_ENDED -> {
                                        Log.d(TAG, "Video ended")
                                    }
                                    Player.STATE_IDLE -> {
                                        Log.d(TAG, "Player idle")
                                    }
                                }
                            }

                            override fun onIsPlayingChanged(isPlaying: Boolean) {
                                Log.d(TAG, "Playback state changed - isPlaying: $isPlaying")
                                if (isPlaying && !hasRenderedFirstFrame) {
                                    // Trigger PlayerView surface update ONLY before first frame
                                    _surfaceUpdateTrigger.value++
                                    Log.d(TAG, "Surface update triggered (pre-first-frame)")
                                }
                            }

                            override fun onRenderedFirstFrame() {
                                Log.d(TAG, "✓✓✓ FIRST FRAME RENDERED ✓✓✓")
                                hasRenderedFirstFrame = true
                            }

                            override fun onPlayerError(error: PlaybackException) {
                                val errorMsg = error.message ?: "Unknown playback error"
                                Log.e(TAG, "Player error: $errorMsg", error)

                                // Attempt automatic reconnection for network errors
                                if (lastContext != null && lastRtspUrl != null && reconnectionAttempts < maxReconnectionAttempts) {
                                    reconnectionAttempts++
                                    Log.d(TAG, "Attempting auto-reconnection (attempt $reconnectionAttempts/$maxReconnectionAttempts)")

                                    viewModelScope.launch {
                                        kotlinx.coroutines.delay(RECONNECTION_DELAY_MS)
                                        reconnect(lastContext!!, lastRtspUrl!!, lastBufferDurationMs)
                                    }
                                } else {
                                    if (reconnectionAttempts >= maxReconnectionAttempts) {
                                        Log.e(TAG, "Max reconnection attempts reached")
                                    }
                                    _videoState.value = VideoState.Error(errorMsg)
                                }
                            }
                        })

                        // Prepare and start playback
                        prepare()
                        play()
                    }

                // Start latency monitoring and periodic maintenance
                connectionStartTime = System.currentTimeMillis()
                startLatencyMonitoring()
                startPeriodicReconnect()

                Log.d(TAG, "Player initialized successfully with latency optimizations")
            } catch (e: Exception) {
                val errorMsg = e.message ?: "Failed to initialize player"
                Log.e(TAG, "Failed to initialize player", e)
                _videoState.value = VideoState.Error(errorMsg)
            }
        }
    }

    /**
     * Release ExoPlayer resources and disconnect from stream
     */
    fun releasePlayer() {
        Log.d(TAG, "Releasing player")

        // Cancel monitoring jobs
        latencyMonitorJob?.cancel()
        latencyMonitorJob = null
        periodicReconnectJob?.cancel()
        periodicReconnectJob = null

        exoPlayer?.release()
        exoPlayer = null
        _videoState.value = VideoState.Disconnected
    }

    /**
     * Get the ExoPlayer instance (for use in PlayerView)
     */
    fun getPlayer(): ExoPlayer? = exoPlayer

    /**
     * Reconnect to the stream (useful after network interruption)
     */
    fun reconnect(context: Context, rtspUrl: String, bufferDurationMs: Long = 500) {
        Log.d(TAG, "Reconnecting to stream")
        releasePlayer()
        initializePlayer(context, rtspUrl, bufferDurationMs)
    }

    /**
     * Start periodic latency monitoring and correction
     * Checks buffer depth and seeks to live edge when necessary
     */
    private fun startLatencyMonitoring() {
        latencyMonitorJob?.cancel()
        latencyMonitorJob = viewModelScope.launch {
            while (isActive) {
                delay(LATENCY_CHECK_INTERVAL_MS)

                val player = exoPlayer ?: continue
                if (!player.isPlaying) continue

                try {
                    // Get buffer information
                    val bufferedPosition = player.bufferedPosition
                    val currentPosition = player.currentPosition
                    val totalBuffer = player.totalBufferedDuration

                    // Calculate latency (how far behind live edge we are)
                    val bufferAhead = bufferedPosition - currentPosition

                    Log.d(TAG, "[Latency Monitor] Buffer: ${totalBuffer}ms | Buffer ahead: ${bufferAhead}ms | Position: ${currentPosition}ms")

                    // ONLY seek if buffer is growing beyond acceptable limits
                    // No periodic seeks - only reactive correction when needed
                    if (bufferAhead > MAX_ACCEPTABLE_LATENCY_MS) {
                        Log.w(TAG, "[Latency Monitor] High latency detected ($bufferAhead ms) - seeking to live edge")
                        seekToLiveEdge()
                    }

                } catch (e: Exception) {
                    Log.e(TAG, "[Latency Monitor] Error during latency check", e)
                }
            }
        }

        Log.d(TAG, "Latency monitoring started - reactive correction only (threshold: ${MAX_ACCEPTABLE_LATENCY_MS}ms)")
    }

    /**
     * Start periodic reconnection as fallback (every 20 minutes)
     * This ensures fresh connection and prevents any accumulated issues
     */
    private fun startPeriodicReconnect() {
        periodicReconnectJob?.cancel()
        periodicReconnectJob = viewModelScope.launch {
            while (isActive) {
                delay(PERIODIC_RECONNECT_INTERVAL_MS)

                val timeSinceStart = System.currentTimeMillis() - connectionStartTime
                Log.d(TAG, "[Periodic Reconnect] Triggering full reconnection after ${timeSinceStart / 60000} minutes")

                // Reconnect to flush all buffers and reset state
                val ctx = lastContext
                val url = lastRtspUrl
                val bufDur = lastBufferDurationMs

                if (ctx != null && url != null) {
                    reconnect(ctx, url, bufDur)
                }
            }
        }

        Log.d(TAG, "Periodic reconnection scheduled (every ${PERIODIC_RECONNECT_INTERVAL_MS / 60000} minutes)")
    }

    /**
     * Seek to live edge to minimize latency
     * This discards buffered frames and jumps to the most recent frame
     */
    private fun seekToLiveEdge() {
        try {
            val player = exoPlayer ?: return

            // For live streams, seek to default position (live edge)
            player.seekToDefaultPosition()

            Log.d(TAG, "[Seek] Seeking to live edge - discarding buffer")
        } catch (e: Exception) {
            Log.e(TAG, "[Seek] Failed to seek to live edge", e)
        }
    }

    override fun onCleared() {
        super.onCleared()
        Log.d(TAG, "ViewModel cleared, releasing player")
        releasePlayer()
    }
}
