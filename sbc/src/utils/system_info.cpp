#include "utils/system_info.h"
#include "utils/logger.h"
#include <fstream>
#include <sstream>
#include <algorithm>
#include <sys/statvfs.h>
#include <unistd.h>

// Initialize static members
SystemInfo::NetworkStats SystemInfo::last_network_stats_ = {0, 0, std::chrono::steady_clock::now()};
bool SystemInfo::network_stats_initialized_ = false;
SystemInfo::CPUStats SystemInfo::last_cpu_stats_ = {0, 0, std::chrono::steady_clock::now()};
bool SystemInfo::cpu_stats_initialized_ = false;

messages::SystemStatus SystemInfo::getStatus() {
    messages::SystemStatus status;

    try {
        status.uptime_seconds = getUptimeSeconds();
        status.cpu_percent = getCPUPercent();
        status.memory_mb = getMemoryUsedMB();
        status.memory_total_mb = getMemoryTotalMB();
        status.disk_free_gb = getDiskFreeGB();
        status.disk_total_gb = getDiskTotalGB();
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
    try {
        std::string content = readFile("/proc/stat");
        std::istringstream iss(content);
        std::string cpu;
        int64_t user, nice, system, idle, iowait, irq, softirq, steal;

        iss >> cpu >> user >> nice >> system >> idle >> iowait >> irq >> softirq >> steal;

        if (cpu != "cpu") {
            return 0.0;
        }

        int64_t total = user + nice + system + idle + iowait + irq + softirq + steal;
        int64_t idle_total = idle + iowait;
        auto now = std::chrono::steady_clock::now();

        // On first call, just store the values
        if (!cpu_stats_initialized_) {
            last_cpu_stats_.total = total;
            last_cpu_stats_.idle = idle_total;
            last_cpu_stats_.timestamp = now;
            cpu_stats_initialized_ = true;
            // Return instant CPU percentage on first call
            double instant_usage = 100.0 * (1.0 - static_cast<double>(idle_total) / total);
            return (instant_usage < 0.0) ? 0.0 : (instant_usage > 100.0) ? 100.0 : instant_usage;
        }

        // Calculate deltas
        int64_t total_delta = total - last_cpu_stats_.total;
        int64_t idle_delta = idle_total - last_cpu_stats_.idle;

        // Update last stats
        last_cpu_stats_.total = total;
        last_cpu_stats_.idle = idle_total;
        last_cpu_stats_.timestamp = now;

        // Calculate CPU usage percentage
        if (total_delta > 0) {
            double usage = 100.0 * (1.0 - static_cast<double>(idle_delta) / total_delta);
            return (usage < 0.0) ? 0.0 : (usage > 100.0) ? 100.0 : usage;
        } else {
            Logger::warning("CPU total_delta is zero or negative: " + std::to_string(total_delta));
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

double SystemInfo::getDiskTotalGB() {
    try {
        struct statvfs stat;
        if (statvfs("/home", &stat) == 0) {
            // Total space in GB
            double total_bytes = static_cast<double>(stat.f_blocks) * stat.f_frsize;
            return total_bytes / (1024.0 * 1024.0 * 1024.0);
        }
    } catch (...) {
        // Ignore errors
    }

    return 0.0;
}

double SystemInfo::getNetworkRxMbps() {
    try {
        std::string content = readFile("/proc/net/dev");
        std::istringstream iss(content);
        std::string line;

        int64_t total_rx = 0;

        // Skip header lines
        std::getline(iss, line);
        std::getline(iss, line);

        // Sum up all network interfaces (excluding lo)
        while (std::getline(iss, line)) {
            size_t colon_pos = line.find(':');
            if (colon_pos == std::string::npos) continue;

            std::string interface = trim(line.substr(0, colon_pos));
            if (interface == "lo") continue; // Skip loopback

            std::istringstream line_iss(line.substr(colon_pos + 1));
            int64_t rx_bytes, rx_packets, rx_errs, rx_drop;
            line_iss >> rx_bytes >> rx_packets >> rx_errs >> rx_drop;

            total_rx += rx_bytes;
        }

        auto now = std::chrono::steady_clock::now();

        // On first call, just store the values
        if (!network_stats_initialized_) {
            last_network_stats_.rx_bytes = total_rx;
            last_network_stats_.timestamp = now;
            return 0.0;
        }

        // Calculate rate
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(now - last_network_stats_.timestamp).count();
        if (duration > 0 && total_rx >= last_network_stats_.rx_bytes) {
            int64_t bytes_delta = total_rx - last_network_stats_.rx_bytes;
            double seconds = duration / 1000.0;
            double mbps = (bytes_delta * 8.0) / (seconds * 1000000.0); // Convert bytes/sec to Mbps

            last_network_stats_.rx_bytes = total_rx;
            last_network_stats_.timestamp = now;

            return mbps;
        }

        // Update last value even if calculation failed
        last_network_stats_.rx_bytes = total_rx;
        last_network_stats_.timestamp = now;

    } catch (...) {
        // Ignore errors
    }

    return 0.0;
}

double SystemInfo::getNetworkTxMbps() {
    try {
        std::string content = readFile("/proc/net/dev");
        std::istringstream iss(content);
        std::string line;

        int64_t total_tx = 0;

        // Skip header lines
        std::getline(iss, line);
        std::getline(iss, line);

        // Sum up all network interfaces (excluding lo)
        while (std::getline(iss, line)) {
            size_t colon_pos = line.find(':');
            if (colon_pos == std::string::npos) continue;

            std::string interface = trim(line.substr(0, colon_pos));
            if (interface == "lo") continue; // Skip loopback

            std::istringstream line_iss(line.substr(colon_pos + 1));
            int64_t rx_bytes, rx_packets, rx_errs, rx_drop;
            int64_t tx_bytes, tx_packets, tx_errs, tx_drop;
            line_iss >> rx_bytes >> rx_packets >> rx_errs >> rx_drop
                     >> rx_drop >> rx_drop >> rx_drop >> rx_drop  // Skip remaining RX columns
                     >> tx_bytes >> tx_packets >> tx_errs >> tx_drop;

            total_tx += tx_bytes;
        }

        auto now = std::chrono::steady_clock::now();

        // On first call, just store the values
        if (!network_stats_initialized_) {
            last_network_stats_.tx_bytes = total_tx;
            last_network_stats_.timestamp = now;
            network_stats_initialized_ = true;
            return 0.0;
        }

        // Calculate rate
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(now - last_network_stats_.timestamp).count();
        if (duration > 0 && total_tx >= last_network_stats_.tx_bytes) {
            int64_t bytes_delta = total_tx - last_network_stats_.tx_bytes;
            double seconds = duration / 1000.0;
            double mbps = (bytes_delta * 8.0) / (seconds * 1000000.0); // Convert bytes/sec to Mbps

            last_network_stats_.tx_bytes = total_tx;
            last_network_stats_.timestamp = now;

            return mbps;
        }

        // Update last value even if calculation failed
        last_network_stats_.tx_bytes = total_tx;
        last_network_stats_.timestamp = now;

    } catch (...) {
        // Ignore errors
    }

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
