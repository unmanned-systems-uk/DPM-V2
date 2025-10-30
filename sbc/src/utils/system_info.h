#ifndef SYSTEM_INFO_H
#define SYSTEM_INFO_H

#include <cstdint>
#include <string>
#include <chrono>
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

    // Network statistics tracking
    struct NetworkStats {
        int64_t rx_bytes;
        int64_t tx_bytes;
        std::chrono::steady_clock::time_point timestamp;
    };
    static NetworkStats last_network_stats_;
    static bool network_stats_initialized_;

    // CPU statistics tracking
    struct CPUStats {
        int64_t total;
        int64_t idle;
        std::chrono::steady_clock::time_point timestamp;
    };
    static CPUStats last_cpu_stats_;
    static bool cpu_stats_initialized_;
};

#endif // SYSTEM_INFO_H
