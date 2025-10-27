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
#include <future>
#include <sstream>
#include <iomanip>

// Sony SDK headers
#include "CRSDK/CameraRemote_SDK.h"
#include "CRSDK/IDeviceCallback.h"
#include "CRSDK/CrCommandData.h"

namespace SDK = SCRSDK;

// Helper function to format values as hex
static std::string toHexString(uint64_t value) {
    std::ostringstream oss;
    oss << "0x" << std::hex << value;
    return oss.str();
}

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

        // Prepare connection parameters
        auto* non_const_camera_info = const_cast<SDK::ICrCameraObjectInfo*>(camera_info);
        auto callback_ptr = callback_.get();

        // Connect to camera with timeout protection (10 second timeout)
        Logger::info("Attempting SDK Connect with 10s timeout...");

        SDK::CrDeviceHandle temp_handle = 0;
        bool connect_success = runWithTimeout([non_const_camera_info, callback_ptr, &temp_handle]() -> bool {
            auto connect_status = SDK::Connect(
                non_const_camera_info,
                callback_ptr,
                &temp_handle,
                SDK::CrSdkControlMode_Remote,
                SDK::CrReconnecting_ON
            );

            if (CR_FAILED(connect_status)) {
                Logger::error("Failed to connect to camera. Status: 0x" +
                             std::to_string(connect_status));
                return false;
            }

            Logger::info("SDK Connect succeeded. Device handle: " +
                        std::to_string(temp_handle));
            return true;
        }, 10000, "camera.connect");

        if (!connect_success) {
            Logger::error("Camera connection timed out or failed");
            callback_.reset();
            camera_list_->Release();
            camera_list_ = nullptr;
            return false;
        }

        // Store the device handle
        device_handle_ = temp_handle;

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
        // Read connection status from callback's atomic flag
        // This is thread-safe and never blocks - the SDK callbacks maintain this flag
        return callback_ && callback_->isConnected();
    }

    messages::CameraStatus getStatus() const override {
        // Check connection using callback's atomic flag (fast, never blocks)
        bool connected = isConnected();

        if (!connected) {
            // Camera disconnected - return disconnected status immediately
            messages::CameraStatus status;
            status.connected = false;
            status.model = "none";
            status.battery_percent = 0;
            status.remaining_shots = 0;
            status.shutter_speed = "";
            status.aperture = "";
            status.iso = "";
            status.white_balance = "";
            status.focus_mode = "";
            status.file_format = "";
            return status;
        }

        // Try to get device handle and model without blocking
        {
            std::unique_lock<std::mutex> lock(mutex_, std::try_to_lock);
            if (!lock.owns_lock()) {
                // Couldn't get lock - return cached status (never blocks)
                cached_status_.connected = connected;
                return cached_status_;
            }

            // Got the lock - update basic status quickly
            // NOTE: We skip detailed property queries here to minimize mutex hold time
            // Properties are queried on-demand via getProperty() when needed
            cached_status_.connected = true;
            cached_status_.model = camera_model_;
            cached_status_.battery_percent = getBatteryLevel();  // Placeholder
            cached_status_.remaining_shots = getRemainingShotsCount();  // Placeholder

            // Keep existing property values from cache
            // (they're updated by setProperty() calls)
        }

        return cached_status_;
    }

    bool capture() override {
        // Check connection using atomic flag first (fast, never blocks)
        if (!isConnected()) {
            Logger::error("Cannot capture: camera not connected");
            return false;
        }

        // Acquire lock for entire operation to prevent concurrent SDK access
        // CRITICAL FIX: Keep lock held during SDK calls to avoid race condition
        std::unique_lock<std::mutex> lock(mutex_, std::try_to_lock);
        if (!lock.owns_lock()) {
            Logger::warning("Cannot capture: camera busy with another operation");
            return false;
        }

        Logger::info("Triggering shutter release...");

        // Send shutter button DOWN (press) - synchronous call while holding mutex
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

    // Timeout wrapper for Sony SDK operations that may block indefinitely
    // CRITICAL: std::future destructor blocks, so we must detach timed-out tasks
    template<typename Func>
    bool runWithTimeout(Func&& func, int timeout_ms, const std::string& operation_name) {
        // Use shared_ptr to manage future lifetime
        auto future_ptr = std::make_shared<std::future<bool>>(
            std::async(std::launch::async, std::forward<Func>(func))
        );

        if (future_ptr->wait_for(std::chrono::milliseconds(timeout_ms)) == std::future_status::timeout) {
            Logger::error(operation_name + " timed out after " + std::to_string(timeout_ms) + "ms - camera may be in incompatible state");
            Logger::warning("Possible causes: camera reviewing image, menu open, or wrong mode");
            Logger::warning("Background thread detached - it will continue running but won't block");

            // Detach the future by moving it to a background cleanup thread
            // This prevents the destructor from blocking
            std::thread([future_ptr]() {
                try {
                    future_ptr->wait();  // Wait for completion in background
                    Logger::debug("Detached SDK operation finally completed");
                } catch (...) {
                    Logger::warning("Detached SDK operation threw exception");
                }
            }).detach();

            return false;
        }

        try {
            return future_ptr->get();
        } catch (const std::exception& e) {
            Logger::error(operation_name + " threw exception: " + std::string(e.what()));
            return false;
        }
    }

    int getBatteryLevel() const {
        // Query battery percentage from camera via SDK
        // Property code: CrDeviceProperty_BatteryRemain (0-100%)
        //
        // IMPORTANT: This is called from status broadcaster (5 Hz) which shouldn't
        // block on mutex. Use cached value if mutex unavailable.

        static int cached_battery = 75;

        // Try to acquire lock without blocking
        std::unique_lock<std::mutex> lock(mutex_, std::try_to_lock);
        if (!lock.owns_lock()) {
            // Can't get lock - return cached value
            return cached_battery;
        }

        // Got the lock - query fresh battery level
        SDK::CrDeviceProperty* property_list = nullptr;
        int property_count = 0;

        auto status = SDK::GetDeviceProperties(device_handle_, &property_list, &property_count);

        if (CR_FAILED(status) || property_count == 0 || !property_list) {
            // Query failed - return cached value
            return cached_battery;
        }

        int battery_percent = cached_battery; // Start with cached value

        // Search for battery property
        for (int i = 0; i < property_count; i++) {
            if (property_list[i].GetCode() == SDK::CrDevicePropertyCode::CrDeviceProperty_BatteryRemain) {
                uint64_t raw_value = property_list[i].GetCurrentValue();

                // Check for "untaken" special value (0xFFFF)
                if (raw_value == 0xFFFF) {
                    Logger::debug("Battery level not available (untaken)");
                    battery_percent = 0;
                } else if (raw_value <= 100) {
                    battery_percent = static_cast<int>(raw_value);
                    Logger::debug("Battery level: " + std::to_string(battery_percent) + "%");
                } else {
                    Logger::warning("Invalid battery value: " + std::to_string(raw_value));
                }
                break;
            }
        }

        SDK::ReleaseDeviceProperties(device_handle_, property_list);

        // Update cache and return
        cached_battery = battery_percent;
        return battery_percent;
    }

    int getRemainingShotsCount() const {
        // TODO: Query actual remaining shots from camera via SDK property
        // For now, return placeholder value
        // Property code: CrDeviceProperty_Media_RemainingNumberOfShots or similar
        return 999; // Placeholder
    }

    bool setProperty(const std::string& property, const std::string& value) override {
        // Check connection using atomic flag first (fast, never blocks)
        if (!isConnected()) {
            Logger::error("Cannot set property: camera not connected");
            return false;
        }

        Logger::info("Setting property: " + property + " = " + value);

        // Acquire lock for entire operation to prevent concurrent SDK access
        // CRITICAL FIX: Keep lock held during SDK call to avoid race condition
        // with getProperty() and getBatteryLevel()
        std::unique_lock<std::mutex> lock(mutex_, std::try_to_lock);
        if (!lock.owns_lock()) {
            Logger::warning("Cannot set property: camera busy with another operation");
            return false;
        }

        // Do property mapping while holding lock
        SDK::CrDeviceProperty prop;

        // Map property name to SDK property code and convert human-readable values
        // Protocol uses human-readable values (e.g., "1/8000", "f/2.8")
        // Air-side converts to Sony SDK format (e.g., 0x00010001, 0x01000280)

        if (property == "shutter_speed") {
            // Reject AUTO/BULB mode - not suitable for UAV operations
            if (value == "auto" || value == "bulb") {
                Logger::error("Cannot set shutter_speed to '" + value + "' - AUTO/BULB modes are disabled for UAV flight operations");
                return false;
            }

            // Shutter speed: map human-readable strings to Sony SDK values
            //
            // FORMAT (from automated discovery 2025-10-27):
            // Fast shutters (1/X): Upper 2 bytes = 0x0001, Lower 2 bytes = X (denominator in hex)
            //   Example: 1/2000 = 0x0001 (numerator) + 0x07D0 (2000 in hex) = 0x000107D0
            //
            // Long exposures (X.X"): Format 0xNNNN000A where NNNN × 0.1 = seconds
            //   Example: 2.5" = 0x0019 (25 tenths) + 0x000A = 0x0019000A
            //
            prop.SetCode(SDK::CrDevicePropertyCode::CrDeviceProperty_ShutterSpeed);
            static const std::unordered_map<std::string, uint32_t> SHUTTER_MAP = {
                // Fast shutter speeds (1/8000 to 1/1000)
                {"1/8000", 0x00011F40}, {"1/6400", 0x00011900}, {"1/5000", 0x00011388},
                {"1/4000", 0x00010FA0}, {"1/3200", 0x00010C80}, {"1/2500", 0x000109C4},
                {"1/2000", 0x000107D0}, {"1/1600", 0x00010640}, {"1/1250", 0x000104E2},
                {"1/1000", 0x000103E8},
                // Medium shutter speeds (1/800 to 1/100)
                {"1/800",  0x00010320}, {"1/640",  0x00010280}, {"1/500",  0x000101F4},
                {"1/400",  0x00010190}, {"1/320",  0x00010140}, {"1/250",  0x000100FA},
                {"1/200",  0x000100C8}, {"1/160",  0x000100A0}, {"1/125",  0x0001007D},
                {"1/100",  0x00010064},
                // Slow shutter speeds (1/80 to 1/3)
                {"1/80",   0x00010050}, {"1/60",   0x0001003C}, {"1/50",   0x00010032},
                {"1/40",   0x00010028}, {"1/30",   0x0001001E}, {"1/25",   0x00010019},
                {"1/20",   0x00010014}, {"1/15",   0x0001000F}, {"1/13",   0x0001000D},
                {"1/10",   0x0001000A}, {"1/8",    0x00010008}, {"1/6",    0x00010006},
                {"1/5",    0x00010005}, {"1/4",    0x00010004}, {"1/3",    0x00010003},
                // Long exposures (0.3" to 30")
                {"0.3\"",  0x0003000A}, {"0.4\"",  0x0004000A}, {"0.5\"",  0x0005000A},
                {"0.6\"",  0x0006000A}, {"0.8\"",  0x0008000A}, {"1.0\"",  0x000A000A},
                {"1.3\"",  0x000D000A}, {"1.6\"",  0x0010000A}, {"2.0\"",  0x0014000A},
                {"2.5\"",  0x0019000A}, {"3.0\"",  0x001E000A}, {"4.0\"",  0x0028000A},
                {"5.0\"",  0x0032000A}, {"6.0\"",  0x003C000A}, {"8.0\"",  0x0050000A},
                {"10\"",   0x0064000A}, {"13\"",   0x0082000A}, {"15\"",   0x0096000A},
                {"20\"",   0x00C8000A}, {"25\"",   0x00FA000A}, {"30\"",   0x012C000A}
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
            // Note: Values stored as 0x0100xxxx but only lower 16 bits (0xxxxx) sent to camera
            prop.SetCode(SDK::CrDevicePropertyCode::CrDeviceProperty_FNumber);
            // Aperture: Sony SDK format is f_number × 100
            // e.g., F/4.0 = 4.0 × 100 = 400 = 0x190
            // e.g., F/16 = 16.0 × 100 = 1600 = 0x640
            static const std::unordered_map<std::string, uint32_t> APERTURE_MAP = {
                {"auto",  0x00000000},
                {"f/1.4", 0x8C},   // 1.4 × 100 = 140
                {"f/1.8", 0xB4},   // 1.8 × 100 = 180
                {"f/2.0", 0xC8},   // 2.0 × 100 = 200
                {"f/2.8", 0x118},  // 2.8 × 100 = 280
                {"f/3.5", 0x15E},  // 3.5 × 100 = 350
                {"f/4.0", 0x190},  // 4.0 × 100 = 400
                {"f/5.6", 0x230},  // 5.6 × 100 = 560
                {"f/6.3", 0x276},  // 6.3 × 100 = 630
                {"f/8.0", 0x320},  // 8.0 × 100 = 800
                {"f/9.0", 0x384},  // 9.0 × 100 = 900
                {"f/10",  0x3E8},  // 10.0 × 100 = 1000
                {"f/11",  0x44C},  // 11.0 × 100 = 1100
                {"f/13",  0x514},  // 13.0 × 100 = 1300
                {"f/14",  0x578},  // 14.0 × 100 = 1400
                {"f/16",  0x640},  // 16.0 × 100 = 1600
                {"f/18",  0x708},  // 18.0 × 100 = 1800
                {"f/20",  0x7D0},  // 20.0 × 100 = 2000
                {"f/22",  0x898}   // 22.0 × 100 = 2200
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
            // Sony SDK uses simple decimal values (not complex hex like shutter speed)
            // Sony Alpha 1 supports full stops and third stops
            prop.SetCode(SDK::CrDevicePropertyCode::CrDeviceProperty_IsoSensitivity);
            static const std::unordered_map<std::string, uint32_t> ISO_MAP = {
                {"auto",   0xFFFFFFFF},
                // Extended low ISO
                {"50",     50},         {"64",     64},     {"80",     80},
                // Standard ISO range - Full stops and third stops (100-102400)
                {"100",    100},        {"125",    125},    {"160",    160},
                {"200",    200},        {"250",    250},    {"320",    320},
                {"400",    400},        {"500",    500},    {"640",    640},
                {"800",    800},        {"1000",   1000},   {"1250",   1250},
                {"1600",   1600},       {"2000",   2000},   {"2500",   2500},
                {"3200",   3200},       {"4000",   4000},   {"5000",   5000},
                {"6400",   6400},       {"8000",   8000},   {"10000",  10000},
                {"12800",  12800},      {"16000",  16000},  {"20000",  20000},
                {"25600",  25600},      {"32000",  32000},  {"40000",  40000},
                {"51200",  51200},      {"64000",  64000},  {"80000",  80000},
                {"102400", 102400}
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

        // IMPORTANT: Check if property is currently writable before attempting to set it
        // Sony SDK requires checking the enable flag first (per SDK documentation)
        SDK::CrDeviceProperty* property_list = nullptr;
        int property_count = 0;

        auto get_status = SDK::GetDeviceProperties(device_handle_, &property_list, &property_count);

        if (CR_FAILED(get_status) || !property_list || property_count == 0) {
            Logger::error("Failed to get device properties before setting. Status: 0x" + std::to_string(get_status));
            if (property_list) {
                SDK::ReleaseDeviceProperties(device_handle_, property_list);
            }
            return false;
        }

        // Find our target property and check if it's writable
        bool property_is_writable = false;
        for (int i = 0; i < property_count; i++) {
            if (property_list[i].GetCode() == prop.GetCode()) {
                // Check if property is currently writable (enable flag)
                if (property_list[i].IsSetEnableCurrentValue()) {
                    property_is_writable = true;
                    Logger::debug("Property is writable (enable flag is set)");
                } else {
                    Logger::warning("Property is NOT writable right now (enable flag is clear)");
                    Logger::warning("Camera may be: reviewing image, in wrong mode, or property locked");
                }
                break;
            }
        }

        SDK::ReleaseDeviceProperties(device_handle_, property_list);

        if (!property_is_writable) {
            Logger::error("Cannot set property: camera is not accepting changes to this property right now");
            return false;
        }

        // Send property to camera - synchronous call while holding mutex
        // CRITICAL: Must execute in same thread that holds mutex (not async)
        // Property changes are fast (<50ms typically), so blocking is acceptable
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

        Logger::debug("Getting property: " + property);

        // Map property name to SDK property code
        SDK::CrDevicePropertyCode prop_code;

        if (property == "shutter_speed") {
            prop_code = SDK::CrDevicePropertyCode::CrDeviceProperty_ShutterSpeed;
        }
        else if (property == "aperture") {
            prop_code = SDK::CrDevicePropertyCode::CrDeviceProperty_FNumber;
        }
        else if (property == "iso") {
            prop_code = SDK::CrDevicePropertyCode::CrDeviceProperty_IsoSensitivity;
        }
        else if (property == "white_balance") {
            prop_code = SDK::CrDevicePropertyCode::CrDeviceProperty_WhiteBalance;
        }
        else if (property == "white_balance_temperature") {
            prop_code = SDK::CrDevicePropertyCode::CrDeviceProperty_Colortemp;
        }
        else if (property == "focus_mode") {
            prop_code = SDK::CrDevicePropertyCode::CrDeviceProperty_FocusMode;
        }
        else if (property == "file_format") {
            prop_code = SDK::CrDevicePropertyCode::CrDeviceProperty_FileType;
        }
        else if (property == "drive_mode") {
            prop_code = SDK::CrDevicePropertyCode::CrDeviceProperty_DriveMode;
        }
        else {
            Logger::error("Unknown property for get: " + property);
            return "";
        }

        // Get all properties from camera
        SDK::CrDeviceProperty* property_list = nullptr;
        int property_count = 0;

        auto status = SDK::GetDeviceProperties(device_handle_, &property_list, &property_count);

        if (CR_FAILED(status) || property_count == 0 || !property_list) {
            Logger::warning("Failed to get properties from camera. Status: 0x" + std::to_string(status));
            if (property_list) {
                SDK::ReleaseDeviceProperties(device_handle_, property_list);
            }
            return "";
        }

        // Search for the property we want
        std::string result;
        bool found = false;

        for (int i = 0; i < property_count; i++) {
            if (property_list[i].GetCode() == prop_code) {
                found = true;
                uint64_t raw_value = property_list[i].GetCurrentValue();

                Logger::debug("Raw SDK value for " + property + ": " +
                             toHexString(raw_value) + " (dec: " + std::to_string(raw_value) + ")");

                if (property == "shutter_speed") {
                    // Reverse lookup in shutter speed map
                    // VERIFIED VALUES from automated discovery script (2025-10-27)
                    // Format for fast shutters: 0x1XXXX where XXXX = denominator of fraction (1/X)
                    // Format for long exposures: 0xNNNN000a where NNNN (hex) × 0.1 = seconds
                    static const std::unordered_map<uint32_t, std::string> SHUTTER_REVERSE = {
                        {0x00000000, "auto"},
                        // Very fast (1/8000 to 1/1000)
                        {0x11F40, "1/8000"}, {0x11900, "1/6400"}, {0x11388, "1/5000"},
                        {0x10FA0, "1/4000"}, {0x10C80, "1/3200"}, {0x109C4, "1/2500"},
                        {0x107D0, "1/2000"}, {0x10640, "1/1600"}, {0x104E2, "1/1250"},
                        {0x103E8, "1/1000"},
                        // Fast (1/800 to 1/100)
                        {0x10320, "1/800"},  {0x10280, "1/640"},  {0x101F4, "1/500"},
                        {0x10190, "1/400"},  {0x10140, "1/320"},  {0x100FA, "1/250"},
                        {0x100C8, "1/200"},  {0x100A0, "1/160"},  {0x1007D, "1/125"},
                        {0x10064, "1/100"},
                        // Medium (1/80 to 1/10)
                        {0x10050, "1/80"},   {0x1003C, "1/60"},   {0x10032, "1/50"},
                        {0x10028, "1/40"},   {0x1001E, "1/30"},   {0x10019, "1/25"},
                        {0x10014, "1/20"},   {0x1000F, "1/15"},   {0x1000D, "1/13"},
                        {0x1000A, "1/10"},
                        // Slow (1/8 to 1/3)
                        {0x10008, "1/8"},    {0x10006, "1/6"},    {0x10005, "1/5"},
                        {0x10004, "1/4"},    {0x10003, "1/3"},
                        // Long exposures (0.3" to 30") - Format: 0xNNNN000a
                        {0x3000a, "0.3\""},  {0x4000a, "0.4\""},  {0x5000a, "0.5\""},
                        {0x6000a, "0.6\""},  {0x8000a, "0.8\""},  {0xa000a, "1.0\""},
                        {0xd000a, "1.3\""},  {0x10000a, "1.6\""}, {0x14000a, "2.0\""},
                        {0x19000a, "2.5\""}, {0x1e000a, "3.0\""}, {0x28000a, "4.0\""},
                        {0x32000a, "5.0\""}, {0x3c000a, "6.0\""}, {0x50000a, "8.0\""},
                        {0x64000a, "10\""},  {0x82000a, "13\""},  {0x96000a, "15\""},
                        {0xc8000a, "20\""},  {0xfa000a, "25\""},  {0x12c000a, "30\""}
                    };
                    auto it = SHUTTER_REVERSE.find(static_cast<uint32_t>(raw_value));
                    result = (it != SHUTTER_REVERSE.end()) ? it->second : "unknown(" + toHexString(raw_value) + ")";
                }
                else if (property == "aperture") {
                    // Reverse lookup in aperture map (f_number × 100)
                    static const std::unordered_map<uint32_t, std::string> APERTURE_REVERSE = {
                        {0x00000000, "auto"},
                        {0x8C, "f/1.4"},   {0xA0, "f/1.6"},   {0xB4, "f/1.8"},
                        {0xC8, "f/2.0"},   {0xDC, "f/2.2"},   {0xFA, "f/2.5"},
                        {0x118, "f/2.8"},  {0x140, "f/3.2"},  {0x15E, "f/3.5"},
                        {0x190, "f/4.0"},  {0x1C2, "f/4.5"},  {0x1F4, "f/5.0"},
                        {0x230, "f/5.6"},  {0x276, "f/6.3"},  {0x2C6, "f/7.1"},
                        {0x320, "f/8.0"},  {0x384, "f/9.0"},  {0x3E8, "f/10"},
                        {0x44C, "f/11"},   {0x514, "f/13"},   {0x578, "f/14"},
                        {0x640, "f/16"},   {0x708, "f/18"},   {0x7D0, "f/20"},
                        {0x898, "f/22"}
                    };
                    auto it = APERTURE_REVERSE.find(static_cast<uint32_t>(raw_value));
                    result = (it != APERTURE_REVERSE.end()) ? it->second : "unknown(" + toHexString(raw_value) + ")";
                }
                else if (property == "iso") {
                    // ISO AUTO can be returned as 0xFFFFFFFF (32-bit) or 0xFFFFFF (24-bit)
                    if (raw_value == 0xFFFFFFFF || raw_value == 0xFFFFFF) {
                        result = "auto";
                    } else {
                        result = std::to_string(raw_value);
                    }
                }
                else {
                    // For other properties, return hex value for now
                    result = "0x" + std::to_string(raw_value);
                }

                break;
            }
        }

        SDK::ReleaseDeviceProperties(device_handle_, property_list);

        if (!found) {
            Logger::warning("Property " + property + " not found in camera property list");
            return "";
        }

        Logger::debug("Camera property " + property + " = " + result);
        return result;
    }

private:
    mutable std::mutex mutex_;
    bool sdk_initialized_;
    SDK::CrDeviceHandle device_handle_;
    std::unique_ptr<SonyCameraCallback> callback_;
    SDK::ICrEnumCameraObjectInfo* camera_list_;
    std::string camera_model_;

    // Cached status for non-blocking getStatus() calls
    mutable messages::CameraStatus cached_status_;
};

// Factory function to create camera interface
extern "C" CameraInterface* createCamera() {
    return new CameraSony();
}
