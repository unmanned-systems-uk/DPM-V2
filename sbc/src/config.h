#ifndef CONFIG_H
#define CONFIG_H

#include <string>
#include <cstdlib>

namespace config {
    // Network configuration
    constexpr int TCP_PORT = 5000;
    constexpr int UDP_STATUS_PORT = 5001;
    constexpr int UDP_HEARTBEAT_PORT = 5002;

    // Alternative UDP ports (for Windows Tools with firewall restrictions)
    constexpr int UDP_STATUS_PORT_ALT = 50001;
    constexpr int UDP_HEARTBEAT_PORT_ALT = 50002;

    constexpr const char* GROUND_IP = "192.168.144.11";  // Default (R16 ethernet)
    constexpr const char* AIR_IP = "192.168.144.20";

    // Dynamic IP configuration (supports WiFi testing via environment variable)
    // Set DPM_GROUND_IP environment variable to override default ground station IP
    // Example: DPM_GROUND_IP=10.0.1.100 ./payload_manager
    inline std::string getGroundStationIP() {
        const char* env_ip = std::getenv("DPM_GROUND_IP");
        if (env_ip != nullptr && env_ip[0] != '\0') {
            return std::string(env_ip);
        }
        return GROUND_IP;  // Default to R16 ethernet IP
    }

    // Timing configuration
    constexpr int STATUS_INTERVAL_MS = 200;      // 5 Hz
    constexpr int HEARTBEAT_INTERVAL_MS = 1000;  // 1 Hz
    constexpr int HEARTBEAT_TIMEOUT_SEC = 10;

    // Protocol configuration
    constexpr const char* PROTOCOL_VERSION = "1.0";
    constexpr const char* SERVER_ID = "payload_manager";
    constexpr const char* SERVER_VERSION = "1.0.0";

    // Logging configuration
    constexpr const char* LOG_FILE = "/home/dpm/DPM/sbc/logs/payload_manager.log";

    // Buffer sizes
    constexpr int TCP_BUFFER_SIZE = 8192;
    constexpr int UDP_BUFFER_SIZE = 4096;
    constexpr int MAX_TCP_CLIENTS = 5;

    // Capabilities (Phase 1)
    constexpr const char* CAPABILITIES[] = {
        "handshake",
        "system.get_status"
    };
    constexpr int CAPABILITIES_COUNT = 2;
}

#endif // CONFIG_H
