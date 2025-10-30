#ifndef UDP_BROADCASTER_H
#define UDP_BROADCASTER_H

#include <string>
#include <thread>
#include <atomic>
#include <memory>
#include <mutex>
#include <set>
#include "camera/camera_interface.h"

class UDPBroadcaster {
public:
    UDPBroadcaster(int port, const std::string& default_target_ip);
    ~UDPBroadcaster();

    // Set camera interface
    void setCamera(std::shared_ptr<CameraInterface> camera);

    // Start broadcasting
    void start();

    // Stop broadcasting
    void stop();

    // Check if broadcasting
    bool isRunning() const { return running_; }

    // Update target IP address (legacy - sets default target)
    void setTargetIP(const std::string& target_ip);

    // Add a client to receive broadcasts (thread-safe)
    void addClient(const std::string& client_ip);

    // Remove a client from receiving broadcasts (thread-safe)
    void removeClient(const std::string& client_ip);

    // Get number of registered clients
    size_t getClientCount() const;

private:
    // Broadcast loop
    void broadcastLoop();

    // Gather and send status
    void sendStatus();

    int socket_fd_;
    int port_;
    std::set<std::string> client_ips_;  // Multiple client IPs
    std::string default_target_ip_;      // Default/fallback target
    mutable std::mutex clients_mutex_;
    std::atomic<bool> running_;
    std::thread broadcast_thread_;
    int sequence_id_;
    std::shared_ptr<CameraInterface> camera_;
};

#endif // UDP_BROADCASTER_H
