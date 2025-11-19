#!/usr/bin/env python3
"""
DPM Remote Control API - Comprehensive Test Suite
==================================================

Tests all 5 phases of the API with DPM_Management_System running.
"""

import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent))

from api import DPMController


def test_phase1_air_side():
    """Test Phase 1: Air-Side Basic Operations"""
    print("\n" + "=" * 80)
    print("PHASE 1: AIR-SIDE BASIC OPERATIONS")
    print("=" * 80)

    dpm = DPMController()
    results = []

    # Test 1: Connect to Air-Side
    print("\n[Test 1.1] Connecting to Air-Side...")
    result = dpm.air_side.connect(host='10.0.1.53', tcp_port=5000)
    success = result.success
    results.append(("Air-Side Connect", success))
    print(f"  {'✓ PASS' if success else '✗ FAIL'}: {result.data if success else result.error}")

    if success:
        # Test 2: Get Status
        print("\n[Test 1.2] Getting Air-Side status...")
        result = dpm.air_side.get_status()
        success = result.success
        results.append(("Air-Side Status", success))
        print(f"  {'✓ PASS' if success else '✗ FAIL'}: {result.data if success else result.error}")

        # Test 3: Send Command
        print("\n[Test 1.3] Sending camera.get_properties command...")
        result = dpm.air_side.send_command('camera.get_properties', {})
        success = result.success
        results.append(("Send Command", success))
        print(f"  {'✓ PASS' if success else '✗ FAIL'}")
        if success:
            print(f"  Response: {result.data.get('response', 'N/A')}")

        # Test 4: Disconnect
        print("\n[Test 1.4] Disconnecting from Air-Side...")
        result = dpm.air_side.disconnect()
        success = result.success
        results.append(("Air-Side Disconnect", success))
        print(f"  {'✓ PASS' if success else '✗ FAIL'}")

    return results


def test_phase3_ground_side():
    """Test Phase 3: Ground-Side Control"""
    print("\n" + "=" * 80)
    print("PHASE 3: GROUND-SIDE CONTROL")
    print("=" * 80)

    dpm = DPMController()
    results = []

    # Test 1: Connect to Ground-Side (expected to fail gracefully - H16 offline)
    print("\n[Test 3.1] Connecting to Ground-Side (H16 may be offline)...")
    result = dpm.ground_side.connect(host='10.0.1.92', port=5555)
    success = result.success
    results.append(("Ground-Side Connect", success))

    if success:
        print(f"  ✓ PASS: Connected to {result.data['host']}")

        # Test 2: Get Diagnostics
        print("\n[Test 3.2] Getting H16 diagnostics...")
        result = dpm.ground_side.get_diagnostics()
        success = result.success
        results.append(("H16 Diagnostics", success))
        print(f"  {'✓ PASS' if success else '✗ FAIL'}")
        if success:
            print(f"  Battery: {result.data.get('battery', 'N/A')}")
            print(f"  CPU: {result.data.get('cpu', 'N/A')}")

        # Disconnect
        dpm.ground_side.disconnect()
    else:
        print(f"  ⚠ EXPECTED: H16 offline - {result.error}")
        print("  ✓ PASS: Graceful failure handling")
        results.append(("Graceful Failure", True))

    return results


def test_phase4_systemtools():
    """Test Phase 4: SystemTools Operations"""
    print("\n" + "=" * 80)
    print("PHASE 4: SYSTEMTOOLS OPERATIONS")
    print("=" * 80)

    dpm = DPMController()
    results = []

    # Test 1: Query Logs
    print("\n[Test 4.1] Querying recent logs...")
    result = dpm.system.query_logs(limit=10)
    success = result.success
    results.append(("Query Logs", success))
    print(f"  {'✓ PASS' if success else '✗ FAIL'}")
    if success:
        print(f"  Found {result.data['count']} logs")

    # Test 2: Get System Status
    print("\n[Test 4.2] Getting SystemTools status...")
    result = dpm.system.get_system_status()
    success = result.success
    results.append(("System Status", success))
    print(f"  {'✓ PASS' if success else '✗ FAIL'}")
    if success:
        print(f"  Log queue size: {result.data.get('log_aggregator', {}).get('log_queue_size', 'N/A')}")

    # Test 3: Get Analytics
    print("\n[Test 4.3] Getting performance analytics...")
    result = dpm.system.get_analytics()
    success = result.success
    results.append(("Analytics", success))
    print(f"  {'✓ PASS' if success else '✗ FAIL'}")

    return results


