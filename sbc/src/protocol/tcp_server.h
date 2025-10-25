#ifndef TCP_SERVER_H
#define TCP_SERVER_H

#include <string>
#include <thread>
#include <vector>
#include <atomic>
#include <memory>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

// Forward declaration
class CameraInterface;

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

    // Validate message
    bool validateMessage(const json& msg, std::string& error);

    int server_socket_;
    int port_;
    std::atomic<bool> running_;
    std::thread accept_thread_;
    std::vector<std::thread> client_threads_;
    std::shared_ptr<CameraInterface> camera_;
};

#endif // TCP_SERVER_H
