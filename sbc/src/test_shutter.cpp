#include <iostream>
#include <string>
#include <memory>
#include <chrono>
#include <thread>
#include "CRSDK/CameraRemote_SDK.h"
#include "CRSDK/IDeviceCallback.h"
#include "CRSDK/CrCommandData.h"

namespace SDK = SCRSDK;

// Simple camera callback
class ShutterTestCallback : public SDK::IDeviceCallback
{
public:
    ShutterTestCallback() : connected_(false), capture_started_(false), transfer_complete_(false) {}
    ~ShutterTestCallback() {}

    void OnConnected(SDK::DeviceConnectionVersioin version) override {
        std::cout << "[Callback] Camera connected!" << std::endl;
        connected_ = true;
    }

    void OnDisconnected(CrInt32u error) override {
        std::cout << "[Callback] Camera disconnected. Error: 0x" << std::hex << error << std::endl;
        connected_ = false;
    }

    void OnPropertyChanged() override {}
    void OnLvPropertyChanged() override {}

    void OnNotifyContentsTransfer(CrInt32u notify, SDK::CrContentHandle handle, CrChar* filename) override {
        auto now = std::chrono::steady_clock::now();
        auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(now - shutter_down_time_).count();

        if (notify == SDK::CrNotify_ContentsTransfer_Start) {
            std::cout << "[CONTENTS TRANSFER] Start - Handle: 0x" << std::hex << handle << std::dec << " (" << elapsed << "ms)" << std::endl;
        } else if (notify == SDK::CrNotify_ContentsTransfer_Complete) {
            std::cout << "[CONTENTS TRANSFER] Complete! (" << elapsed << "ms total)" << std::endl;
            if (filename) {
                std::cout << "[CONTENTS TRANSFER] Filename: " << filename << std::endl;
            }
            transfer_complete_ = true;
        } else {
            std::cout << "[CONTENTS TRANSFER] Notify: 0x" << std::hex << notify << std::dec << " (" << elapsed << "ms)" << std::endl;
        }
    }

    void OnWarning(CrInt32u warning) override {
        auto now = std::chrono::steady_clock::now();
        auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(now - shutter_down_time_).count();

        // Specific notifications we care about
        if (warning == SDK::CrNotify_Captured_Event) {
            std::cout << "[CAPTURE EVENT] Photo captured! (" << elapsed << "ms after shutter down)" << std::endl;
            capture_started_ = true;
        } else if (warning == SDK::CrNotify_ContentsTransfer_Start) {
            std::cout << "[WARNING->TRANSFER] Starting to write photo to memory card... (" << elapsed << "ms)" << std::endl;
        } else if (warning == SDK::CrNotify_ContentsTransfer_Complete) {
            std::cout << "[WARNING->TRANSFER COMPLETE] Photo saved! (" << elapsed << "ms total)" << std::endl;
            transfer_complete_ = true;
        } else {
            std::cout << "[Warning] 0x" << std::hex << warning << std::dec << " (" << elapsed << "ms)" << std::endl;
        }
    }

    void OnWarningExt(CrInt32u warning, CrInt32 param1, CrInt32 param2, CrInt32 param3) override {
        auto now = std::chrono::steady_clock::now();
        auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(now - shutter_down_time_).count();
        std::cout << "[WarningExt] 0x" << std::hex << warning << std::dec
                  << " params(" << param1 << "," << param2 << "," << param3 << ") (" << elapsed << "ms)" << std::endl;
    }

    void OnError(CrInt32u error) override {
        std::cout << "[Error] 0x" << std::hex << error << std::endl;
    }

    bool isConnected() const { return connected_; }
    bool captureComplete() const { return transfer_complete_; }

    void startTiming() {
        shutter_down_time_ = std::chrono::steady_clock::now();
        capture_started_ = false;
        transfer_complete_ = false;
    }

private:
    bool connected_;
    bool capture_started_;
    bool transfer_complete_;
    std::chrono::steady_clock::time_point shutter_down_time_;
};

