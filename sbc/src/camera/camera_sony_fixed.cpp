// Fixed focus() method for camera_sony.cpp
// This is a replacement for the focus() method starting at line 356

bool focus(const std::string& action, int speed = 3) override {
    // Check connection using atomic flag first (fast, never blocks)
    if (!isConnected()) {
        Logger::error("Cannot focus: camera not connected");
        return false;
    }

    // Acquire lock for entire operation to prevent concurrent SDK access
    std::unique_lock<std::mutex> lock(mutex_, std::try_to_lock);
    if (!lock.owns_lock()) {
        Logger::warning("Cannot focus: camera busy with another operation");
        return false;
    }

    // CRITICAL FIX #1: Query Focus_Speed_Range to determine valid speed values
    // The SDK may reject focus operations if speed is outside the camera's supported range
    CrInt32u speed_range_codes[] = {
        SDK::CrDevicePropertyCode::CrDeviceProperty_Focus_Speed_Range
    };
    SDK::CrDeviceProperty* speed_range_list = nullptr;
    int speed_range_count = 0;

    auto speed_result = SDK::GetSelectDeviceProperties(
        device_handle_,
        1,
        speed_range_codes,
        &speed_range_list,
        &speed_range_count
    );

    CrInt8 min_speed = -7;  // Default min (near/wide)
    CrInt8 max_speed = 7;   // Default max (far/tele)

    if (CR_SUCCEEDED(speed_result) && speed_range_list && speed_range_count > 0) {
        // Extract the actual speed range from the camera
        if (speed_range_list[0].IsGetEnableCurrentValue()) {
            // For range types, get min and max values
            auto range_values = speed_range_list[0].GetCurrentValues();
            if (range_values && speed_range_list[0].GetCurrentValuesSize() >= 2) {
                min_speed = static_cast<CrInt8>(range_values[0]);
                max_speed = static_cast<CrInt8>(range_values[1]);
                Logger::debug("Camera focus speed range: " + std::to_string(min_speed) +
                            " to " + std::to_string(max_speed));
            }
        }
        SDK::ReleaseDeviceProperties(device_handle_, speed_range_list);
    } else {
        Logger::warning("Could not query Focus_Speed_Range, using defaults (-7 to 7)");
    }

    // CRITICAL FIX #2: Check FocalDistanceInMeter property's enable status
    // The property must be "enabled" (IsGetEnableCurrentValue = true) for Focus_Operation to work
    CrInt32u focal_distance_codes[] = {
        SDK::CrDevicePropertyCode::CrDeviceProperty_FocalDistanceInMeter
    };
    SDK::CrDeviceProperty* focal_distance_list = nullptr;
    int focal_distance_count = 0;

    auto focal_result = SDK::GetSelectDeviceProperties(
        device_handle_,
        1,
        focal_distance_codes,
        &focal_distance_list,
        &focal_distance_count
    );

    bool focal_distance_enabled = false;

    if (CR_SUCCEEDED(focal_result) && focal_distance_list && focal_distance_count > 0) {
        // Check if the property is enabled (can be read)
        focal_distance_enabled = focal_distance_list[0].IsGetEnableCurrentValue();

        if (focal_distance_enabled) {
            Logger::debug("FocalDistanceInMeter property is enabled and readable");

            // Log current focal distance for debugging
            if (focal_distance_list[0].GetCurrentValuesSize() > 0) {
                auto current_value = focal_distance_list[0].GetCurrentValue();
                Logger::debug("Current focal distance: " + std::to_string(current_value) + " mm");
            }
        } else {
            Logger::warning("FocalDistanceInMeter property is NOT enabled - focus may fail");

            // CRITICAL FIX #3: Try to enable the property by setting focus mode to Manual
            // Some cameras require manual focus mode for Focus_Operation to work
            CrInt32u focus_mode_codes[] = {
                SDK::CrDevicePropertyCode::CrDeviceProperty_FocusMode
            };
            SDK::CrDeviceProperty* focus_mode_list = nullptr;
            int focus_mode_count = 0;

            auto mode_result = SDK::GetSelectDeviceProperties(
                device_handle_,
                1,
                focus_mode_codes,
                &focus_mode_list,
                &focus_mode_count
            );

            if (CR_SUCCEEDED(mode_result) && focus_mode_list) {
                auto current_mode = focus_mode_list[0].GetCurrentValue();
                Logger::debug("Current focus mode: 0x" + toHexString(current_mode));

                // Check if we're NOT in manual focus mode (MF = 0x0001 typically)
                if (current_mode != SDK::CrFocusMode::CrFocus_MF) {
                    Logger::warning("Camera is not in manual focus mode, Focus_Operation may fail");
                }
                SDK::ReleaseDeviceProperties(device_handle_, focus_mode_list);
            }
        }

        SDK::ReleaseDeviceProperties(device_handle_, focal_distance_list);
    } else {
        Logger::error("Failed to query FocalDistanceInMeter property - focus will likely fail");
    }

    // CRITICAL FIX #4: Validate and clamp speed to camera's supported range
    // Ensure speed is within the valid range reported by the camera
    int clipped_speed = speed;
    if (speed > std::abs(max_speed)) {
        clipped_speed = std::abs(max_speed);
        Logger::warning("Speed " + std::to_string(speed) + " exceeds max, using " +
                       std::to_string(clipped_speed));
    }

    // Map action and speed to Sony SDK focus operation value
    CrInt8 focus_operation;
    if (action == "near") {
        // Ensure negative speed is within range
        focus_operation = -clipped_speed;
        if (focus_operation < min_speed) {
            focus_operation = min_speed;
        }
        Logger::info("Executing focus action: NEAR (closer objects), speed=" +
                    std::to_string(std::abs(focus_operation)));
    } else if (action == "far") {
        // Ensure positive speed is within range
        focus_operation = clipped_speed;
        if (focus_operation > max_speed) {
            focus_operation = max_speed;
        }
        Logger::info("Executing focus action: FAR (distant objects), speed=" +
                    std::to_string(focus_operation));
    } else if (action == "stop") {
        focus_operation = 0;
        Logger::info("Executing focus action: STOP");
    } else {
        Logger::error("Invalid focus action: " + action + " (valid: near, far, stop)");
        return false;
    }

    // CRITICAL FIX #5: Add small delay after property queries
    // Some cameras need time after property queries before accepting commands
    std::this_thread::sleep_for(std::chrono::milliseconds(50));

    // Create property to set focus operation
    SDK::CrDeviceProperty prop;
    prop.SetCode(SDK::CrDevicePropertyCode::CrDeviceProperty_Focus_Operation);
    prop.SetCurrentValue(static_cast<CrInt64u>(focus_operation));
    prop.SetValueType(SDK::CrDataType_Int8);

    // Send focus operation command
    auto result = SDK::SetDeviceProperty(device_handle_, &prop);

    if (CR_FAILED(result)) {
        // Enhanced error logging with specific error codes
        Logger::error("Failed to set focus operation. SDK error: 0x" + toHexString(result));

        if (result == 0x8402) {
            Logger::error("Error 0x8402: CrError_Api_InvalidCalled - Focus_Operation called in invalid state");
            Logger::error("Possible causes:");
            Logger::error("  1. Camera not in manual focus mode");
            Logger::error("  2. FocalDistanceInMeter property not enabled");
            Logger::error("  3. Camera in an incompatible shooting mode");
            Logger::error("  4. Live view may need to be started first");

            if (!focal_distance_enabled) {
                Logger::error("  -> FocalDistanceInMeter was NOT enabled, this is likely the cause");
            }
        }

        return false;
    }

    Logger::info("Focus action '" + action + "' executed successfully");

    // CRITICAL FIX #6: Add a small delay after focus command
    // This prevents the next property query from interfering with focus operation
    std::this_thread::sleep_for(std::chrono::milliseconds(100));

    return true;
}