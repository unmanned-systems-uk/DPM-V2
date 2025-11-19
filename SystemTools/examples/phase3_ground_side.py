#!/usr/bin/env python3
"""
Phase 3: Ground-Side Operations - Examples
===========================================

Demonstrates Ground-Side control operations for Android H16:
- ADB connection management
- H16 diagnostics (battery, CPU, memory, temperature)
- App lifecycle control (start/stop/install)
- Input simulation (tap, swipe, key press)
- Screen capture
- Logcat streaming
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from api import DPMController


def example_connection():
    """Example: Connect to Ground-Side (Android H16)"""
    print("=" * 60)
    print("Example 1: Ground-Side Connection")
    print("=" * 60)

    dpm = DPMController()

    print("\n1. Connecting to Ground-Side via ADB...")
    result = dpm.ground_side.connect(host='10.0.1.92', port=5555)

    if result.success:
        print(f"   ✓ Connected to {result.data['host']}:{result.data['port']}")
        print(f"   ADB Status: {result.data['adb_connected']}")
    else:
        print(f"   ✗ Connection failed: {result.error}")

    print("\n2. Checking connection status...")
    if dpm.ground_side.is_connected():
        print("   ✓ Ground-Side is connected")
    else:
        print("   ✗ Ground-Side is NOT connected")

    print("\n3. Disconnecting...")
    result = dpm.ground_side.disconnect()
    if result.success:
        print("   ✓ Disconnected successfully")


def example_diagnostics():
    """Example: Get H16 diagnostics"""
    print("\n" + "=" * 60)
    print("Example 2: H16 Diagnostics")
    print("=" * 60)

    dpm = DPMController()

    print("\n1. Connecting to Ground-Side...")
    connect_result = dpm.ground_side.connect()

    if not connect_result.success:
        print(f"   ✗ Failed to connect: {connect_result.error}")
        return

    print("   ✓ Connected")

    print("\n2. Retrieving H16 diagnostics...")
    result = dpm.ground_side.get_diagnostics()

    if result.success:
        print("   ✓ Diagnostics retrieved:")
        for key, value in result.data.items():
            print(f"     {key}: {value}")
    else:
        print(f"   ✗ Failed to get diagnostics: {result.error}")

    dpm.ground_side.disconnect()


def example_adb_commands():
    """Example: Execute ADB shell commands"""
    print("\n" + "=" * 60)
    print("Example 3: Execute ADB Commands")
    print("=" * 60)

    dpm = DPMController()

    print("\n1. Connecting to Ground-Side...")
    dpm.ground_side.connect()

    print("\n2. Getting Android version...")
    result = dpm.ground_side.execute_adb_command("getprop ro.build.version.release")

    if result.success:
        print(f"   ✓ Android Version: {result.data['output'].strip()}")
    else:
        print(f"   ✗ Command failed: {result.error}")

    print("\n3. Getting device model...")
    result = dpm.ground_side.execute_adb_command("getprop ro.product.model")

    if result.success:
        print(f"   ✓ Device Model: {result.data['output'].strip()}")

    print("\n4. Listing running apps...")
    result = dpm.ground_side.execute_adb_command("pm list packages | grep dpm")

    if result.success:
        packages = result.data['output'].strip().split('\n')
        print(f"   ✓ Found {len(packages)} DPM packages:")
        for pkg in packages:
            print(f"     {pkg}")

    dpm.ground_side.disconnect()


def example_app_control():
    """Example: Control Android app lifecycle"""
    print("\n" + "=" * 60)
    print("Example 4: App Lifecycle Control")
    print("=" * 60)

    dpm = DPMController()

    print("\n1. Connecting to Ground-Side...")
    dpm.ground_side.connect()

    app_package = 'uk.unmannedsystems.dpm_android'

    print(f"\n2. Starting app: {app_package}...")
    result = dpm.ground_side.start_app(app_package)

    if result.success:
        print(f"   ✓ App started")
        print(f"   Output: {result.data.get('output', 'N/A')}")
    else:
        print(f"   ✗ Failed to start app: {result.error}")

    print("\n3. Waiting for app to initialize...")
    import time
    time.sleep(2)

    print(f"\n4. Stopping app: {app_package}...")
    result = dpm.ground_side.stop_app(app_package)

    if result.success:
        print("   ✓ App stopped")
    else:
        print(f"   ✗ Failed to stop app: {result.error}")

    dpm.ground_side.disconnect()


def example_input_simulation():
    """Example: Simulate user input"""
    print("\n" + "=" * 60)
    print("Example 5: Input Simulation")
    print("=" * 60)

    dpm = DPMController()

    print("\n1. Connecting to Ground-Side...")
    dpm.ground_side.connect()

    print("\n2. Simulating screen tap at (500, 500)...")
    result = dpm.ground_side.tap(500, 500)

    if result.success:
        print("   ✓ Tap executed")
    else:
        print(f"   ✗ Tap failed: {result.error}")

    print("\n3. Simulating swipe gesture (top to bottom)...")
    result = dpm.ground_side.swipe(540, 200, 540, 1800, duration_ms=500)

    if result.success:
        print("   ✓ Swipe executed")
    else:
        print(f"   ✗ Swipe failed: {result.error}")

    print("\n4. Pressing BACK button (keycode 4)...")
    result = dpm.ground_side.press_key(4)

    if result.success:
        print("   ✓ Key press executed")
    else:
        print(f"   ✗ Key press failed: {result.error}")

    print("\n5. Pressing HOME button (keycode 3)...")
    result = dpm.ground_side.press_key(3)

    if result.success:
        print("   ✓ HOME button pressed")

    dpm.ground_side.disconnect()


def example_screen_capture():
    """Example: Capture screenshot from H16"""
    print("\n" + "=" * 60)
    print("Example 6: Screen Capture")
    print("=" * 60)

    dpm = DPMController()

    print("\n1. Connecting to Ground-Side...")
    dpm.ground_side.connect()

    print("\n2. Capturing screenshot...")
    result = dpm.ground_side.get_screen_capture('/tmp/h16_screenshot.png')

    if result.success:
        print(f"   ✓ Screenshot captured")
        print(f"   Remote path: {result.data['remote_path']}")
        print(f"   Local path: {result.data['local_path']}")
        print(f"   Note: {result.data['note']}")
    else:
        print(f"   ✗ Capture failed: {result.error}")

    dpm.ground_side.disconnect()


def example_logcat():
    """Example: Logcat operations"""
    print("\n" + "=" * 60)
    print("Example 7: Logcat Streaming")
    print("=" * 60)

    dpm = DPMController()

    print("\n1. Connecting to Ground-Side...")
    dpm.ground_side.connect()

    print("\n2. Clearing logcat buffer...")
    result = dpm.ground_side.clear_logcat()

    if result.success:
        print("   ✓ Logcat buffer cleared")
    else:
        print(f"   ✗ Clear failed: {result.error}")

    print("\n3. Starting logcat stream (filtered to 'DPM' tag)...")
    result = dpm.ground_side.start_logcat(filter_tag='DPM')

    if result.success:
        print(f"   ✓ Logcat started")
        print(f"   Command: {result.data['logcat_command']}")
        print(f"   Filter: {result.data['filter_tag']}")
        print(f"   Running: {result.data['running']}")
    else:
        print(f"   ✗ Start failed: {result.error}")

    print("\n4. Stopping logcat...")
    result = dpm.ground_side.stop_logcat()

    if result.success:
        print("   ✓ Logcat stopped")
    else:
        print(f"   ✗ Stop failed: {result.error}")

    dpm.ground_side.disconnect()


def example_automated_test():
    """Example: Automated testing workflow"""
    print("\n" + "=" * 60)
    print("Example 8: Automated Testing Workflow")
    print("=" * 60)

    dpm = DPMController()

    print("\n1. Connecting to Ground-Side...")
    if not dpm.ground_side.connect().success:
        print("   ✗ Connection failed - aborting test")
        return

    print("   ✓ Connected")

    # Test sequence
    test_results = []

    # Test 1: Check H16 health
    print("\n2. Test: Check H16 health...")
    result = dpm.ground_side.get_diagnostics()
    test_results.append(('H16 Diagnostics', result.success))
    print(f"   {'✓' if result.success else '✗'} Diagnostics: {result.success}")

    # Test 2: Start app
    print("\n3. Test: Launch DPM app...")
    result = dpm.ground_side.start_app('uk.unmannedsystems.dpm_android')
    test_results.append(('App Launch', result.success))
    print(f"   {'✓' if result.success else '✗'} App launch: {result.success}")

    # Test 3: Simulate user interaction
    print("\n4. Test: Simulate user tap...")
    result = dpm.ground_side.tap(540, 960)
    test_results.append(('User Tap', result.success))
    print(f"   {'✓' if result.success else '✗'} User interaction: {result.success}")

    # Test 4: Capture evidence
    print("\n5. Test: Capture screenshot...")
    result = dpm.ground_side.get_screen_capture('/tmp/test_evidence.png')
    test_results.append(('Screenshot', result.success))
    print(f"   {'✓' if result.success else '✗'} Screenshot: {result.success}")

    # Test 5: Stop app
    print("\n6. Test: Stop app...")
    result = dpm.ground_side.stop_app('uk.unmannedsystems.dpm_android')
    test_results.append(('App Stop', result.success))
    print(f"   {'✓' if result.success else '✗'} App stop: {result.success}")

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(1 for _, success in test_results if success)
    total = len(test_results)
    print(f"\nPassed: {passed}/{total}")
    for test_name, success in test_results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"  {status}: {test_name}")

    dpm.ground_side.disconnect()


def main():
    """Run all Phase 3 examples"""
    print("\n" + "=" * 60)
    print("Phase 3: Ground-Side Operations")
    print("=" * 60)
    print("\nDemonstrates Ground-Side control via ADB for Android H16\n")

    try:
        example_connection()
        example_diagnostics()
        example_adb_commands()
        example_app_control()
        example_input_simulation()
        example_screen_capture()
        example_logcat()
        example_automated_test()

        print("\n" + "=" * 60)
        print("Phase 3 Examples Complete")
        print("=" * 60)
        print("\nPhase 3 provides:")
        print("- ✓ ADB connection management")
        print("- ✓ H16 diagnostics (battery, CPU, memory, temp)")
        print("- ✓ App lifecycle control")
        print("- ✓ Input simulation (tap, swipe, keys)")
        print("- ✓ Screen capture")
        print("- ✓ Logcat streaming")
        print("- ✓ Automated testing workflows")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
