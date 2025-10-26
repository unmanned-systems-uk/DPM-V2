@echo off
echo ========================================
echo DPM Android DETAILED Connection Monitor
echo ========================================
echo.
echo Shows ALL network activity including:
echo   - Connection State Changes
echo   - Commands Sent (with JSON)
echo   - Camera Property Changes
echo   - Heartbeat Activity
echo   - Errors and Warnings
echo.
echo Press Ctrl+C to stop monitoring
echo ========================================
echo.

REM Clear log first
adb -s 10.0.1.92:5555 logcat -c

REM Monitor with detailed output
adb -s 10.0.1.92:5555 logcat -v time NetworkClient:D NetworkManager:D CameraViewModel:D *:S
