#include "camera_sony.h"
#include "../utils/logger.h"
#include <sstream>
#include <iomanip>
#include <ctime>

// ============================================================================
// SonyCameraCallback Implementation
// ============================================================================

SonyCameraCallback::SonyCameraCallback() = default;

SonyCameraCallback::~SonyCameraCallback() = default;

void SonyCameraCallback::OnConnected(SDK::DeviceConnectionVersioin version)
{
    connected_.store(true);
    Logger::info("Sony camera connected");
}

void SonyCameraCallback::OnDisconnected(CrInt32u error)
{
    connected_.store(false);

    std::lock_guard<std::mutex> lock(error_mutex_);
    std::ostringstream oss;
    oss << "Camera disconnected with error code: 0x" << std::hex << error;
    last_error_ = oss.str();

    Logger::warning(last_error_);
}

void SonyCameraCallback::OnPropertyChanged()
{
    // Property changed - can be very frequent, don't log
}

void SonyCameraCallback::OnLvPropertyChanged()
{
    // LiveView property changed - very frequent, don't log
}

void SonyCameraCallback::OnWarning(CrInt32u warning)
{
    std::ostringstream oss;
    oss << "Sony camera warning: 0x" << std::hex << warning;
    Logger::warning(oss.str());
}

void SonyCameraCallback::OnError(CrInt32u error)
{
    std::lock_guard<std::mutex> lock(error_mutex_);
    std::ostringstream oss;
    oss << "Sony camera error: 0x" << std::hex << error;
    last_error_ = oss.str();

    Logger::error(last_error_);
}

std::string SonyCameraCallback::getLastError() const
{
    std::lock_guard<std::mutex> lock(error_mutex_);
    return last_error_;
}

// ============================================================================
// CameraSony Implementation
// ============================================================================

CameraSony::CameraSony()
    : device_handle_(0)
    , camera_list_(nullptr)
{
    Logger::info("Sony camera interface initialized");
}

CameraSony::~CameraSony()
{
    disconnect();
    releaseSDK();
}

bool CameraSony::connect()
{
    std::lock_guard<std::mutex> lock(mutex_);

    if (connected_.load()) {
        Logger::debug("Camera already connected");
        return true;
    }

    Logger::info("Attempting to connect to Sony camera...");

    // Initialize SDK if not already done
    if (!sdk_initialized_.load()) {
        if (!initializeSDK()) {
            Logger::error("Failed to initialize Sony Remote SDK");
            return false;
        }
    }

    // Enumerate and connect to camera
    if (!enumerateAndConnect()) {
        Logger::error("Failed to enumerate or connect to camera");
        return false;
    }

    connected_.store(true);
    Logger::info("Successfully connected to Sony camera: " + camera_model_);
    return true;
}

void CameraSony::disconnect()
{
    std::lock_guard<std::mutex> lock(mutex_);

    if (!connected_.load()) {
        return;
    }

    Logger::info("Disconnecting from Sony camera...");

    // Disconnect from camera
    if (device_handle_ != 0) {
        auto status = SDK::Disconnect(device_handle_);
        if (CR_SUCCEEDED(status)) {
            Logger::info("Camera disconnected successfully");
        } else {
            Logger::warning("Camera disconnect returned error code: 0x" +
                          std::to_string(status));
        }
        device_handle_ = 0;
    }

    // Release camera list
    if (camera_list_ != nullptr) {
        camera_list_->Release();
        camera_list_ = nullptr;
    }

    connected_.store(false);
    camera_model_.clear();
    camera_id_.clear();
}

bool CameraSony::isConnected() const
{
    return connected_.load() && callback_ && callback_->isConnected();
}

messages::CameraStatus CameraSony::getStatus() const
{
    messages::CameraStatus status;

    std::lock_guard<std::mutex> lock(mutex_);

    if (!connected_.load()) {
        status.connected = false;
        status.model = "unknown";
        status.battery_percent = 0;
        status.remaining_shots = 0;
        return status;
    }

    status.connected = isConnected();
    status.model = camera_model_;

    // Get camera properties
    auto properties = readCameraProperties();

    // Extract values from properties JSON
    if (properties.contains("battery_percent")) {
        status.battery_percent = properties["battery_percent"];
    } else {
        status.battery_percent = 0;
    }

    if (properties.contains("remaining_shots")) {
        status.remaining_shots = properties["remaining_shots"];
    } else {
        status.remaining_shots = 0;
    }

    return status;
}

