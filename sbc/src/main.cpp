#include <iostream>
#include <csignal>
#include <memory>
#include <atomic>
#include <thread>
#include <chrono>
#include "config.h"
#include "utils/logger.h"
#include "protocol/tcp_server.h"
#include "protocol/udp_broadcaster.h"
#include "protocol/heartbeat.h"
#include "camera/camera_interface.h"

// Global components for signal handler access
std::unique_ptr<TCPServer> g_tcp_server;
std::unique_ptr<UDPBroadcaster> g_udp_broadcaster;
std::unique_ptr<Heartbeat> g_heartbeat;
std::shared_ptr<CameraInterface> g_camera;
std::atomic<bool> g_shutdown_requested(false);

// Factory function from camera_sony.cpp
extern "C" CameraInterface* createCamera();

// Signal handler
void signalHandler(int signal) {
    if (signal == SIGINT || signal == SIGTERM) {
        Logger::info("Received shutdown signal (" + std::to_string(signal) + ")");
        g_shutdown_requested = true;
    }
}

// Print version information
void printVersion() {
    std::cout << "Payload Manager v" << config::SERVER_VERSION << std::endl;
    std::cout << "Protocol version: " << config::PROTOCOL_VERSION << std::endl;
    std::cout << "Phase 1 - Initial Connectivity (MVP)" << std::endl;
}

// Print startup banner
void printBanner() {
    std::cout << "========================================\n";
    std::cout << "   DPM Payload Manager Service\n";
    std::cout << "   Air Side - Raspberry Pi\n";
    std::cout << "========================================\n";
    std::cout << "Version: " << config::SERVER_VERSION << "\n";
    std::cout << "Protocol: " << config::PROTOCOL_VERSION << "\n";
    std::cout << "Phase: 1 (Initial Connectivity)\n";
    std::cout << "========================================\n\n";
}

