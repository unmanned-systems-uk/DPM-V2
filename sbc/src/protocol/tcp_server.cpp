#include "protocol/tcp_server.h"
#include "config.h"
#include "protocol/messages.h"
#include "protocol/udp_broadcaster.h"
#include "protocol/heartbeat.h"
#include "utils/logger.h"
#include "utils/system_info.h"
#include "camera/camera_interface.h"
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <cstring>
#include <errno.h>
#include <sstream>
#include <algorithm>

TCPServer::TCPServer(int port)
    : server_socket_(-1)
    , port_(port)
    , running_(false)
    , udp_broadcaster_(nullptr)
    , heartbeat_(nullptr)
{
}

TCPServer::~TCPServer() {
    stop();
}

void TCPServer::start() {
    if (running_) {
        Logger::warning("TCP server already running");
        return;
    }

    // Create socket
    server_socket_ = socket(AF_INET, SOCK_STREAM, 0);
    if (server_socket_ < 0) {
        Logger::error("Failed to create TCP socket: " + std::string(strerror(errno)));
        throw std::runtime_error("Failed to create socket");
    }

    // Set socket options
    int opt = 1;
    if (setsockopt(server_socket_, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) < 0) {
        Logger::warning("Failed to set SO_REUSEADDR: " + std::string(strerror(errno)));
    }

    // Also set SO_REUSEPORT for better reconnection handling
    if (setsockopt(server_socket_, SOL_SOCKET, SO_REUSEPORT, &opt, sizeof(opt)) < 0) {
        Logger::warning("Failed to set SO_REUSEPORT: " + std::string(strerror(errno)));
    }

    // Bind to address
    struct sockaddr_in server_addr{};
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;  // Listen on all interfaces
    server_addr.sin_port = htons(port_);

    if (bind(server_socket_, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        close(server_socket_);
        Logger::error("Failed to bind to port " + std::to_string(port_) + ": " + std::string(strerror(errno)));
        throw std::runtime_error("Failed to bind socket");
    }

    // Listen for connections
    if (listen(server_socket_, config::MAX_TCP_CLIENTS) < 0) {
        close(server_socket_);
        Logger::error("Failed to listen on socket: " + std::string(strerror(errno)));
        throw std::runtime_error("Failed to listen on socket");
    }

    running_ = true;
    Logger::info("TCP server listening on port " + std::to_string(port_));

    // Start accept thread
    accept_thread_ = std::thread(&TCPServer::acceptLoop, this);
}

void TCPServer::stop() {
    if (!running_) {
        return;
    }

    Logger::info("Stopping TCP server...");
    running_ = false;

    // Close server socket to unblock accept()
    if (server_socket_ >= 0) {
        close(server_socket_);
        server_socket_ = -1;
    }

    // Wait for accept thread
    if (accept_thread_.joinable()) {
        accept_thread_.join();
    }

    // Wait for all client threads (they should exit when connections close)
    for (auto& thread : client_threads_) {
        if (thread.joinable()) {
            thread.join();
        }
    }
    client_threads_.clear();

    Logger::info("TCP server stopped");
}

void TCPServer::acceptLoop() {
    Logger::debug("TCP accept loop started");

    while (running_) {
        struct sockaddr_in client_addr{};
        socklen_t client_addr_len = sizeof(client_addr);

        int client_socket = accept(server_socket_, (struct sockaddr*)&client_addr, &client_addr_len);

        if (client_socket < 0) {
            if (running_) {
                Logger::error("Failed to accept connection: " + std::string(strerror(errno)));
            }
            break;
        }

        std::string client_ip = inet_ntoa(client_addr.sin_addr);
        Logger::info("Accepted connection from " + client_ip);

        // Update UDP broadcasters with client IP (dynamic discovery)
        if (udp_broadcaster_) {
            udp_broadcaster_->setTargetIP(client_ip);
        }
        if (heartbeat_) {
            heartbeat_->setTargetIP(client_ip);
        }

        // Set client socket options for better handling
        int opt = 1;
        // Disable Nagle's algorithm for lower latency
        if (setsockopt(client_socket, IPPROTO_TCP, TCP_NODELAY, &opt, sizeof(opt)) < 0) {
            Logger::warning("Failed to set TCP_NODELAY: " + std::string(strerror(errno)));
        }

        // Enable keepalive to detect dead connections
        if (setsockopt(client_socket, SOL_SOCKET, SO_KEEPALIVE, &opt, sizeof(opt)) < 0) {
            Logger::warning("Failed to set SO_KEEPALIVE: " + std::string(strerror(errno)));
        }

        // Spawn thread to handle client
        client_threads_.emplace_back(&TCPServer::handleClient, this, client_socket, client_ip);
        client_threads_.back().detach();  // Detach so it cleans up automatically
    }

    Logger::debug("TCP accept loop ended");
}

void TCPServer::handleClient(int client_socket, const std::string& client_ip) {
    Logger::debug("Handling client " + client_ip);

    // Add client to active clients list
    {
        std::lock_guard<std::mutex> lock(clients_mutex_);
        active_clients_.push_back(client_socket);
    }

    char buffer[config::TCP_BUFFER_SIZE];
    std::string message_buffer;

    while (running_) {
        ssize_t bytes_received = recv(client_socket, buffer, sizeof(buffer) - 1, 0);

        if (bytes_received < 0) {
            Logger::error("Failed to receive from " + client_ip + ": " + std::string(strerror(errno)));
            break;
        }

        if (bytes_received == 0) {
            Logger::info("Client " + client_ip + " disconnected");
            break;
        }

        buffer[bytes_received] = '\0';
        message_buffer += buffer;

        // Process complete JSON messages (one per line or complete JSON object)
        size_t newline_pos;
        while ((newline_pos = message_buffer.find('\n')) != std::string::npos) {
            std::string message = message_buffer.substr(0, newline_pos);
            message_buffer = message_buffer.substr(newline_pos + 1);

            if (message.empty()) {
                continue;
            }

            Logger::debug("Received from " + client_ip + ": " + message);

            try {
                json command = json::parse(message);
                json response = processCommand(command);

                std::string response_str = response.dump() + "\n";
                ssize_t bytes_sent = send(client_socket, response_str.c_str(), response_str.size(), 0);

                if (bytes_sent < 0) {
                    Logger::error("Failed to send to " + client_ip + ": " + std::string(strerror(errno)));
                    break;
                }

                Logger::debug("Sent to " + client_ip + ": " + response_str);
            } catch (const json::exception& e) {
                Logger::warning("JSON parse error from " + client_ip + ": " + std::string(e.what()));

                // Send error response
                json error_response = messages::createErrorResponse(
                    0, "unknown", messages::ErrorCode::INVALID_JSON,
                    "Invalid JSON: " + std::string(e.what())
                );

                std::string response_str = error_response.dump() + "\n";
                send(client_socket, response_str.c_str(), response_str.size(), 0);
            } catch (const std::exception& e) {
                Logger::error("Error processing command from " + client_ip + ": " + std::string(e.what()));
            }
        }
    }

    // Remove client from active clients list
    {
        std::lock_guard<std::mutex> lock(clients_mutex_);
        active_clients_.erase(
            std::remove(active_clients_.begin(), active_clients_.end(), client_socket),
            active_clients_.end()
        );
    }

    // Remove client from UDP broadcaster and heartbeat
    if (udp_broadcaster_) {
        udp_broadcaster_->removeClient(client_ip);
    }
    if (heartbeat_) {
        heartbeat_->removeClient(client_ip);
    }

    // Graceful shutdown: stop sending, allow receiving for a moment
    shutdown(client_socket, SHUT_WR);

    // Brief delay to allow final data to be read
    char discard_buffer[256];
    recv(client_socket, discard_buffer, sizeof(discard_buffer), MSG_DONTWAIT);

    close(client_socket);
    Logger::info("Disconnected client: " + client_ip);
}

json TCPServer::processCommand(const json& command) {
    try {
        // Validate message structure
        std::string error;
        if (!validateMessage(command, error)) {
            return messages::createErrorResponse(
                command.value("sequence_id", 0),
                command.value("payload", json::object()).value("command", "unknown"),
                messages::ErrorCode::INVALID_JSON,
                error
            );
        }

        int seq_id = command["sequence_id"];
        std::string message_type = command["message_type"].get<std::string>();

        // Handle handshake separately (doesn't use "command" field)
        if (message_type == "handshake") {
            Logger::info("Processing handshake");
            return handleHandshake(command["payload"], seq_id);
        }

        // For other messages, get command from payload
        std::string cmd = command["payload"]["command"];
        Logger::info("Processing command: " + cmd);

        // Route to appropriate handler
        if (cmd == "handshake") {
            return handleHandshake(command["payload"], seq_id);
        } else if (cmd == "system.get_status") {
            return handleSystemGetStatus(command["payload"], seq_id);
        } else if (cmd == "camera.capture") {
            return handleCameraCapture(command["payload"], seq_id);
        } else if (cmd == "camera.set_property") {
            return handleCameraSetProperty(command["payload"], seq_id);
        } else if (cmd == "camera.get_properties") {
            return handleCameraGetProperties(command["payload"], seq_id);
        } else {
            // Check if it's a Phase 2 command
            if (cmd.find("camera.") == 0 || cmd.find("gimbal.") == 0) {
                return messages::createErrorResponse(
                    seq_id, cmd,
                    messages::ErrorCode::COMMAND_NOT_IMPLEMENTED,
                    "This command will be implemented in Phase 2"
                );
            } else {
                return messages::createErrorResponse(
                    seq_id, cmd,
                    messages::ErrorCode::UNKNOWN_COMMAND,
                    "Unknown command: " + cmd
                );
            }
        }
    } catch (const std::exception& e) {
        Logger::error("Exception in processCommand: " + std::string(e.what()));
        return messages::createErrorResponse(
            0, "unknown",
            messages::ErrorCode::INTERNAL_ERROR,
            std::string(e.what())
        );
    }
}

json TCPServer::handleHandshake(const json& payload, int seq_id) {
    // Handle both old format (with "parameters") and new format (direct fields)
    std::string client_id = payload.value("client_id",
                            payload.value("parameters", json::object()).value("client_id", "unknown"));
    std::string client_version = payload.value("client_version",
                                 payload.value("parameters", json::object()).value("client_version", "unknown"));

    Logger::info("Handshake from client: " + client_id + " v" + client_version);

    // Build capabilities list
    json capabilities = json::array();
    for (int i = 0; i < config::CAPABILITIES_COUNT; ++i) {
        capabilities.push_back(config::CAPABILITIES[i]);
    }

    json result = {
        {"server_id", config::SERVER_ID},
        {"server_version", config::SERVER_VERSION},
        {"capabilities", capabilities}
    };

    return messages::createSuccessResponse(seq_id, "handshake", result);
}

json TCPServer::handleSystemGetStatus(const json& payload, int seq_id) {
    messages::SystemStatus system = SystemInfo::getStatus();

    return messages::createSuccessResponse(seq_id, "system.get_status", system.toJson());
}

json TCPServer::handleCameraCapture(const json& payload, int seq_id) {
    (void)payload; // Suppress unused parameter warning

    // Check if camera is available
    if (!camera_) {
        return messages::createErrorResponse(
            seq_id, "camera.capture",
            messages::ErrorCode::INTERNAL_ERROR,
            "Camera interface not initialized"
        );
    }

    // Check if camera is connected
    // Note: We don't attempt immediate reconnection here to avoid blocking the TCP handler thread
    // The health check thread handles reconnection every 30 seconds
    if (!camera_->isConnected()) {
        Logger::warning("Camera not connected - cannot capture");
        return messages::createErrorResponse(
            seq_id, "camera.capture",
            messages::ErrorCode::COMMAND_FAILED,
            "Camera not connected. Reconnection in progress, please retry in a few seconds."
        );
    }

    // Trigger capture
    Logger::info("Executing camera.capture command");
    bool success = camera_->capture();

    if (!success) {
        return messages::createErrorResponse(
            seq_id, "camera.capture",
            messages::ErrorCode::COMMAND_FAILED,
            "Failed to trigger camera shutter"
        );
    }

    // Return success response
    json result = {
        {"status", "captured"},
        {"message", "Shutter released successfully"}
    };

    return messages::createSuccessResponse(seq_id, "camera.capture", result);
}

json TCPServer::handleCameraSetProperty(const json& payload, int seq_id) {
    // Check if camera is available
    if (!camera_) {
        return messages::createErrorResponse(
            seq_id, "camera.set_property",
            messages::ErrorCode::INTERNAL_ERROR,
            "Camera interface not initialized"
        );
    }

    // Check if camera is connected
    // Note: We don't attempt immediate reconnection here to avoid blocking the TCP handler thread
    // The health check thread handles reconnection every 30 seconds
    if (!camera_->isConnected()) {
        Logger::warning("Camera not connected - cannot set property");
        return messages::createErrorResponse(
            seq_id, "camera.set_property",
            messages::ErrorCode::COMMAND_FAILED,
            "Camera not connected. Reconnection in progress, please retry in a few seconds."
        );
    }

    // Validate parameters
    if (!payload.contains("parameters")) {
        return messages::createErrorResponse(
            seq_id, "camera.set_property",
            messages::ErrorCode::INVALID_JSON,
            "Missing required 'parameters' object"
        );
    }

    const auto& params = payload["parameters"];
    if (!params.contains("property") || !params.contains("value")) {
        return messages::createErrorResponse(
            seq_id, "camera.set_property",
            messages::ErrorCode::INVALID_JSON,
            "Missing required parameters: property and value"
        );
    }

    std::string property = params["property"].get<std::string>();
    std::string value = params["value"].is_string() ?
                        params["value"].get<std::string>() :
                        std::to_string(params["value"].get<int>());

    Logger::info("Executing camera.set_property: " + property + " = " + value);

    // Set the property
    bool success = camera_->setProperty(property, value);

    if (!success) {
        return messages::createErrorResponse(
            seq_id, "camera.set_property",
            messages::ErrorCode::COMMAND_FAILED,
            "Failed to set camera property: " + property
        );
    }

    // Read back actual value from camera for verification
    std::string actual_value = camera_->getProperty(property);
    if (!actual_value.empty()) {
        Logger::info("Property comparison - Requested: '" + value + "' → Camera has: '" + actual_value + "'");
    } else {
        Logger::warning("Could not read back property value from camera");
    }

    // Return success response
    json result = {
        {"property", property},
        {"value", value},
        {"status", "success"}
    };

    return messages::createSuccessResponse(seq_id, "camera.set_property", result);
}

json TCPServer::handleCameraGetProperties(const json& payload, int seq_id) {
    // Check if camera is available
    if (!camera_) {
        return messages::createErrorResponse(
            seq_id, "camera.get_properties",
            messages::ErrorCode::INTERNAL_ERROR,
            "Camera interface not initialized"
        );
    }

    // Check if camera is connected, attempt immediate reconnection if needed
    if (!camera_->isConnected()) {
        Logger::info("Camera not connected - attempting immediate reconnection for get_properties command");

        bool reconnected = camera_->connect();
        if (reconnected) {
            Logger::info("Camera reconnected successfully!");

            // Send notification about reconnection
            sendNotification(
                messages::NotificationLevel::INFO,
                messages::NotificationCategory::CAMERA,
                "Camera Connected",
                "Camera successfully reconnected and ready",
                "",
                true
            );
        } else {
            Logger::warning("Camera reconnection failed");
            return messages::createErrorResponse(
                seq_id, "camera.get_properties",
                messages::ErrorCode::COMMAND_FAILED,
                "Camera not connected"
            );
        }
    }

    // Validate parameters
    if (!payload.contains("parameters")) {
        return messages::createErrorResponse(
            seq_id, "camera.get_properties",
            messages::ErrorCode::INVALID_JSON,
            "Missing required parameter: parameters"
        );
    }

    json parameters = payload["parameters"];
    if (!parameters.contains("properties")) {
        return messages::createErrorResponse(
            seq_id, "camera.get_properties",
            messages::ErrorCode::INVALID_JSON,
            "Missing required parameter: properties (array)"
        );
    }

    json properties_array = parameters["properties"];
    if (!properties_array.is_array()) {
        return messages::createErrorResponse(
            seq_id, "camera.get_properties",
            messages::ErrorCode::INVALID_JSON,
            "Parameter 'properties' must be an array"
        );
    }

    Logger::info("Executing camera.get_properties for " +
                 std::to_string(properties_array.size()) + " properties");

    // Get each property
    json result = json::object();
    for (const auto& prop : properties_array) {
        std::string property = prop.get<std::string>();
        std::string value = camera_->getProperty(property);
        result[property] = value;
    }

    return messages::createSuccessResponse(seq_id, "camera.get_properties", result);
}

void TCPServer::sendNotification(messages::NotificationLevel level,
                                 messages::NotificationCategory category,
                                 const std::string& title,
                                 const std::string& message,
                                 const std::string& action,
                                 bool dismissible) {
    // Create notification message
    int seq_id = notification_seq_id_++;
    json notification = messages::createNotificationMessage(
        seq_id, level, category, title, message, action, dismissible
    );

    std::string notification_str = notification.dump() + "\n";

    Logger::info("Broadcasting notification: " + title);

    // Send to all connected clients
    std::lock_guard<std::mutex> lock(clients_mutex_);
    for (int client_socket : active_clients_) {
        ssize_t bytes_sent = send(client_socket, notification_str.c_str(),
                                 notification_str.size(), MSG_DONTWAIT);
        if (bytes_sent < 0) {
            Logger::warning("Failed to send notification to client socket " +
                          std::to_string(client_socket) + ": " +
                          std::string(strerror(errno)));
        }
    }
}

bool TCPServer::validateMessage(const json& msg, std::string& error) {
    if (!msg.contains("protocol_version")) {
        error = "Missing protocol_version";
        return false;
    }

    if (msg["protocol_version"] != config::PROTOCOL_VERSION) {
        error = "Invalid protocol version: " + msg["protocol_version"].get<std::string>();
        return false;
    }

    if (!msg.contains("message_type")) {
        error = "Missing message_type";
        return false;
    }

    if (!msg.contains("sequence_id")) {
        error = "Missing sequence_id";
        return false;
    }

    if (!msg.contains("payload")) {
        error = "Missing payload";
        return false;
    }

    // Special case: handshake messages don't need "command" field
    std::string message_type = msg["message_type"].get<std::string>();
    if (message_type != "handshake" && !msg["payload"].contains("command")) {
        error = "Missing command in payload";
        return false;
    }

    return true;
}
