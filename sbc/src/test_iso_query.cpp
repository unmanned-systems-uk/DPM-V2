// test_iso_query.cpp - Diagnostic tool to query camera for available ISO values
// This tool helps diagnose why extended ISO values (AUTO, 50, 64, 80, etc.) might not be working

#include "utils/logger.h"
#include "camera/property_loader.h"
#include <iostream>
#include <iomanip>
#include <thread>
#include <chrono>

// Sony SDK headers
#include "CRSDK/CameraRemote_SDK.h"
#include "CRSDK/IDeviceCallback.h"
#include "CRSDK/CrDeviceProperty.h"

namespace SDK = SCRSDK;

// Simple callback for connection events
class DiagnosticCallback : public SDK::IDeviceCallback
{
public:
    DiagnosticCallback() : connected_(false) {}
    virtual ~DiagnosticCallback() = default;

    void OnConnected(SDK::DeviceConnectionVersioin version) override {
        connected_ = true;
        std::cout << "[CONNECTED] Camera connected successfully" << std::endl;
        (void)version;
    }

    void OnDisconnected(CrInt32u error) override {
        connected_ = false;
        if (error != 0) {
            std::cout << "[DISCONNECTED] Error: 0x" << std::hex << error << std::dec << std::endl;
        } else {
            std::cout << "[DISCONNECTED] Camera disconnected" << std::endl;
        }
    }

    void OnPropertyChanged() override {}
    void OnLvPropertyChanged() override {}
    void OnCompleteDownload(CrChar* filename) override { (void)filename; }
    void OnNotifyContentsTransfer(CrInt32u notify, SDK::CrContentHandle content_handle, CrChar* filename) override {
        (void)notify; (void)content_handle; (void)filename;
    }
    void OnWarning(CrInt32u warning) override { (void)warning; }
    void OnError(CrInt32u error) override { (void)error; }

    bool isConnected() const { return connected_; }

private:
    bool connected_;
};

// Map Sony SDK hex values back to our string format
std::string isoValueToString(uint32_t value) {
    if (value == 0xFFFFFFFF) return "auto";
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
    auto init_result = SDK::Init();
    if (!init_result) {
        std::cerr << "[ERROR] Failed to initialize Sony SDK" << std::endl;
        return 1;
    }
    std::cout << "[OK] Sony SDK initialized" << std::endl;
    std::cout << std::endl;

    // Enumerate cameras
    std::cout << "[SCAN] Searching for connected cameras..." << std::endl;
    SDK::ICrEnumCameraObjectInfo* camera_list = nullptr;
    auto enum_status = SDK::EnumCameraObjects(&camera_list);
    if (!enum_status || !camera_list) {
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
    std::cout << "[INFO] Camera ID: " << camera_info->GetId() << std::endl;
    std::cout << std::endl;

    // Connect to camera
    std::cout << "[CONNECT] Connecting to camera..." << std::endl;
    auto callback = new DiagnosticCallback();
    SDK::CrDeviceHandle device_handle = nullptr;

    auto connect_status = SDK::Connect(camera_info, callback, &device_handle);
    if (!connect_status || !device_handle) {
        std::cerr << "[ERROR] Failed to connect to camera" << std::endl;
        delete callback;
        camera_list->Release();
        SDK::Release();
        return 1;
    }

    // Wait for connection callback
    std::this_thread::sleep_for(std::chrono::seconds(2));

    if (!callback->isConnected()) {
        std::cerr << "[ERROR] Connection timeout - camera did not connect" << std::endl;
        SDK::Disconnect(device_handle);
        delete callback;
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
    CrInt32u num_props = 0;
    SDK::CrDeviceProperty* prop_list = nullptr;
    auto prop_status = SDK::GetDeviceProperties(device_handle, &prop_list, &num_props);

    if (!prop_status || !prop_list) {
        std::cerr << "[ERROR] Failed to get device properties" << std::endl;
    } else {
        std::cout << "[INFO] Camera reports " << num_props << " total properties" << std::endl;
        std::cout << std::endl;

        // Find ISO property
        bool found_iso = false;
        for (CrInt32u i = 0; i < num_props; ++i) {
            if (prop_list[i].GetCode() == SDK::CrDevicePropertyCode::CrDeviceProperty_IsoSensitivity) {
                found_iso = true;
                auto& iso_prop = prop_list[i];

                std::cout << "[FOUND] ISO Sensitivity Property" << std::endl;
                std::cout << "-----------------------------------------------------------" << std::endl;

                // Current value
                if (iso_prop.IsGetEnableCurrentValue()) {
                    uint32_t current = iso_prop.GetCurrentValue();
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

                    CrInt64u* values = iso_prop.GetValues();
                    for (CrInt32u j = 0; j < num_values; ++j) {
                        uint32_t value = static_cast<uint32_t>(values[j]);
                        std::string str_value = isoValueToString(value);

                        // Check if this value is in our specification
                        bool in_spec = PropertyLoader::isValidValue("iso", str_value);

                        std::cout << "  [" << std::setw(2) << j << "] "
                                  << std::setw(8) << std::left << str_value
                                  << " (0x" << std::hex << std::setw(8) << std::setfill('0')
                                  << value << std::dec << std::setfill(' ') << ")";

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
    delete callback;
    camera_list->Release();
    SDK::Release();

    std::cout << "[DONE] Diagnostic complete" << std::endl;
    return 0;
}
