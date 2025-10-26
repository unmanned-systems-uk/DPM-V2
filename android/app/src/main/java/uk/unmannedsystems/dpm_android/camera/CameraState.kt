package uk.unmannedsystems.dpm_android.camera

/**
 * Represents the current state of the camera
 */
data class CameraState(
    val mode: CameraMode = CameraMode.MANUAL,
    val shutterSpeed: ShutterSpeed = ShutterSpeed.Speed_1_125,
    val aperture: Aperture = Aperture.F4_0,
    val iso: ISO = ISO.ISO_800,
    val exposureCompensation: Float = 0.0f,
    val whiteBalance: WhiteBalance = WhiteBalance.AUTO,
    val focusMode: FocusMode = FocusMode.AUTO,
    val fileFormat: FileFormat = FileFormat.JPEG,
    val isRecording: Boolean = false,
    val batteryLevel: Int = 100,
    val remainingShots: Int = 999,
    val isConnected: Boolean = false
)

/**
 * Camera shooting modes
 */
enum class CameraMode(val displayName: String, val shortName: String) {
    MANUAL("Manual", "M"),
    APERTURE_PRIORITY("Aperture Priority", "Av"),
    SHUTTER_PRIORITY("Shutter Priority", "Tv"),
    PROGRAM("Program", "P"),
    AUTO("Auto", "Auto")
}

/**
 * Shutter speed values - Sony Alpha 1 supported range
 *
 * All 35 shutter speeds supported in Manual (M) mode
 * Range: 1/8000 to 1/3 second
 *
 * Note: Long exposures (>0.5 seconds) require Bulb mode and are not supported
 * via the shutter_speed property. Future Phase 2 implementation.
 *
 * Source: /docs/protocol/CAMERA_SHUTTER_SPEEDS.md
 */
enum class ShutterSpeed(val displayValue: String, val seconds: Double) {
    Speed_1_8000("1/8000", 1.0 / 8000),
    Speed_1_6400("1/6400", 1.0 / 6400),
    Speed_1_5000("1/5000", 1.0 / 5000),
    Speed_1_4000("1/4000", 1.0 / 4000),
    Speed_1_3200("1/3200", 1.0 / 3200),
    Speed_1_2500("1/2500", 1.0 / 2500),
    Speed_1_2000("1/2000", 1.0 / 2000),
    Speed_1_1600("1/1600", 1.0 / 1600),
    Speed_1_1250("1/1250", 1.0 / 1250),
    Speed_1_1000("1/1000", 1.0 / 1000),
    Speed_1_800("1/800", 1.0 / 800),
    Speed_1_640("1/640", 1.0 / 640),
    Speed_1_500("1/500", 1.0 / 500),
    Speed_1_400("1/400", 1.0 / 400),
    Speed_1_320("1/320", 1.0 / 320),
    Speed_1_250("1/250", 1.0 / 250),
    Speed_1_200("1/200", 1.0 / 200),
    Speed_1_160("1/160", 1.0 / 160),
    Speed_1_125("1/125", 1.0 / 125),
    Speed_1_100("1/100", 1.0 / 100),
    Speed_1_80("1/80", 1.0 / 80),
    Speed_1_60("1/60", 1.0 / 60),
    Speed_1_50("1/50", 1.0 / 50),
    Speed_1_40("1/40", 1.0 / 40),
    Speed_1_30("1/30", 1.0 / 30),
    Speed_1_25("1/25", 1.0 / 25),
    Speed_1_20("1/20", 1.0 / 20),
    Speed_1_15("1/15", 1.0 / 15),
    Speed_1_13("1/13", 1.0 / 13),
    Speed_1_10("1/10", 1.0 / 10),
    Speed_1_8("1/8", 1.0 / 8),
    Speed_1_6("1/6", 1.0 / 6),
    Speed_1_5("1/5", 1.0 / 5),
    Speed_1_4("1/4", 1.0 / 4),
    Speed_1_3("1/3", 1.0 / 3);

    companion object {
        fun fromOrdinal(ordinal: Int): ShutterSpeed {
            return entries.getOrNull(ordinal) ?: Speed_1_125
        }
    }
}

/**
 * Aperture (f-stop) values
 */
enum class Aperture(val displayValue: String, val fNumber: Float) {
    F1_4("1.4", 1.4f),
    F1_8("1.8", 1.8f),
    F2_0("2.0", 2.0f),
    F2_8("2.8", 2.8f),
    F4_0("4.0", 4.0f),
    F5_6("5.6", 5.6f),
    F8_0("8.0", 8.0f),
    F11_0("11", 11.0f),
    F16_0("16", 16.0f),
    F22_0("22", 22.0f);

    companion object {
        fun fromOrdinal(ordinal: Int): Aperture {
            return entries.getOrNull(ordinal) ?: F4_0
        }
    }
}

/**
 * ISO sensitivity values
 */
enum class ISO(val displayValue: String, val value: Int) {
    ISO_100("100", 100),
    ISO_200("200", 200),
    ISO_400("400", 400),
    ISO_800("800", 800),
    ISO_1600("1600", 1600),
    ISO_3200("3200", 3200),
    ISO_6400("6400", 6400),
    ISO_12800("12800", 12800),
    ISO_25600("25600", 25600),
    ISO_51200("51200", 51200);

    companion object {
        fun fromOrdinal(ordinal: Int): ISO {
            return entries.getOrNull(ordinal) ?: ISO_800
        }
    }
}

/**
 * White balance modes
 */
enum class WhiteBalance(val displayName: String, val shortName: String) {
    AUTO("Auto", "AWB"),
    DAYLIGHT("Daylight", "DAY"),
    CLOUDY("Cloudy", "CLY"),
    TUNGSTEN("Tungsten", "TUN"),
    FLUORESCENT("Fluorescent", "FLU"),
    FLASH("Flash", "FLS"),
    CUSTOM("Custom", "CUS")
}

/**
 * Focus modes
 */
enum class FocusMode(val displayName: String) {
    AUTO("Auto Focus"),
    MANUAL("Manual Focus"),
    CONTINUOUS("Continuous AF")
}

/**
 * File format options
 */
enum class FileFormat(val displayName: String) {
    JPEG("JPEG"),
    RAW("RAW"),
    JPEG_PLUS_RAW("JPEG+RAW")
}
