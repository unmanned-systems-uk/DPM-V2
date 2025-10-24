#include "utils/system_info.h"
#include "utils/logger.h"
#include <fstream>
#include <sstream>
#include <algorithm>
#include <sys/statvfs.h>
#include <unistd.h>

messages::SystemStatus SystemInfo::getStatus() {
    messages::SystemStatus status;

    try {
        status.uptime_seconds = getUptimeSeconds();
        status.cpu_percent = getCPUPercent();
        status.memory_mb = getMemoryUsedMB();
        status.memory_total_mb = getMemoryTotalMB();
        status.disk_free_gb = getDiskFreeGB();
        status.network_rx_mbps = getNetworkRxMbps();
        status.network_tx_mbps = getNetworkTxMbps();
    } catch (const std::exception& e) {
        Logger::error("Failed to get system status: " + std::string(e.what()));
    }

    return status;
}

int64_t SystemInfo::getUptimeSeconds() {
    try {
        std::string content = readFile("/proc/uptime");
        std::istringstream iss(content);
        double uptime;
        iss >> uptime;
        return static_cast<int64_t>(uptime);
    } catch (...) {
        return 0;
    }
}

double SystemInfo::getCPUPercent() {
    // Simple CPU usage calculation
    // For Phase 1, we'll use a basic approach
    // Read /proc/stat twice with a small delay for more accurate measurement

    try {
        std::string content = readFile("/proc/stat");
        std::istringstream iss(content);
        std::string cpu;
        int64_t user, nice, system, idle, iowait, irq, softirq;

        iss >> cpu >> user >> nice >> system >> idle >> iowait >> irq >> softirq;

        if (cpu != "cpu") {
            return 0.0;
        }

        int64_t total = user + nice + system + idle + iowait + irq + softirq;
        int64_t work = user + nice + system;

        // For Phase 1, return a simple estimate
        // In a real implementation, we'd compare with previous reading
        if (total > 0) {
            return (work * 100.0) / total;
        }
    } catch (...) {
        // Ignore errors
    }

    return 0.0;
}

int64_t SystemInfo::getMemoryUsedMB() {
    try {
        std::string content = readFile("/proc/meminfo");
        std::istringstream iss(content);
        std::string line;

        int64_t mem_total = 0, mem_available = 0;

        while (std::getline(iss, line)) {
            if (line.find("MemTotal:") == 0) {
                std::istringstream line_iss(line);
                std::string key, value;
                line_iss >> key >> mem_total;
            } else if (line.find("MemAvailable:") == 0) {
                std::istringstream line_iss(line);
                std::string key, value;
                line_iss >> key >> mem_available;
            }
        }

        // mem_total and mem_available are in kB, convert to MB
        return (mem_total - mem_available) / 1024;
    } catch (...) {
        return 0;
    }
}

int64_t SystemInfo::getMemoryTotalMB() {
    try {
        std::string content = readFile("/proc/meminfo");
        std::istringstream iss(content);
        std::string line;

        while (std::getline(iss, line)) {
            if (line.find("MemTotal:") == 0) {
                std::istringstream line_iss(line);
                std::string key;
                int64_t value;
                line_iss >> key >> value;
                // Value is in kB, convert to MB
                return value / 1024;
            }
        }
    } catch (...) {
        // Ignore errors
    }

    return 0;
}

double SystemInfo::getDiskFreeGB() {
    try {
        struct statvfs stat;
        if (statvfs("/home", &stat) == 0) {
            // Available space in GB
            double free_bytes = static_cast<double>(stat.f_bavail) * stat.f_frsize;
            return free_bytes / (1024.0 * 1024.0 * 1024.0);
        }
    } catch (...) {
        // Ignore errors
    }

    return 0.0;
}

double SystemInfo::getNetworkRxMbps() {
    // For Phase 1, return placeholder
    // In a real implementation, we'd read /proc/net/dev and calculate rate
    return 0.0;
}

double SystemInfo::getNetworkTxMbps() {
    // For Phase 1, return placeholder
    // In a real implementation, we'd read /proc/net/dev and calculate rate
    return 0.0;
}

std::string SystemInfo::readFile(const std::string& path) {
    std::ifstream file(path);
    if (!file.is_open()) {
        throw std::runtime_error("Failed to open file: " + path);
    }

    std::ostringstream ss;
    ss << file.rdbuf();
    return ss.str();
}

std::string SystemInfo::trim(const std::string& str) {
    auto start = str.begin();
    while (start != str.end() && std::isspace(*start)) {
        start++;
    }

    auto end = str.end();
    do {
        end--;
    } while (std::distance(start, end) > 0 && std::isspace(*end));

    return std::string(start, end + 1);
}
