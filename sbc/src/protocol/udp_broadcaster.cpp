#include "protocol/udp_broadcaster.h"
#include "config.h"
#include "protocol/messages.h"
#include "utils/logger.h"
#include "utils/system_info.h"
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <cstring>
#include <errno.h>
#include <chrono>
#include <thread>

UDPBroadcaster::UDPBroadcaster(int port, const std::string& default_target_ip)
    : socket_fd_(-1)
    , port_(port)
    , default_target_ip_(default_target_ip)
    , running_(false)
    , sequence_id_(0)
    , camera_(nullptr)
{
    // Add default target to client list
    client_ips_.insert(default_target_ip);
}

UDPBroadcaster::~UDPBroadcaster() {
    stop();
}

void UDPBroadcaster::setCamera(std::shared_ptr<CameraInterface> camera) {
    camera_ = camera;
}

void UDPBroadcaster::setTargetIP(const std::string& target_ip) {
    // Legacy method - adds client if not already present
    addClient(target_ip);
}

void UDPBroadcaster::addClient(const std::string& client_ip) {
    std::lock_guard<std::mutex> lock(clients_mutex_);
    if (client_ips_.insert(client_ip).second) {
        Logger::info("UDP broadcaster: Added client " + client_ip + " (total clients: " + std::to_string(client_ips_.size()) + ")");
    }
}

void UDPBroadcaster::removeClient(const std::string& client_ip) {
    std::lock_guard<std::mutex> lock(clients_mutex_);
    if (client_ips_.erase(client_ip) > 0) {
        Logger::info("UDP broadcaster: Removed client " + client_ip + " (remaining clients: " + std::to_string(client_ips_.size()) + ")");
    }
}

size_t UDPBroadcaster::getClientCount() const {
    std::lock_guard<std::mutex> lock(clients_mutex_);
    return client_ips_.size();
}

void UDPBroadcaster::start() {
    if (running_) {
        Logger::warning("UDP broadcaster already running");
        return;
    }

    // Create UDP socket
    socket_fd_ = socket(AF_INET, SOCK_DGRAM, 0);
    if (socket_fd_ < 0) {
        Logger::error("Failed to create UDP socket: " + std::string(strerror(errno)));
        throw std::runtime_error("Failed to create UDP socket");
    }

    running_ = true;
    Logger::info("UDP broadcaster started (default target: " + default_target_ip_ + ":" + std::to_string(port_) + " at 5 Hz)");

    // Start broadcast thread
    broadcast_thread_ = std::thread(&UDPBroadcaster::broadcastLoop, this);
}

void UDPBroadcaster::stop() {
    if (!running_) {
        return;
    }

    Logger::info("Stopping UDP broadcaster...");
    running_ = false;

    // Wait for broadcast thread
    if (broadcast_thread_.joinable()) {
        broadcast_thread_.join();
    }

    // Close socket
    if (socket_fd_ >= 0) {
        close(socket_fd_);
        socket_fd_ = -1;
    }

    Logger::info("UDP broadcaster stopped");
}

void UDPBroadcaster::broadcastLoop() {
    Logger::debug("UDP broadcast loop started");

    auto next_broadcast = std::chrono::steady_clock::now();

    while (running_) {
        // Send status
        sendStatus();

        // Calculate next broadcast time (5 Hz = 200ms interval)
        next_broadcast += std::chrono::milliseconds(config::STATUS_INTERVAL_MS);

        // Sleep until next broadcast
        auto now = std::chrono::steady_clock::now();
        if (next_broadcast > now) {
            std::this_thread::sleep_until(next_broadcast);
        } else {
            // We're behind schedule, log warning
            Logger::warning("UDP broadcast falling behind schedule");
            next_broadcast = now;
        }
    }

    Logger::debug("UDP broadcast loop ended");
}

void UDPBroadcaster::sendStatus() {
    try {
        // Gather system status
        messages::SystemStatus system = SystemInfo::getStatus();

        // Gather camera status
        messages::CameraStatus camera;
        if (camera_) {
            camera = camera_->getStatus();
        } else {
            // Default camera status (not connected)
            camera.connected = false;
            camera.model = "unknown";
            camera.battery_percent = 0;
            camera.remaining_shots = 0;
        }

        // Gimbal status (Phase 3)
        messages::GimbalStatus gimbal;
        gimbal.connected = false;

        // Create status message
        json status_msg = messages::createStatusMessage(
            sequence_id_++,
            system,
            camera,
            gimbal
        );

        // Send to all registered clients
        std::string message_str = status_msg.dump();

        // Get client IPs (thread-safe)
        std::set<std::string> clients;
        {
            std::lock_guard<std::mutex> lock(clients_mutex_);
            clients = client_ips_;  // Copy the set
        }

        // Send to each client
        for (const auto& client_ip : clients) {
            // Send to primary port
            struct sockaddr_in target_addr{};
            target_addr.sin_family = AF_INET;
            target_addr.sin_port = htons(port_);
            inet_pton(AF_INET, client_ip.c_str(), &target_addr.sin_addr);

            ssize_t bytes_sent = sendto(
                socket_fd_,
                message_str.c_str(),
                message_str.size(),
                0,
                (struct sockaddr*)&target_addr,
                sizeof(target_addr)
            );

            if (bytes_sent < 0) {
                Logger::error("Failed to send UDP status to " + client_ip + ":" + std::to_string(port_) + ": " + std::string(strerror(errno)));
            } else {
                Logger::debug("Sent UDP status to " + client_ip + ":" + std::to_string(port_) + " (seq=" + std::to_string(sequence_id_ - 1) + ", bytes=" + std::to_string(bytes_sent) + ")");
            }

            // Send to alternative port (for Windows Tools with firewall restrictions)
            struct sockaddr_in target_addr_alt{};
            target_addr_alt.sin_family = AF_INET;
            target_addr_alt.sin_port = htons(config::UDP_STATUS_PORT_ALT);
            inet_pton(AF_INET, client_ip.c_str(), &target_addr_alt.sin_addr);

            ssize_t bytes_sent_alt = sendto(
                socket_fd_,
                message_str.c_str(),
                message_str.size(),
                0,
                (struct sockaddr*)&target_addr_alt,
                sizeof(target_addr_alt)
            );

            if (bytes_sent_alt < 0) {
                Logger::error("Failed to send UDP status to " + client_ip + ":" + std::to_string(config::UDP_STATUS_PORT_ALT) + ": " + std::string(strerror(errno)));
            } else {
                Logger::debug("Sent UDP status to " + client_ip + ":" + std::to_string(config::UDP_STATUS_PORT_ALT) + " (seq=" + std::to_string(sequence_id_ - 1) + ", bytes=" + std::to_string(bytes_sent_alt) + ")");
            }
        }
    } catch (const std::exception& e) {
        Logger::error("Exception in sendStatus: " + std::string(e.what()));
    }
}
