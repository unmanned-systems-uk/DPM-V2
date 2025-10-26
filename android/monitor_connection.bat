@echo off
echo ========================================
echo DPM Android Connection Monitor
echo ========================================
echo.
echo Monitoring:
echo   - Connection Status
echo   - Commands Sent to Air-Side
echo   - Heartbeats
echo   - Errors
echo.
echo Press Ctrl+C to stop monitoring
echo ========================================
echo.

adb -s 10.0.1.92:5555 logcat -v time NetworkClient:I NetworkManager:I CameraViewModel:I *:S
