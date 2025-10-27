/**
 * discover_shutter_speeds.cpp
 *
 * Query Sony SDK to discover all available shutter speed values.
 * This will help us map the complete range of shutter speeds the camera supports.
 */

#include <iostream>
#include <iomanip>
#include <vector>
#include <thread>
#include <chrono>
#include "CRSDK/CameraRemote_SDK.h"
#include "CRSDK/IDeviceCallback.h"
#include "CRSDK/CrDeviceProperty.h"

using namespace SCRSDK;

class DiscoveryCallback : public IDeviceCallback {
public:
    void OnConnected(DeviceConnectionVersioin version) override {
        std::cout << "[INFO] Camera connected" << std::endl;
    }

    void OnDisconnected() override {
        std::cout << "[INFO] Camera disconnected" << std::endl;
    }

    void OnPropertyChanged() override {}
    void OnLvPropertyChanged() override {}
    void OnCompleteDownload(CrChar* filename) override {}
    void OnNotifyContentsTransfer(CrInt32u num) override {}
    void OnWarning(CrInt32u warning) override {}
    void OnError(CrInt32u error) override {}
};

int main() {
    std::cout << "========================================" << std::endl;
    std::cout << "  Shutter Speed Discovery Tool" << std::endl;
    std::cout << "========================================" << std::endl;
    std::cout << std::endl;

    // Initialize SDK
    auto init_result = Init();
    if (CrError_None != init_result) {
        std::cerr << "[ERROR] Failed to initialize SDK: 0x" << std::hex << init_result << std::endl;
        return 1;
    }
    std::cout << "[OK] Sony SDK initialized" << std::endl;

    // Enumerate cameras
    ICrEnumCameraObjectInfo* camera_list = nullptr;
    auto enum_result = EnumCameraObjects(&camera_list);
    if (CrError_None != enum_result || camera_list == nullptr) {
        std::cerr << "[ERROR] Failed to enumerate cameras: 0x" << std::hex << enum_result << std::endl;
        Release();
        return 1;
    }

    auto num_cameras = camera_list->GetCount();
    if (num_cameras == 0) {
        std::cerr << "[ERROR] No cameras found" << std::endl;
        camera_list->Release();
        Release();
        return 1;
    }

    std::cout << "[OK] Found " << std::dec << num_cameras << " camera(s)" << std::endl;

    // Connect to first camera
    auto* camera_info = camera_list->GetCameraObjectInfo(0);
    std::cout << "[INFO] Connecting to: " << camera_info->GetModel() << std::endl;

    DiscoveryCallback callback;
    auto* device = Connect(camera_info, &callback);
    if (!device) {
        std::cerr << "[ERROR] Failed to connect to camera" << std::endl;
        camera_list->Release();
        Release();
        return 1;
    }

    std::cout << "[OK] Camera connected" << std::endl;
    std::cout << std::endl;

    // Wait for connection to stabilize
    std::this_thread::sleep_for(std::chrono::milliseconds(1000));

    // Get shutter speed property list
    std::cout << "Querying available shutter speeds..." << std::endl;
    std::cout << "========================================" << std::endl;

    CrInt32u num_props = 0;
    CrDeviceProperty* prop_list = nullptr;

    auto get_result = device->GetDeviceProperties(&prop_list, &num_props);
    if (CrError_None != get_result) {
        std::cerr << "[ERROR] Failed to get device properties: 0x" << std::hex << get_result << std::endl;
    } else {
        std::cout << "[INFO] Retrieved " << std::dec << num_props << " properties" << std::endl;
        std::cout << std::endl;

        // Find shutter speed property
        bool found = false;
        for (CrInt32u i = 0; i < num_props; i++) {
            if (prop_list[i].GetCode() == CrDevicePropertyCode::CrDeviceProperty_ShutterSpeed) {
                found = true;
                std::cout << "SHUTTER SPEED PROPERTY FOUND" << std::endl;
                std::cout << "----------------------------------------" << std::endl;

                // Get current value
                CrInt64u current_value = prop_list[i].GetCurrentValue();
                std::cout << "Current value: 0x" << std::hex << current_value << std::dec << std::endl;
                std::cout << std::endl;

                // Get available values
                CrInt32u value_count = prop_list[i].GetValueSize();
                std::cout << "Number of available values: " << value_count << std::endl;
                std::cout << std::endl;

                if (value_count > 0) {
                    std::cout << "Available shutter speed values:" << std::endl;
                    std::cout << "Index | Hex Value  | Decimal    " << std::endl;
                    std::cout << "------|------------|------------" << std::endl;

                    CrInt64u* values = prop_list[i].GetValues();
                    for (CrInt32u j = 0; j < value_count; j++) {
                        std::cout << std::setw(5) << j << " | "
                                  << "0x" << std::hex << std::setfill('0') << std::setw(8) << values[j]
                                  << std::dec << std::setfill(' ')
                                  << " | " << values[j]
                                  << std::endl;
                    }

                    std::cout << std::endl;
                    std::cout << "Total: " << value_count << " shutter speed values" << std::endl;
                } else {
                    std::cout << "[WARNING] No available values list (property may be read-only or camera-dependent)" << std::endl;
                }

                break;
            }
        }

        if (!found) {
            std::cout << "[WARNING] Shutter speed property not found in property list" << std::endl;
        }

        device->ReleaseDeviceProperties(prop_list);
    }

    std::cout << std::endl;
    std::cout << "========================================" << std::endl;
    std::cout << "Discovery complete" << std::endl;
    std::cout << "========================================" << std::endl;

    // Cleanup
    Disconnect(device);
    camera_list->Release();
    Release();

    return 0;
}
