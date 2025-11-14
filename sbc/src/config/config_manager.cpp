#include "config/config_manager.h"
#include "utils/logger.h"
#include <fstream>
#include <sstream>
#include <cstdlib>
#include <filesystem>
#include "logging/structured_logger.h"

namespace fs = std::filesystem;

ConfigManager& ConfigManager::getInstance() {
    static ConfigManager instance;
    return instance;
}

void ConfigManager::load(const std::string& environment) {
    std::lock_guard<std::mutex> lock(mutex_);

    // Determine config directory (try /app/config first, fallback to relative path)
    if (fs::exists("/app/config")) {
        config_dir_ = "/app/config";
    } else {
        config_dir_ = "./sbc/config";
    }

    LOG_INFO(LogContext::SYSTEM, "ConfigManager: Loading configuration from " + config_dir_);

    // Load default.json (required)
    std::string default_path = config_dir_ + "/default.json";
    if (!fs::exists(default_path)) {
        LOG_ERROR(LogContext::SYSTEM, "ConfigManager: default.json not found at " + default_path);
        throw std::runtime_error("default.json not found");
    }
    loadFile(default_path);

    // Load environment-specific config
    std::string env = environment;
    if (env.empty()) {
        const char* env_var = std::getenv("ENVIRONMENT");
        env = env_var ? env_var : "production";
    }

    std::string env_path = config_dir_ + "/" + env + ".json";
    if (fs::exists(env_path)) {
        loadFile(env_path);
        LOG_INFO(LogContext::SYSTEM, "ConfigManager: Loaded environment config: " + env);
    } else {
        LOG_WARNING(LogContext::SYSTEM, "ConfigManager: Environment config not found: " + env_path);
    }

    // Load local.json (optional, for runtime changes)
    std::string local_path = config_dir_ + "/local.json";
    if (fs::exists(local_path)) {
        loadFile(local_path);
        LOG_INFO(LogContext::SYSTEM, "ConfigManager: Loaded local.json");
    }

    // Apply environment variables (override config)
    // Example: DPM_NETWORK_GROUND_IP overrides network.ground_ip
    if (const char* ground_ip = std::getenv("DPM_NETWORK_GROUND_IP")) {
        setValue("network.ground_ip", json(ground_ip));
        LOG_INFO(LogContext::SYSTEM, "ConfigManager: Applied env var DPM_NETWORK_GROUND_IP=" + std::string(ground_ip));
    }

    std::string version = config_.contains("version") ? config_["version"].get<std::string>() : "unknown";
    LOG_INFO(LogContext::SYSTEM, "ConfigManager: Configuration loaded (env=" + env + ", version=" + version + ")");
}

void ConfigManager::loadFile(const std::string& filename) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        LOG_WARNING(LogContext::SYSTEM, "ConfigManager: Could not open file: " + filename);
        return;
    }

    try {
        json file_json;
        file >> file_json;
        mergeJson(file_json);
        LOG_DEBUG(LogContext::SYSTEM, "ConfigManager: Loaded file: " + filename);
    } catch (const json::parse_error& e) {
        LOG_ERROR(LogContext::SYSTEM, "ConfigManager: JSON parse error in " + filename + ": " + e.what());
        throw;
    }
}

void ConfigManager::mergeJson(const json& source) {
    // Deep merge (source overwrites config_)
    config_.merge_patch(source);
}

json ConfigManager::getValue(const std::string& path) const {
    std::lock_guard<std::mutex> lock(mutex_);

    // Parse dot notation: "network.tcp_port" → config_["network"]["tcp_port"]
    json result = config_;
    std::istringstream iss(path);
    std::string token;

    while (std::getline(iss, token, '.')) {
        if (!result.contains(token)) {
            LOG_ERROR(LogContext::SYSTEM, "ConfigManager: Config path not found: " + path);
            throw std::runtime_error("Config path not found: " + path);
        }
        result = result[token];
    }

    return result;
}

void ConfigManager::setValue(const std::string& path, const json& value) {
    std::lock_guard<std::mutex> lock(mutex_);

    // Navigate to parent object
    json* current = &config_;
    std::istringstream iss(path);
    std::string token;
    std::vector<std::string> tokens;

    while (std::getline(iss, token, '.')) {
        tokens.push_back(token);
    }

    // Navigate to parent
    for (size_t i = 0; i < tokens.size() - 1; i++) {
        if (!current->contains(tokens[i])) {
            (*current)[tokens[i]] = json::object();
        }
        current = &(*current)[tokens[i]];
    }

    // Set value
    (*current)[tokens.back()] = value;
}

int ConfigManager::getInt(const std::string& path) const {
    return getValue(path).get<int>();
}

float ConfigManager::getFloat(const std::string& path) const {
    return getValue(path).get<float>();
}

std::string ConfigManager::getString(const std::string& path) const {
    return getValue(path).get<std::string>();
}

bool ConfigManager::getBool(const std::string& path) const {
    return getValue(path).get<bool>();
}

bool ConfigManager::set(const std::string& path, const json& value) {
    try {
        setValue(path, value);
        LOG_INFO(LogContext::SYSTEM, "ConfigManager: Set " + path + " = " + value.dump());
        return true;
    } catch (const std::exception& e) {
        LOG_ERROR(LogContext::SYSTEM, "ConfigManager: Failed to set " + path + ": " + e.what());
        return false;
    }
}

void ConfigManager::saveLocal() {
    std::lock_guard<std::mutex> lock(mutex_);

    std::string local_path = config_dir_ + "/local.json";

    try {
        std::ofstream file(local_path);
        if (!file.is_open()) {
            LOG_ERROR(LogContext::SYSTEM, "ConfigManager: Could not open local.json for writing");
            return;
        }

        file << config_.dump(2);  // Pretty print with 2-space indent
        LOG_INFO(LogContext::SYSTEM, "ConfigManager: Saved configuration to local.json");
    } catch (const std::exception& e) {
        LOG_ERROR(LogContext::SYSTEM, "ConfigManager: Failed to save local.json: " + std::string(e.what()));
    }
}

json ConfigManager::exportConfig() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return config_;
}

void ConfigManager::importConfig(const json& config) {
    std::lock_guard<std::mutex> lock(mutex_);
    config_ = config;
    LOG_INFO(LogContext::SYSTEM, "ConfigManager: Imported configuration");
}

bool ConfigManager::validate(const json& config) const {
    // Basic validation - check required fields exist
    // TODO: Implement full JSON schema validation when needed
    if (!config.contains("version")) {
        LOG_ERROR(LogContext::SYSTEM, "ConfigManager: Missing required field: version");
        return false;
    }

    if (!config.contains("network")) {
        LOG_ERROR(LogContext::SYSTEM, "ConfigManager: Missing required field: network");
        return false;
    }

    return true;
}

bool ConfigManager::validatePath(const std::string& path, const json& value) const {
    // TODO: Implement schema-based validation
    // For now, just check basic type compatibility
    return true;
}
