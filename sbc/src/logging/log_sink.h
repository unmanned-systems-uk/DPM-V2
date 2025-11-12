#ifndef LOG_SINK_H
#define LOG_SINK_H

#include <nlohmann/json.hpp>

using json = nlohmann::json;

class LogSink {
public:
    virtual ~LogSink() = default;

    // Write a log entry (as JSON) to the sink
    virtual void write(const json& log_entry) = 0;

    // Flush any buffered data
    virtual void flush() = 0;

    // Get sink name for debugging
    virtual std::string name() const = 0;
};

#endif // LOG_SINK_H
