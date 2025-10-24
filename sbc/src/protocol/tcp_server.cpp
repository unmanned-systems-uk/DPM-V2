#include "protocol/tcp_server.h"
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
#include <sstream>

TCPServer::TCPServer(int port)
    : server_socket_(-1)
    , port_(port)
    , running_(false)
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

        // Spawn thread to handle client
        client_threads_.emplace_back(&TCPServer::handleClient, this, client_socket, client_ip);
        client_threads_.back().detach();  // Detach so it cleans up automatically
    }

    Logger::debug("TCP accept loop ended");
}

void TCPServer::handleClient(int client_socket, const std::string& client_ip) {
    Logger::debug("Handling client " + client_ip);

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

    close(client_socket);
    Logger::debug("Closed connection to " + client_ip);
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
        std::string cmd = command["payload"]["command"];

        Logger::info("Processing command: " + cmd);

        // Route to appropriate handler
        if (cmd == "handshake") {
            return handleHandshake(command["payload"], seq_id);
        } else if (cmd == "system.get_status") {
            return handleSystemGetStatus(command["payload"], seq_id);
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
    std::string client_id = payload.value("parameters", json::object()).value("client_id", "unknown");
    std::string client_version = payload.value("parameters", json::object()).value("client_version", "unknown");

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

    if (!msg["payload"].contains("command")) {
        error = "Missing command in payload";
        return false;
    }

    return true;
}
