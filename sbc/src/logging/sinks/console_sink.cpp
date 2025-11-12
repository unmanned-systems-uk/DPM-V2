#include "console_sink.h"

void ConsoleSink::write(const json& log_entry) {
    // Output as compact JSON (one line)
    std::cout << log_entry.dump() << std::endl;
}

void ConsoleSink::flush() {
    std::cout.flush();
}

std::string ConsoleSink::name() const {
    return "console";
}
