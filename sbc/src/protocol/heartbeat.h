#ifndef HEARTBEAT_H
#define HEARTBEAT_H

#include <string>
#include <thread>
#include <atomic>
#include <chrono>

class Heartbeat {
public:
    Heartbeat(int port, const std::string& target_ip);
    ~Heartbeat();

    // Start heartbeat
    void start();

    // Stop heartbeat
    void stop();

    // Check if running
    bool isRunning() const { return running_; }

    // Get time since last received heartbeat (in seconds)
    double getTimeSinceLastHeartbeat() const;

private:
    // Send heartbeat loop
    void sendLoop();

    // Receive heartbeat loop
    void receiveLoop();

    int socket_fd_;
    int port_;
    std::string target_ip_;
    std::atomic<bool> running_;
    std::thread send_thread_;
    std::thread receive_thread_;
    int sequence_id_;
    std::chrono::steady_clock::time_point last_received_;
    std::atomic<bool> heartbeat_received_;
};

#endif // HEARTBEAT_H
