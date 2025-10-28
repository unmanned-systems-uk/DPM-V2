package uk.unmannedsystems.dpm_android.camera

import android.content.Context
import android.util.Log
import org.json.JSONObject

/**
 * PropertyLoader - Loads and validates camera property values from specification JSON
 *
 * This class implements the specification-first architecture by loading camera
 * property values from assets/camera_properties.json at runtime.
 *
 * Background:
 * Previously, property values (ISO, shutter speed, aperture) were hardcoded
 * independently in Air-Side C++ and Ground-Side Android, causing synchronization
 * failures. This class ensures both sides use identical value lists from a
 * single source of truth.
 *
 * Usage:
 *   PropertyLoader.initialize(context)
 *   if (!PropertyLoader.isInitialized()) {
 *       // Handle error
 *   }
 *   val isoValues = PropertyLoader.getIsoValues()
 *   val isValid = PropertyLoader.isValidValue("iso", "800")
 *
 * See: docs/CAMERA_PROPERTIES_FIX_TRACKING.md for complete context
 * See: docs/CC_READ_THIS_FIRST.md lines 29-111 for specification-first rules
 */
object PropertyLoader {
    private const val TAG = "PropertyLoader"
    private const val JSON_FILENAME = "camera_properties.json"

    private var initialized = false
    private val isoValues = mutableSetOf<String>()
    private val shutterSpeedValues = mutableSetOf<String>()
    private val apertureValues = mutableSetOf<String>()

    /**
     * Initialize PropertyLoader by loading camera_properties.json from assets
     *
     * @param context Android context for accessing assets
     * @return true if initialization successful, false on error
     *
     * This should be called once at application startup, before any camera
     * operations. Logs detailed error messages on failure.
     */
    fun initialize(context: Context): Boolean {
        if (initialized) {
            Log.w(TAG, "PropertyLoader.initialize() called multiple times - ignoring")
            return true
        }

        Log.i(TAG, "PropertyLoader: Loading camera properties from $JSON_FILENAME")

        try {
            // Load JSON from assets
            val jsonString = context.assets.open(JSON_FILENAME).bufferedReader().use {
                it.readText()
            }

            val spec = JSONObject(jsonString)

            // Validate JSON structure
            if (!spec.has("properties")) {
                Log.e(TAG, "PropertyLoader: Invalid JSON - missing 'properties' field")
                return false
            }

            val properties = spec.getJSONObject("properties")

            // Load ISO values
            if (properties.has("iso")) {
                val isoProperty = properties.getJSONObject("iso")
                if (isoProperty.has("validation")) {
                    val validation = isoProperty.getJSONObject("validation")
                    if (validation.has("values")) {
                        val values = validation.getJSONArray("values")
                        for (i in 0 until values.length()) {
                            isoValues.add(values.getString(i))
                        }
                        Log.i(TAG, "PropertyLoader: Loaded ${isoValues.size} ISO values")
                    } else {
                        Log.e(TAG, "PropertyLoader: ISO validation missing 'values'")
                        return false
                    }
                } else {
                    Log.e(TAG, "PropertyLoader: ISO property missing 'validation'")
                    return false
                }
            } else {
                Log.e(TAG, "PropertyLoader: Missing 'iso' property in JSON")
                return false
            }

            // Load Shutter Speed values
            if (properties.has("shutter_speed")) {
                val shutterProperty = properties.getJSONObject("shutter_speed")
                if (shutterProperty.has("validation")) {
                    val validation = shutterProperty.getJSONObject("validation")
                    if (validation.has("values")) {
                        val values = validation.getJSONArray("values")
                        for (i in 0 until values.length()) {
                            shutterSpeedValues.add(values.getString(i))
                        }
                        Log.i(TAG, "PropertyLoader: Loaded ${shutterSpeedValues.size} shutter speed values")
                    } else {
                        Log.e(TAG, "PropertyLoader: Shutter speed validation missing 'values'")
                        return false
                    }
                } else {
                    Log.e(TAG, "PropertyLoader: Shutter speed property missing 'validation'")
                    return false
                }
            } else {
                Log.e(TAG, "PropertyLoader: Missing 'shutter_speed' property in JSON")
                return false
            }

            // Load Aperture values
            if (properties.has("aperture")) {
                val apertureProperty = properties.getJSONObject("aperture")
                if (apertureProperty.has("validation")) {
                    val validation = apertureProperty.getJSONObject("validation")
                    if (validation.has("values")) {
                        val values = validation.getJSONArray("values")
                        for (i in 0 until values.length()) {
                            apertureValues.add(values.getString(i))
                        }
                        Log.i(TAG, "PropertyLoader: Loaded ${apertureValues.size} aperture values")
                    } else {
                        Log.e(TAG, "PropertyLoader: Aperture validation missing 'values'")
                        return false
                    }
                } else {
                    Log.e(TAG, "PropertyLoader: Aperture property missing 'validation'")
                    return false
                }
            } else {
                Log.e(TAG, "PropertyLoader: Missing 'aperture' property in JSON")
                return false
            }

            // Validation: Ensure we loaded expected counts
            if (isoValues.size < 10) {
                Log.w(TAG, "PropertyLoader: Only loaded ${isoValues.size} ISO values - expected ~35")
            }
            if (shutterSpeedValues.size < 10) {
                Log.w(TAG, "PropertyLoader: Only loaded ${shutterSpeedValues.size} shutter speed values - expected ~56")
            }
            if (apertureValues.size < 5) {
                Log.w(TAG, "PropertyLoader: Only loaded ${apertureValues.size} aperture values - expected ~23")
            }

            initialized = true
            Log.i(TAG, "PropertyLoader: Initialization complete")
            Log.i(TAG, "PropertyLoader: Loaded total of ${isoValues.size + shutterSpeedValues.size + apertureValues.size} property values from specification")

            return true

        } catch (e: Exception) {
            Log.e(TAG, "PropertyLoader: Unexpected error during initialization", e)
            return false
        }
    }

