#include "udp_discovery_listener.h"
#include "../logging/structured_logger.h"
#include <nlohmann/json.hpp>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <cstring>
#include <iostream>

using json = nlohmann::json;

UdpDiscoveryListener::UdpDiscoveryListener(int port)
    : port_(port), socket_fd_(-1), running_(false), last_discovery_time_(0) {
}

UdpDiscoveryListener::~UdpDiscoveryListener() {
    stop();
}

void UdpDiscoveryListener::start() {
    if (running_) {
        LOG_WARNING(LogContext::NETWORK, "UDP discovery listener already running");
        return;
    }

    // Create UDP socket
    socket_fd_ = socket(AF_INET, SOCK_DGRAM, 0);
    if (socket_fd_ < 0) {
        LOG_ERROR(LogContext::NETWORK, "Failed to create UDP discovery socket: " + std::string(strerror(errno)));
        return;
    }

    // Set socket to reuse address
    int opt = 1;
    if (setsockopt(socket_fd_, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) < 0) {
        LOG_WARNING(LogContext::NETWORK, "Failed to set SO_REUSEADDR on discovery socket");
    }

    // Bind to port
    sockaddr_in server_addr{};
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(port_);

    if (bind(socket_fd_, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        LOG_ERROR(LogContext::NETWORK, "Failed to bind UDP discovery socket to port " + std::to_string(port_) + ": " + std::string(strerror(errno)));
        close(socket_fd_);
        socket_fd_ = -1;
        return;
    }

    running_ = true;
    listener_thread_ = std::thread(&UdpDiscoveryListener::listenerThread, this);

    LOG_INFO(LogContext::NETWORK, "UDP discovery listener started on port " + std::to_string(port_));
}

void UdpDiscoveryListener::stop() {
    if (!running_) {
        return;
    }

    LOG_INFO(LogContext::NETWORK, "Stopping UDP discovery listener...");
    running_ = false;

    // Close socket to unblock recvfrom()
    if (socket_fd_ >= 0) {
        close(socket_fd_);
        socket_fd_ = -1;
    }

    // Wait for thread to finish
    if (listener_thread_.joinable()) {
        listener_thread_.join();
    }

    LOG_INFO(LogContext::NETWORK, "UDP discovery listener stopped");
}

bool UdpDiscoveryListener::isRunning() const {
    return running_;
}

std::string UdpDiscoveryListener::getDetectedIP() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return detected_ip_;
}

int UdpDiscoveryListener::getTimeSinceLastDiscovery() const {
    std::lock_guard<std::mutex> lock(mutex_);
    if (last_discovery_time_ == 0) {
        return -1;  // Never received
    }
    return static_cast<int>(time(nullptr) - last_discovery_time_);
}

void UdpDiscoveryListener::listenerThread() {
    LOG_DEBUG(LogContext::NETWORK, "UDP discovery listener thread started");

    char buffer[4096];
    sockaddr_in client_addr{};
    socklen_t client_addr_len = sizeof(client_addr);

    while (running_) {
        ssize_t received = recvfrom(socket_fd_, buffer, sizeof(buffer) - 1, 0,
                                     (struct sockaddr*)&client_addr, &client_addr_len);

        if (received < 0) {
            if (running_) {
                LOG_ERROR(LogContext::NETWORK, "UDP discovery recvfrom error: " + std::string(strerror(errno)));
            }
            break;
        }

        if (received == 0) {
            continue;
        }

        // Null-terminate the received data
        buffer[received] = '\0';
        std::string data(buffer, received);

        // Extract source IP
        std::string source_ip = inet_ntoa(client_addr.sin_addr);

        // Validate discovery packet
        if (!validateDiscoveryPacket(data)) {
            LOG_DEBUG(LogContext::NETWORK, "Ignored invalid discovery packet from " + source_ip);
            continue;
        }

        // Update detected IP and timestamp
        {
            std::lock_guard<std::mutex> lock(mutex_);
            bool ip_changed = (detected_ip_ != source_ip);
            detected_ip_ = source_ip;
            last_discovery_time_ = time(nullptr);

            if (ip_changed) {
                LOG_INFO(LogContext::NETWORK, "SystemTools IP auto-detected: " + source_ip + " (UDP discovery)");

                // Update StructuredLogger with new SystemTools IP
                StructuredLogger::getInstance().setSystemToolsIP(source_ip);
            }
        }
    }

    LOG_DEBUG(LogContext::NETWORK, "UDP discovery listener thread ended");
}

bool UdpDiscoveryListener::validateDiscoveryPacket(const std::string& data) {
    try {
        json packet = json::parse(data);

        // Validate required fields
        if (!packet.contains("type") || !packet.contains("source")) {
            return false;
        }

        // Check packet type
        if (packet["type"].get<std::string>() != "discovery") {
            return false;
        }

        // Check source
        if (packet["source"].get<std::string>() != "systemtools") {
            return false;
        }

        // Optional fields: version, timestamp (for future use)
        return true;

    } catch (const json::exception& e) {
        LOG_DEBUG(LogContext::NETWORK, "Failed to parse discovery packet: " + std::string(e.what()));
        return false;
    }
}
