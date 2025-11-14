#include "property_loader.h"
#include "../utils/logger.h"
#include <nlohmann/json.hpp>
#include <fstream>
#include <sstream>
#include "logging/structured_logger.h"

using json = nlohmann::json;

// Initialize static members
bool PropertyLoader::initialized_ = false;
std::unordered_set<std::string> PropertyLoader::iso_values_;
std::unordered_set<std::string> PropertyLoader::shutter_speed_values_;
std::unordered_set<std::string> PropertyLoader::aperture_values_;

bool PropertyLoader::initialize(const std::string& json_path) {
    if (initialized_) {
        LOG_WARNING(LogContext::CAMERA, "PropertyLoader::initialize() called multiple times - ignoring");
        return true;
    }

    LOG_INFO(LogContext::CAMERA, "PropertyLoader: Loading camera properties from " + json_path);

    try {
        // Load JSON file
        std::ifstream file(json_path);
        if (!file.is_open()) {
            LOG_ERROR(LogContext::CAMERA, "PropertyLoader: Failed to open " + json_path);
            LOG_ERROR(LogContext::CAMERA, "PropertyLoader: Make sure camera_properties.json exists at ~/DPM-V2/protocol/");
            LOG_ERROR(LogContext::CAMERA, "PropertyLoader: This is a shared specification file - NEVER in docs/ folder!");
            return false;
        }

        json spec;
        file >> spec;
        file.close();

        // Validate JSON structure
        if (!spec.contains("properties")) {
            LOG_ERROR(LogContext::CAMERA, "PropertyLoader: Invalid JSON - missing 'properties' field");
            return false;
        }

        json properties = spec["properties"];

        // Load ISO values
        if (properties.contains("iso")) {
            auto iso_property = properties["iso"];
            if (iso_property.contains("validation") && iso_property["validation"].contains("values")) {
                auto values = iso_property["validation"]["values"];
                if (values.is_array()) {
                    for (const auto& val : values) {
                        if (val.is_string()) {
                            iso_values_.insert(val.get<std::string>());
                        }
                    }
                    LOG_INFO(LogContext::CAMERA, "PropertyLoader: Loaded " + std::to_string(iso_values_.size()) + " ISO values");
                } else {
                    LOG_ERROR(LogContext::CAMERA, "PropertyLoader: ISO validation.values is not an array");
                    return false;
                }
            } else {
                LOG_ERROR(LogContext::CAMERA, "PropertyLoader: ISO property missing validation.values");
                return false;
            }
        } else {
            LOG_ERROR(LogContext::CAMERA, "PropertyLoader: Missing 'iso' property in JSON");
            return false;
        }

        // Load Shutter Speed values
        if (properties.contains("shutter_speed")) {
            auto shutter_property = properties["shutter_speed"];
            if (shutter_property.contains("validation") && shutter_property["validation"].contains("values")) {
                auto values = shutter_property["validation"]["values"];
                if (values.is_array()) {
                    for (const auto& val : values) {
                        if (val.is_string()) {
                            shutter_speed_values_.insert(val.get<std::string>());
                        }
                    }
                    LOG_INFO(LogContext::CAMERA, "PropertyLoader: Loaded " + std::to_string(shutter_speed_values_.size()) + " shutter speed values");
                } else {
                    LOG_ERROR(LogContext::CAMERA, "PropertyLoader: Shutter speed validation.values is not an array");
                    return false;
                }
            } else {
                LOG_ERROR(LogContext::CAMERA, "PropertyLoader: Shutter speed property missing validation.values");
                return false;
            }
        } else {
            LOG_ERROR(LogContext::CAMERA, "PropertyLoader: Missing 'shutter_speed' property in JSON");
            return false;
        }

        // Load Aperture values
        if (properties.contains("aperture")) {
            auto aperture_property = properties["aperture"];
            if (aperture_property.contains("validation") && aperture_property["validation"].contains("values")) {
                auto values = aperture_property["validation"]["values"];
                if (values.is_array()) {
                    for (const auto& val : values) {
                        if (val.is_string()) {
                            aperture_values_.insert(val.get<std::string>());
                        }
                    }
                    LOG_INFO(LogContext::CAMERA, "PropertyLoader: Loaded " + std::to_string(aperture_values_.size()) + " aperture values");
                } else {
                    LOG_ERROR(LogContext::CAMERA, "PropertyLoader: Aperture validation.values is not an array");
                    return false;
                }
            } else {
                LOG_ERROR(LogContext::CAMERA, "PropertyLoader: Aperture property missing validation.values");
                return false;
            }
        } else {
            LOG_ERROR(LogContext::CAMERA, "PropertyLoader: Missing 'aperture' property in JSON");
            return false;
        }

        // Validation: Ensure we loaded expected counts
        if (iso_values_.size() < 10) {
            LOG_WARNING(LogContext::CAMERA, "PropertyLoader: Only loaded " + std::to_string(iso_values_.size()) + " ISO values - expected ~35");
        }
        if (shutter_speed_values_.size() < 10) {
            LOG_WARNING(LogContext::CAMERA, "PropertyLoader: Only loaded " + std::to_string(shutter_speed_values_.size()) + " shutter speed values - expected ~56");
        }
        if (aperture_values_.size() < 5) {
            LOG_WARNING(LogContext::CAMERA, "PropertyLoader: Only loaded " + std::to_string(aperture_values_.size()) + " aperture values - expected ~23");
        }

        initialized_ = true;
        LOG_INFO(LogContext::CAMERA, "PropertyLoader: Initialization complete");
        LOG_INFO(LogContext::CAMERA, "PropertyLoader: Loaded total of " +
                    std::to_string(iso_values_.size() + shutter_speed_values_.size() + aperture_values_.size()) +
                    " property values from specification");

        return true;

    } catch (const json::parse_error& e) {
        LOG_ERROR(LogContext::CAMERA, "PropertyLoader: JSON parse error: " + std::string(e.what()));
        return false;
    } catch (const json::type_error& e) {
        LOG_ERROR(LogContext::CAMERA, "PropertyLoader: JSON type error: " + std::string(e.what()));
        return false;
    } catch (const std::exception& e) {
        LOG_ERROR(LogContext::CAMERA, "PropertyLoader: Unexpected error: " + std::string(e.what()));
        return false;
    }
}