def test_phase5_multi_domain():
    """Test Phase 5: Multi-Domain Coordination"""
    print("\n" + "=" * 80)
    print("PHASE 5: MULTI-DOMAIN COORDINATION")
    print("=" * 80)

    dpm = DPMController()
    results = []

    # Test 1: Health Check Workflow
    print("\n[Test 5.1] Running multi-domain health check...")
    result = dpm.multi_domain.run_health_check_workflow(include_ground_side=False)
    success = result.success
    results.append(("Health Check", success))
    print(f"  {'✓ PASS' if success else '✗ FAIL'}")

    if success:
        print(f"  Overall Health: {'✓ HEALTHY' if result.data['overall_healthy'] else '✗ UNHEALTHY'}")
        for domain, status in result.data['domains'].items():
            health = "✓" if status.get('healthy', False) else "✗"
            print(f"    {domain}: {health}")

    # Test 2: Integration Test
    print("\n[Test 5.2] Running integration test...")
    test_steps = [
        {'domain': 'air_side', 'operation': 'connect', 'params': {}, 'verify': False},
        {'domain': 'air_side', 'operation': 'get_status', 'params': {}, 'verify': False},
        {'domain': 'air_side', 'operation': 'disconnect', 'params': {}, 'verify': False}
    ]

    result = dpm.multi_domain.run_integration_test(
        test_name="api_test",
        test_steps=test_steps,
        verify_each_step=False
    )
    success = result.success
    results.append(("Integration Test", success))

    if success:
        passed = result.data['passed']
        total = result.data['total']
        print(f"  {'✓ PASS' if passed == total else '✗ FAIL'}: {passed}/{total} steps passed")
    else:
        print(f"  ✗ FAIL: {result.error}")

    return results


def test_phase2_extended_air_side():
    """Test Phase 2: Extended Air-Side Operations"""
    print("\n" + "=" * 80)
    print("PHASE 2: EXTENDED AIR-SIDE OPERATIONS")
    print("=" * 80)

    dpm = DPMController()
    results = []

    # Test 1: Docker Container Status
    print("\n[Test 2.1] Getting Docker container status...")
    result = dpm.air_side.manage_docker_container(action='status')
    success = result.success
    results.append(("Docker Status", success))
    print(f"  {'✓ PASS' if success else '✗ FAIL'}")
    if success:
        print(f"  Container: {result.data.get('container', 'N/A')}")
        print(f"  Status: {result.data.get('output', 'N/A')}")

    return results


def print_summary(all_results):
    """Print test summary"""
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    total_tests = sum(len(results) for results in all_results.values())
    total_passed = sum(
        sum(1 for _, success in results if success)
        for results in all_results.values()
    )

    print(f"\nOverall: {total_passed}/{total_tests} tests passed")
    print(f"Success Rate: {(total_passed/total_tests*100):.1f}%\n")

    for phase, results in all_results.items():
        print(f"\n{phase}:")
        for test_name, success in results:
            status = "✓ PASS" if success else "✗ FAIL"
            print(f"  {status}: {test_name}")

    print("\n" + "=" * 80)
    if total_passed == total_tests:
        print("✓ ALL TESTS PASSED")
    else:
        print(f"⚠ {total_tests - total_passed} TEST(S) FAILED")
    print("=" * 80)


def main():
    """Run all API tests"""
    print("\n" + "=" * 80)
    print("DPM REMOTE CONTROL API - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print("\nTesting all 5 phases with DPM_Management_System running...")

    all_results = {}

    try:
        # Phase 1: Air-Side Basic Operations
        all_results["Phase 1: Air-Side Basic"] = test_phase1_air_side()
        time.sleep(1)

        # Phase 4: SystemTools (test before Phase 3 to ensure logs are available)
        all_results["Phase 4: SystemTools"] = test_phase4_systemtools()
        time.sleep(1)

        # Phase 3: Ground-Side Control
        all_results["Phase 3: Ground-Side"] = test_phase3_ground_side()
        time.sleep(1)

        # Phase 5: Multi-Domain Coordination
        all_results["Phase 5: Multi-Domain"] = test_phase5_multi_domain()
        time.sleep(1)

        # Phase 2: Extended Air-Side
        all_results["Phase 2: Extended Air-Side"] = test_phase2_extended_air_side()

        # Print summary
        print_summary(all_results)

    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\n✗ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
