#ifndef CAMERA_INTERFACE_H
#define CAMERA_INTERFACE_H

#include <string>
#include "protocol/messages.h"

// Abstract camera interface
// Phase 1: Implemented by CameraStub
// Phase 2: Implemented by CameraSony
class CameraInterface {
public:
    virtual ~CameraInterface() = default;

    // Connect to camera
    virtual bool connect() = 0;

    // Disconnect from camera
    virtual void disconnect() = 0;

    // Check if connected
    virtual bool isConnected() const = 0;

    // Get camera status
    virtual messages::CameraStatus getStatus() const = 0;

    // Phase 2: Additional methods for camera control
    // virtual bool setProperty(const std::string& property, const std::string& value) = 0;
    // virtual std::string getProperty(const std::string& property) const = 0;
    // virtual bool capture() = 0;
    // virtual bool startRecording() = 0;
    // virtual bool stopRecording() = 0;
};

#endif // CAMERA_INTERFACE_H
