// Diagnostic version of focus() method for camera_sony.cpp
// This version includes extensive logging to identify the exact issue

bool focus(const std::string& action, int speed = 3) override {
    LOG_INFO(LogContext::CAMERA, "=== FOCUS DEBUG START ===");
    LOG_INFO(LogContext::CAMERA, "Requested action: " + action + ", speed: " + std::to_string(speed));

    // Check connection
    if (!isConnected()) {
        LOG_ERROR(LogContext::CAMERA, "Cannot focus: camera not connected");
        return false;
    }

    // Acquire lock
    std::unique_lock<std::mutex> lock(mutex_, std::try_to_lock);
    if (!lock.owns_lock()) {
        LOG_WARNING(LogContext::CAMERA, "Cannot focus: camera busy with another operation");
        return false;
    }

    // DIAGNOSTIC: Query multiple relevant properties
    LOG_INFO(LogContext::CAMERA, "DIAGNOSTIC: Querying camera properties...");

    // 1. Query Focus Mode
    {
        CrInt32u codes[] = { SDK::CrDevicePropertyCode::CrDeviceProperty_FocusMode };
        SDK::CrDeviceProperty* props = nullptr;
        int count = 0;
        auto result = SDK::GetSelectDeviceProperties(device_handle_, 1, codes, &props, &count);

        if (CR_SUCCEEDED(result) && props) {
            LOG_INFO(LogContext::CAMERA, "Focus Mode:");
            LOG_INFO(LogContext::CAMERA, "  - IsGetEnableCurrentValue: " +
                        std::string(props[0].IsGetEnableCurrentValue() ? "true" : "false"));
            LOG_INFO(LogContext::CAMERA, "  - IsSetEnableCurrentValue: " +
                        std::string(props[0].IsSetEnableCurrentValue() ? "true" : "false"));
            LOG_INFO(LogContext::CAMERA, "  - Current value: 0x" + toHexString(props[0].GetCurrentValue()));
            LOG_INFO(LogContext::CAMERA, "  - Value type: " + std::to_string(props[0].GetValueType()));

            // Log if it's manual focus (typically 0x0001)
            if (props[0].GetCurrentValue() == 0x0001) {
                LOG_INFO(LogContext::CAMERA, "  -> Camera IS in Manual Focus mode");
            } else {
                LOG_WARNING(LogContext::CAMERA, "  -> Camera is NOT in Manual Focus mode!");
            }

            SDK::ReleaseDeviceProperties(device_handle_, props);
        } else {
            LOG_ERROR(LogContext::CAMERA, "Failed to query FocusMode: 0x" + toHexString(result));
        }
    }

    // 2. Query Focus_Speed_Range
    {
        CrInt32u codes[] = { SDK::CrDevicePropertyCode::CrDeviceProperty_Focus_Speed_Range };
        SDK::CrDeviceProperty* props = nullptr;
        int count = 0;
        auto result = SDK::GetSelectDeviceProperties(device_handle_, 1, codes, &props, &count);

        if (CR_SUCCEEDED(result) && props) {
            LOG_INFO(LogContext::CAMERA, "Focus_Speed_Range:");
            LOG_INFO(LogContext::CAMERA, "  - IsGetEnableCurrentValue: " +
                        std::string(props[0].IsGetEnableCurrentValue() ? "true" : "false"));
            LOG_INFO(LogContext::CAMERA, "  - IsSetEnableCurrentValue: " +
                        std::string(props[0].IsSetEnableCurrentValue() ? "true" : "false"));

            if (props[0].IsGetEnableCurrentValue()) {
                auto values = props[0].GetCurrentValues();
                auto size = props[0].GetCurrentValuesSize();
                LOG_INFO(LogContext::CAMERA, "  - Values count: " + std::to_string(size));
                if (values && size >= 2) {
                    LOG_INFO(LogContext::CAMERA, "  - Min speed: " + std::to_string(static_cast<CrInt8>(values[0])));
                    LOG_INFO(LogContext::CAMERA, "  - Max speed: " + std::to_string(static_cast<CrInt8>(values[1])));
                }
            } else {
                LOG_WARNING(LogContext::CAMERA, "  -> Focus_Speed_Range is NOT readable!");
            }

            SDK::ReleaseDeviceProperties(device_handle_, props);
        } else {
            LOG_ERROR(LogContext::CAMERA, "Failed to query Focus_Speed_Range: 0x" + toHexString(result));
        }
    }

    // 3. Query FocalDistanceInMeter
    {
        CrInt32u codes[] = { SDK::CrDevicePropertyCode::CrDeviceProperty_FocalDistanceInMeter };
        SDK::CrDeviceProperty* props = nullptr;
        int count = 0;
        auto result = SDK::GetSelectDeviceProperties(device_handle_, 1, codes, &props, &count);

        if (CR_SUCCEEDED(result) && props) {
            LOG_INFO(LogContext::CAMERA, "FocalDistanceInMeter:");
            LOG_INFO(LogContext::CAMERA, "  - IsGetEnableCurrentValue: " +
                        std::string(props[0].IsGetEnableCurrentValue() ? "true" : "false"));
            LOG_INFO(LogContext::CAMERA, "  - IsSetEnableCurrentValue: " +
                        std::string(props[0].IsSetEnableCurrentValue() ? "true" : "false"));

            if (props[0].IsGetEnableCurrentValue()) {
                auto value = props[0].GetCurrentValue();
                LOG_INFO(LogContext::CAMERA, "  - Current value: " + std::to_string(value) + " mm");

                // Check for special values
                if (value == 0xFFFFFFFF) {
                    LOG_INFO(LogContext::CAMERA, "  - Distance: INFINITY");
                } else if (value == 0) {
                    LOG_WARNING(LogContext::CAMERA, "  - Distance: 0 (may indicate property not active)");
                }
            } else {
                LOG_ERROR(LogContext::CAMERA, "  -> FocalDistanceInMeter is NOT enabled/readable!");
                LOG_ERROR(LogContext::CAMERA, "     This is likely why Focus_Operation fails!");
            }

            SDK::ReleaseDeviceProperties(device_handle_, props);
        } else {
            LOG_ERROR(LogContext::CAMERA, "Failed to query FocalDistanceInMeter: 0x" + toHexString(result));
        }
    }

    // 4. Query Focus_Operation itself to see if it's settable
    {
        CrInt32u codes[] = { SDK::CrDevicePropertyCode::CrDeviceProperty_Focus_Operation };
        SDK::CrDeviceProperty* props = nullptr;
        int count = 0;
        auto result = SDK::GetSelectDeviceProperties(device_handle_, 1, codes, &props, &count);

        if (CR_SUCCEEDED(result) && props) {
            LOG_INFO(LogContext::CAMERA, "Focus_Operation:");
            LOG_INFO(LogContext::CAMERA, "  - IsGetEnableCurrentValue: " +
                        std::string(props[0].IsGetEnableCurrentValue() ? "true" : "false"));
            LOG_INFO(LogContext::CAMERA, "  - IsSetEnableCurrentValue: " +
                        std::string(props[0].IsSetEnableCurrentValue() ? "true" : "false"));

            if (!props[0].IsSetEnableCurrentValue()) {
                LOG_ERROR(LogContext::CAMERA, "  -> Focus_Operation is NOT settable!");
                LOG_ERROR(LogContext::CAMERA, "     Camera is in a state where focus control is disabled");
            }

            SDK::ReleaseDeviceProperties(device_handle_, props);
        } else {
            LOG_ERROR(LogContext::CAMERA, "Failed to query Focus_Operation: 0x" + toHexString(result));
        }
    }

    // 5. Query Live View Status (some cameras require live view for focus)
    {
        CrInt32u codes[] = { SDK::CrDevicePropertyCode::CrDeviceProperty_LiveView_Status };
        SDK::CrDeviceProperty* props = nullptr;
        int count = 0;
        auto result = SDK::GetSelectDeviceProperties(device_handle_, 1, codes, &props, &count);

        if (CR_SUCCEEDED(result) && props) {
            LOG_INFO(LogContext::CAMERA, "LiveView_Status:");
            auto value = props[0].GetCurrentValue();
            LOG_INFO(LogContext::CAMERA, "  - Current value: 0x" + toHexString(value));
            if (value == 0x01) {
                LOG_INFO(LogContext::CAMERA, "  -> Live View is ON");
            } else {
                LOG_INFO(LogContext::CAMERA, "  -> Live View is OFF (some cameras need it ON for focus)");
            }
            SDK::ReleaseDeviceProperties(device_handle_, props);
        }
    }

    LOG_INFO(LogContext::CAMERA, "DIAGNOSTIC: Property queries complete");
    LOG_INFO(LogContext::CAMERA, "----------------------------------------");

    // Calculate focus operation value
    CrInt8 focus_operation;
    if (action == "near") {
        focus_operation = -speed;
        LOG_INFO(LogContext::CAMERA, "Attempting NEAR focus, operation value: " + std::to_string(focus_operation));
    } else if (action == "far") {
        focus_operation = speed;
        LOG_INFO(LogContext::CAMERA, "Attempting FAR focus, operation value: " + std::to_string(focus_operation));
    } else if (action == "stop") {
        focus_operation = 0;
        LOG_INFO(LogContext::CAMERA, "Attempting STOP focus");
    } else {
        LOG_ERROR(LogContext::CAMERA, "Invalid action: " + action);
        return false;
    }

    // Try to set Focus_Operation
    LOG_INFO(LogContext::CAMERA, "Sending Focus_Operation command...");
    SDK::CrDeviceProperty prop;
    prop.SetCode(SDK::CrDevicePropertyCode::CrDeviceProperty_Focus_Operation);
    prop.SetCurrentValue(static_cast<CrInt64u>(focus_operation));
    prop.SetValueType(SDK::CrDataType_Int8);

    auto result = SDK::SetDeviceProperty(device_handle_, &prop);

    if (CR_FAILED(result)) {
        LOG_ERROR(LogContext::CAMERA, "Focus_Operation FAILED with error: 0x" + toHexString(result));

        // Decode specific error codes
        switch (result) {
            case 0x8402:
                LOG_ERROR(LogContext::CAMERA, "0x8402 = CrError_Api_InvalidCalled");
                LOG_ERROR(LogContext::CAMERA, "The API was called in an invalid state");
                LOG_ERROR(LogContext::CAMERA, "Check the diagnostic output above to identify the issue");
                break;
            case 0x8401:
                LOG_ERROR(LogContext::CAMERA, "0x8401 = CrError_Api_InvalidParam");
                LOG_ERROR(LogContext::CAMERA, "Invalid parameter passed to the API");
                break;
            case 0x8403:
                LOG_ERROR(LogContext::CAMERA, "0x8403 = CrError_Api_OperationDenied");
                LOG_ERROR(LogContext::CAMERA, "Operation denied by the camera");
                break;
            default:
                LOG_ERROR(LogContext::CAMERA, "Unknown error code");
        }

        LOG_INFO(LogContext::CAMERA, "=== FOCUS DEBUG END (FAILED) ===");
        return false;
    }

    LOG_INFO(LogContext::CAMERA, "Focus_Operation SUCCESS!");
    LOG_INFO(LogContext::CAMERA, "=== FOCUS DEBUG END (SUCCESS) ===");
    return true;
}