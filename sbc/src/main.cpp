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
#include "camera/property_loader.h"
#include "config/config_manager.h"
#include "logging/structured_logger.h"
#include "logging/sinks/console_sink.h"
#include "logging/sinks/file_sink.h"
#include "logging/sinks/network_sink.h"
#include "health/health_monitor.h"
#include "utils/system_info.h"

// Global components for signal handler access
std::unique_ptr<TCPServer> g_tcp_server;
std::unique_ptr<UDPBroadcaster> g_udp_broadcaster;
std::unique_ptr<Heartbeat> g_heartbeat;
std::shared_ptr<CameraInterface> g_camera;
std::atomic<bool> g_shutdown_requested(false);
std::atomic<bool> g_health_check_running(false);
std::thread g_health_check_thread;

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

// Camera health check thread - monitors connection and auto-reconnects
void cameraHealthCheckThread() {
    Logger::info("Camera health check thread started (30s interval)");

    bool was_connected = g_camera->isConnected();
    const int CHECK_INTERVAL_SEC = 30;

    while (g_health_check_running) {
        // Sleep in small chunks so we can respond quickly to shutdown
        for (int i = 0; i < CHECK_INTERVAL_SEC && g_health_check_running; ++i) {
            std::this_thread::sleep_for(std::chrono::seconds(1));
        }

        if (!g_health_check_running) break;

        bool is_connected = g_camera->isConnected();

        // Detect connection state changes
        if (was_connected && !is_connected) {
            Logger::warning("Camera disconnected - attempting reconnection");

            // Send notification via TCP
            if (g_tcp_server) {
                g_tcp_server->sendNotification(
                    messages::NotificationLevel::WARNING,
                    messages::NotificationCategory::CAMERA,
                    "Camera Disconnected",
                    "Camera connection lost - attempting automatic reconnection",
                    "reconnecting",
                    false  // Not dismissible while reconnecting
                );
            }

            was_connected = false;
        }

        // Attempt reconnection if disconnected
        if (!is_connected) {
            Logger::info("Attempting camera reconnection...");
            bool reconnected = g_camera->connect();

            if (reconnected) {
                Logger::info("Camera reconnected successfully!");

                // Send success notification
                if (g_tcp_server) {
                    g_tcp_server->sendNotification(
                        messages::NotificationLevel::INFO,
                        messages::NotificationCategory::CAMERA,
                        "Camera Connected",
                        "Camera successfully reconnected and ready",
                        "",
                        true  // Dismissible
                    );
                }

                was_connected = true;
            } else {
                Logger::debug("Camera reconnection attempt failed - will retry in " +
                            std::to_string(CHECK_INTERVAL_SEC) + " seconds");
            }
        }
    }

    Logger::info("Camera health check thread stopped");
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

        // Initialize ConfigManager (Phase 1: Gap 3)
        Logger::info("Initializing ConfigManager...");
        ConfigManager::getInstance().load();
        Logger::info("ConfigManager initialized - config loaded from JSON files");

        // Initialize StructuredLogger (Phase 1: Gap 1)
        Logger::info("Initializing StructuredLogger with sinks...");
        StructuredLogger::getInstance().init();

        // Add console sink
        auto console_sink = std::make_shared<ConsoleSink>();
        StructuredLogger::getInstance().addSink(console_sink);

        // Add file sink with rotation
        auto file_sink = std::make_shared<FileSink>(
            CONFIG_STRING("logging.file_path"),
            CONFIG_INT("logging.file_max_size_mb") * 1024 * 1024,  // Convert MB to bytes
            CONFIG_INT("logging.file_max_count")
        );
        StructuredLogger::getInstance().addSink(file_sink);

        // Add network sink (dual UDP: Ground on-demand + SystemTools always-on)
        auto network_sink = std::make_shared<NetworkSink>(
            CONFIG_STRING("network.ground_ip"),
            CONFIG_INT("logging.network_port"),
            CONFIG_STRING("logging.network_systemtools_ip"),
            CONFIG_INT("logging.network_systemtools_port"),
            CONFIG_BOOL("logging.network_systemtools_enabled")
        );
        StructuredLogger::getInstance().addSink(network_sink);

        Logger::info("StructuredLogger initialized with 3 sinks (console, file, network)");

        // Initialize HealthMonitor (Phase 1: Gap 2)
        Logger::info("Initializing HealthMonitor...");
        HealthMonitor::getInstance().init();
        Logger::info("HealthMonitor initialized with 3-tier retention");

        // Initialize PropertyLoader (specification-first architecture)
        Logger::info("Loading camera property specifications from camera_properties.json...");
        if (!PropertyLoader::initialize()) {
            Logger::error("Failed to initialize PropertyLoader - check camera_properties.json exists");
            return 1;
        }
        Logger::info("PropertyLoader initialized successfully");
        Logger::info("Loaded properties: ISO=" + std::to_string(PropertyLoader::getValueCount("iso")) +
                    ", Shutter=" + std::to_string(PropertyLoader::getValueCount("shutter_speed")) +
                    ", Aperture=" + std::to_string(PropertyLoader::getValueCount("aperture")));

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

        // Connect TCP server to broadcasters for dynamic IP discovery
        g_tcp_server->setUDPBroadcaster(g_udp_broadcaster.get());
        g_tcp_server->setHeartbeat(g_heartbeat.get());
        Logger::info("Dynamic IP discovery enabled - broadcasters will auto-update when client connects");

        // Start all components
        Logger::info("========================================");
        Logger::info("Starting all components...");
        Logger::info("========================================");

        g_tcp_server->start();
        g_udp_broadcaster->start();
        g_heartbeat->start();

        // Start HealthMonitor broadcasting (Phase 1: Gap 2)
        std::string health_broadcast_ip = CONFIG_STRING("network.ground_ip");
        int health_broadcast_port = CONFIG_INT("network.udp_health_port");
        HealthMonitor::getInstance().startBroadcasting(health_broadcast_ip, health_broadcast_port);
        Logger::info("HealthMonitor broadcasting started: " + health_broadcast_ip + ":" + std::to_string(health_broadcast_port) + " (5 Hz)");

        // Start camera health check thread
        g_health_check_running = true;
        g_health_check_thread = std::thread(cameraHealthCheckThread);

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

            // Collect and update system metrics for HealthMonitor (every 500ms)
            SystemMetrics sys_metrics;
            sys_metrics.cpu_percent = SystemInfo::getCPUPercent();
            sys_metrics.memory_used_mb = SystemInfo::getMemoryUsedMB();
            sys_metrics.memory_total_mb = SystemInfo::getMemoryTotalMB();
            sys_metrics.disk_used_mb = (SystemInfo::getDiskTotalGB() - SystemInfo::getDiskFreeGB()) * 1024;
            sys_metrics.disk_total_mb = SystemInfo::getDiskTotalGB() * 1024;
            sys_metrics.network_rx_mbps = SystemInfo::getNetworkRxMbps();
            sys_metrics.network_tx_mbps = SystemInfo::getNetworkTxMbps();
            HealthMonitor::getInstance().updateSystemMetrics(sys_metrics);

            // Update camera metrics
            CameraMetrics cam_metrics;
            cam_metrics.connected = g_camera ? g_camera->isConnected() : false;
            // TODO: Add SDK latency tracking in camera_sony.cpp
            cam_metrics.sdk_latency_ms = 0.0f;
            cam_metrics.usb_traffic_mbps = 0;
            cam_metrics.error_count = 0;
            HealthMonitor::getInstance().updateCameraMetrics(cam_metrics);

            // Update network metrics
            NetworkMetrics net_metrics;
            net_metrics.tcp_connected = g_tcp_server ? g_tcp_server->isRunning() : false;
            net_metrics.tcp_latency_ms = 0.0f;  // TODO: Track TCP latency
            net_metrics.udp_loss_percent = 0.0f;  // TODO: Track UDP packet loss
            net_metrics.command_queue_depth = 0;  // TODO: Track command queue
            HealthMonitor::getInstance().updateNetworkMetrics(net_metrics);

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

        // Stop health check thread first
        if (g_health_check_running) {
            Logger::info("Stopping camera health check...");
            g_health_check_running = false;
            if (g_health_check_thread.joinable()) {
                g_health_check_thread.join();
            }
        }

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

        // Shutdown Phase 1 components
        Logger::info("Stopping HealthMonitor...");
        HealthMonitor::getInstance().stopBroadcasting();
        HealthMonitor::getInstance().shutdown();

        Logger::info("Stopping StructuredLogger...");
        StructuredLogger::getInstance().shutdown();

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
        if (g_health_check_running) {
            g_health_check_running = false;
            if (g_health_check_thread.joinable()) {
                g_health_check_thread.join();
            }
        }
        if (g_heartbeat) g_heartbeat->stop();
        if (g_udp_broadcaster) g_udp_broadcaster->stop();
        if (g_tcp_server) g_tcp_server->stop();
        if (g_camera) g_camera->disconnect();

        // Shutdown Phase 1 components on error
        HealthMonitor::getInstance().stopBroadcasting();
        HealthMonitor::getInstance().shutdown();
        StructuredLogger::getInstance().shutdown();

        Logger::close();
        return 1;
    }
}
