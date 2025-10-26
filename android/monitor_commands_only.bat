@echo off
echo ========================================
echo DPM Android COMMANDS Monitor
echo ========================================
echo.
echo Shows ONLY commands sent to Air-Side
echo (Filters out connection status noise)
echo.
echo Press Ctrl+C to stop monitoring
echo ========================================
echo.

REM Clear log first
adb -s 10.0.1.92:5555 logcat -c

REM Monitor commands only
adb -s 10.0.1.92:5555 logcat -v time NetworkClient:D CameraViewModel:D *:S | findstr /C:"Sending command" /C:"Setting camera property" /C:"response" /C:"ERROR"
