#include "protocol/heartbeat.h"
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

Heartbeat::Heartbeat(int port, const std::string& default_target_ip)
    : socket_fd_(-1)
    , port_(port)
    , default_target_ip_(default_target_ip)
    , running_(false)
    , sequence_id_(0)
    , last_received_(std::chrono::steady_clock::now())
    , heartbeat_received_(false)
{
    // Add default target to client list
    client_ips_.insert(default_target_ip);
}

Heartbeat::~Heartbeat() {
    stop();
}

void Heartbeat::start() {
    if (running_) {
        Logger::warning("Heartbeat already running");
        return;
    }

    // Create UDP socket
    socket_fd_ = socket(AF_INET, SOCK_DGRAM, 0);
    if (socket_fd_ < 0) {
        Logger::error("Failed to create heartbeat socket: " + std::string(strerror(errno)));
        throw std::runtime_error("Failed to create heartbeat socket");
    }

    // Bind socket for receiving
    struct sockaddr_in bind_addr{};
    bind_addr.sin_family = AF_INET;
    bind_addr.sin_addr.s_addr = INADDR_ANY;
    bind_addr.sin_port = htons(port_);

    if (bind(socket_fd_, (struct sockaddr*)&bind_addr, sizeof(bind_addr)) < 0) {
        close(socket_fd_);
        Logger::error("Failed to bind heartbeat socket: " + std::string(strerror(errno)));
        throw std::runtime_error("Failed to bind heartbeat socket");
    }

    // Set receive timeout (non-blocking with timeout)
    struct timeval tv;
    tv.tv_sec = 1;   // 1 second timeout
    tv.tv_usec = 0;
    setsockopt(socket_fd_, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));

    running_ = true;
    last_received_ = std::chrono::steady_clock::now();

    Logger::info("Heartbeat started (port " + std::to_string(port_) + ", default target: " + default_target_ip_ + ")");

    // Start send and receive threads
    send_thread_ = std::thread(&Heartbeat::sendLoop, this);
    receive_thread_ = std::thread(&Heartbeat::receiveLoop, this);
}

void Heartbeat::stop() {
    if (!running_) {
        return;
    }

    Logger::info("Stopping heartbeat...");
    running_ = false;

    // Wait for threads
    if (send_thread_.joinable()) {
        send_thread_.join();
    }

    if (receive_thread_.joinable()) {
        receive_thread_.join();
    }

    // Close socket
    if (socket_fd_ >= 0) {
        close(socket_fd_);
        socket_fd_ = -1;
    }

    Logger::info("Heartbeat stopped");
}

double Heartbeat::getTimeSinceLastHeartbeat() const {
    auto now = std::chrono::steady_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(now - last_received_);
    return duration.count() / 1000.0;
}

void Heartbeat::setTargetIP(const std::string& target_ip) {
    // Legacy method - adds client if not already present
    addClient(target_ip);
}

void Heartbeat::addClient(const std::string& client_ip) {
    std::lock_guard<std::mutex> lock(clients_mutex_);
    if (client_ips_.insert(client_ip).second) {
        Logger::info("Heartbeat: Added client " + client_ip + " (total clients: " + std::to_string(client_ips_.size()) + ")");
    }
}

void Heartbeat::removeClient(const std::string& client_ip) {
    std::lock_guard<std::mutex> lock(clients_mutex_);
    if (client_ips_.erase(client_ip) > 0) {
        Logger::info("Heartbeat: Removed client " + client_ip + " (remaining clients: " + std::to_string(client_ips_.size()) + ")");
    }
}

size_t Heartbeat::getClientCount() const {
    std::lock_guard<std::mutex> lock(clients_mutex_);
    return client_ips_.size();
}

