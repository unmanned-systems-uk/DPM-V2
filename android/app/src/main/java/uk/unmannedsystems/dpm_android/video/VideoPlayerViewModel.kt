package uk.unmannedsystems.dpm_android.video

import android.content.Context
import android.util.Log
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import androidx.media3.common.MediaItem
import androidx.media3.common.PlaybackException
import androidx.media3.common.Player
import androidx.media3.exoplayer.ExoPlayer
import androidx.media3.exoplayer.DefaultLoadControl
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

/**
 * ViewModel for managing RTSP video stream playback using ExoPlayer
 */
class VideoPlayerViewModel : ViewModel() {

    private val _videoState = MutableStateFlow<VideoState>(VideoState.Disconnected)
    val videoState: StateFlow<VideoState> = _videoState.asStateFlow()

    private var exoPlayer: ExoPlayer? = null

    companion object {
        private const val TAG = "VideoPlayerViewModel"
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
                Log.d(TAG, "Initializing player for URL: $rtspUrl with buffer: ${bufferDurationMs}ms")
                _videoState.value = VideoState.Connecting

                // Configure low-latency load control
                val loadControl = DefaultLoadControl.Builder()
                    .setBufferDurationsMs(
                        bufferDurationMs.toInt(),  // Min buffer
                        (bufferDurationMs * 2).toInt(),  // Max buffer
                        (bufferDurationMs / 2).toInt(),  // Buffer for playback
                        bufferDurationMs.toInt()   // Buffer for rebuffer
                    )
                    .build()

                exoPlayer = ExoPlayer.Builder(context)
                    .setLoadControl(loadControl)
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
                                        Log.d(TAG, "Video ready: $resolution")
                                        _videoState.value = VideoState.Connected(resolution)
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

                            override fun onPlayerError(error: PlaybackException) {
                                val errorMsg = error.message ?: "Unknown playback error"
                                Log.e(TAG, "Player error: $errorMsg", error)
                                _videoState.value = VideoState.Error(errorMsg)
                            }
                        })

                        // Prepare and start playback
                        prepare()
                        play()
                    }

                Log.d(TAG, "Player initialized successfully")
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

    override fun onCleared() {
        super.onCleared()
        Log.d(TAG, "ViewModel cleared, releasing player")
        releasePlayer()
    }
}