int main() {
    std::cout << "\n=== Sony Camera Shutter Test ===" << std::endl;
    std::cout << "This will test taking a photo via USB\n" << std::endl;

    // Print SDK constants for debugging
    std::cout << "\nSDK Constants:" << std::endl;
    std::cout << "CrNotify_Captured_Event = 0x" << std::hex << SDK::CrNotify_Captured_Event << std::dec << std::endl;
    std::cout << "CrNotify_ContentsTransfer_Start = 0x" << std::hex << SDK::CrNotify_ContentsTransfer_Start << std::dec << std::endl;
    std::cout << "CrNotify_ContentsTransfer_Complete = 0x" << std::hex << SDK::CrNotify_ContentsTransfer_Complete << std::dec << std::endl;
    std::cout << std::endl;

    // Get SDK version
    uint32_t version = SDK::GetSDKVersion();
    int major = (version & 0xFF000000) >> 24;
    int minor = (version & 0x00FF0000) >> 16;
    int patch = (version & 0x0000FF00) >> 8;
    std::cout << "Sony SDK: " << major << "." << minor << "." << patch << std::endl;

    // Initialize SDK
    std::cout << "Initializing SDK..." << std::endl;
    if (!SDK::Init(0)) {
        std::cerr << "ERROR: Failed to initialize SDK!" << std::endl;
        return 1;
    }
    std::cout << "SDK initialized." << std::endl;

    // Enumerate cameras
    std::cout << "\nEnumerating cameras (5 sec timeout)..." << std::endl;
    SDK::ICrEnumCameraObjectInfo* camera_list = nullptr;
    auto enum_status = SDK::EnumCameraObjects(&camera_list, 5);

    if (CR_FAILED(enum_status) || camera_list == nullptr) {
        std::cerr << "ERROR: No cameras found!" << std::endl;
        std::cerr << "Make sure camera is:" << std::endl;
        std::cerr << "  1. Powered ON" << std::endl;
        std::cerr << "  2. Connected via USB" << std::endl;
        std::cerr << "  3. In PC Remote mode" << std::endl;
        SDK::Release();
        return 1;
    }

    auto ncams = camera_list->GetCount();
    std::cout << "Found " << ncams << " camera(s)" << std::endl;

    if (ncams == 0) {
        std::cerr << "ERROR: Enumeration returned 0 cameras!" << std::endl;
        camera_list->Release();
        SDK::Release();
        return 1;
    }

    // Get first camera
    auto camera_info = camera_list->GetCameraObjectInfo(0);
    std::cout << "\nCamera: " << camera_info->GetModel() << std::endl;
    std::cout << "Type: " << camera_info->GetConnectionTypeName() << std::endl;

    // Create callback and connect
    std::cout << "\nConnecting to camera..." << std::endl;
    ShutterTestCallback callback;
    SDK::CrDeviceHandle device_handle = 0;

    auto* non_const_camera_info = const_cast<SDK::ICrCameraObjectInfo*>(camera_info);

    // Use Remote mode (RemoteTransferMode not supported for USB)
    auto connect_status = SDK::Connect(
        non_const_camera_info,
        &callback,
        &device_handle,
        SDK::CrSdkControlMode_Remote,
        SDK::CrReconnecting_ON
    );

    if (CR_FAILED(connect_status)) {
        std::cerr << "ERROR: Failed to connect! Status: 0x" << std::hex << connect_status << std::endl;
        camera_list->Release();
        SDK::Release();
        return 1;
    }

    std::cout << "Connected! Device handle: " << device_handle << std::endl;

    // Wait for connection callback (critical - camera won't accept commands until OnConnected is called)
    std::cout << "Waiting for OnConnected callback..." << std::endl;
    int wait_count = 0;
    while (!callback.isConnected() && wait_count < 20) {
        std::this_thread::sleep_for(std::chrono::milliseconds(500));
        wait_count++;
        if (wait_count % 4 == 0) {
            std::cout << "  Still waiting... (" << (wait_count / 2) << "s)" << std::endl;
        }
    }

    if (!callback.isConnected()) {
        std::cerr << "ERROR: Connection callback never received after " << (wait_count / 2) << " seconds!" << std::endl;
        std::cerr << "Camera is not ready to accept commands." << std::endl;
        SDK::Disconnect(device_handle);
        camera_list->Release();
        SDK::Release();
        return 1;
    }

    std::cout << "OnConnected callback received! Camera is ready." << std::endl;

    // Give camera a bit more time to fully stabilize
    std::cout << "Waiting for camera to fully stabilize..." << std::endl;
    std::this_thread::sleep_for(std::chrono::milliseconds(500));

    // Now test the shutter!
    std::cout << "\n=== SHUTTER TEST ===" << std::endl;
    std::cout << "Sending shutter DOWN command..." << std::endl;

    // Start timing
    callback.startTiming();

    auto shutter_down = SDK::SendCommand(
        device_handle,
        SDK::CrCommandId::CrCommandId_Release,
        SDK::CrCommandParam::CrCommandParam_Down
    );

    if (CR_FAILED(shutter_down)) {
        std::cerr << "ERROR: Shutter DOWN failed! Status: 0x" << std::hex << shutter_down << std::endl;
    } else {
        std::cout << "Shutter DOWN sent successfully!" << std::endl;
    }

    // Hold shutter for camera to focus and meter exposure
    // Testing 300ms delay (500ms worked, 2000ms worked previously)
    std::cout << "Holding shutter (300ms for focus/metering)..." << std::endl;
    std::this_thread::sleep_for(std::chrono::milliseconds(300));

    // Release shutter
    std::cout << "Sending shutter UP command..." << std::endl;
    auto shutter_up = SDK::SendCommand(
        device_handle,
        SDK::CrCommandId::CrCommandId_Release,
        SDK::CrCommandParam::CrCommandParam_Up
    );

    if (CR_FAILED(shutter_up)) {
        std::cerr << "ERROR: Shutter UP failed! Status: 0x" << std::hex << shutter_up << std::endl;
    } else {
        std::cout << "Shutter UP sent successfully!" << std::endl;
    }

    // Wait for capture confirmation
    std::cout << "\nWaiting for capture confirmation..." << std::endl;
    int capture_wait = 0;
    while (!callback.captureComplete() && capture_wait < 40) {
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        capture_wait++;
    }

    if (callback.captureComplete()) {
        std::cout << "✓ Photo capture confirmed!" << std::endl;
    } else {
        std::cout << "✗ Timeout waiting for capture confirmation (may still have succeeded)" << std::endl;
    }

    std::cout << "\n=== TEST COMPLETE ===" << std::endl;
    std::cout << "Check your camera's display or memory card to verify photo was taken!" << std::endl;

    // Cleanup
    std::cout << "\nDisconnecting..." << std::endl;
    SDK::Disconnect(device_handle);
    camera_list->Release();
    SDK::Release();

    std::cout << "Done!" << std::endl;
    return 0;
}
