#!/usr/bin/env python3
"""
DPM Remote Control API - Usage Examples
========================================

Demonstrates how to use the DPM Remote Control API for automation,
testing, and remote diagnostics.

This enables:
- PM automation for multi-domain testing
- Automated integration test suites
- Remote diagnostics and control
- CI/CD integration
"""

import sys
import time
from pathlib import Path

# Add SystemTools to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api import DPMController


def example_basic_usage():
    """Basic API usage - connect, send command, disconnect"""
    print("=" * 60)
    print("Example 1: Basic Usage")
    print("=" * 60)

    # Create controller
    dpm = DPMController()

    # Connect to Air-Side
    print("\n1. Connecting to Air-Side...")
    result = dpm.air_side.connect(host='10.0.1.53')

    if result.success:
        print(f"   ✓ Connected: {result.data}")
    else:
        print(f"   ✗ Connection failed: {result.error}")
        return

    # Get status
    print("\n2. Getting Air-Side status...")
    status = dpm.air_side.get_status()

    if status.success:
        print(f"   ✓ Status received: {status.data}")
    else:
        print(f"   ✗ Failed to get status: {status.error}")

    # Send camera command
    print("\n3. Sending camera command...")
    cmd_result = dpm.air_side.send_command(
        'camera.get_properties',
        {}
    )

    if cmd_result.success:
        print(f"   ✓ Command sent: {cmd_result.data}")
    else:
        print(f"   ✗ Command failed: {cmd_result.error}")

    # Disconnect
    print("\n4. Disconnecting...")
    disconnect_result = dpm.air_side.disconnect()
    print(f"   ✓ Disconnected: {disconnect_result.data}")


def example_context_manager():
    """Using context manager for automatic cleanup"""
    print("\n" + "=" * 60)
    print("Example 2: Context Manager (Auto-Cleanup)")
    print("=" * 60)

    with DPMController() as dpm:
        print("\n1. Connecting...")
        result = dpm.air_side.connect()

        if result.success:
            print(f"   ✓ Connected")

            # Perform operations
            print("\n2. Sending test command...")
            cmd = dpm.air_side.send_command('camera.get_properties', {})
            print(f"   Command result: {cmd.success}")

        # Automatic disconnect on exit

    print("\n   ✓ Automatically disconnected (context manager)")


def example_configuration_management():
    """Configuration management example"""
    print("\n" + "=" * 60)
    print("Example 3: Configuration Management")
    print("=" * 60)

    dpm = DPMController()

    print("\n1. Connecting...")
    if not dpm.air_side.connect().success:
        print("   ✗ Failed to connect")
        return

    # Get configuration
    print("\n2. Getting configuration...")
    config = dpm.air_side.get_configuration()
    if config.success:
        print(f"   ✓ Config: {config.data}")

    # Set configuration
    print("\n3. Setting configuration value...")
    result = dpm.air_side.set_configuration('log_level', 'DEBUG')
    if result.success:
        print(f"   ✓ Config updated: {result.data}")
    else:
        print(f"   ✗ Failed: {result.error}")

    dpm.air_side.disconnect()


def example_ssh_commands():
    """SSH command execution example"""
    print("\n" + "=" * 60)
    print("Example 4: SSH Command Execution")
    print("=" * 60)

    dpm = DPMController()

    print("\n1. Connecting via SSH...")
    # Note: SSH requires credentials - would need to be configured
    print("   (Skipping SSH example - requires credentials)")

    # Example code (when credentials available):
    # result = dpm.air_side.execute_ssh_command('uptime')
    # if result.success:
    #     print(f"   Uptime: {result.data['stdout']}")


def example_automated_test():
    """Example automated integration test"""
    print("\n" + "=" * 60)
    print("Example 5: Automated Integration Test")
    print("=" * 60)

    test_results = []

    with DPMController() as dpm:
        # Test 1: Connection
        print("\nTest 1: Air-Side Connection")
        result = dpm.air_side.connect()
        test_results.append(("Connection", result.success))
        print(f"   {'✓ PASS' if result.success else '✗ FAIL'}")

        if not result.success:
            return

        # Test 2: Status Query
        print("\nTest 2: Status Query")
        result = dpm.air_side.get_status()
        test_results.append(("Status Query", result.success))
        print(f"   {'✓ PASS' if result.success else '✗ FAIL'}")

        # Test 3: Command Execution
        print("\nTest 3: Command Execution")
        result = dpm.air_side.send_command('camera.get_properties', {})
        test_results.append(("Command Execution", result.success))
        print(f"   {'✓ PASS' if result.success else '✗ FAIL'}")

        # Test 4: Configuration Management
        print("\nTest 4: Configuration Management")
        result = dpm.air_side.get_configuration()
        test_results.append(("Configuration", result.success))
        print(f"   {'✓ PASS' if result.success else '✗ FAIL'}")

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(1 for _, success in test_results if success)
    total = len(test_results)
    print(f"Passed: {passed}/{total}")

    for test_name, success in test_results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"  {status}: {test_name}")


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("DPM Remote Control API - Examples")
    print("=" * 60)
    print("\nThese examples demonstrate programmatic control of DPM system")
    print("for automation, testing, and remote diagnostics.\n")

    try:
        # Run examples
        example_basic_usage()
        example_context_manager()
        example_configuration_management()
        example_ssh_commands()
        example_automated_test()

        print("\n" + "=" * 60)
        print("Examples Complete")
        print("=" * 60)
        print("\nFor PM automation, use these patterns to:")
        print("- Orchestrate multi-domain testing")
        print("- Run automated integration test suites")
        print("- Perform remote diagnostics")
        print("- Monitor system health")

    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