int main(int argc, char* argv[]) {
    // Check for --version flag
    if (argc > 1 && std::string(argv[1]) == "--version") {
        printVersion();
        return 0;
    }

    // Print banner
    printBanner();

    try {
        // Initialize logger
        Logger::init(config::LOG_FILE);
        Logger::setLevel(Logger::Level::DEBUG);

        Logger::info("========================================");
        Logger::info("Payload Manager Service Starting...");
        Logger::info("========================================");
        Logger::info("Version: " + std::string(config::SERVER_VERSION));
        Logger::info("Protocol: " + std::string(config::PROTOCOL_VERSION));
        Logger::info("Phase: 1 (Initial Connectivity - MVP)");
        Logger::info("Log file: " + std::string(config::LOG_FILE));

        // Register signal handlers
        std::signal(SIGINT, signalHandler);
        std::signal(SIGTERM, signalHandler);
        Logger::info("Signal handlers registered (SIGINT, SIGTERM)");

        // Create camera interface (Sony SDK integration)
        Logger::info("Creating camera interface (Sony SDK)...");
        g_camera = std::shared_ptr<CameraInterface>(createCamera());
        if (!g_camera) {
            Logger::error("Failed to create camera interface");
            return 1;
        }

        // Attempt to connect camera (Sony SDK)
        Logger::info("Attempting to connect to Sony camera...");
        bool camera_connected = g_camera->connect();
        if (camera_connected) {
            Logger::info("Sony camera connected successfully!");
        } else {
            Logger::warning("Sony camera connection failed - will retry automatically");
        }

        // Create TCP server
        Logger::info("Creating TCP server on port " + std::to_string(config::TCP_PORT) + "...");
        g_tcp_server = std::make_unique<TCPServer>(config::TCP_PORT);
        g_tcp_server->setCamera(g_camera);

        // Create UDP broadcaster
        std::string ground_ip = config::getGroundStationIP();
        Logger::info("Creating UDP broadcaster (target: " + ground_ip + ":" + std::to_string(config::UDP_STATUS_PORT) + ")...");
        g_udp_broadcaster = std::make_unique<UDPBroadcaster>(
            config::UDP_STATUS_PORT,
            ground_ip.c_str()
        );
        g_udp_broadcaster->setCamera(g_camera);

        // Create heartbeat handler
        Logger::info("Creating heartbeat handler (port " + std::to_string(config::UDP_HEARTBEAT_PORT) + ")...");
        g_heartbeat = std::make_unique<Heartbeat>(
            config::UDP_HEARTBEAT_PORT,
            ground_ip.c_str()
        );

        // Start all components
        Logger::info("========================================");
        Logger::info("Starting all components...");
        Logger::info("========================================");

        g_tcp_server->start();
        g_udp_broadcaster->start();
        g_heartbeat->start();

        Logger::info("========================================");
        Logger::info("Payload Manager Service Running");
        Logger::info("========================================");
        Logger::info("TCP Command Server: 0.0.0.0:" + std::to_string(config::TCP_PORT));
        Logger::info("UDP Status Broadcast: " + ground_ip + ":" + std::to_string(config::UDP_STATUS_PORT) + " (5 Hz)");
        Logger::info("Heartbeat: " + ground_ip + ":" + std::to_string(config::UDP_HEARTBEAT_PORT) + " (1 Hz)");
        Logger::info(std::string("Camera: Sony SDK ") + (camera_connected ? "(connected)" : "(not connected)"));
        Logger::info("========================================");
        Logger::info("Press Ctrl+C to stop");
        Logger::info("========================================");

        std::cout << "\nService started successfully!\n";
        std::cout << "TCP server: port " << config::TCP_PORT << "\n";
        std::cout << "UDP status: " << ground_ip << ":" << config::UDP_STATUS_PORT << " (5 Hz)\n";
        std::cout << "Heartbeat: " << ground_ip << ":" << config::UDP_HEARTBEAT_PORT << " (1 Hz)\n";
        std::cout << "\nPress Ctrl+C to stop...\n\n";

        // Main loop - wait for shutdown signal
        while (!g_shutdown_requested) {
            std::this_thread::sleep_for(std::chrono::milliseconds(500));

            // Periodic heartbeat check
            double time_since_heartbeat = g_heartbeat->getTimeSinceLastHeartbeat();
            if (time_since_heartbeat > config::HEARTBEAT_TIMEOUT_SEC) {
                static auto last_warning = std::chrono::steady_clock::now();
                auto now = std::chrono::steady_clock::now();
                auto duration = std::chrono::duration_cast<std::chrono::seconds>(now - last_warning);

                // Log warning every 10 seconds
                if (duration.count() >= 10) {
                    Logger::warning("Ground heartbeat timeout: " + std::to_string(static_cast<int>(time_since_heartbeat)) + " seconds since last heartbeat");
                    last_warning = now;
                }
            }
        }

        // Shutdown sequence
        Logger::info("========================================");
        Logger::info("Shutdown requested - stopping components...");
        Logger::info("========================================");

        std::cout << "\nShutting down...\n";

        if (g_heartbeat) {
            Logger::info("Stopping heartbeat handler...");
            g_heartbeat->stop();
        }

        if (g_udp_broadcaster) {
            Logger::info("Stopping UDP broadcaster...");
            g_udp_broadcaster->stop();
        }

        if (g_tcp_server) {
            Logger::info("Stopping TCP server...");
            g_tcp_server->stop();
        }

        if (g_camera) {
            Logger::info("Disconnecting camera...");
            g_camera->disconnect();
        }

        Logger::info("========================================");
        Logger::info("Payload Manager Service Stopped");
        Logger::info("========================================");

        std::cout << "Shutdown complete.\n";

        Logger::close();

        return 0;

    } catch (const std::exception& e) {
        Logger::error("Fatal error: " + std::string(e.what()));
        std::cerr << "FATAL ERROR: " << e.what() << std::endl;

        // Cleanup on error
        if (g_heartbeat) g_heartbeat->stop();
        if (g_udp_broadcaster) g_udp_broadcaster->stop();
        if (g_tcp_server) g_tcp_server->stop();
        if (g_camera) g_camera->disconnect();

        Logger::close();
        return 1;
    }
}
