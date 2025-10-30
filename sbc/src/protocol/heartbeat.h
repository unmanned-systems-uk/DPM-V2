#ifndef HEARTBEAT_H
#define HEARTBEAT_H

#include <string>
#include <thread>
#include <atomic>
#include <mutex>
#include <chrono>
#include <set>

class Heartbeat {
public:
    Heartbeat(int port, const std::string& default_target_ip);
    ~Heartbeat();

    // Start heartbeat
    void start();

    // Stop heartbeat
    void stop();

    // Check if running
    bool isRunning() const { return running_; }

    // Get time since last received heartbeat (in seconds)
    double getTimeSinceLastHeartbeat() const;

    // Update target IP address (legacy - adds client)
    void setTargetIP(const std::string& target_ip);

    // Add a client to receive heartbeats (thread-safe)
    void addClient(const std::string& client_ip);

    // Remove a client from receiving heartbeats (thread-safe)
    void removeClient(const std::string& client_ip);

    // Get number of registered clients
    size_t getClientCount() const;

private:
    // Send heartbeat loop
    void sendLoop();

    // Receive heartbeat loop
    void receiveLoop();

    int socket_fd_;
    int port_;
    std::set<std::string> client_ips_;  // Multiple client IPs
    std::string default_target_ip_;      // Default/fallback target
    mutable std::mutex clients_mutex_;
    std::atomic<bool> running_;
    std::thread send_thread_;
    std::thread receive_thread_;
    int sequence_id_;
    std::chrono::steady_clock::time_point last_received_;
    std::atomic<bool> heartbeat_received_;
};

#endif // HEARTBEAT_H
