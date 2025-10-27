#ifndef TCP_SERVER_H
#define TCP_SERVER_H

#include <string>
#include <thread>
#include <vector>
#include <atomic>
#include <memory>
#include <mutex>
#include <nlohmann/json.hpp>
#include "protocol/messages.h"

using json = nlohmann::json;

// Forward declarations
class CameraInterface;
class UDPBroadcaster;
class Heartbeat;

class TCPServer {
public:
    explicit TCPServer(int port);
    ~TCPServer();

    // Start the server
    void start();

    // Stop the server
    void stop();

    // Check if server is running
    bool isRunning() const { return running_; }

    // Set camera interface
    void setCamera(std::shared_ptr<CameraInterface> camera) { camera_ = camera; }

    // Set UDP broadcaster (for dynamic IP updates)
    void setUDPBroadcaster(UDPBroadcaster* broadcaster) { udp_broadcaster_ = broadcaster; }

    // Set heartbeat handler (for dynamic IP updates)
    void setHeartbeat(Heartbeat* heartbeat) { heartbeat_ = heartbeat; }

    // Send notification to all connected clients
    void sendNotification(messages::NotificationLevel level,
                         messages::NotificationCategory category,
                         const std::string& title,
                         const std::string& message,
                         const std::string& action = "",
                         bool dismissible = true);

private:
    // Accept connections in a loop
    void acceptLoop();

    // Handle a single client connection
    void handleClient(int client_socket, const std::string& client_ip);

    // Process incoming command
    json processCommand(const json& command);

    // Command handlers
    json handleHandshake(const json& payload, int seq_id);
    json handleSystemGetStatus(const json& payload, int seq_id);
    json handleCameraCapture(const json& payload, int seq_id);
    json handleCameraSetProperty(const json& payload, int seq_id);
    json handleCameraGetProperties(const json& payload, int seq_id);

    // Validate message
    bool validateMessage(const json& msg, std::string& error);

    int server_socket_;
    int port_;
    std::atomic<bool> running_;
    std::thread accept_thread_;
    std::vector<std::thread> client_threads_;
    std::shared_ptr<CameraInterface> camera_;

    // UDP broadcasters (for dynamic IP updates)
    UDPBroadcaster* udp_broadcaster_;
    Heartbeat* heartbeat_;

    // Client tracking for notifications
    std::mutex clients_mutex_;
    std::vector<int> active_clients_;
    std::atomic<int> notification_seq_id_{0};
};

#endif // TCP_SERVER_H
