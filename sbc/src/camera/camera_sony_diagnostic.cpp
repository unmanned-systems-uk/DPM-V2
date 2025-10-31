// Diagnostic version of focus() method for camera_sony.cpp
// This version includes extensive logging to identify the exact issue

bool focus(const std::string& action, int speed = 3) override {
    Logger::info("=== FOCUS DEBUG START ===");
    Logger::info("Requested action: " + action + ", speed: " + std::to_string(speed));

    // Check connection
    if (!isConnected()) {
        Logger::error("Cannot focus: camera not connected");
        return false;
    }

    // Acquire lock
    std::unique_lock<std::mutex> lock(mutex_, std::try_to_lock);
    if (!lock.owns_lock()) {
        Logger::warning("Cannot focus: camera busy with another operation");
        return false;
    }

    // DIAGNOSTIC: Query multiple relevant properties
    Logger::info("DIAGNOSTIC: Querying camera properties...");

    // 1. Query Focus Mode
    {
        CrInt32u codes[] = { SDK::CrDevicePropertyCode::CrDeviceProperty_FocusMode };
        SDK::CrDeviceProperty* props = nullptr;
        int count = 0;
        auto result = SDK::GetSelectDeviceProperties(device_handle_, 1, codes, &props, &count);

        if (CR_SUCCEEDED(result) && props) {
            Logger::info("Focus Mode:");
            Logger::info("  - IsGetEnableCurrentValue: " +
                        std::string(props[0].IsGetEnableCurrentValue() ? "true" : "false"));
            Logger::info("  - IsSetEnableCurrentValue: " +
                        std::string(props[0].IsSetEnableCurrentValue() ? "true" : "false"));
            Logger::info("  - Current value: 0x" + toHexString(props[0].GetCurrentValue()));
            Logger::info("  - Value type: " + std::to_string(props[0].GetValueType()));

            // Log if it's manual focus (typically 0x0001)
            if (props[0].GetCurrentValue() == 0x0001) {
                Logger::info("  -> Camera IS in Manual Focus mode");
            } else {
                Logger::warning("  -> Camera is NOT in Manual Focus mode!");
            }

            SDK::ReleaseDeviceProperties(device_handle_, props);
        } else {
            Logger::error("Failed to query FocusMode: 0x" + toHexString(result));
        }
    }

    // 2. Query Focus_Speed_Range
    {
        CrInt32u codes[] = { SDK::CrDevicePropertyCode::CrDeviceProperty_Focus_Speed_Range };
        SDK::CrDeviceProperty* props = nullptr;
        int count = 0;
        auto result = SDK::GetSelectDeviceProperties(device_handle_, 1, codes, &props, &count);

        if (CR_SUCCEEDED(result) && props) {
            Logger::info("Focus_Speed_Range:");
            Logger::info("  - IsGetEnableCurrentValue: " +
                        std::string(props[0].IsGetEnableCurrentValue() ? "true" : "false"));
            Logger::info("  - IsSetEnableCurrentValue: " +
                        std::string(props[0].IsSetEnableCurrentValue() ? "true" : "false"));

            if (props[0].IsGetEnableCurrentValue()) {
                auto values = props[0].GetCurrentValues();
                auto size = props[0].GetCurrentValuesSize();
                Logger::info("  - Values count: " + std::to_string(size));
                if (values && size >= 2) {
                    Logger::info("  - Min speed: " + std::to_string(static_cast<CrInt8>(values[0])));
                    Logger::info("  - Max speed: " + std::to_string(static_cast<CrInt8>(values[1])));
                }
            } else {
                Logger::warning("  -> Focus_Speed_Range is NOT readable!");
            }

            SDK::ReleaseDeviceProperties(device_handle_, props);
        } else {
            Logger::error("Failed to query Focus_Speed_Range: 0x" + toHexString(result));
        }
    }

    // 3. Query FocalDistanceInMeter
    {
        CrInt32u codes[] = { SDK::CrDevicePropertyCode::CrDeviceProperty_FocalDistanceInMeter };
        SDK::CrDeviceProperty* props = nullptr;
        int count = 0;
        auto result = SDK::GetSelectDeviceProperties(device_handle_, 1, codes, &props, &count);

        if (CR_SUCCEEDED(result) && props) {
            Logger::info("FocalDistanceInMeter:");
            Logger::info("  - IsGetEnableCurrentValue: " +
                        std::string(props[0].IsGetEnableCurrentValue() ? "true" : "false"));
            Logger::info("  - IsSetEnableCurrentValue: " +
                        std::string(props[0].IsSetEnableCurrentValue() ? "true" : "false"));

            if (props[0].IsGetEnableCurrentValue()) {
                auto value = props[0].GetCurrentValue();
                Logger::info("  - Current value: " + std::to_string(value) + " mm");

                // Check for special values
                if (value == 0xFFFFFFFF) {
                    Logger::info("  - Distance: INFINITY");
                } else if (value == 0) {
                    Logger::warning("  - Distance: 0 (may indicate property not active)");
                }
            } else {
                Logger::error("  -> FocalDistanceInMeter is NOT enabled/readable!");
                Logger::error("     This is likely why Focus_Operation fails!");
            }

            SDK::ReleaseDeviceProperties(device_handle_, props);
        } else {
            Logger::error("Failed to query FocalDistanceInMeter: 0x" + toHexString(result));
        }
    }

    // 4. Query Focus_Operation itself to see if it's settable
    {
        CrInt32u codes[] = { SDK::CrDevicePropertyCode::CrDeviceProperty_Focus_Operation };
        SDK::CrDeviceProperty* props = nullptr;
        int count = 0;
        auto result = SDK::GetSelectDeviceProperties(device_handle_, 1, codes, &props, &count);

        if (CR_SUCCEEDED(result) && props) {
            Logger::info("Focus_Operation:");
            Logger::info("  - IsGetEnableCurrentValue: " +
                        std::string(props[0].IsGetEnableCurrentValue() ? "true" : "false"));
            Logger::info("  - IsSetEnableCurrentValue: " +
                        std::string(props[0].IsSetEnableCurrentValue() ? "true" : "false"));

            if (!props[0].IsSetEnableCurrentValue()) {
                Logger::error("  -> Focus_Operation is NOT settable!");
                Logger::error("     Camera is in a state where focus control is disabled");
            }

            SDK::ReleaseDeviceProperties(device_handle_, props);
        } else {
            Logger::error("Failed to query Focus_Operation: 0x" + toHexString(result));
        }
    }

    // 5. Query Live View Status (some cameras require live view for focus)
    {
        CrInt32u codes[] = { SDK::CrDevicePropertyCode::CrDeviceProperty_LiveView_Status };
        SDK::CrDeviceProperty* props = nullptr;
        int count = 0;
        auto result = SDK::GetSelectDeviceProperties(device_handle_, 1, codes, &props, &count);

        if (CR_SUCCEEDED(result) && props) {
            Logger::info("LiveView_Status:");
            auto value = props[0].GetCurrentValue();
            Logger::info("  - Current value: 0x" + toHexString(value));
            if (value == 0x01) {
                Logger::info("  -> Live View is ON");
            } else {
                Logger::info("  -> Live View is OFF (some cameras need it ON for focus)");
            }
            SDK::ReleaseDeviceProperties(device_handle_, props);
        }
    }

    Logger::info("DIAGNOSTIC: Property queries complete");
    Logger::info("----------------------------------------");

    // Calculate focus operation value
    CrInt8 focus_operation;
    if (action == "near") {
        focus_operation = -speed;
        Logger::info("Attempting NEAR focus, operation value: " + std::to_string(focus_operation));
    } else if (action == "far") {
        focus_operation = speed;
        Logger::info("Attempting FAR focus, operation value: " + std::to_string(focus_operation));
    } else if (action == "stop") {
        focus_operation = 0;
        Logger::info("Attempting STOP focus");
    } else {
        Logger::error("Invalid action: " + action);
        return false;
    }

    // Try to set Focus_Operation
    Logger::info("Sending Focus_Operation command...");
    SDK::CrDeviceProperty prop;
    prop.SetCode(SDK::CrDevicePropertyCode::CrDeviceProperty_Focus_Operation);
    prop.SetCurrentValue(static_cast<CrInt64u>(focus_operation));
    prop.SetValueType(SDK::CrDataType_Int8);

    auto result = SDK::SetDeviceProperty(device_handle_, &prop);

    if (CR_FAILED(result)) {
        Logger::error("Focus_Operation FAILED with error: 0x" + toHexString(result));

        // Decode specific error codes
        switch (result) {
            case 0x8402:
                Logger::error("0x8402 = CrError_Api_InvalidCalled");
                Logger::error("The API was called in an invalid state");
                Logger::error("Check the diagnostic output above to identify the issue");
                break;
            case 0x8401:
                Logger::error("0x8401 = CrError_Api_InvalidParam");
                Logger::error("Invalid parameter passed to the API");
                break;
            case 0x8403:
                Logger::error("0x8403 = CrError_Api_OperationDenied");
                Logger::error("Operation denied by the camera");
                break;
            default:
                Logger::error("Unknown error code");
        }

        Logger::info("=== FOCUS DEBUG END (FAILED) ===");
        return false;
    }

    Logger::info("Focus_Operation SUCCESS!");
    Logger::info("=== FOCUS DEBUG END (SUCCESS) ===");
    return true;
}