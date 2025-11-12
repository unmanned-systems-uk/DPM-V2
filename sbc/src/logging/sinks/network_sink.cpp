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
      socket_fd_(-1) {

    // Create UDP socket
    socket_fd_ = socket(AF_INET, SOCK_DGRAM, 0);
    if (socket_fd_ < 0) {
        std::cerr << "NetworkSink: Failed to create UDP socket" << std::endl;
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

    // Send to Ground-Side if streaming is enabled
    if (ground_streaming_enabled_) {
        sendUDP(ground_ip_, ground_port_, data);
    }

    // Send to SystemTools if enabled
    if (systemtools_enabled_) {
        sendUDP(systemtools_ip_, systemtools_port_, data);
    }
}

void NetworkSink::flush() {
    // UDP doesn't buffer, nothing to flush
}

std::string NetworkSink::name() const {
    return "network";
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
