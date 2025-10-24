#ifndef LOGGER_H
#define LOGGER_H

#include <string>
#include <fstream>
#include <mutex>
#include <sstream>
#include <thread>

class Logger {
public:
    enum class Level {
        DEBUG,
        INFO,
        WARNING,
        ERROR
    };

    // Initialize logger with file path
    static void init(const std::string& log_file_path);

    // Set minimum log level
    static void setLevel(Level min_level);

    // Close log file
    static void close();

    // Logging methods
    static void debug(const std::string& message);
    static void info(const std::string& message);
    static void warning(const std::string& message);
    static void error(const std::string& message);

private:
    // Internal logging function
    static void log(Level level, const std::string& message);

    // Helper functions
    static std::string levelToString(Level level);
    static std::string getTimestamp();
    static std::string getThreadId();

    // Static members
    static std::ofstream log_file_;
    static std::mutex mutex_;
    static Level min_level_;
    static bool initialized_;
};

#endif // LOGGER_H
