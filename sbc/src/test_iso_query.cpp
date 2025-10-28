// test_iso_query.cpp - Diagnostic tool to query camera for available ISO values
// Based on test_camera.cpp structure

#include <iostream>
#include <iomanip>
#include <string>
#include "CRSDK/CameraRemote_SDK.h"
#include "CRSDK/IDeviceCallback.h"
#include "CRSDK/CrDefines.h"
#include "CRSDK/CrDeviceProperty.h"
#include "camera/property_loader.h"

namespace SDK = SCRSDK;

// Simple callback for connection events
class TestCameraCallback : public SDK::IDeviceCallback
{
public:
    void OnConnected(SDK::DeviceConnectionVersioin version) override {
        std::cout << "[OK] Camera connected (version " << std::hex << version << ")" << std::endl;
    }

    void OnDisconnected(CrInt32u error) override {
        if (error) {
            std::cout << "[WARNING] Camera disconnected with error: 0x" << std::hex << error << std::endl;
        }
    }

    void OnPropertyChanged() override {}
    void OnLvPropertyChanged() override {}
    void OnNotifyContentsTransfer(CrInt32u notify, SDK::CrContentHandle contentHandle, CrChar* filename) override {
        (void)notify; (void)contentHandle; (void)filename;
    }
    void OnWarning(CrInt32u warning) override { (void)warning; }
    void OnError(CrInt32u error) override { (void)error; }
};

// Convert ISO SDK value to string
std::string isoValueToString(CrInt64u value) {
    // Check for AUTO
    if (value == 0xFFFFFFFF || value == 0xFFFFFF) {
        return "auto";
    }

    // Check for extended ISO (flag 0x10000000)
    if ((value & 0x10000000) != 0) {
        // Extended ISO - strip the flag
        return std::to_string(value & 0x0FFFFFFF);
    }

    // Standard ISO
    return std::to_string(value);
}

