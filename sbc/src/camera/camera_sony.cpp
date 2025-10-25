// camera_sony.cpp - Sony Camera Integration via Sony SDK
// Implements CameraInterface for Sony Alpha cameras via USB

#include "camera/camera_interface.h"
#include "utils/logger.h"
#include <memory>
#include <atomic>
#include <mutex>
#include <chrono>
#include <thread>
#include <unordered_map>

// Sony SDK headers
#include "CRSDK/CameraRemote_SDK.h"
#include "CRSDK/IDeviceCallback.h"
#include "CRSDK/CrCommandData.h"

namespace SDK = SCRSDK;

// Sony camera callback handler
class SonyCameraCallback : public SDK::IDeviceCallback
{
public:
    SonyCameraCallback() : connected_(false), error_code_(0) {}
    ~SonyCameraCallback() = default;

    void OnConnected(SDK::DeviceConnectionVersioin version) override {
        connected_ = true;
        Logger::info("Camera connected (SDK connection version)");
        (void)version; // Suppress unused parameter warning
    }

    void OnDisconnected(CrInt32u error) override {
        connected_ = false;
        error_code_ = error;
        if (error != 0) {
            Logger::warning("Camera disconnected with error: 0x" +
                          std::to_string(error));
        } else {
            Logger::info("Camera disconnected normally");
        }
    }

    void OnPropertyChanged() override {}
    void OnLvPropertyChanged() override {}

    void OnWarning(CrInt32u warning) override {
        Logger::debug("Camera warning: 0x" + std::to_string(warning));
    }

    void OnError(CrInt32u error) override {
        error_code_ = error;
        Logger::error("Camera error: 0x" + std::to_string(error));
    }

    bool isConnected() const {
        return connected_;
    }

    CrInt32u getLastError() const {
        return error_code_;
    }

private:
    std::atomic<bool> connected_;
    std::atomic<CrInt32u> error_code_;
};

// Sony Camera Implementation
class CameraSony : public CameraInterface {
public:
    CameraSony()
        : sdk_initialized_(false)
        , device_handle_(0)
        , callback_(nullptr)
        , camera_list_(nullptr)
    {
        Logger::info("CameraSony created - initializing Sony SDK...");
        initializeSDK();
    }

    ~CameraSony() override {
        disconnect();
        shutdownSDK();
    }

    bool connect() override {
        std::lock_guard<std::mutex> lock(mutex_);

        if (!sdk_initialized_) {
            Logger::error("Cannot connect: SDK not initialized");
            return false;
        }

        if (isConnectedLocked()) {
            Logger::warning("Already connected to camera");
            return true;
        }

        Logger::info("Enumerating cameras...");

        // Enumerate cameras
        auto enum_status = SDK::EnumCameraObjects(&camera_list_, 5);

        if (CR_FAILED(enum_status) || camera_list_ == nullptr) {
            Logger::error("Failed to enumerate cameras. Status: 0x" +
                         std::to_string(enum_status));
            Logger::error("Make sure camera is: 1) Powered ON, 2) Connected via USB, 3) In PC Remote mode");
            return false;
        }

        auto ncams = camera_list_->GetCount();
        Logger::info("Found " + std::to_string(ncams) + " camera(s)");

        if (ncams == 0) {
            Logger::error("No cameras found");
            camera_list_->Release();
            camera_list_ = nullptr;
            return false;
        }

        // Get first camera
        auto camera_info = camera_list_->GetCameraObjectInfo(0);
        camera_model_ = camera_info->GetModel();

        Logger::info("Connecting to camera: " + camera_model_);
        Logger::info("Connection type: " +
                    std::string(camera_info->GetConnectionTypeName()));

        // Create callback
        callback_ = std::make_unique<SonyCameraCallback>();

        // Connect to camera
        auto* non_const_camera_info = const_cast<SDK::ICrCameraObjectInfo*>(camera_info);

        auto connect_status = SDK::Connect(
            non_const_camera_info,
            callback_.get(),
            &device_handle_,
            SDK::CrSdkControlMode_Remote,
            SDK::CrReconnecting_ON
        );

        if (CR_FAILED(connect_status)) {
            Logger::error("Failed to connect to camera. Status: 0x" +
                         std::to_string(connect_status));
            callback_.reset();
            camera_list_->Release();
            camera_list_ = nullptr;
            return false;
        }

        Logger::info("SDK Connect succeeded. Device handle: " +
                    std::to_string(device_handle_));

        // Wait for OnConnected callback (critical - camera won't accept commands until this fires)
        Logger::info("Waiting for OnConnected callback...");
        int wait_count = 0;
        while (!callback_->isConnected() && wait_count < 20) {
            std::this_thread::sleep_for(std::chrono::milliseconds(500));
            wait_count++;
        }

        if (!callback_->isConnected()) {
            Logger::error("OnConnected callback did not fire within 10 seconds");
            // Don't disconnect here - keep the connection attempt active
            // The callback might still fire, and the connection might still work
        } else {
            Logger::info("Camera fully connected and ready!");
        }

        return callback_->isConnected();
    }

