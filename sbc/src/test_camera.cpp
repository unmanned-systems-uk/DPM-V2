#include <iostream>
#include <string>
#include <memory>
#include <chrono>
#include <thread>
#include "CRSDK/CameraRemote_SDK.h"
#include "CRSDK/IDeviceCallback.h"

namespace SDK = SCRSDK;

// Simple camera callback for testing
class TestCameraCallback : public SDK::IDeviceCallback
{
public:
    TestCameraCallback() {}
    ~TestCameraCallback() {}

    // Called when camera is connected
    void OnConnected(SDK::DeviceConnectionVersioin version) override {
        std::cout << "[Callback] Camera connected" << std::endl;
    }

    // Called when camera is disconnected
    void OnDisconnected(CrInt32u error) override {
        std::cout << "[Callback] Camera disconnected. Error: 0x" << std::hex << error << std::endl;
    }

    // Called when a camera property changes
    void OnPropertyChanged() override {
        // Property changed (can be frequent, don't log)
    }

    // Called when LiveView property changes
    void OnLvPropertyChanged() override {
        // LiveView property changed (very frequent, don't log)
    }

    void OnWarning(CrInt32u warning) override {
        std::cout << "[Warning] Code: 0x" << std::hex << warning << std::endl;
    }

    void OnError(CrInt32u error) override {
        std::cout << "[Error] Code: 0x" << std::hex << error << std::endl;
    }
};

void print_camera_info(const SDK::ICrCameraObjectInfo* camera_info) {
    std::cout << "\n=== Camera Information ===" << std::endl;
    std::cout << "Model: " << camera_info->GetModel() << std::endl;
    std::cout << "Connection Type: " << camera_info->GetConnectionTypeName() << std::endl;

    const char* conn_type = camera_info->GetConnectionTypeName();
    if (std::string(conn_type) == "IP") {
        std::cout << "MAC Address: ";
        const char* mac = (const char*)camera_info->GetMACAddressChar();
        int mac_size = camera_info->GetMACAddressCharSize();
        for (int i = 0; i < mac_size && i < 17; i++) {
            std::cout << mac[i];
        }
        std::cout << std::endl;
    } else {
        std::cout << "ID: " << (const char*)camera_info->GetId() << std::endl;
    }
    std::cout << "==========================" << std::endl;
}

