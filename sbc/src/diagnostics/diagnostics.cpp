#include "diagnostics.h"
#include <iostream>
#include <iomanip>
#include <string>
#include "CRSDK/CameraRemote_SDK.h"
#include "CRSDK/IDeviceCallback.h"
#include "CRSDK/CrDefines.h"
#include "CRSDK/CrDeviceProperty.h"
#include "camera/property_loader.h"
#include "utils/logger.h"

namespace SDK = SCRSDK;

namespace {

// Simple callback for diagnostic connections
class DiagnosticCallback : public SDK::IDeviceCallback
{
public:
    void OnConnected(SDK::DeviceConnectionVersioin version) override {
        std::cout << "[OK] Camera connected (version " << std::hex << version << std::dec << ")" << std::endl;
    }

    void OnDisconnected(CrInt32u error) override {
        if (error) {
            std::cout << "[WARNING] Camera disconnected with error: 0x" << std::hex << error << std::dec << std::endl;
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

// Connect to camera for diagnostics
bool connectToCamera(SDK::CrDeviceHandle* device_handle, DiagnosticCallback* callback) {
    std::cout << "[SCAN] Searching for connected cameras..." << std::endl;
    SDK::ICrEnumCameraObjectInfo* camera_list = nullptr;
    auto enum_status = SDK::EnumCameraObjects(&camera_list, 5);

    if (CR_FAILED(enum_status) || !camera_list) {
        std::cerr << "[ERROR] No cameras found" << std::endl;
        return false;
    }

    auto num_cameras = camera_list->GetCount();
    std::cout << "[OK] Found " << num_cameras << " camera(s)" << std::endl;

    if (num_cameras == 0) {
        std::cerr << "[ERROR] No cameras connected" << std::endl;
        camera_list->Release();
        return false;
    }

    // Use first camera
    auto camera_info = camera_list->GetCameraObjectInfo(0);
    std::cout << "[INFO] Camera Model: " << camera_info->GetModel() << std::endl;
    std::cout << std::endl;

    // Connect to camera
    std::cout << "[CONNECT] Connecting to camera..." << std::endl;
    auto* non_const_camera_info = const_cast<SDK::ICrCameraObjectInfo*>(camera_info);

    auto connect_status = SDK::Connect(
        non_const_camera_info,
        callback,
        device_handle,
        SDK::CrSdkControlMode_Remote,
        SDK::CrReconnecting_ON
    );

    camera_list->Release();

    if (CR_FAILED(connect_status)) {
        std::cerr << "[ERROR] Failed to connect to camera" << std::endl;
        std::cerr << "Error code: 0x" << std::hex << connect_status << std::dec << std::endl;
        return false;
    }

    std::cout << "[OK] Connected to camera" << std::endl;
    std::cout << std::endl;
    return true;
}

} // anonymous namespace

namespace Diagnostics {

int runISODiagnostic() {
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

    // Connect to camera
    DiagnosticCallback callback;
    SDK::CrDeviceHandle device_handle;

    if (!connectToCamera(&device_handle, &callback)) {
        SDK::Release();
        return 1;
    }

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
                    std::cout << "  NOTE: This may indicate camera is in wrong shooting mode" << std::endl;
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
    SDK::Release();

    std::cout << "[DONE] ISO Diagnostic complete" << std::endl;
    return 0;
}

int runExposureModeDiagnostic() {
    std::cout << "===========================================================" << std::endl;
    std::cout << "  Sony Camera Exposure Mode Diagnostic Tool" << std::endl;
    std::cout << "===========================================================" << std::endl;
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

    // Connect to camera
    DiagnosticCallback callback;
    SDK::CrDeviceHandle device_handle;

    if (!connectToCamera(&device_handle, &callback)) {
        SDK::Release();
        return 1;
    }

    // Query exposure mode property
    std::cout << "===========================================================" << std::endl;
    std::cout << "  Querying Exposure Mode Property" << std::endl;
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

        // Find exposure program mode property
        bool found_mode = false;
        for (int i = 0; i < num_props; ++i) {
            if (prop_list[i].GetCode() == SDK::CrDevicePropertyCode::CrDeviceProperty_ExposureProgramMode) {
                found_mode = true;
                auto& mode_prop = prop_list[i];

                std::cout << "[FOUND] Exposure Program Mode Property" << std::endl;
                std::cout << "-----------------------------------------------------------" << std::endl;

                // Current value
                if (mode_prop.IsGetEnableCurrentValue()) {
                    CrInt64u current = mode_prop.GetCurrentValue();
                    std::string mode_str;

                    switch (current) {
                        case 0x01: mode_str = "P (Program Auto)"; break;
                        case 0x02: mode_str = "A (Aperture Priority)"; break;
                        case 0x03: mode_str = "S (Shutter Priority)"; break;
                        case 0x04: mode_str = "M (Manual)"; break;
                        case 0x8000: mode_str = "Auto"; break;
                        case 0x8001: mode_str = "Auto+"; break;
                        default: mode_str = "Unknown (0x" + std::to_string(current) + ")";
                    }

                    std::cout << "  Current Mode: " << mode_str << std::endl;
                    std::cout << "  Raw Value: 0x" << std::hex << current << std::dec << std::endl;

                    // Provide guidance based on mode
                    if (current == 0x04) {
                        std::cout << std::endl;
                        std::cout << "  ⚠️  MANUAL MODE DETECTED" << std::endl;
                        std::cout << "  ISO Auto is typically NOT available in Manual mode." << std::endl;
                        std::cout << "  To use ISO Auto, switch camera to P, A, or S mode." << std::endl;
                    } else if (current == 0x01 || current == 0x02 || current == 0x03) {
                        std::cout << std::endl;
                        std::cout << "  ✓ ISO Auto should be available in this mode" << std::endl;
                    }
                } else {
                    std::cout << "  Current Mode: [NOT READABLE]" << std::endl;
                }

                std::cout << std::endl;
                break;
            }
        }

        if (!found_mode) {
            std::cout << "[WARNING] Exposure Program Mode property not found" << std::endl;
            std::cout << "Camera may not support this property" << std::endl;
        }

        SDK::ReleaseDeviceProperties(device_handle, prop_list);
    }

    // Cleanup
    std::cout << "[CLEANUP] Disconnecting..." << std::endl;
    SDK::Disconnect(device_handle);
    SDK::Release();

    std::cout << "[DONE] Exposure Mode Diagnostic complete" << std::endl;
    return 0;
}

int runPropertiesListDiagnostic() {
    std::cout << "===========================================================" << std::endl;
    std::cout << "  Sony Camera Properties List" << std::endl;
    std::cout << "===========================================================" << std::endl;
    std::cout << std::endl;

    std::cout << "[INFO] This diagnostic lists all available camera properties" << std::endl;
    std::cout << "[INFO] Implementation pending..." << std::endl;

    return 0;
}

int runPropertyMappingDiagnostic() {
    std::cout << "===========================================================" << std::endl;
    std::cout << "  Property Mapping Test" << std::endl;
    std::cout << "===========================================================" << std::endl;
    std::cout << std::endl;

    std::cout << "[INFO] This diagnostic tests value mapping conversions" << std::endl;
    std::cout << "[INFO] Implementation pending..." << std::endl;

    return 0;
}

int parseDiagnosticCommand(int argc, char* argv[]) {
    // Look for --diagnostic flag
    for (int i = 1; i < argc; ++i) {
        std::string arg(argv[i]);

        if (arg.find("--diagnostic=") == 0) {
            std::string mode = arg.substr(13);  // Length of "--diagnostic="

            std::cout << "Running diagnostic mode: " << mode << std::endl;
            std::cout << std::endl;

            if (mode == "iso") {
                return runISODiagnostic();
            } else if (mode == "exposure-mode") {
                return runExposureModeDiagnostic();
            } else if (mode == "properties") {
                return runPropertiesListDiagnostic();
            } else if (mode == "property-mapping") {
                return runPropertyMappingDiagnostic();
            } else {
                std::cerr << "Unknown diagnostic mode: " << mode << std::endl;
                std::cerr << std::endl;
                std::cerr << "Available modes:" << std::endl;
                std::cerr << "  --diagnostic=iso              - ISO sensitivity diagnostics" << std::endl;
                std::cerr << "  --diagnostic=exposure-mode    - Exposure mode diagnostics" << std::endl;
                std::cerr << "  --diagnostic=properties       - List all properties" << std::endl;
                std::cerr << "  --diagnostic=property-mapping - Test property mapping" << std::endl;
                return 1;
            }
        }
    }

    // Not a diagnostic command
    return -1;
}

} // namespace Diagnostics
