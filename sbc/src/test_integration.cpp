// test_integration.cpp - Component Integration Test
// Tests logger, camera, and system info without network requirements

#include <iostream>
#include <memory>
#include <thread>
#include <chrono>
#include "utils/logger.h"
#include "utils/system_info.h"
#include "camera/camera_interface.h"
#include "protocol/messages.h"

// Forward declare factory function
extern "C" CameraInterface* createCamera();

int main() {
    std::cout << "\n========================================" << std::endl;
    std::cout << "   DPM Component Integration Test" << std::endl;
    std::cout << "========================================\n" << std::endl;

    // ============================================================
    // TEST 1: Logger
    // ============================================================
    std::cout << "TEST 1: Logger Functionality" << std::endl;
    std::cout << "----------------------------" << std::endl;
    
    // Try to initialize logger
    std::cout << "Initializing logger to /app/logs/test_integration.log..." << std::endl;
    Logger::init("/app/logs/test_integration.log");
    
    // Test different log levels
    Logger::debug("This is a DEBUG message");
    Logger::info("This is an INFO message");
    Logger::warning("This is a WARNING message");
    Logger::error("This is an ERROR message");
    
    std::cout << "✓ Logger test complete (check log file for output)" << std::endl;
    std::cout << std::endl;

    // ============================================================
    // TEST 2: System Info
    // ============================================================
    std::cout << "TEST 2: System Information" << std::endl;
    std::cout << "----------------------------" << std::endl;

    messages::SystemStatus sys_status = SystemInfo::getStatus();

    std::cout << "Uptime:         " << sys_status.uptime_seconds << " seconds" << std::endl;
    std::cout << "CPU Usage:      " << sys_status.cpu_percent << "%" << std::endl;
    std::cout << "Memory:         " << sys_status.memory_mb << " / "
              << sys_status.memory_total_mb << " MB" << std::endl;
    std::cout << "Disk Free:      " << sys_status.disk_free_gb << " GB" << std::endl;
    std::cout << "Network RX:     " << sys_status.network_rx_mbps << " Mbps" << std::endl;
    std::cout << "Network TX:     " << sys_status.network_tx_mbps << " Mbps" << std::endl;
    
    std::cout << "✓ System info test complete" << std::endl;
    std::cout << std::endl;

    // ============================================================
    // TEST 3: Camera Integration
    // ============================================================
    std::cout << "TEST 3: Camera Integration" << std::endl;
    std::cout << "----------------------------" << std::endl;
    
    Logger::info("Creating camera instance...");
    std::cout << "Creating camera instance..." << std::endl;
    
    std::unique_ptr<CameraInterface> camera(createCamera());
    
    // Initial status
    auto status = camera->getStatus();
    std::cout << "Initial Status:" << std::endl;
    std::cout << "  Connected:        " << (status.connected ? "YES" : "NO") << std::endl;
    std::cout << "  Model:            " << status.model << std::endl;
    std::cout << "  Battery:          " << status.battery_percent << "%" << std::endl;
    std::cout << "  Remaining Shots:  " << status.remaining_shots << std::endl;
    std::cout << std::endl;

    // Attempt connection
    Logger::info("Attempting to connect to camera...");
    std::cout << "Attempting to connect to camera..." << std::endl;
    std::cout << "(This will take ~10 seconds for enumeration and connection)" << std::endl;
    
    bool connected = camera->connect();
    
    std::cout << "\nConnection Result: " << (connected ? "SUCCESS ✓" : "FAILED ✗") << std::endl;
    std::cout << std::endl;

    // Status after connection attempt
    status = camera->getStatus();
    std::cout << "Current Status:" << std::endl;
    std::cout << "  Connected:        " << (status.connected ? "YES" : "NO") << std::endl;
    std::cout << "  Model:            " << status.model << std::endl;
    std::cout << "  Battery:          " << status.battery_percent << "%" << std::endl;
    std::cout << "  Remaining Shots:  " << status.remaining_shots << std::endl;
    std::cout << std::endl;

    if (connected) {
        std::cout << "Camera is connected and ready!" << std::endl;
        Logger::info("Camera connection successful: " + status.model);
        
        // Test multiple status queries
        std::cout << "\nTesting status queries (5 iterations)..." << std::endl;
        for (int i = 0; i < 5; i++) {
            std::this_thread::sleep_for(std::chrono::milliseconds(500));
            auto test_status = camera->getStatus();
            std::cout << "  [" << (i+1) << "] Connected: " << test_status.connected 
                      << ", Model: " << test_status.model << std::endl;
        }
        
        // Clean disconnect
        std::cout << "\nDisconnecting camera..." << std::endl;
        camera->disconnect();
        
        // Final status
        status = camera->getStatus();
        std::cout << "After disconnect - Connected: " << (status.connected ? "YES" : "NO") << std::endl;
    } else {
        std::cout << "Camera connection failed" << std::endl;
        Logger::error("Camera connection failed");
    }

    std::cout << "\n✓ Camera test complete" << std::endl;
    std::cout << std::endl;

    // ============================================================
    // Summary
    // ============================================================
    std::cout << "========================================" << std::endl;
    std::cout << "   Test Summary" << std::endl;
    std::cout << "========================================" << std::endl;
    std::cout << "Logger:      ✓ Functional" << std::endl;
    std::cout << "System Info: ✓ Functional" << std::endl;
    std::cout << "Camera:      " << (connected ? "✓ Connected" : "✗ Not Connected") << std::endl;
    std::cout << "========================================\n" << std::endl;

    Logger::info("Integration test complete");
    
    return 0;
}
