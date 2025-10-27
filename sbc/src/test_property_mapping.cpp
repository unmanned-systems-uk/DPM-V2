/**
 * @file test_property_mapping.cpp
 * @brief Automated property mapping discovery tool
 *
 * This test program:
 * 1. Sets camera properties via Sony SDK
 * 2. Reads back the values from SDK
 * 3. Captures webcam images of the camera LCD
 * 4. Logs all three for comparison
 *
 * Purpose: Discover correct Sony SDK value mappings by comparing:
 * - What we request (e.g., "1/250")
 * - What SDK reports back (e.g., "1/250" or "unknown(0x00010006)")
 * - What the LCD actually shows (visual verification)
 */

#include "camera/camera_interface.h"
#include "utils/logger.h"
#include <iostream>
#include <thread>
#include <chrono>
#include <cstdlib>
#include <vector>
#include <string>

// Factory function from camera_sony.cpp
extern "C" CameraInterface* createCamera();

/**
 * @brief Capture image from USB webcam viewing the camera LCD
 * @param filename Output filename for captured image
 */
void captureWebcam(const std::string& filename) {
    std::string cmd = "fswebcam -d /dev/video0 -r 1280x720 --no-banner " + filename + " 2>/dev/null";
    int result = system(cmd.c_str());
    if (result != 0) {
        Logger::warning("Webcam capture failed: " + filename);
    }
}

/**
 * @brief Test setting a property and compare requested vs SDK vs LCD
 * @param camera Camera interface
 * @param property Property name (e.g., "shutter_speed", "aperture")
 * @param value Value to set (e.g., "1/250", "f/5.6")
 */
void testProperty(CameraInterface* camera, const std::string& property, const std::string& value) {
    std::cout << "\n========================================\n";
    std::cout << "Testing: " << property << " = " << value << "\n";
    std::cout << "========================================\n";

    // Sanitize value for filename (replace / with _)
    std::string safe_value = value;
    for (char& c : safe_value) {
        if (c == '/') c = '_';
        if (c == '.') c = '_';
    }

    // 1. Capture BEFORE image
    std::string before_img = "/tmp/before_" + property + "_" + safe_value + ".jpg";
    std::cout << "1. Capturing BEFORE image of LCD...\n";
    captureWebcam(before_img);
    std::cout << "   Saved: " << before_img << "\n";

    // 2. Set property
    std::cout << "2. Setting property via SDK: " << property << " = " << value << "\n";
    bool success = camera->setProperty(property, value);

    if (!success) {
        std::cout << "   ❌ ERROR: SDK failed to set property!\n";
        Logger::error("Failed to set " + property + " to " + value);
        std::cout << "   Skipping this test...\n";
        return;
    }

    std::cout << "   ✓ SDK setProperty() succeeded\n";
    Logger::info("Set " + property + " to " + value + " - SDK reports success");

    // 3. Wait for camera to update (give it time to process)
    std::cout << "3. Waiting 500ms for camera to update...\n";
    std::this_thread::sleep_for(std::chrono::milliseconds(500));

    // 4. Read back property from SDK
    std::cout << "4. Reading back property from SDK...\n";
    std::string actual = camera->getProperty(property);

    if (actual.empty()) {
        std::cout << "   ⚠ WARNING: SDK getProperty() returned empty!\n";
        Logger::warning("getProperty returned empty for " + property);
        actual = "(failed to read)";
    } else {
        std::cout << "   SDK reports current value: " << actual << "\n";
    }

    // 5. Capture AFTER image
    std::string after_img = "/tmp/after_" + property + "_" + safe_value + ".jpg";
    std::cout << "5. Capturing AFTER image of LCD...\n";
    captureWebcam(after_img);
    std::cout << "   Saved: " << after_img << "\n";

    // 6. Summary and comparison
    std::cout << "\n--- COMPARISON SUMMARY ---\n";
    std::cout << "  Requested:  " << value << "\n";
    std::cout << "  SDK says:   " << actual << "\n";
    std::cout << "  LCD check:  View " << after_img << " (visual verification)\n";

    bool match = (actual == value);
    std::cout << "  SDK Match:  " << (match ? "✓ YES" : "✗ NO") << "\n";

    if (!match && actual.find("unknown") != std::string::npos) {
        std::cout << "  Note: SDK returned raw hex - need to add mapping!\n";
        Logger::warning("Mapping missing: requested '" + value + "' but SDK returned '" + actual + "'");
    }

    // Log for later analysis
    Logger::info("COMPARISON: " + property + " | Requested: '" + value +
                 "' | SDK: '" + actual + "' | Images: " + before_img + " -> " + after_img);
}

