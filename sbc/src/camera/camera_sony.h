#ifndef CAMERA_SONY_H
#define CAMERA_SONY_H

#include "camera_interface.h"
#include "CRSDK/CameraRemote_SDK.h"
#include "CRSDK/IDeviceCallback.h"
#include "../protocol/messages.h"
#include <nlohmann/json.hpp>
#include <memory>
#include <mutex>
#include <atomic>
#include <string>

namespace SDK = SCRSDK;

// Camera callback handler for Sony SDK events
class SonyCameraCallback : public SDK::IDeviceCallback
{
public:
    SonyCameraCallback();
    ~SonyCameraCallback();

    // IDeviceCallback interface
    void OnConnected(SDK::DeviceConnectionVersioin version) override;
    void OnDisconnected(CrInt32u error) override;
    void OnPropertyChanged() override;
    void OnLvPropertyChanged() override;
    void OnWarning(CrInt32u warning) override;
    void OnError(CrInt32u error) override;

    // Connection state
    bool isConnected() const { return connected_.load(); }
    std::string getLastError() const;

private:
    std::atomic<bool> connected_{false};
    mutable std::mutex error_mutex_;
    std::string last_error_;
};

// Sony camera implementation
class CameraSony : public CameraInterface
{
public:
    CameraSony();
    ~CameraSony() override;

    // CameraInterface implementation
    bool connect() override;
    void disconnect() override;
    bool isConnected() const override;
    messages::CameraStatus getStatus() const override;
    bool capture() override;
    bool focus(const std::string& action, int speed = 3) override;
    bool autoFocusHold(const std::string& state) override;
    float getFocalDistanceMeters() const override;
    bool setProperty(const std::string& property, const std::string& value) override;
    std::string getProperty(const std::string& property) const override;

private:
    bool initializeSDK();
    void releaseSDK();
    bool enumerateAndConnect();
    nlohmann::json readCameraProperties() const;

    std::unique_ptr<SonyCameraCallback> callback_;
    SDK::CrDeviceHandle device_handle_;
    SDK::ICrEnumCameraObjectInfo* camera_list_;

    mutable std::mutex mutex_;
    std::atomic<bool> sdk_initialized_{false};
    std::atomic<bool> connected_{false};

    std::string camera_model_;
    std::string camera_id_;
};

#endif // CAMERA_SONY_H