bool PropertyLoader::isInitialized() {
    return initialized_;
}

const std::unordered_set<std::string>& PropertyLoader::getIsoValues() {
    if (!initialized_) {
        LOG_ERROR(LogContext::CAMERA, "PropertyLoader::getIsoValues() called before initialization!");
        static std::unordered_set<std::string> empty;
        return empty;
    }
    return iso_values_;
}

const std::unordered_set<std::string>& PropertyLoader::getShutterSpeedValues() {
    if (!initialized_) {
        LOG_ERROR(LogContext::CAMERA, "PropertyLoader::getShutterSpeedValues() called before initialization!");
        static std::unordered_set<std::string> empty;
        return empty;
    }
    return shutter_speed_values_;
}

const std::unordered_set<std::string>& PropertyLoader::getApertureValues() {
    if (!initialized_) {
        LOG_ERROR(LogContext::CAMERA, "PropertyLoader::getApertureValues() called before initialization!");
        static std::unordered_set<std::string> empty;
        return empty;
    }
    return aperture_values_;
}

bool PropertyLoader::isValidValue(const std::string& property, const std::string& value) {
    if (!initialized_) {
        LOG_ERROR(LogContext::CAMERA, "PropertyLoader::isValidValue() called before initialization!");
        return false;
    }

    if (property == "iso") {
        return iso_values_.find(value) != iso_values_.end();
    } else if (property == "shutter_speed") {
        return shutter_speed_values_.find(value) != shutter_speed_values_.end();
    } else if (property == "aperture") {
        return aperture_values_.find(value) != aperture_values_.end();
    } else {
        LOG_WARNING(LogContext::CAMERA, "PropertyLoader::isValidValue() called with unknown property: " + property);
        return false;
    }
}

size_t PropertyLoader::getValueCount(const std::string& property) {
    if (!initialized_) {
        return 0;
    }

    if (property == "iso") {
        return iso_values_.size();
    } else if (property == "shutter_speed") {
        return shutter_speed_values_.size();
    } else if (property == "aperture") {
        return aperture_values_.size();
    } else {
        return 0;
    }
}
