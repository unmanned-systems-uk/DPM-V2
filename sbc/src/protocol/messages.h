#ifndef MESSAGES_H
#define MESSAGES_H

#include <string>
#include <vector>
#include <ctime>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

namespace messages {

// Error codes
enum class ErrorCode {
    INVALID_JSON = 5000,
    INVALID_PROTOCOL_VERSION = 5001,
    COMMAND_NOT_IMPLEMENTED = 5002,
    UNKNOWN_COMMAND = 5003,
    INTERNAL_ERROR = 5004,
    COMMAND_FAILED = 5005
};

// Notification levels
enum class NotificationLevel {
    INFO,
    WARNING,
    ERROR
};

// Notification categories
enum class NotificationCategory {
    CAMERA,
    GIMBAL,
    SYSTEM,
    NETWORK
};

inline std::string errorCodeToString(ErrorCode code) {
    switch (code) {
        case ErrorCode::INVALID_JSON:
            return "Invalid JSON format";
        case ErrorCode::INVALID_PROTOCOL_VERSION:
            return "Invalid protocol version";
        case ErrorCode::COMMAND_NOT_IMPLEMENTED:
            return "Command not implemented";
        case ErrorCode::UNKNOWN_COMMAND:
            return "Unknown command";
        case ErrorCode::INTERNAL_ERROR:
            return "Internal server error";
        case ErrorCode::COMMAND_FAILED:
            return "Command execution failed";
        default:
            return "Unknown error";
    }
}

inline std::string notificationLevelToString(NotificationLevel level) {
    switch (level) {
        case NotificationLevel::INFO: return "info";
        case NotificationLevel::WARNING: return "warning";
        case NotificationLevel::ERROR: return "error";
        default: return "info";
    }
}

inline std::string notificationCategoryToString(NotificationCategory category) {
    switch (category) {
        case NotificationCategory::CAMERA: return "camera";
        case NotificationCategory::GIMBAL: return "gimbal";
        case NotificationCategory::SYSTEM: return "system";
        case NotificationCategory::NETWORK: return "network";
        default: return "system";
    }
}

// Base message structure
struct BaseMessage {
    std::string protocol_version;
    std::string message_type;
    int sequence_id;
    int64_t timestamp;
    json payload;

    json toJson() const {
        return {
            {"protocol_version", protocol_version},
            {"message_type", message_type},
            {"sequence_id", sequence_id},
            {"timestamp", timestamp},
            {"payload", payload}
        };
    }
};

// System status structure
struct SystemStatus {
    int64_t uptime_seconds;
    double cpu_percent;
    int64_t memory_mb;
    int64_t memory_total_mb;
    double disk_free_gb;
    double disk_total_gb;
    double network_rx_mbps;
    double network_tx_mbps;

    json toJson() const {
        return {
            {"uptime_seconds", uptime_seconds},
            {"cpu_percent", cpu_percent},
            {"memory_mb", memory_mb},
            {"memory_total_mb", memory_total_mb},
            {"disk_free_gb", disk_free_gb},
            {"disk_total_gb", disk_total_gb},
            {"network_rx_mbps", network_rx_mbps},
            {"network_tx_mbps", network_tx_mbps}
        };
    }
};

// Camera status structure
struct CameraStatus {
    bool connected;
    std::string model;
    int battery_percent;
    int remaining_shots;

    // Current camera properties (for UI synchronization)
    std::string shutter_speed;
    std::string aperture;
    std::string iso;
    std::string white_balance;
    std::string focus_mode;
    std::string file_format;

    json toJson() const {
        json result = {
            {"connected", connected},
            {"model", model},
            {"battery_percent", battery_percent},
            {"remaining_shots", remaining_shots}
        };

        // Add current settings if camera is connected
        if (connected) {
            result["settings"] = {
                {"shutter_speed", shutter_speed},
                {"aperture", aperture},
                {"iso", iso},
                {"white_balance", white_balance},
                {"focus_mode", focus_mode},
                {"file_format", file_format}
            };
        }

        return result;
    }
};

// Gimbal status structure (Phase 3)
struct GimbalStatus {
    bool connected;

    json toJson() const {
        return {
            {"connected", connected}
        };
    }
};

// Create success response
inline json createSuccessResponse(int seq_id, const std::string& command, const json& result) {
    return {
        {"protocol_version", "1.0"},
        {"message_type", "response"},
        {"sequence_id", seq_id},
        {"timestamp", std::time(nullptr)},
        {"payload", {
            {"command", command},
            {"status", "success"},
            {"result", result}
        }}
    };
}

// Create error response
inline json createErrorResponse(int seq_id, const std::string& command,
                               ErrorCode error_code, const std::string& details = "") {
    return {
        {"protocol_version", "1.0"},
        {"message_type", "response"},
        {"sequence_id", seq_id},
        {"timestamp", std::time(nullptr)},
        {"payload", {
            {"command", command},
            {"status", "error"},
            {"error", {
                {"code", static_cast<int>(error_code)},
                {"message", errorCodeToString(error_code)},
                {"details", details}
            }}
        }}
    };
}

// Create status broadcast message
inline json createStatusMessage(int seq_id, const SystemStatus& system,
                               const CameraStatus& camera, const GimbalStatus& gimbal) {
    return {
        {"protocol_version", "1.0"},
        {"message_type", "status"},
        {"sequence_id", seq_id},
        {"timestamp", std::time(nullptr)},
        {"payload", {
            {"system", system.toJson()},
            {"camera", camera.toJson()},
            {"gimbal", gimbal.toJson()}
        }}
    };
}

// Create heartbeat message (v1.1.0 - includes client_id)
inline json createHeartbeatMessage(int seq_id, const std::string& sender, const std::string& client_id, int64_t uptime) {
    return {
        {"protocol_version", "1.0"},
        {"message_type", "heartbeat"},
        {"sequence_id", seq_id},
        {"timestamp", std::time(nullptr)},
        {"payload", {
            {"sender", sender},
            {"client_id", client_id},
            {"uptime_seconds", uptime}
        }}
    };
}

// Create notification message
inline json createNotificationMessage(int seq_id, NotificationLevel level,
                                     NotificationCategory category,
                                     const std::string& title,
                                     const std::string& message,
                                     const std::string& action = "",
                                     bool dismissible = true) {
    json payload = {
        {"level", notificationLevelToString(level)},
        {"category", notificationCategoryToString(category)},
        {"title", title},
        {"message", message},
        {"dismissible", dismissible}
    };

    if (!action.empty()) {
        payload["action"] = action;
    }

    return {
        {"protocol_version", "1.0"},
        {"message_type", "notification"},
        {"sequence_id", seq_id},
        {"timestamp", std::time(nullptr)},
        {"payload", payload}
    };
}

} // namespace messages

#endif // MESSAGES_H
