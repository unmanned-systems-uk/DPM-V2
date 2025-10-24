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
 * Shutter speed values
 */
enum class ShutterSpeed(val displayValue: String, val seconds: Double) {
    Speed_1_8000("1/8000", 1.0 / 8000),
    Speed_1_4000("1/4000", 1.0 / 4000),
    Speed_1_2000("1/2000", 1.0 / 2000),
    Speed_1_1000("1/1000", 1.0 / 1000),
    Speed_1_500("1/500", 1.0 / 500),
    Speed_1_250("1/250", 1.0 / 250),
    Speed_1_125("1/125", 1.0 / 125),
    Speed_1_60("1/60", 1.0 / 60),
    Speed_1_30("1/30", 1.0 / 30),
    Speed_1_15("1/15", 1.0 / 15),
    Speed_1_8("1/8", 1.0 / 8),
    Speed_1_4("1/4", 1.0 / 4),
    Speed_1_2("1/2", 1.0 / 2),
    Speed_1("1\"", 1.0),
    Speed_2("2\"", 2.0),
    Speed_4("4\"", 4.0),
    Speed_8("8\"", 8.0),
    Speed_15("15\"", 15.0),
    Speed_30("30\"", 30.0);

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