    void disconnect() override {
        std::lock_guard<std::mutex> lock(mutex_);

        if (!isConnectedLocked()) {
            return;
        }

        Logger::info("Disconnecting from camera...");

        if (device_handle_ != 0) {
            auto status = SDK::Disconnect(device_handle_);
            if (CR_FAILED(status)) {
                Logger::warning("Disconnect returned error: 0x" +
                              std::to_string(status));
            }
            device_handle_ = 0;
        }

        // Release camera list
        if (camera_list_ != nullptr) {
            camera_list_->Release();
            camera_list_ = nullptr;
        }

        callback_.reset();
        camera_model_.clear();

        Logger::info("Camera disconnected");
    }

    bool isConnected() const override {
        std::lock_guard<std::mutex> lock(mutex_);
        return isConnectedLocked();
    }

    messages::CameraStatus getStatus() const override {
        std::lock_guard<std::mutex> lock(mutex_);

        messages::CameraStatus status;

        if (isConnectedLocked()) {
            status.connected = true;
            status.model = camera_model_;

            // Query battery level from camera
            status.battery_percent = getBatteryLevel();

            // Query remaining shots from camera
            status.remaining_shots = getRemainingShotsCount();
        } else {
            status.connected = false;
            status.model = "none";
            status.battery_percent = 0;
            status.remaining_shots = 0;
        }

        return status;
    }

    bool capture() override {
        std::lock_guard<std::mutex> lock(mutex_);

        if (!isConnectedLocked()) {
            Logger::error("Cannot capture: camera not connected");
            return false;
        }

        Logger::info("Triggering shutter release...");

        // Send shutter button DOWN (press)
        auto status_down = SDK::SendCommand(
            device_handle_,
            SDK::CrCommandId_Release,
            SDK::CrCommandParam_Down
        );

        if (CR_FAILED(status_down)) {
            Logger::error("Failed to send shutter DOWN command. Status: 0x" +
                         std::to_string(status_down));
            return false;
        }

        Logger::debug("Shutter DOWN command sent");

        // Small delay to allow shutter press to register
        std::this_thread::sleep_for(std::chrono::milliseconds(100));

        // Send shutter button UP (release)
        auto status_up = SDK::SendCommand(
            device_handle_,
            SDK::CrCommandId_Release,
            SDK::CrCommandParam_Up
        );

        if (CR_FAILED(status_up)) {
            Logger::error("Failed to send shutter UP command. Status: 0x" +
                         std::to_string(status_up));
            // Try to recover by sending UP again
            SDK::SendCommand(device_handle_, SDK::CrCommandId_Release, SDK::CrCommandParam_Up);
            return false;
        }

        Logger::debug("Shutter UP command sent");
        Logger::info("Shutter release sequence completed successfully");
        return true;
    }

private:
    void initializeSDK() {
        Logger::info("Initializing Sony SDK...");

        if (SDK::Init(0)) {
            sdk_initialized_ = true;

            // Get SDK version
            uint32_t version = SDK::GetSDKVersion();
            int major = (version & 0xFF000000) >> 24;
            int minor = (version & 0x00FF0000) >> 16;
            int patch = (version & 0x0000FF00) >> 8;

            Logger::info("Sony SDK initialized successfully (v" +
                        std::to_string(major) + "." +
                        std::to_string(minor) + "." +
                        std::to_string(patch) + ")");
        } else {
            Logger::error("Failed to initialize Sony SDK");
            sdk_initialized_ = false;
        }
    }

    void shutdownSDK() {
        if (sdk_initialized_) {
            Logger::info("Shutting down Sony SDK...");
            SDK::Release();
            sdk_initialized_ = false;
        }
    }

    bool isConnectedLocked() const {
        // Must hold mutex_ when calling this
        return callback_ != nullptr &&
               callback_->isConnected() &&
               device_handle_ != 0;
    }

    int getBatteryLevel() const {
        // TODO: Query actual battery level from camera via SDK property
        // For now, return placeholder value
        // Property code: CrDeviceProperty_S1BatteryLevel or similar
        return 75; // Placeholder
    }

    int getRemainingShotsCount() const {
        // TODO: Query actual remaining shots from camera via SDK property
        // For now, return placeholder value
        // Property code: CrDeviceProperty_Media_RemainingNumberOfShots or similar
        return 999; // Placeholder
    }

