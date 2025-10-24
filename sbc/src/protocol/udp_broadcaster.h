#ifndef UDP_BROADCASTER_H
#define UDP_BROADCASTER_H

#include <string>
#include <thread>
#include <atomic>
#include <memory>
#include "camera/camera_interface.h"

class UDPBroadcaster {
public:
    UDPBroadcaster(int port, const std::string& target_ip);
    ~UDPBroadcaster();

    // Set camera interface
    void setCamera(std::shared_ptr<CameraInterface> camera);

    // Start broadcasting
    void start();

    // Stop broadcasting
    void stop();

    // Check if broadcasting
    bool isRunning() const { return running_; }

private:
    // Broadcast loop
    void broadcastLoop();

    // Gather and send status
    void sendStatus();

    int socket_fd_;
    int port_;
    std::string target_ip_;
    std::atomic<bool> running_;
    std::thread broadcast_thread_;
    int sequence_id_;
    std::shared_ptr<CameraInterface> camera_;
};

#endif // UDP_BROADCASTER_H
