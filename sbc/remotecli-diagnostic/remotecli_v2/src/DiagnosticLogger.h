#pragma once

#include <iostream>
#include <fstream>
#include <sstream>
#include <chrono>
#include <iomanip>
#include <mutex>
#include <ctime>

/**
 * DiagnosticLogger - Comprehensive logging for RemoteCli v2
 *
 * Provides timestamped, thread-safe logging to both console and file
 * for detailed diagnostic information during Sony SDK operations.
 */
class DiagnosticLogger {
public:
    enum class Level {
        DEBUG,
        INFO,
        WARN,
        ERROR
    };

    static DiagnosticLogger& instance() {
        static DiagnosticLogger logger;
        return logger;
    }

    void init(const std::string& log_file = "/app/logs/remotecli_v2.log") {
        std::lock_guard<std::mutex> lock(mutex_);
        if (!file_stream_.is_open()) {
            file_stream_.open(log_file, std::ios::out | std::ios::app);
            if (file_stream_.is_open()) {
                log(Level::INFO, "DiagnosticLogger", "Log file opened: " + log_file);
            }
        }
    }

    void log(Level level, const std::string& component, const std::string& message) {
        std::lock_guard<std::mutex> lock(mutex_);

        std::string timestamp = get_timestamp();
        std::string level_str = level_to_string(level);

        std::ostringstream oss;
        oss << "[" << timestamp << "] "
            << "[" << level_str << "] "
            << "[" << component << "] "
            << message;

        std::string log_line = oss.str();

        // Output to console
        std::cout << log_line << std::endl;

        // Output to file
        if (file_stream_.is_open()) {
            file_stream_ << log_line << std::endl;
            file_stream_.flush();
        }
    }

    void log_sdk_call(const std::string& function_name, int result_code) {
        std::ostringstream oss;
        oss << "SDK Call: " << function_name
            << " -> Result: 0x" << std::hex << result_code << std::dec;
        if (result_code == 0) {
            oss << " (SUCCESS)";
            log(Level::INFO, "SDK", oss.str());
        } else {
            oss << " (FAILED)";
            log(Level::ERROR, "SDK", oss.str());
        }
    }

    void log_property(const std::string& property_name, uint64_t value) {
        std::ostringstream oss;
        oss << "Property: " << property_name
            << " = 0x" << std::hex << value << std::dec
            << " (" << value << ")";
        log(Level::INFO, "PROPERTY", oss.str());
    }

    void log_callback(const std::string& callback_name, const std::string& details) {
        std::ostringstream oss;
        oss << "Callback: " << callback_name;
        if (!details.empty()) {
            oss << " - " << details;
        }
        log(Level::INFO, "CALLBACK", oss.str());
    }

    void debug(const std::string& component, const std::string& message) {
        log(Level::DEBUG, component, message);
    }

    void info(const std::string& component, const std::string& message) {
        log(Level::INFO, component, message);
    }

    void warn(const std::string& component, const std::string& message) {
        log(Level::WARN, component, message);
    }

    void error(const std::string& component, const std::string& message) {
        log(Level::ERROR, component, message);
    }

    ~DiagnosticLogger() {
        if (file_stream_.is_open()) {
            log(Level::INFO, "DiagnosticLogger", "Closing log file");
            file_stream_.close();
        }
    }

private:
    DiagnosticLogger() = default;
    DiagnosticLogger(const DiagnosticLogger&) = delete;
    DiagnosticLogger& operator=(const DiagnosticLogger&) = delete;

    std::string get_timestamp() {
        auto now = std::chrono::system_clock::now();
        auto now_c = std::chrono::system_clock::to_time_t(now);
        auto now_ms = std::chrono::duration_cast<std::chrono::milliseconds>(
            now.time_since_epoch()) % 1000;

        std::tm tm_buf;
        localtime_r(&now_c, &tm_buf);

        std::ostringstream oss;
        oss << std::put_time(&tm_buf, "%Y-%m-%d %H:%M:%S")
            << '.' << std::setfill('0') << std::setw(3) << now_ms.count();
        return oss.str();
    }

    std::string level_to_string(Level level) {
        switch (level) {
            case Level::DEBUG: return "DEBUG";
            case Level::INFO:  return "INFO ";
            case Level::WARN:  return "WARN ";
            case Level::ERROR: return "ERROR";
            default: return "?????";
        }
    }

    std::mutex mutex_;
    std::ofstream file_stream_;
};

// Convenience macros for logging
#define DIAG_LOG_DEBUG(component, message) DiagnosticLogger::instance().debug(component, message)
#define DIAG_LOG_INFO(component, message) DiagnosticLogger::instance().info(component, message)
#define DIAG_LOG_WARN(component, message) DiagnosticLogger::instance().warn(component, message)
#define DIAG_LOG_ERROR(component, message) DiagnosticLogger::instance().error(component, message)
#define DIAG_LOG_SDK(function, result) DiagnosticLogger::instance().log_sdk_call(function, result)
#define DIAG_LOG_PROPERTY(name, value) DiagnosticLogger::instance().log_property(name, value)
#define DIAG_LOG_CALLBACK(name, details) DiagnosticLogger::instance().log_callback(name, details)