    bool setProperty(const std::string& property, const std::string& value) override {
        std::lock_guard<std::mutex> lock(mutex_);

        if (!isConnectedLocked()) {
            Logger::error("Cannot set property: camera not connected");
            return false;
        }

        Logger::info("Setting property: " + property + " = " + value);

        SDK::CrDeviceProperty prop;

        // Map property name to SDK property code and convert human-readable values
        // Protocol uses human-readable values (e.g., "1/8000", "f/2.8")
        // Air-side converts to Sony SDK format (e.g., 0x00010001, 0x01000280)

        if (property == "shutter_speed") {
            // Shutter speed: map human-readable strings to Sony SDK values
            prop.SetCode(SDK::CrDevicePropertyCode::CrDeviceProperty_ShutterSpeed);
            static const std::unordered_map<std::string, uint32_t> SHUTTER_MAP = {
                {"auto",   0x00000000}, {"1/8000", 0x00010001}, {"1/4000", 0x00010002},
                {"1/2000", 0x00010003}, {"1/1000", 0x00010004}, {"1/500",  0x00010005},
                {"1/250",  0x00010006}, {"1/125",  0x00010007}, {"1/60",   0x00010008},
                {"1/30",   0x00010009}, {"1/15",   0x0001000A}, {"1/8",    0x0001000B},
                {"1/4",    0x0001000C}, {"1/2",    0x0001000D}, {"1",      0x0001000E},
                {"2",      0x0001000F}, {"4",      0x00010010}, {"8",      0x00010011},
                {"15",     0x00010012}, {"30",     0x00010013}
            };
            auto it = SHUTTER_MAP.find(value);
            if (it == SHUTTER_MAP.end()) {
                Logger::error("Invalid shutter speed value: " + value);
                return false;
            }
            prop.SetCurrentValue(it->second);
            prop.SetValueType(SDK::CrDataType::CrDataType_UInt32Array);
        }
        else if (property == "aperture") {
            // Aperture: map f-stop strings to Sony SDK values
            prop.SetCode(SDK::CrDevicePropertyCode::CrDeviceProperty_FNumber);
            static const std::unordered_map<std::string, uint32_t> APERTURE_MAP = {
                {"auto",  0x00000000}, {"f/1.4", 0x01000140}, {"f/2.0", 0x01000200},
                {"f/2.8", 0x01000280}, {"f/4.0", 0x01000400}, {"f/5.6", 0x01000560},
                {"f/8.0", 0x01000800}, {"f/11",  0x01001100}, {"f/16",  0x01001600},
                {"f/22",  0x01002200}
            };
            auto it = APERTURE_MAP.find(value);
            if (it == APERTURE_MAP.end()) {
                Logger::error("Invalid aperture value: " + value);
                return false;
            }
            prop.SetCurrentValue(static_cast<uint16_t>(it->second & 0xFFFF));
            prop.SetValueType(SDK::CrDataType::CrDataType_UInt16Array);
        }
        else if (property == "iso") {
            // ISO: map ISO strings to Sony SDK values
            prop.SetCode(SDK::CrDevicePropertyCode::CrDeviceProperty_IsoSensitivity);
            static const std::unordered_map<std::string, uint32_t> ISO_MAP = {
                {"auto",   0xFFFFFFFF}, {"100",    100},    {"200",    200},
                {"400",    400},        {"800",    800},    {"1600",   1600},
                {"3200",   3200},       {"6400",   6400},   {"12800",  12800},
                {"25600",  25600},      {"51200",  51200},  {"102400", 102400}
            };
            auto it = ISO_MAP.find(value);
            if (it == ISO_MAP.end()) {
                Logger::error("Invalid ISO value: " + value);
                return false;
            }
            prop.SetCurrentValue(it->second);
            prop.SetValueType(SDK::CrDataType::CrDataType_UInt32Array);
        }
        else if (property == "white_balance") {
            // White balance: map preset names to Sony SDK enums
            prop.SetCode(SDK::CrDevicePropertyCode::CrDeviceProperty_WhiteBalance);
            static const std::unordered_map<std::string, uint16_t> WB_MAP = {
                {"auto", 0x0000}, {"daylight", 0x0011}, {"shade", 0x0012}, {"cloudy", 0x0013},
                {"tungsten", 0x0014}, {"fluorescent_warm", 0x0021}, {"fluorescent_cool", 0x0022},
                {"fluorescent_day", 0x0023}, {"fluorescent_daylight", 0x0024}, {"flash", 0x0030},
                {"temperature", 0x0100}, {"custom", 0x0104}
            };
            auto it = WB_MAP.find(value);
            if (it == WB_MAP.end()) {
                Logger::error("Invalid white balance value: " + value);
                return false;
            }
            prop.SetCurrentValue(it->second);
            prop.SetValueType(SDK::CrDataType::CrDataType_UInt16Array);
        }
        else if (property == "white_balance_temperature") {
            // WB Temperature: direct Kelvin value (2500-9900)
            // Note: white_balance must be set to "temperature" first
            prop.SetCode(SDK::CrDevicePropertyCode::CrDeviceProperty_Colortemp);
            int kelvin = std::stoi(value);
            if (kelvin < 2500 || kelvin > 9900) {
                Logger::error("White balance temperature out of range (2500-9900): " + value);
                return false;
            }
            prop.SetCurrentValue(static_cast<uint32_t>(kelvin));
            prop.SetValueType(SDK::CrDataType::CrDataType_UInt32Array);
        }
        else if (property == "focus_mode") {
            // Focus mode: map mode names to Sony SDK enums
            prop.SetCode(SDK::CrDevicePropertyCode::CrDeviceProperty_FocusMode);
            static const std::unordered_map<std::string, uint16_t> FOCUS_MAP = {
                {"af_s", 0x0002}, {"af_c", 0x0003}, {"af_a", 0x0004},
                {"dmf", 0x0006}, {"manual", 0x0001}
            };
            auto it = FOCUS_MAP.find(value);
            if (it == FOCUS_MAP.end()) {
                Logger::error("Invalid focus mode value: " + value);
                return false;
            }
            prop.SetCurrentValue(it->second);
            prop.SetValueType(SDK::CrDataType::CrDataType_UInt16Array);
        }
        else if (property == "file_format") {
            // File format: map format names to Sony SDK enums
            prop.SetCode(SDK::CrDevicePropertyCode::CrDeviceProperty_FileType);
            static const std::unordered_map<std::string, uint16_t> FORMAT_MAP = {
                {"jpeg", 0x0001}, {"raw", 0x0002}, {"jpeg_raw", 0x0003}
            };
            auto it = FORMAT_MAP.find(value);
            if (it == FORMAT_MAP.end()) {
                Logger::error("Invalid file format value: " + value);
                return false;
            }
            prop.SetCurrentValue(it->second);
            prop.SetValueType(SDK::CrDataType::CrDataType_UInt16Array);
        }
        else if (property == "drive_mode") {
            // Drive mode: map mode names to Sony SDK enums
            prop.SetCode(SDK::CrDevicePropertyCode::CrDeviceProperty_DriveMode);
            static const std::unordered_map<std::string, uint32_t> DRIVE_MAP = {
                {"single", 0x00000001}, {"continuous_lo", 0x00010004},
                {"continuous_hi", 0x00010001}, {"self_timer_10s", 0x00030003},
                {"self_timer_2s", 0x00030001}, {"bracket", 0x00040301}
            };
            auto it = DRIVE_MAP.find(value);
            if (it == DRIVE_MAP.end()) {
                Logger::error("Invalid drive mode value: " + value);
                return false;
            }
            prop.SetCurrentValue(it->second);
            prop.SetValueType(SDK::CrDataType::CrDataType_UInt32Array);
        }
        else {
            Logger::error("Unknown or unsupported property: " + property);
            Logger::error("Supported properties: shutter_speed, aperture, iso, white_balance, white_balance_temperature, focus_mode, file_format, drive_mode");
            return false;
        }

        // Send property to camera
        auto status = SDK::SetDeviceProperty(device_handle_, &prop);

        if (CR_FAILED(status)) {
            Logger::error("Failed to set property. Status: 0x" + std::to_string(status));
            return false;
        }

        Logger::info("Property set successfully");
        return true;
    }

    std::string getProperty(const std::string& property) const override {
        std::lock_guard<std::mutex> lock(mutex_);

        if (!isConnectedLocked()) {
            Logger::error("Cannot get property: camera not connected");
            return "";
        }

        Logger::info("Getting property: " + property);

        // For now, return empty string - full implementation requires
        // querying camera property list via SDK::GetDeviceProperty()
        // This will be implemented in the next iteration
        Logger::warning("getProperty not yet fully implemented");
        return "";
    }

private:
    mutable std::mutex mutex_;
    bool sdk_initialized_;
    SDK::CrDeviceHandle device_handle_;
    std::unique_ptr<SonyCameraCallback> callback_;
    SDK::ICrEnumCameraObjectInfo* camera_list_;
    std::string camera_model_;
};

// Factory function to create camera interface
extern "C" CameraInterface* createCamera() {
    return new CameraSony();
}
