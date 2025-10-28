#pragma once

#include <unordered_map>
#include <unordered_set>
#include <string>
#include <vector>
#include <nlohmann/json.hpp>

/**
 * PropertyLoader - Loads camera property valid values from specification JSON
 *
 * This class implements the specification-first architecture by loading camera
 * property values from docs/protocol/camera_properties.json at runtime.
 *
 * Background:
 * Previously, property values (ISO, shutter speed, aperture) were hardcoded
 * independently in Air-Side C++ and Ground-Side Android, causing synchronization
 * failures. This class ensures both sides use identical value lists from a
 * single source of truth.
 *
 * Usage:
 *   PropertyLoader::initialize("../docs/protocol/camera_properties.json");
 *   if (!PropertyLoader::isInitialized()) {
 *       // Handle error
 *   }
 *   auto iso_values = PropertyLoader::getIsoValues();
 *
 * See: docs/CAMERA_PROPERTIES_FIX_TRACKING.md for complete context
 * See: docs/CC_READ_THIS_FIRST.md lines 29-111 for specification-first rules
 */
class PropertyLoader {
public:
    /**
     * Initialize PropertyLoader by loading camera_properties.json
     *
     * @param json_path Path to camera_properties.json specification file
     * @return true if initialization successful, false on error
     *
     * This should be called once at application startup, before any camera
     * operations. Logs detailed error messages on failure.
     */
    static bool initialize(const std::string& json_path = "docs/protocol/camera_properties.json");

    /**
     * Check if PropertyLoader has been successfully initialized
     *
     * @return true if initialize() completed successfully
     */
    static bool isInitialized();

    /**
     * Get list of valid ISO values from specification
     *
     * @return Set of valid ISO value strings (e.g., "auto", "100", "200", ...)
     *
     * Returns all 35 ISO values including:
     * - "auto" (0xFFFFFFFF)
     * - Extended low: "50", "64", "80"
     * - Standard range: "100" through "102400" (full and third stops)
     */
    static const std::unordered_set<std::string>& getIsoValues();

    /**
     * Get list of valid shutter speed values from specification
     *
     * @return Set of valid shutter speed strings (e.g., "1/8000", "0.3\"", ...)
     *
     * Returns all 56 shutter speed values:
     * - 35 fast speeds: "1/8000" through "1/3"
     * - 21 long exposures: "0.3\"" through "30\""
     *
     * Note: AUTO and BULB modes are disabled for UAV safety
     */
    static const std::unordered_set<std::string>& getShutterSpeedValues();

    /**
     * Get list of valid aperture (f-stop) values from specification
     *
     * @return Set of valid aperture strings (e.g., "f/1.4", "f/2.8", ...)
     *
     * Returns all 23 aperture values from f/1.4 to f/22
     */
    static const std::unordered_set<std::string>& getApertureValues();

    /**
     * Validate that a property value exists in specification
     *
     * @param property Property name ("iso", "shutter_speed", "aperture")
     * @param value Value string to validate
     * @return true if value is valid for this property
     */
    static bool isValidValue(const std::string& property, const std::string& value);

    /**
     * Get count of valid values for a property (for diagnostics)
     *
     * @param property Property name ("iso", "shutter_speed", "aperture")
     * @return Number of valid values, or 0 if property unknown
     */
    static size_t getValueCount(const std::string& property);

private:
    // Singleton pattern - no public constructor
    PropertyLoader() = delete;
    PropertyLoader(const PropertyLoader&) = delete;
    PropertyLoader& operator=(const PropertyLoader&) = delete;

    // Initialization state
    static bool initialized_;

    // Property value sets loaded from JSON
    static std::unordered_set<std::string> iso_values_;
    static std::unordered_set<std::string> shutter_speed_values_;
    static std::unordered_set<std::string> aperture_values_;

    // Helper methods (not used in current implementation)
    // Future: Could add helper methods for loading individual properties
};
