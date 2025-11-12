#ifndef CONFIG_MANAGER_H
#define CONFIG_MANAGER_H

#include <string>
#include <mutex>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

class ConfigManager {
public:
    static ConfigManager& getInstance();

    // Load configuration (call once at startup)
    void load(const std::string& environment = "");

    // Type-safe getters (with dot notation)
    int getInt(const std::string& path) const;
    float getFloat(const std::string& path) const;
    std::string getString(const std::string& path) const;
    bool getBool(const std::string& path) const;

    // Runtime updates (from Ground-Side)
    bool set(const std::string& path, const json& value);

    // Persistence
    void saveLocal();  // Save current config to local.json

    // Export/import
    json exportConfig() const;
    void importConfig(const json& config);

    // Validation
    bool validate(const json& config) const;

private:
    ConfigManager() = default;
    ~ConfigManager() = default;

    // Delete copy/move constructors and operators
    ConfigManager(const ConfigManager&) = delete;
    ConfigManager& operator=(const ConfigManager&) = delete;
    ConfigManager(ConfigManager&&) = delete;
    ConfigManager& operator=(ConfigManager&&) = delete;

    void loadFile(const std::string& filename);
    void mergeJson(const json& source);
    json getValue(const std::string& path) const;
    void setValue(const std::string& path, const json& value);
    bool validatePath(const std::string& path, const json& value) const;

    json config_;
    json schema_;
    std::string config_dir_;
    mutable std::mutex mutex_;
};

// Convenience macros
#define CONFIG_INT(path) ConfigManager::getInstance().getInt(path)
#define CONFIG_FLOAT(path) ConfigManager::getInstance().getFloat(path)
#define CONFIG_STRING(path) ConfigManager::getInstance().getString(path)
#define CONFIG_BOOL(path) ConfigManager::getInstance().getBool(path)

#endif // CONFIG_MANAGER_H
