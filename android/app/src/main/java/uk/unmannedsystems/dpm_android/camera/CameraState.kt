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
    val isConnected: Boolean = false,
    val cameraError: String? = null  // Error message when camera not connected, etc.
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
 * Range: 1/8000 second to 30 seconds, plus AUTO
 * Includes both fast shutter speeds (fractions) and long exposures (full seconds)
 *
 * Source: /docs/protocol/CAMERA_SHUTTER_SPEEDS.md
 */
enum class ShutterSpeed(val displayValue: String, val seconds: Double) {
    // Fast shutter speeds (fractions of a second)
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
    Speed_1_3("1/3", 1.0 / 3),

    // Long exposures (full seconds)
    Speed_0_3_SEC("0.3\"", 0.3),
    Speed_0_4_SEC("0.4\"", 0.4),
    Speed_0_5_SEC("0.5\"", 0.5),
    Speed_0_6_SEC("0.6\"", 0.6),
    Speed_0_8_SEC("0.8\"", 0.8),
    Speed_1_0_SEC("1.0\"", 1.0),
    Speed_1_3_SEC("1.3\"", 1.3),
    Speed_1_6_SEC("1.6\"", 1.6),
    Speed_2_0_SEC("2.0\"", 2.0),
    Speed_2_5_SEC("2.5\"", 2.5),
    Speed_3_0_SEC("3.0\"", 3.0),
    Speed_4_0_SEC("4.0\"", 4.0),
    Speed_5_0_SEC("5.0\"", 5.0),
    Speed_6_0_SEC("6.0\"", 6.0),
    Speed_8_0_SEC("8.0\"", 8.0),
    Speed_10_SEC("10\"", 10.0),
    Speed_13_SEC("13\"", 13.0),
    Speed_15_SEC("15\"", 15.0),
    Speed_20_SEC("20\"", 20.0),
    Speed_25_SEC("25\"", 25.0),
    Speed_30_SEC("30\"", 30.0),

    // Auto mode
    Speed_AUTO("auto", 0.0);

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
    F1_6("1.6", 1.6f),
    F1_8("1.8", 1.8f),
    F2_0("2.0", 2.0f),
    F2_2("2.2", 2.2f),
    F2_5("2.5", 2.5f),
    F2_8("2.8", 2.8f),
    F3_2("3.2", 3.2f),
    F3_5("3.5", 3.5f),
    F4_0("4.0", 4.0f),
    F4_5("4.5", 4.5f),
    F5_0("5.0", 5.0f),
    F5_6("5.6", 5.6f),
    F6_3("6.3", 6.3f),
    F7_1("7.1", 7.1f),
    F8_0("8.0", 8.0f),
    F9_0("9.0", 9.0f),
    F10("10", 10.0f),
    F11("11", 11.0f),
    F13("13", 13.0f),
    F14("14", 14.0f),
    F16("16", 16.0f),
    F18("18", 18.0f),
    F20("20", 20.0f),
    F22("22", 22.0f),
    F25("25", 25.0f),
    F29("29", 29.0f),
    F32("32", 32.0f);

    companion object {
        fun fromOrdinal(ordinal: Int): Aperture {
            return entries.getOrNull(ordinal) ?: F4_0
        }
    }
}

/**
 * ISO sensitivity values - Sony Alpha 1 full range with third-stop increments
 * Complete range from Air-Side: AUTO, 50-102400 (35 total values)
 */
enum class ISO(val displayValue: String, val value: Int) {
    ISO_AUTO("auto", 0),
    ISO_50("50", 50),
    ISO_64("64", 64),
    ISO_80("80", 80),
    ISO_100("100", 100),
    ISO_125("125", 125),
    ISO_160("160", 160),
    ISO_200("200", 200),
    ISO_250("250", 250),
    ISO_320("320", 320),
    ISO_400("400", 400),
    ISO_500("500", 500),
    ISO_640("640", 640),
    ISO_800("800", 800),
    ISO_1000("1000", 1000),
    ISO_1250("1250", 1250),
    ISO_1600("1600", 1600),
    ISO_2000("2000", 2000),
    ISO_2500("2500", 2500),
    ISO_3200("3200", 3200),
    ISO_4000("4000", 4000),
    ISO_5000("5000", 5000),
    ISO_6400("6400", 6400),
    ISO_8000("8000", 8000),
    ISO_10000("10000", 10000),
    ISO_12800("12800", 12800),
    ISO_16000("16000", 16000),
    ISO_20000("20000", 20000),
    ISO_25600("25600", 25600),
    ISO_32000("32000", 32000),
    ISO_40000("40000", 40000),
    ISO_51200("51200", 51200),
    ISO_64000("64000", 64000),
    ISO_80000("80000", 80000),
    ISO_102400("102400", 102400);

    companion object {
        fun fromOrdinal(ordinal: Int): ISO {
            return entries.getOrNull(ordinal) ?: ISO_800
        }
    }
}

/**
 * White balance modes
 * Matches camera_properties.json specification (13 modes total)
 */
enum class WhiteBalance(val displayName: String, val shortName: String) {
    AUTO("Auto", "AWB"),
    DAYLIGHT("Daylight", "DAY"),
    SHADE("Shade", "SHA"),
    CLOUDY("Cloudy", "CLY"),
    TUNGSTEN("Tungsten", "TUN"),
    FLUORESCENT_WARM("Fluorescent Warm", "FWM"),
    FLUORESCENT_COOL("Fluorescent Cool", "FCL"),
    FLUORESCENT_DAY("Fluorescent Day", "FDY"),
    FLUORESCENT_DAYLIGHT("Fluorescent Daylight", "FDL"),
    FLASH("Flash", "FLS"),
    UNDERWATER("Underwater", "UW"),
    CUSTOM("Custom", "CUS"),
    TEMPERATURE("Temperature", "K")
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