// ============================================================================
// Private Methods
// ============================================================================

bool CameraSony::initializeSDK()
{
    Logger::info("Initializing Sony Remote SDK...");

    // Get SDK version
    uint32_t version = SDK::GetSDKVersion();
    int major = (version & 0xFF000000) >> 24;
    int minor = (version & 0x00FF0000) >> 16;
    int patch = (version & 0x0000FF00) >> 8;

    Logger::info("Sony Remote SDK version: " + std::to_string(major) + "." +
                 std::to_string(minor) + "." + std::to_string(patch));

    // Initialize SDK (0 = no logging)
    auto init_success = SDK::Init(0);
    if (!init_success) {
        Logger::error("SDK::Init() failed");
        return false;
    }

    sdk_initialized_.store(true);
    Logger::info("Sony Remote SDK initialized successfully");
    return true;
}

void CameraSony::releaseSDK()
{
    if (sdk_initialized_.load()) {
        Logger::info("Releasing Sony Remote SDK...");
        SDK::Release();
        sdk_initialized_.store(false);
    }
}

bool CameraSony::enumerateAndConnect()
{
    Logger::info("Enumerating connected cameras...");

    // Enumerate cameras with 5 second timeout
    auto enum_status = SDK::EnumCameraObjects(&camera_list_, 5);

    if (CR_FAILED(enum_status) || camera_list_ == nullptr) {
        Logger::error("No cameras detected. Enum status: 0x" +
                     std::to_string(enum_status));
        return false;
    }

    auto ncams = camera_list_->GetCount();
    Logger::info("Found " + std::to_string(ncams) + " camera(s)");

    if (ncams == 0) {
        Logger::error("Camera enumeration returned 0 cameras");
        camera_list_->Release();
        camera_list_ = nullptr;
        return false;
    }

    // Get first camera
    auto camera_info = camera_list_->GetCameraObjectInfo(0);
    camera_model_ = std::string(camera_info->GetModel());

    const char* conn_type = camera_info->GetConnectionTypeName();
    if (std::string(conn_type) == "IP") {
        // Network camera - get MAC address
        const char* mac = (const char*)camera_info->GetMACAddressChar();
        int mac_size = camera_info->GetMACAddressCharSize();
        camera_id_ = std::string(mac, std::min(mac_size, 17));
    } else {
        // USB camera - get ID
        camera_id_ = std::string((const char*)camera_info->GetId());
    }

    Logger::info("Connecting to: " + camera_model_ + " (" +
                 std::string(conn_type) + ") ID: " + camera_id_);

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
        camera_list_->Release();
        camera_list_ = nullptr;
        callback_.reset();
        return false;
    }

    Logger::info("Camera connection initiated. Device handle: " +
                 std::to_string(static_cast<long>(device_handle_)));

    // Wait a bit for connection callback
    std::this_thread::sleep_for(std::chrono::milliseconds(500));

    return true;
}

nlohmann::json CameraSony::readCameraProperties() const
{
    nlohmann::json props;

    if (device_handle_ == 0) {
        return props;
    }

    // Get device properties
    SDK::CrDeviceProperty* properties = nullptr;
    int property_count = 0;

    auto prop_status = SDK::GetDeviceProperties(device_handle_, &properties, &property_count);

    if (CR_FAILED(prop_status) || properties == nullptr) {
        Logger::debug("Could not retrieve camera properties (may be normal for some cameras)");
        return props;
    }

    Logger::debug("Retrieved " + std::to_string(property_count) + " camera properties");

    // Parse common properties
    for (int i = 0; i < property_count; i++) {
        CrInt32u code = properties[i].GetCode();

        // Battery level (SDK::CrDevicePropertyCode::CrDeviceProperty_BatteryLevel)
        // Note: Actual property codes would be from Sony SDK documentation
        // For now, just store property count
        props["property_count"] = property_count;

        // TODO: Parse specific properties based on Sony SDK documentation
        // Examples would include:
        // - Battery level
        // - Remaining shots
        // - Recording state
        // - Current settings (ISO, aperture, shutter speed, etc.)
    }

    // Release properties
    SDK::ReleaseDeviceProperties(device_handle_, properties);

    // Set default values for now
    props["battery_percent"] = 100;  // TODO: Read actual battery level
    props["remaining_shots"] = 9999; // TODO: Read actual remaining shots

    return props;
}

// Factory function for main.cpp
extern "C" CameraInterface* createCamera()
{
    return new CameraSony();
}
