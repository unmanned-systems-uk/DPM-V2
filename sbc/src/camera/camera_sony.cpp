// camera_sony.cpp - Sony Camera Integration via Sony SDK
// Implements CameraInterface for Sony Alpha cameras via USB

#include "camera/camera_interface.h"
#include "utils/logger.h"
#include <memory>
#include <atomic>
#include <mutex>
#include <chrono>
#include <thread>

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
        std::lock_guard<std::mutex> lock(mutex_);
        connected_ = true;
        Logger::info("Camera connected (SDK connection version)");
    }

    void OnDisconnected(CrInt32u error) override {
        std::lock_guard<std::mutex> lock(mutex_);
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
        std::lock_guard<std::mutex> lock(mutex_);
        error_code_ = error;
        Logger::error("Camera error: 0x" + std::to_string(error));
    }

    bool isConnected() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return connected_;
    }

    CrInt32u getLastError() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return error_code_;
    }

private:
    mutable std::mutex mutex_;
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