    /**
     * Check if PropertyLoader has been successfully initialized
     *
     * @return true if initialize() completed successfully
     */
    fun isInitialized(): Boolean {
        return initialized
    }

    /**
     * Get set of valid ISO values from specification
     *
     * @return Set of valid ISO value strings (e.g., "auto", "100", "200", ...)
     *
     * Returns all 35 ISO values including:
     * - "auto" (0xFFFFFFFF)
     * - Extended low: "50", "64", "80"
     * - Standard range: "100" through "102400" (full and third stops)
     */
    fun getIsoValues(): Set<String> {
        if (!initialized) {
            Log.e(TAG, "PropertyLoader.getIsoValues() called before initialization!")
            return emptySet()
        }
        return isoValues.toSet()
    }

    /**
     * Get set of valid shutter speed values from specification
     *
     * @return Set of valid shutter speed strings (e.g., "1/8000", "0.3\"", ...)
     *
     * Returns all 56 shutter speed values:
     * - 35 fast speeds: "1/8000" through "1/3"
     * - 21 long exposures: "0.3\"" through "30\""
     *
     * Note: AUTO and BULB modes are disabled for UAV safety
     */
    fun getShutterSpeedValues(): Set<String> {
        if (!initialized) {
            Log.e(TAG, "PropertyLoader.getShutterSpeedValues() called before initialization!")
            return emptySet()
        }
        return shutterSpeedValues.toSet()
    }

    /**
     * Get set of valid aperture (f-stop) values from specification
     *
     * @return Set of valid aperture strings (e.g., "f/1.4", "f/2.8", ...)
     *
     * Returns all 23 aperture values from f/1.4 to f/22
     */
    fun getApertureValues(): Set<String> {
        if (!initialized) {
            Log.e(TAG, "PropertyLoader.getApertureValues() called before initialization!")
            return emptySet()
        }
        return apertureValues.toSet()
    }

    /**
     * Validate that a property value exists in specification
     *
     * @param property Property name ("iso", "shutter_speed", "aperture")
     * @param value Value string to validate
     * @return true if value is valid for this property
     */
    fun isValidValue(property: String, value: String): Boolean {
        if (!initialized) {
            Log.e(TAG, "PropertyLoader.isValidValue() called before initialization!")
            return false
        }

        return when (property) {
            "iso" -> isoValues.contains(value)
            "shutter_speed" -> shutterSpeedValues.contains(value)
            "aperture" -> {
                // Handle both "f/2.8" and "2.8" formats
                val normalizedValue = value.removePrefix("f/")
                apertureValues.any { it.removePrefix("f/") == normalizedValue }
            }
            else -> {
                Log.w(TAG, "PropertyLoader.isValidValue() called with unknown property: $property")
                false
            }
        }
    }

    /**
     * Get count of valid values for a property (for diagnostics)
     *
     * @param property Property name ("iso", "shutter_speed", "aperture")
     * @return Number of valid values, or 0 if property unknown
     */
    fun getValueCount(property: String): Int {
        if (!initialized) {
            return 0
        }

        return when (property) {
            "iso" -> isoValues.size
            "shutter_speed" -> shutterSpeedValues.size
            "aperture" -> apertureValues.size
            else -> 0
        }
    }
}
