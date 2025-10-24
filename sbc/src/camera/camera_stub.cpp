#include "camera/camera_interface.h"
#include "utils/logger.h"

// Camera stub implementation for Phase 1
// Returns placeholder data without Sony SDK integration
class CameraStub : public CameraInterface {
public:
    CameraStub() : connected_(false) {
        Logger::info("CameraStub created (Phase 1 - no Sony SDK)");
    }

    ~CameraStub() override {
        disconnect();
    }

    bool connect() override {
        Logger::info("CameraStub: connect() called (stub - always returns false)");
        connected_ = false;  // Always false in Phase 1
        return false;
    }

    void disconnect() override {
        if (connected_) {
            Logger::info("CameraStub: disconnect() called");
            connected_ = false;
        }
    }

    bool isConnected() const override {
        return connected_;
    }

    messages::CameraStatus getStatus() const override {
        // Return placeholder status for Phase 1
        messages::CameraStatus status;
        status.connected = false;
        status.model = "unknown";
        status.battery_percent = 0;
        status.remaining_shots = 0;

        return status;
    }

private:
    bool connected_;
};

// Factory function to create camera interface
// In Phase 2, this will create CameraSony instead
extern "C" CameraInterface* createCamera() {
    return new CameraStub();
}