int main() {
    // Initialize logger
    Logger::init("/tmp/test_property_mapping.log");
    Logger::setLevel(Logger::Level::DEBUG);

    std::cout << "\n";
    std::cout << "╔════════════════════════════════════════════════════════╗\n";
    std::cout << "║  Property Mapping Discovery Tool                      ║\n";
    std::cout << "║  Automated testing with visual LCD verification       ║\n";
    std::cout << "╚════════════════════════════════════════════════════════╝\n";
    std::cout << "\n";

    Logger::info("========================================");
    Logger::info("Property Mapping Discovery Test Started");
    Logger::info("========================================");

    // Create camera interface
    std::cout << "Creating camera interface...\n";
    auto camera = std::shared_ptr<CameraInterface>(createCamera());
    if (!camera) {
        std::cerr << "❌ ERROR: Failed to create camera interface\n";
        Logger::error("Failed to create camera interface");
        return 1;
    }
    std::cout << "✓ Camera interface created\n\n";

    // Connect to camera
    std::cout << "Connecting to Sony camera...\n";
    if (!camera->connect()) {
        std::cerr << "❌ ERROR: Failed to connect to camera\n";
        std::cerr << "   Make sure:\n";
        std::cerr << "   - Camera is powered on and charged\n";
        std::cerr << "   - USB cable is connected\n";
        std::cerr << "   - Camera is in PC Remote mode\n";
        Logger::error("Failed to connect to camera");
        return 1;
    }

    std::cout << "✓ Camera connected successfully!\n\n";
    Logger::info("Camera connected - starting tests");

    std::cout << "Tests will run with 2-second delays between changes.\n";
    std::cout << "All images saved to /tmp/before_*.jpg and /tmp/after_*.jpg\n";
    std::cout << "Log file: /tmp/test_property_mapping.log\n\n";

    std::cout << "Press Enter to start testing...";
    std::cin.get();

    // ========================================
    // Test Shutter Speed Values
    // ========================================
    std::cout << "\n\n╔════════════════════════════════════════╗\n";
    std::cout << "║  TESTING: Shutter Speed Values         ║\n";
    std::cout << "╚════════════════════════════════════════╝\n";

    std::vector<std::string> shutter_speeds = {
        "1/8000", "1/4000", "1/2000", "1/1000",
        "1/500", "1/250", "1/125", "1/60", "1/30"
    };

    for (const auto& speed : shutter_speeds) {
        testProperty(camera.get(), "shutter_speed", speed);
        std::this_thread::sleep_for(std::chrono::seconds(2));
    }

    // ========================================
    // Test Aperture Values
    // ========================================
    std::cout << "\n\n╔════════════════════════════════════════╗\n";
    std::cout << "║  TESTING: Aperture Values              ║\n";
    std::cout << "╚════════════════════════════════════════╝\n";

    std::vector<std::string> apertures = {
        "f/2.8", "f/4.0", "f/5.6", "f/8.0", "f/11", "f/16"
    };

    for (const auto& aperture : apertures) {
        testProperty(camera.get(), "aperture", aperture);
        std::this_thread::sleep_for(std::chrono::seconds(2));
    }

    // ========================================
    // Test ISO Values
    // ========================================
    std::cout << "\n\n╔════════════════════════════════════════╗\n";
    std::cout << "║  TESTING: ISO Values                   ║\n";
    std::cout << "╚════════════════════════════════════════╝\n";

    std::vector<std::string> iso_values = {
        "100", "200", "400", "800", "1600", "3200"
    };

    for (const auto& iso : iso_values) {
        testProperty(camera.get(), "iso", iso);
        std::this_thread::sleep_for(std::chrono::seconds(2));
    }

    // ========================================
    // Cleanup and Summary
    // ========================================
    std::cout << "\n\n╔════════════════════════════════════════════════════════╗\n";
    std::cout << "║  TEST COMPLETE!                                        ║\n";
    std::cout << "╚════════════════════════════════════════════════════════╝\n\n";

    std::cout << "Results:\n";
    std::cout << "  - All images saved to /tmp/before_*.jpg and /tmp/after_*.jpg\n";
    std::cout << "  - Detailed log: /tmp/test_property_mapping.log\n";
    std::cout << "  - Claude can now analyze the images and logs\n\n";

    std::cout << "Next steps:\n";
    std::cout << "  1. Claude will read all the 'after' images\n";
    std::cout << "  2. Compare LCD display values with requested values\n";
    std::cout << "  3. Build accurate Sony SDK mapping table\n\n";

    Logger::info("========================================");
    Logger::info("All tests completed successfully");
    Logger::info("========================================");

    // Disconnect
    std::cout << "Disconnecting camera...\n";
    camera->disconnect();
    std::cout << "✓ Disconnected\n\n";

    Logger::close();

    return 0;
}
