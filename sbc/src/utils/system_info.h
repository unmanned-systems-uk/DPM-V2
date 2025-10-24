#ifndef SYSTEM_INFO_H
#define SYSTEM_INFO_H

#include <cstdint>
#include <string>
#include "protocol/messages.h"

class SystemInfo {
public:
    // Get current system status
    static messages::SystemStatus getStatus();

private:
    // Individual metric readers
    static int64_t getUptimeSeconds();
    static double getCPUPercent();
    static int64_t getMemoryUsedMB();
    static int64_t getMemoryTotalMB();
    static double getDiskFreeGB();
    static double getNetworkRxMbps();
    static double getNetworkTxMbps();

    // Helper functions
    static std::string readFile(const std::string& path);
    static std::string trim(const std::string& str);
};

#endif // SYSTEM_INFO_H
