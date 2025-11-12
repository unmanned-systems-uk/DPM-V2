#ifndef CONSOLE_SINK_H
#define CONSOLE_SINK_H

#include "../log_sink.h"
#include <iostream>

class ConsoleSink : public LogSink {
public:
    ConsoleSink() = default;
    ~ConsoleSink() override = default;

    void write(const json& log_entry) override;
    void flush() override;
    std::string name() const override;
};

#endif // CONSOLE_SINK_H
