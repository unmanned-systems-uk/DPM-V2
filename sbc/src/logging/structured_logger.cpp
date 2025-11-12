#include "logging/structured_logger.h"
#include "logging/log_sink.h"
#include <chrono>
#include <iomanip>
#include <sstream>
#include <thread>

StructuredLogger& StructuredLogger::getInstance() {
    static StructuredLogger instance;
    return instance;
}

void StructuredLogger::init() {
    std::lock_guard<std::mutex> lock(mutex_);
    // Initialization if needed
}

void StructuredLogger::shutdown() {
    std::lock_guard<std::mutex> lock(mutex_);

    // Flush all sinks
    for (auto& sink : sinks_) {
        sink->flush();
    }

    sinks_.clear();
}

void StructuredLogger::setLevel(LogLevel level) {
    std::lock_guard<std::mutex> lock(mutex_);
    min_level_ = level;
}

void StructuredLogger::addSink(std::shared_ptr<LogSink> sink) {
    std::lock_guard<std::mutex> lock(mutex_);
    sinks_.push_back(sink);
}

void StructuredLogger::removeSink(std::shared_ptr<LogSink> sink) {
    std::lock_guard<std::mutex> lock(mutex_);
    sinks_.erase(std::remove(sinks_.begin(), sinks_.end(), sink), sinks_.end());
}

void StructuredLogger::log(LogLevel level, LogContext context,
                            const std::string& message, const json& fields) {
    // Check log level (without lock for performance)
    if (level < min_level_) {
        return;
    }

    // Build log entry
    json log_entry = buildLogEntry(level, context, message, fields);

    // Write to all sinks
    std::lock_guard<std::mutex> lock(mutex_);
    for (auto& sink : sinks_) {
        try {
            sink->write(log_entry);
        } catch (const std::exception& e) {
            // Sink failure should not crash the application
            // TODO: Consider fallback logging
        }
    }
}

json StructuredLogger::buildLogEntry(LogLevel level, LogContext context,
                                      const std::string& message, const json& fields) {
    // Get current timestamp in ISO 8601 format
    auto now = std::chrono::system_clock::now();
    auto now_time_t = std::chrono::system_clock::to_time_t(now);
    auto now_ms = std::chrono::duration_cast<std::chrono::milliseconds>(
        now.time_since_epoch()) % 1000;

    std::stringstream timestamp_ss;
    timestamp_ss << std::put_time(std::gmtime(&now_time_t), "%Y-%m-%dT%H:%M:%S")
                 << '.' << std::setfill('0') << std::setw(3) << now_ms.count() << 'Z';

    // Get thread ID
    std::stringstream thread_ss;
    thread_ss << std::this_thread::get_id();

    // Build base log entry
    json entry;
    entry["timestamp"] = timestamp_ss.str();
    entry["level"] = levelToString(level);
    entry["context"] = contextToString(context);
    entry["thread"] = thread_ss.str();
    entry["message"] = message;

    // Merge additional structured fields
    if (!fields.is_null() && fields.is_object()) {
        for (auto& [key, value] : fields.items()) {
            entry[key] = value;
        }
    }

    return entry;
}

std::string StructuredLogger::levelToString(LogLevel level) {
    switch (level) {
        case LogLevel::DEBUG:   return "DEBUG";
        case LogLevel::INFO:    return "INFO";
        case LogLevel::WARNING: return "WARNING";
        case LogLevel::ERROR:   return "ERROR";
        default:                return "UNKNOWN";
    }
}

std::string StructuredLogger::contextToString(LogContext context) {
    switch (context) {
        case LogContext::CAMERA:  return "CAMERA";
        case LogContext::NETWORK: return "NETWORK";
        case LogContext::SYNC:    return "SYNC";
        case LogContext::COMMAND: return "COMMAND";
        case LogContext::SYSTEM:  return "SYSTEM";
        case LogContext::STORAGE: return "STORAGE";
        default:                  return "UNKNOWN";
    }
}
