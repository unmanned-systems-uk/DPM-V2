#ifndef UDP_DISCOVERY_LISTENER_H
#define UDP_DISCOVERY_LISTENER_H

#include <string>
#include <atomic>
#include <thread>
#include <mutex>

/**
 * UDP Discovery Listener - Automatic SystemTools IP Detection
 *
 * Listens on UDP port 5009 for discovery packets from SystemTools.
 * When received, extracts source IP and updates NetworkSink dynamically.
 *
 * Protocol: JSON over UDP
 * {
 *   "type": "discovery",
 *   "source": "systemtools",
 *   "version": "1.0",
 *   "timestamp": "2025-11-15T10:00:00Z"
 * }
 *
 * Related: Issue #110, Issue #99
 */
class UdpDiscoveryListener {
public:
    UdpDiscoveryListener(int port);
    ~UdpDiscoveryListener();

    void start();
    void stop();
    bool isRunning() const;

    // Get last detected SystemTools IP
    std::string getDetectedIP() const;

    // Get time since last discovery packet (seconds)
    int getTimeSinceLastDiscovery() const;

private:
    void listenerThread();
    bool validateDiscoveryPacket(const std::string& data);

    int port_;
    int socket_fd_;
    std::atomic<bool> running_;
    std::thread listener_thread_;

    // Last detected SystemTools IP
    std::string detected_ip_;
    time_t last_discovery_time_;
    mutable std::mutex mutex_;
};

#endif // UDP_DISCOVERY_LISTENER_H
