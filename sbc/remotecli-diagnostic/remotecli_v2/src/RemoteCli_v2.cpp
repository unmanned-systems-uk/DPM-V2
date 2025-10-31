/**
 * RemoteCli v2 - Enhanced Diagnostic Version
 *
 * Based on Sony Camera Remote SDK RemoteCli sample application
 * Enhanced with comprehensive logging for debugging camera connection
 * and control issues.
 *
 * Key enhancements:
 * - Detailed timestamped logging to console and file
 * - SDK call result logging with error codes
 * - Camera enumeration details
 * - Connection state tracking
 * - Property access logging
 * - Callback event logging
 */

#include <cstdlib>
#include <filesystem>
namespace fs = std::filesystem;

#include <cstdint>
#include <iomanip>
#include <thread>
#include <chrono>

#include "CRSDK/CameraRemote_SDK.h"
#include "CameraDevice.h"
#include "Text.h"
#include "DiagnosticLogger.h"

namespace SDK = SCRSDK;

int main()
{
    // Initialize diagnostic logger
    DiagnosticLogger::instance().init();
    DIAG_LOG_INFO("MAIN", "========================================");
    DIAG_LOG_INFO("MAIN", "RemoteCli v2 - Diagnostic Version");
    DIAG_LOG_INFO("MAIN", "Enhanced Sony SDK diagnostic tool");
    DIAG_LOG_INFO("MAIN", "========================================");

    // Change global locale to native locale
    std::locale::global(std::locale(""));
    cli::tin.imbue(std::locale());
    cli::tout.imbue(std::locale());

    cli::tout << "\n===========================================\n";
    cli::tout << "  RemoteCli v2 - Diagnostic Version\n";
    cli::tout << "  Enhanced with comprehensive logging\n";
    cli::tout << "===========================================\n\n";

    // Get SDK version
    CrInt32u version = SDK::GetSDKVersion();
    int major = (version & 0xFF000000) >> 24;
    int minor = (version & 0x00FF0000) >> 16;
    int patch = (version & 0x0000FF00) >> 8;

    std::ostringstream version_str;
    version_str << major << "." << minor << "." << std::setfill('0') << std::setw(2) << patch;

    cli::tout << "Remote SDK version: " << version_str.str() << "\n";
    DIAG_LOG_INFO("SDK", "Sony SDK Version: " + version_str.str());

    // Working directory
    cli::tout << "Working directory: " << fs::current_path() << "\n\n";
    DIAG_LOG_INFO("MAIN", "Working directory: " + fs::current_path().string());

    // Initialize SDK
    cli::tout << "Initializing Remote SDK...\n";
    DIAG_LOG_INFO("SDK", "Calling SDK::Init()...");

    auto init_start = std::chrono::steady_clock::now();
    auto init_success = SDK::Init();
    auto init_end = std::chrono::steady_clock::now();
    auto init_duration = std::chrono::duration_cast<std::chrono::milliseconds>(init_end - init_start);

    DIAG_LOG_SDK("SDK::Init", init_success ? 0 : -1);

    if (!init_success) {
        cli::tout << "ERROR: Failed to initialize Remote SDK!\n";
        DIAG_LOG_ERROR("SDK", "SDK initialization failed - terminating");
        SDK::Release();
        std::exit(EXIT_FAILURE);
    }

    std::ostringstream init_msg;
    init_msg << "SDK initialized successfully in " << init_duration.count() << " ms";
    cli::tout << init_msg.str() << "\n\n";
    DIAG_LOG_INFO("SDK", init_msg.str());

    // Enumerate cameras
    cli::tout << "Enumerating connected camera devices...\n";
    DIAG_LOG_INFO("CAMERA", "Calling SDK::EnumCameraObjects()...");

    SDK::ICrEnumCameraObjectInfo* camera_list = nullptr;
    auto enum_start = std::chrono::steady_clock::now();
    auto enum_status = SDK::EnumCameraObjects(&camera_list);
    auto enum_end = std::chrono::steady_clock::now();
    auto enum_duration = std::chrono::duration_cast<std::chrono::milliseconds>(enum_end - enum_start);

    DIAG_LOG_SDK("SDK::EnumCameraObjects", enum_status);

    std::ostringstream enum_msg;
    enum_msg << "Enumeration completed in " << enum_duration.count() << " ms";
    DIAG_LOG_INFO("CAMERA", enum_msg.str());

    if (CR_FAILED(enum_status)) {
        std::ostringstream err_msg;
        err_msg << "Camera enumeration failed with error code: 0x"
                << std::hex << enum_status << std::dec;
        cli::tout << "ERROR: " << err_msg.str() << "\n";
        DIAG_LOG_ERROR("CAMERA", err_msg.str());
        SDK::Release();
        std::exit(EXIT_FAILURE);
    }

    if (camera_list == nullptr) {
        cli::tout << "ERROR: Camera list is null\n";
        DIAG_LOG_ERROR("CAMERA", "EnumCameraObjects returned null camera list");
        SDK::Release();
        std::exit(EXIT_FAILURE);
    }

    auto ncams = camera_list->GetCount();
    std::ostringstream count_msg;
    count_msg << "Camera enumeration successful - " << ncams << " camera(s) detected";
    cli::tout << count_msg.str() << "\n\n";
    DIAG_LOG_INFO("CAMERA", count_msg.str());

    if (ncams == 0) {
        cli::tout << "No cameras detected. Please:\n";
        cli::tout << "  1. Connect a Sony camera via USB\n";
        cli::tout << "  2. Power ON the camera\n";
        cli::tout << "  3. Set camera to PC Remote mode\n";
        DIAG_LOG_WARN("CAMERA", "No cameras detected - check USB connection and camera mode");
        SDK::Release();
        std::exit(EXIT_FAILURE);
    }

    // Display camera details
    cli::tout << "Detected cameras:\n";
    cli::tout << "-----------------\n";

    for (CrInt32u i = 0; i < ncams; ++i) {
        auto camera_info = camera_list->GetCameraObjectInfo(i);

        cli::text conn_type(camera_info->GetConnectionTypeName());
        cli::text model(camera_info->GetModel());
        cli::text id = TEXT("");

        if (TEXT("IP") == conn_type) {
            id.append((TCHAR*)camera_info->GetMACAddressChar(),
                     (size_t)camera_info->GetMACAddressCharSize());
        } else {
            id = ((TCHAR*)camera_info->GetId());
        }

        cli::tout << "  [" << (i + 1) << "] " << model.data()
                  << " (ID: " << id.data() << ")\n";
        cli::tout << "      Connection: " << conn_type.data() << "\n";

        // Log detailed camera info
        std::ostringstream cam_msg;
        cam_msg << "Camera[" << i << "]: Model=" << model.data()
                << ", ID=" << id.data()
                << ", Connection=" << conn_type.data();
        DIAG_LOG_INFO("CAMERA", cam_msg.str());
    }

    cli::tout << "\nSelect camera number to connect (1-" << ncams << "): ";
    cli::text connectNo;
    std::getline(cli::tin, connectNo);
    cli::tout << '\n';

    int connect_index = 0;
    try {
        connect_index = std::stoi(connectNo) - 1;
    } catch (...) {
        cli::tout << "ERROR: Invalid camera selection\n";
        DIAG_LOG_ERROR("MAIN", "Invalid camera selection: " + std::string(connectNo.begin(), connectNo.end()));
        camera_list->Release();
        SDK::Release();
        std::exit(EXIT_FAILURE);
    }

    if (connect_index < 0 || connect_index >= (int)ncams) {
        cli::tout << "ERROR: Camera selection out of range\n";
        DIAG_LOG_ERROR("MAIN", "Camera selection out of range: " + std::to_string(connect_index));
        camera_list->Release();
        SDK::Release();
        std::exit(EXIT_FAILURE);
    }

    // Get selected camera info
    auto selected_camera = camera_list->GetCameraObjectInfo(connect_index);
    cli::text selected_model(selected_camera->GetModel());

    std::ostringstream sel_msg;
    sel_msg << "Selected camera [" << (connect_index + 1) << "]: " << selected_model.data();
    cli::tout << sel_msg.str() << "\n";
    DIAG_LOG_INFO("CAMERA", sel_msg.str());

    // Create camera device
    cli::tout << "Creating camera device object...\n";
    DIAG_LOG_INFO("CAMERA", "Creating CameraDevice instance");

    typedef std::shared_ptr<cli::CameraDevice> CameraDevicePtr;
    CameraDevicePtr camera = CameraDevicePtr(new cli::CameraDevice(connect_index, selected_camera));

    camera_list->Release();
    DIAG_LOG_INFO("CAMERA", "Camera list released");

    // Connect to camera
    cli::tout << "Connecting to camera...\n";
    std::ostringstream conn_msg;
    conn_msg << "Initiating connection to camera index " << connect_index;
    DIAG_LOG_INFO("CAMERA", conn_msg.str());

    auto conn_start = std::chrono::steady_clock::now();
    bool connected = camera->connect(SDK::CrSdkControlMode_Remote, SDK::CrReconnecting_ON);
    auto conn_end = std::chrono::steady_clock::now();
    auto conn_duration = std::chrono::duration_cast<std::chrono::milliseconds>(conn_end - conn_start);

    if (!connected) {
        cli::tout << "ERROR: Failed to connect to camera!\n";
        std::ostringstream err_msg;
        err_msg << "Camera connection failed after " << conn_duration.count() << " ms";
        DIAG_LOG_ERROR("CAMERA", err_msg.str());
        SDK::Release();
        std::exit(EXIT_FAILURE);
    }

    std::ostringstream success_msg;
    success_msg << "Successfully connected to camera in " << conn_duration.count() << " ms";
    cli::tout << success_msg.str() << "\n\n";
    DIAG_LOG_INFO("CAMERA", success_msg.str());

    // Wait for camera to be ready
    cli::tout << "Waiting for camera initialization...\n";
    DIAG_LOG_INFO("CAMERA", "Waiting 2 seconds for camera initialization");
    std::this_thread::sleep_for(std::chrono::seconds(2));

    // Display connection status
    cli::tout << "===========================================\n";
    cli::tout << "  Camera Connection Successful!\n";
    cli::tout << "===========================================\n";
    cli::tout << "  Model: " << selected_model.data() << "\n";
    cli::tout << "  Status: CONNECTED\n";
    cli::tout << "  Mode: Remote Control\n";
    cli::tout << "===========================================\n\n";
    DIAG_LOG_INFO("CAMERA", "Camera connection fully established and ready");

    // Interactive menu loop
    bool running = true;
    while (running) {
        cli::tout << "\n--- RemoteCli v2 Diagnostic Menu ---\n";
        cli::tout << "  1. Get camera properties\n";
        cli::tout << "  2. Take photo (shutter)\n";
        cli::tout << "  3. Display connection info\n";
        cli::tout << "  4. Test property read/write\n";
        cli::tout << "  5. Disconnect and exit\n";
        cli::tout << "Select option: ";

        cli::text input;
        std::getline(cli::tin, input);

        try {
            int choice = std::stoi(input);
            DIAG_LOG_INFO("MENU", "User selected option: " + std::to_string(choice));

            switch (choice) {
                case 1:
                    cli::tout << "\nGet camera properties feature requires specific property codes.\n";
                    cli::tout << "This is a simplified diagnostic version.\n";
                    cli::tout << "Use option 3 to see connection status instead.\n";
                    DIAG_LOG_INFO("CAMERA", "Property query option selected (simplified mode)");
                    // Note: get_property() requires specific CrDeviceProperty argument
                    // Full implementation would iterate through property list
                    break;

                case 2:
                    cli::tout << "\nTaking photo...\n";
                    DIAG_LOG_INFO("CAMERA", "Executing shutter command (S2 button)");
                    camera->execute_downup_property(SDK::CrDeviceProperty_S2);
                    cli::tout << "Photo capture command sent.\n";
                    break;

                case 3:
                    cli::tout << "\n=== Connection Info ===\n";
                    cli::tout << "Model: " << selected_model.data() << "\n";
                    cli::tout << "Connected: " << (camera->is_connected() ? "YES" : "NO") << "\n";
                    DIAG_LOG_INFO("CAMERA", "Connection status check");
                    break;

                case 4:
                    cli::tout << "\nProperty read/write test feature requires specific property implementation.\n";
                    cli::tout << "This is a simplified diagnostic version.\n";
                    cli::tout << "Use payload_manager for full property control.\n";
                    DIAG_LOG_INFO("CAMERA", "Property test option selected (simplified mode)");
                    // Note: Property testing would require implementing specific
                    // property read/write operations with proper CrDeviceProperty objects
                    break;

                case 5:
                    cli::tout << "\nDisconnecting...\n";
                    DIAG_LOG_INFO("CAMERA", "User requested disconnect");
                    running = false;
                    break;

                default:
                    cli::tout << "Invalid option\n";
                    DIAG_LOG_WARN("MENU", "Invalid menu selection: " + std::to_string(choice));
                    break;
            }
        } catch (...) {
            cli::tout << "Invalid input\n";
            DIAG_LOG_WARN("MENU", "Invalid menu input");
        }
    }

    // Disconnect and cleanup
    cli::tout << "Disconnecting from camera...\n";
    DIAG_LOG_INFO("CAMERA", "Initiating camera disconnect");
    camera->disconnect();
    DIAG_LOG_INFO("CAMERA", "Camera disconnected successfully");

    cli::tout << "Releasing SDK...\n";
    DIAG_LOG_INFO("SDK", "Calling SDK::Release()");
    SDK::Release();
    DIAG_LOG_INFO("SDK", "SDK released successfully");

    cli::tout << "\nRemoteCli v2 terminated successfully\n";
    DIAG_LOG_INFO("MAIN", "========================================");
    DIAG_LOG_INFO("MAIN", "RemoteCli v2 session ended");
    DIAG_LOG_INFO("MAIN", "========================================");

    return 0;
}