void Heartbeat::sendLoop() {
    Logger::debug("Heartbeat send loop started");

    auto next_send = std::chrono::steady_clock::now();

    while (running_) {
        try {
            // Create heartbeat message (v1.1.0 - includes client_id)
            int64_t uptime = SystemInfo::getStatus().uptime_seconds;
            json heartbeat_msg = messages::createHeartbeatMessage(
                sequence_id_++,
                "air",
                "RPi-Air",
                uptime
            );

            // Send to all registered clients
            std::string message_str = heartbeat_msg.dump();

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
                    Logger::error("Failed to send heartbeat to " + client_ip + ":" + std::to_string(port_) + ": " + std::string(strerror(errno)));
                } else {
                    Logger::debug("Sent heartbeat to " + client_ip + ":" + std::to_string(port_) + " (seq=" + std::to_string(sequence_id_ - 1) + ")");
                }

                // Send to alternative port (for Windows Tools with firewall restrictions)
                struct sockaddr_in target_addr_alt{};
                target_addr_alt.sin_family = AF_INET;
                target_addr_alt.sin_port = htons(config::UDP_HEARTBEAT_PORT_ALT);
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
                    Logger::error("Failed to send heartbeat to " + client_ip + ":" + std::to_string(config::UDP_HEARTBEAT_PORT_ALT) + ": " + std::string(strerror(errno)));
                } else {
                    Logger::debug("Sent heartbeat to " + client_ip + ":" + std::to_string(config::UDP_HEARTBEAT_PORT_ALT) + " (seq=" + std::to_string(sequence_id_ - 1) + ")");
                }
            }
        } catch (const std::exception& e) {
            Logger::error("Exception in sendLoop: " + std::string(e.what()));
        }

        // Calculate next send time (1 Hz = 1000ms interval)
        next_send += std::chrono::milliseconds(config::HEARTBEAT_INTERVAL_MS);

        // Sleep until next send
        auto now = std::chrono::steady_clock::now();
        if (next_send > now) {
            std::this_thread::sleep_until(next_send);
        } else {
            Logger::warning("Heartbeat send falling behind schedule");
            next_send = now;
        }
    }

    Logger::debug("Heartbeat send loop ended");
}

void Heartbeat::receiveLoop() {
    Logger::debug("Heartbeat receive loop started");

    char buffer[config::UDP_BUFFER_SIZE];

    while (running_) {
        struct sockaddr_in sender_addr{};
        socklen_t sender_addr_len = sizeof(sender_addr);

        ssize_t bytes_received = recvfrom(
            socket_fd_,
            buffer,
            sizeof(buffer) - 1,
            0,
            (struct sockaddr*)&sender_addr,
            &sender_addr_len
        );

        if (bytes_received < 0) {
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                // Timeout - check if we haven't received heartbeat in a while
                double time_since = getTimeSinceLastHeartbeat();
                if (time_since > config::HEARTBEAT_TIMEOUT_SEC) {
                    Logger::warning("No heartbeat received for " + std::to_string(static_cast<int>(time_since)) + " seconds");
                }
                continue;
            } else {
                if (running_) {
                    Logger::error("Failed to receive heartbeat: " + std::string(strerror(errno)));
                }
                break;
            }
        }

        if (bytes_received == 0) {
            continue;
        }

        buffer[bytes_received] = '\0';

        try {
            json heartbeat_msg = json::parse(buffer);

            // Validate it's a heartbeat message
            if (heartbeat_msg.value("message_type", "") == "heartbeat") {
                std::string sender = heartbeat_msg["payload"].value("sender", "unknown");
                int seq_id = heartbeat_msg.value("sequence_id", 0);

                Logger::debug("Received heartbeat from " + sender + " (seq=" + std::to_string(seq_id) + ")");

                last_received_ = std::chrono::steady_clock::now();
                heartbeat_received_ = true;
            }
        } catch (const json::exception& e) {
            Logger::warning("Invalid heartbeat message: " + std::string(e.what()));
        } catch (const std::exception& e) {
            Logger::error("Exception in receiveLoop: " + std::string(e.what()));
        }
    }

    Logger::debug("Heartbeat receive loop ended");
}
