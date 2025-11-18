#include "network_sink.h"
#include <arpa/inet.h>
#include <unistd.h>
#include <cstring>
#include <iostream>

NetworkSink::NetworkSink(const std::string& ground_ip, int ground_port,
                         const std::string& systemtools_ip, int systemtools_port,
                         bool systemtools_enabled)
    : ground_ip_(ground_ip), ground_port_(ground_port),
      systemtools_ip_(systemtools_ip), systemtools_port_(systemtools_port),
      systemtools_enabled_(systemtools_enabled), ground_streaming_enabled_(false),
      ground_streaming_end_time_(std::chrono::system_clock::now()),
      socket_fd_(-1) {

    // Create UDP socket
    socket_fd_ = socket(AF_INET, SOCK_DGRAM, 0);
    if (socket_fd_ < 0) {
        std::cerr << "NetworkSink: Failed to create UDP socket" << std::endl;
    }

    // Add default ground IP to client list (for backwards compatibility)
    if (!ground_ip.empty() && ground_ip != "0.0.0.0") {
        client_ips_.insert(ground_ip);
    }
}

NetworkSink::~NetworkSink() {
    if (socket_fd_ >= 0) {
        close(socket_fd_);
    }
}

void NetworkSink::write(const json& log_entry) {
    std::lock_guard<std::mutex> lock(mutex_);

    // Check ground streaming timeout
    checkGroundStreamingTimeout();

    std::string data = log_entry.dump();

    // Send to Ground-Side clients if streaming is enabled
    if (ground_streaming_enabled_) {
        // Send to all registered Ground-Side clients (dynamic discovery)
        for (const auto& client_ip : client_ips_) {
            sendUDP(client_ip, ground_port_, data);
        }
    }

    // Send to SystemTools if enabled (always-on monitoring)
    // CRITICAL: Always send ERROR logs regardless of enabled state (Issue #148)
    // This ensures critical errors are visible in SystemTools even when passive logging is disabled
    bool is_error_log = log_entry.contains("level") && log_entry["level"] == "ERROR";
    if (systemtools_enabled_ || is_error_log) {
        sendUDP(systemtools_ip_, systemtools_port_, data);
    }
}

void NetworkSink::flush() {
    // UDP doesn't buffer, nothing to flush
}

std::string NetworkSink::name() const {
    return "NetworkSink";
}

void NetworkSink::enableGroundStreaming(int duration_sec) {
    std::lock_guard<std::mutex> lock(mutex_);
    ground_streaming_enabled_ = true;
    ground_streaming_end_time_ = std::chrono::system_clock::now() +
                                  std::chrono::seconds(duration_sec);
}

void NetworkSink::disableGroundStreaming() {
    std::lock_guard<std::mutex> lock(mutex_);
    ground_streaming_enabled_ = false;
}

bool NetworkSink::isGroundStreamingEnabled() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return ground_streaming_enabled_;
}

void NetworkSink::sendUDP(const std::string& ip, int port, const std::string& data) {
    if (socket_fd_ < 0) {
        return;
    }

    sockaddr_in dest_addr{};
    dest_addr.sin_family = AF_INET;
    dest_addr.sin_port = htons(port);

    if (inet_pton(AF_INET, ip.c_str(), &dest_addr.sin_addr) <= 0) {
        std::cerr << "NetworkSink: Invalid IP address: " << ip << std::endl;
        return;
    }

    ssize_t sent = sendto(socket_fd_, data.c_str(), data.length(), 0,
                          reinterpret_cast<sockaddr*>(&dest_addr), sizeof(dest_addr));

    if (sent < 0) {
        std::cerr << "NetworkSink: Failed to send UDP packet to " << ip << ":" << port << std::endl;
    }
}

void NetworkSink::checkGroundStreamingTimeout() {
    if (ground_streaming_enabled_) {
        auto now = std::chrono::system_clock::now();
        if (now >= ground_streaming_end_time_) {
            ground_streaming_enabled_ = false;
        }
    }
}

void NetworkSink::addClient(const std::string& client_ip) {
    std::lock_guard<std::mutex> lock(mutex_);
    if (client_ips_.insert(client_ip).second) {
        std::cout << "NetworkSink: Added client " << client_ip
                  << " (total clients: " << client_ips_.size() << ")" << std::endl;
    }
}

void NetworkSink::removeClient(const std::string& client_ip) {
    std::lock_guard<std::mutex> lock(mutex_);
    if (client_ips_.erase(client_ip) > 0) {
        std::cout << "NetworkSink: Removed client " << client_ip
                  << " (remaining clients: " << client_ips_.size() << ")" << std::endl;
    }
}

size_t NetworkSink::getClientCount() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return client_ips_.size();
}

void NetworkSink::setSystemToolsIP(const std::string& ip) {
    std::lock_guard<std::mutex> lock(mutex_);
    if (ip != systemtools_ip_) {
        std::cout << "NetworkSink: SystemTools IP updated from " << systemtools_ip_
                  << " to " << ip << " (dynamic detection)" << std::endl;
        systemtools_ip_ = ip;
    }
}

void NetworkSink::setSystemToolsEnabled(bool enabled) {
    std::lock_guard<std::mutex> lock(mutex_);
    if (enabled != systemtools_enabled_) {
        systemtools_enabled_ = enabled;
        std::cout << "NetworkSink: SystemTools logging "
                  << (enabled ? "ENABLED" : "DISABLED")
                  << " (runtime config update)" << std::endl;
    }
}