int main() {
    std::cout << "===========================================================" << std::endl;
    std::cout << "  Sony Camera ISO Capability Diagnostic Tool" << std::endl;
    std::cout << "===========================================================" << std::endl;
    std::cout << std::endl;

    // Initialize PropertyLoader
    std::cout << "[INIT] Loading property specifications..." << std::endl;
    if (!PropertyLoader::initialize()) {
        std::cerr << "[ERROR] Failed to load camera_properties.json" << std::endl;
        return 1;
    }
    std::cout << "[OK] PropertyLoader initialized with "
              << PropertyLoader::getValueCount("iso") << " ISO values" << std::endl;
    std::cout << std::endl;

    // Initialize Sony SDK
    std::cout << "[INIT] Initializing Sony Camera Remote SDK..." << std::endl;
    auto init_result = SDK::Init(0);
    if (!init_result) {
        std::cerr << "[ERROR] Failed to initialize Sony SDK" << std::endl;
        return 1;
    }
    std::cout << "[OK] Sony SDK initialized" << std::endl;
    std::cout << std::endl;

    // Enumerate cameras
    std::cout << "[SCAN] Searching for connected cameras..." << std::endl;
    SDK::ICrEnumCameraObjectInfo* camera_list = nullptr;
    auto enum_status = SDK::EnumCameraObjects(&camera_list, 5);
    if (CR_FAILED(enum_status) || !camera_list) {
        std::cerr << "[ERROR] No cameras found" << std::endl;
        SDK::Release();
        return 1;
    }

    auto num_cameras = camera_list->GetCount();
    std::cout << "[OK] Found " << num_cameras << " camera(s)" << std::endl;

    if (num_cameras == 0) {
        std::cerr << "[ERROR] No cameras connected" << std::endl;
        camera_list->Release();
        SDK::Release();
        return 1;
    }

    // Use first camera
    auto camera_info = camera_list->GetCameraObjectInfo(0);
    std::cout << "[INFO] Camera Model: " << camera_info->GetModel() << std::endl;
    std::cout << std::endl;

    // Connect to camera
    std::cout << "[CONNECT] Connecting to camera..." << std::endl;
    TestCameraCallback callback;
    SDK::CrDeviceHandle device_handle;

    auto* non_const_camera_info = const_cast<SDK::ICrCameraObjectInfo*>(camera_info);

    auto connect_status = SDK::Connect(
        non_const_camera_info,
        &callback,
        &device_handle,
        SDK::CrSdkControlMode_Remote,
        SDK::CrReconnecting_ON
    );

    if (CR_FAILED(connect_status)) {
        std::cerr << "[ERROR] Failed to connect to camera" << std::endl;
        std::cerr << "Error code: 0x" << std::hex << connect_status << std::endl;
        camera_list->Release();
        SDK::Release();
        return 1;
    }

    std::cout << "[OK] Connected to camera" << std::endl;
    std::cout << std::endl;

    // Query ISO property
    std::cout << "===========================================================" << std::endl;
    std::cout << "  Querying ISO Sensitivity Property" << std::endl;
    std::cout << "===========================================================" << std::endl;
    std::cout << std::endl;

    // Get device properties
    SDK::CrDeviceProperty* prop_list = nullptr;
    int num_props = 0;
    auto prop_status = SDK::GetDeviceProperties(device_handle, &prop_list, &num_props);

    if (CR_FAILED(prop_status) || !prop_list) {
        std::cerr << "[ERROR] Failed to get device properties" << std::endl;
    } else {
        std::cout << "[INFO] Camera reports " << num_props << " total properties" << std::endl;
        std::cout << std::endl;

        // Find ISO property
        bool found_iso = false;
        for (int i = 0; i < num_props; ++i) {
            if (prop_list[i].GetCode() == SDK::CrDevicePropertyCode::CrDeviceProperty_IsoSensitivity) {
                found_iso = true;
                auto& iso_prop = prop_list[i];

                std::cout << "[FOUND] ISO Sensitivity Property" << std::endl;
                std::cout << "-----------------------------------------------------------" << std::endl;

                // Current value
                if (iso_prop.IsGetEnableCurrentValue()) {
                    CrInt64u current = iso_prop.GetCurrentValue();
                    std::cout << "  Current Value: " << isoValueToString(current)
                              << " (0x" << std::hex << current << std::dec << ")" << std::endl;
                } else {
                    std::cout << "  Current Value: [NOT READABLE]" << std::endl;
                }

                // Writable flag
                if (iso_prop.IsSetEnableCurrentValue()) {
                    std::cout << "  Writable: YES ✓" << std::endl;
                } else {
                    std::cout << "  Writable: NO ✗ (Property is READ-ONLY in current camera state)" << std::endl;
                }

                std::cout << std::endl;

                // Available values
                CrInt32u num_values = iso_prop.GetValueSize();
                if (num_values > 0) {
                    std::cout << "  Available ISO Values (" << num_values << " total):" << std::endl;
                    std::cout << "  -----------------------------------------------------------" << std::endl;

                    CrInt8u* values_ptr = iso_prop.GetValues();
                    CrInt64u* values = reinterpret_cast<CrInt64u*>(values_ptr);

                    for (CrInt32u j = 0; j < num_values; ++j) {
                        std::string str_value = isoValueToString(values[j]);

                        // Check if this value is in our specification
                        bool in_spec = PropertyLoader::isValidValue("iso", str_value);

                        std::cout << "  [" << std::setw(2) << j << "] "
                                  << std::setw(8) << std::left << str_value
                                  << " (0x" << std::hex << std::setw(8) << std::setfill('0')
                                  << values[j] << std::dec << std::setfill(' ') << ")";

                        if (in_spec) {
                            std::cout << " ✓ IN SPEC";
                        } else {
                            std::cout << " ✗ NOT IN SPEC";
                        }
                        std::cout << std::endl;
                    }
                } else {
                    std::cout << "  Available Values: [NOT QUERYABLE]" << std::endl;
                    std::cout << "  Note: Camera does not report available values for this property" << std::endl;
                }

                std::cout << std::endl;
                break;
            }
        }

        if (!found_iso) {
            std::cerr << "[ERROR] ISO Sensitivity property not found in camera properties!" << std::endl;
        }

        SDK::ReleaseDeviceProperties(device_handle, prop_list);
    }

    std::cout << "===========================================================" << std::endl;
    std::cout << "  Specification Comparison" << std::endl;
    std::cout << "===========================================================" << std::endl;
    std::cout << std::endl;

    std::cout << "ISO values defined in camera_properties.json specification:" << std::endl;
    auto spec_values = PropertyLoader::getIsoValues();
    int count = 0;
    for (const auto& val : spec_values) {
        std::cout << "  " << std::setw(8) << std::left << val;
        if (++count % 6 == 0) std::cout << std::endl;
    }
    if (count % 6 != 0) std::cout << std::endl;

    std::cout << std::endl;
    std::cout << "Total in specification: " << spec_values.size() << " values" << std::endl;
    std::cout << std::endl;

    // Cleanup
    std::cout << "[CLEANUP] Disconnecting..." << std::endl;
    SDK::Disconnect(device_handle);
    camera_list->Release();
    SDK::Release();

    std::cout << "[DONE] Diagnostic complete" << std::endl;
    return 0;
}
