#ifndef STRUCTURED_LOGGER_H
#define STRUCTURED_LOGGER_H

#include <string>
#include <vector>
#include <memory>
#include <mutex>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

// Forward declarations
class LogSink;

enum class LogLevel {
    DEBUG,
    INFO,
    WARNING,
    ERROR
};

enum class LogContext {
    CAMERA,
    NETWORK,
    SYNC,
    COMMAND,
    SYSTEM,
    STORAGE
};

class StructuredLogger {
public:
    static StructuredLogger& getInstance();

    // Initialize logger (call once at startup)
    void init();

    // Shutdown logger
    void shutdown();

    // Set minimum log level
    void setLevel(LogLevel level);

    // Add/remove sinks
    void addSink(std::shared_ptr<LogSink> sink);
    void removeSink(std::shared_ptr<LogSink> sink);

    // Network streaming control (for Ground-Side on-demand logging)
    void enableGroundStreaming(int duration_sec = 300);
    void disableGroundStreaming();
    bool isGroundStreamingEnabled() const;

    // Core logging method with structured fields
    void log(LogLevel level, LogContext context, const std::string& message,
             const json& fields = json::object());

    // Helper methods
    static std::string levelToString(LogLevel level);
    static std::string contextToString(LogContext context);

private:
    StructuredLogger() = default;
    ~StructuredLogger() = default;

    // Delete copy/move constructors and operators
    StructuredLogger(const StructuredLogger&) = delete;
    StructuredLogger& operator=(const StructuredLogger&) = delete;
    StructuredLogger(StructuredLogger&&) = delete;
    StructuredLogger& operator=(StructuredLogger&&) = delete;

    // Build log entry as JSON
    json buildLogEntry(LogLevel level, LogContext context,
                       const std::string& message, const json& fields);

    std::vector<std::shared_ptr<LogSink>> sinks_;
    LogLevel min_level_ = LogLevel::INFO;
    mutable std::mutex mutex_;
};

// Logging macros with structured fields
#define LOG_DEBUG(context, message, ...) \
    StructuredLogger::getInstance().log(LogLevel::DEBUG, context, message, ##__VA_ARGS__)

#define LOG_INFO(context, message, ...) \
    StructuredLogger::getInstance().log(LogLevel::INFO, context, message, ##__VA_ARGS__)

#define LOG_WARNING(context, message, ...) \
    StructuredLogger::getInstance().log(LogLevel::WARNING, context, message, ##__VA_ARGS__)

#define LOG_ERROR(context, message, ...) \
    StructuredLogger::getInstance().log(LogLevel::ERROR, context, message, ##__VA_ARGS__)

#endif // STRUCTURED_LOGGER_H
