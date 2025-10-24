#include "utils/logger.h"
#include <iostream>
#include <iomanip>
#include <ctime>
#include <chrono>
#include <sys/stat.h>

// Initialize static members
std::ofstream Logger::log_file_;
std::mutex Logger::mutex_;
Logger::Level Logger::min_level_ = Logger::Level::INFO;
bool Logger::initialized_ = false;

void Logger::init(const std::string& log_file_path) {
    std::lock_guard<std::mutex> lock(mutex_);

    if (initialized_) {
        return;
    }

    // Create logs directory if it doesn't exist
    std::string dir = log_file_path.substr(0, log_file_path.find_last_of('/'));
    mkdir(dir.c_str(), 0755);

    log_file_.open(log_file_path, std::ios::out | std::ios::app);

    if (!log_file_.is_open()) {
        std::cerr << "Failed to open log file: " << log_file_path << std::endl;
        return;
    }

    initialized_ = true;

    // Write header
    log_file_ << "\n========================================\n";
    log_file_ << "Logger initialized at " << getTimestamp() << "\n";
    log_file_ << "========================================\n";
    log_file_.flush();
}

void Logger::setLevel(Level min_level) {
    std::lock_guard<std::mutex> lock(mutex_);
    min_level_ = min_level;
}

void Logger::close() {
    std::lock_guard<std::mutex> lock(mutex_);

    if (log_file_.is_open()) {
        log_file_ << "Logger closed at " << getTimestamp() << "\n";
        log_file_.close();
    }

    initialized_ = false;
}

void Logger::debug(const std::string& message) {
    log(Level::DEBUG, message);
}

void Logger::info(const std::string& message) {
    log(Level::INFO, message);
}

void Logger::warning(const std::string& message) {
    log(Level::WARNING, message);
}

void Logger::error(const std::string& message) {
    log(Level::ERROR, message);
}

void Logger::log(Level level, const std::string& message) {
    std::lock_guard<std::mutex> lock(mutex_);

    // Check if logging is enabled for this level
    if (level < min_level_) {
        return;
    }

    // Create log entry
    std::ostringstream oss;
    oss << "[" << getTimestamp() << "] "
        << "[" << levelToString(level) << "] "
        << "[" << getThreadId() << "] "
        << message;

    // Write to file if initialized
    if (initialized_ && log_file_.is_open()) {
        log_file_ << oss.str() << std::endl;
        log_file_.flush();
    }

    // Also write to console for errors
    if (level == Level::ERROR) {
        std::cerr << oss.str() << std::endl;
    }
}

std::string Logger::levelToString(Level level) {
    switch (level) {
        case Level::DEBUG:   return "DEBUG";
        case Level::INFO:    return "INFO ";
        case Level::WARNING: return "WARN ";
        case Level::ERROR:   return "ERROR";
        default:             return "UNKNOWN";
    }
}

std::string Logger::getTimestamp() {
    auto now = std::chrono::system_clock::now();
    auto now_time_t = std::chrono::system_clock::to_time_t(now);
    auto now_ms = std::chrono::duration_cast<std::chrono::milliseconds>(
        now.time_since_epoch()) % 1000;

    std::tm tm_buf;
    localtime_r(&now_time_t, &tm_buf);

    std::ostringstream oss;
    oss << std::put_time(&tm_buf, "%Y-%m-%d %H:%M:%S")
        << '.' << std::setfill('0') << std::setw(3) << now_ms.count();

    return oss.str();
}

std::string Logger::getThreadId() {
    std::ostringstream oss;
    oss << std::this_thread::get_id();
    return oss.str();
}