int main() {
    std::cout << "\n*** Sony Camera Connection Test ***\n" << std::endl;

    // Get SDK version
    uint32_t version = SDK::GetSDKVersion();
    int major = (version & 0xFF000000) >> 24;
    int minor = (version & 0x00FF0000) >> 16;
    int patch = (version & 0x0000FF00) >> 8;

    std::cout << "Sony Remote SDK version: " << major << "." << minor << "." << patch << std::endl;
    std::cout << std::endl;

    // Initialize SDK with logging enabled
    std::cout << "Initializing Sony Remote SDK..." << std::endl;
    auto init_success = SDK::Init(0); // 0 = no logging, 1 = enable logging
    if (!init_success) {
        std::cerr << "ERROR: Failed to initialize Sony Remote SDK!" << std::endl;
        SDK::Release();
        return 1;
    }
    std::cout << "Sony Remote SDK initialized successfully." << std::endl;
    std::cout << std::endl;

    // Enumerate cameras with 5 second timeout
    std::cout << "Enumerating connected cameras (waiting 5 seconds)..." << std::endl;
    SDK::ICrEnumCameraObjectInfo* camera_list = nullptr;
    auto enum_status = SDK::EnumCameraObjects(&camera_list, 5);

    if (CR_FAILED(enum_status) || camera_list == nullptr) {
        std::cerr << "ERROR: No cameras detected!" << std::endl;
        std::cerr << "Please check:" << std::endl;
        std::cerr << "  1. Camera is powered on" << std::endl;
        std::cerr << "  2. Camera is connected via USB or network" << std::endl;
        std::cerr << "  3. Camera is in Remote Control mode" << std::endl;
        SDK::Release();
        return 1;
    }

    auto ncams = camera_list->GetCount();
    std::cout << "Found " << ncams << " camera(s):" << std::endl;
    std::cout << std::endl;

    // Display all cameras
    for (uint32_t i = 0; i < ncams; ++i) {
        auto camera_info = camera_list->GetCameraObjectInfo(i);
        std::cout << "[" << (i + 1) << "] ";
        std::cout << camera_info->GetModel();

        const char* conn_type = camera_info->GetConnectionTypeName();
        if (std::string(conn_type) == "IP") {
            std::cout << " (Network)";
        } else {
            std::cout << " (USB)";
        }
        std::cout << std::endl;
    }
    std::cout << std::endl;

    // Select camera
    uint32_t selected_camera = 0;
    if (ncams == 1) {
        selected_camera = 0;
        std::cout << "Auto-selecting the only camera..." << std::endl;
    } else {
        std::cout << "Select camera number (1-" << ncams << "): ";
        int input;
        std::cin >> input;

        if (input < 1 || input > (int)ncams) {
            std::cerr << "Invalid camera number!" << std::endl;
            camera_list->Release();
            SDK::Release();
            return 1;
        }
        selected_camera = input - 1;
    }

    auto camera_info = camera_list->GetCameraObjectInfo(selected_camera);
    print_camera_info(camera_info);
    std::cout << std::endl;

    // Create device handle
    std::cout << "Connecting to camera..." << std::endl;

    TestCameraCallback callback;
    SDK::CrDeviceHandle device_handle;

    // Need to cast away const - API requires non-const pointer
    auto* non_const_camera_info = const_cast<SDK::ICrCameraObjectInfo*>(camera_info);

    auto connect_status = SDK::Connect(
        non_const_camera_info,
        &callback,
        &device_handle,
        SDK::CrSdkControlMode_Remote,
        SDK::CrReconnecting_ON
    );

    if (CR_FAILED(connect_status)) {
        std::cerr << "ERROR: Failed to connect to camera!" << std::endl;
        std::cerr << "Error code: 0x" << std::hex << connect_status << std::endl;
        camera_list->Release();
        SDK::Release();
        return 1;
    }

    std::cout << "Successfully connected to camera!" << std::endl;
    std::cout << "Device handle: " << device_handle << std::endl;
    std::cout << std::endl;

    // Get device properties
    std::cout << "Retrieving camera properties..." << std::endl;
    SDK::CrDeviceProperty* properties = nullptr;
    int property_count = 0;

    auto prop_status = SDK::GetDeviceProperties(device_handle, &properties, &property_count);
    if (CR_SUCCEEDED(prop_status)) {
        std::cout << "Retrieved " << property_count << " camera properties" << std::endl;

        // Display some interesting properties
        for (int i = 0; i < property_count && i < 10; i++) {
            std::cout << "  Property[" << i << "]: Code=0x" << std::hex << properties[i].GetCode()
                      << " Size=" << std::dec << properties[i].GetValueSize() << std::endl;
        }

        SDK::ReleaseDeviceProperties(device_handle, properties);
    } else {
        std::cout << "Could not retrieve properties (this is normal for some cameras)" << std::endl;
    }
    std::cout << std::endl;

    // Keep connection alive for testing
    std::cout << "Camera connected successfully!" << std::endl;
    std::cout << "Press Enter to disconnect and exit..." << std::endl;
    std::cin.ignore();
    std::cin.get();

    // Disconnect
    std::cout << "\nDisconnecting from camera..." << std::endl;
    auto disconnect_status = SDK::Disconnect(device_handle);
    if (CR_SUCCEEDED(disconnect_status)) {
        std::cout << "Disconnected successfully." << std::endl;
    } else {
        std::cerr << "Warning: Disconnect returned error code: 0x" << std::hex << disconnect_status << std::endl;
    }

    // Cleanup
    std::cout << "Releasing camera list..." << std::endl;
    camera_list->Release();

    std::cout << "Releasing Sony SDK..." << std::endl;
    SDK::Release();

    std::cout << "\nTest completed successfully!" << std::endl;
    return 0;
}
