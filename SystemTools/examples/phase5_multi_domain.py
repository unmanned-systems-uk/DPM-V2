#!/usr/bin/env python3
"""
Phase 5: Multi-Domain Coordination - Examples
==============================================

Demonstrates multi-domain orchestration workflows:
- End-to-end capture workflow
- Cross-domain health checks
- Integration test framework
- Synchronized Air-Ground operations
- Test result export
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from api import DPMController


def example_capture_workflow():
    """Example: End-to-end capture workflow with verification"""
    print("=" * 60)
    print("Example 1: End-to-End Capture Workflow")
    print("=" * 60)

    dpm = DPMController()

    print("\n1. Running complete capture workflow...")
    print("   - Connect to Air-Side")
    print("   - Send camera.capture command")
    print("   - Verify command in logs")
    print("   - Verify Ground-Side status (optional)")
    print("   - Capture H16 screenshot (optional)")

    result = dpm.multi_domain.run_capture_workflow(
        quality=95,
        verify_logs=True,
        verify_ground_side=False,  # Set to True if H16 connected
        capture_screenshot=False    # Set to True if H16 connected
    )

    if result.success:
        print(f"\n   ✓ Workflow completed successfully")
        print(f"   Steps completed: {result.data['steps_completed']}")
        print(f"   Duration: {result.data['total_duration_ms']}ms")
        print(f"   Overall success: {result.data['overall_success']}")

        print("\n   Step Details:")
        for step in result.data['steps']:
            status = "✓" if step['success'] else "✗"
            print(f"     {status} {step['step']}: {step.get('duration_ms', 0)}ms")
    else:
        print(f"\n   ✗ Workflow failed: {result.error}")


def example_health_check():
    """Example: Comprehensive health check across all domains"""
    print("\n" + "=" * 60)
    print("Example 2: Multi-Domain Health Check")
    print("=" * 60)

    dpm = DPMController()

    print("\n1. Running health check across all domains...")
    result = dpm.multi_domain.run_health_check_workflow(
        include_ground_side=False  # Set to True if H16 connected
    )

    if result.success:
        print(f"\n   Overall Health: {'✓ HEALTHY' if result.data['overall_healthy'] else '✗ UNHEALTHY'}")

        print("\n   Domain Status:")
        for domain, status in result.data['domains'].items():
            health = "✓ HEALTHY" if status.get('healthy', False) else "✗ UNHEALTHY"
            print(f"     {domain}: {health}")

            if status.get('connected') is not None:
                print(f"       Connected: {status['connected']}")

            if status.get('error'):
                print(f"       Error: {status['error']}")
    else:
        print(f"\n   ✗ Health check failed: {result.error}")


def example_integration_test():
    """Example: Custom integration test framework"""
    print("\n" + "=" * 60)
    print("Example 3: Integration Test Framework")
    print("=" * 60)

    dpm = DPMController()

    # Define test steps
    test_steps = [
        {
            'domain': 'air_side',
            'operation': 'connect',
            'params': {},
            'verify': True
        },
        {
            'domain': 'air_side',
            'operation': 'get_status',
            'params': {},
            'verify': True
        },
        {
            'domain': 'air_side',
            'operation': 'send_command',
            'params': {
                'command': 'camera.get_properties',
                'parameters': {}
            },
            'verify': True
        },
        {
            'domain': 'system',
            'operation': 'query_logs',
            'params': {
                'message_filter': 'camera',
                'limit': 10
            },
            'verify': False
        },
        {
            'domain': 'air_side',
            'operation': 'disconnect',
            'params': {},
            'verify': False
        }
    ]

    print("\n1. Running integration test...")
    print(f"   Test steps: {len(test_steps)}")

    result = dpm.multi_domain.run_integration_test(
        test_name="camera_properties_test",
        test_steps=test_steps,
        verify_each_step=True
    )

    if result.success:
        print(f"\n   ✓ Test completed")
        print(f"   Passed: {result.data['passed']}/{result.data['total']}")
        print(f"   Success Rate: {result.data['success_rate']:.1f}%")
        print(f"   Total Duration: {result.data['total_duration_ms']}ms")

        print("\n   Step Results:")
        for step in result.data['steps']:
            status = "✓ PASS" if step['success'] else "✗ FAIL"
            print(f"     {status} Step {step['step']}: {step['domain']}.{step['operation']} ({step['duration_ms']}ms)")
            if step.get('log_verified'):
                print(f"         Verified in logs: {step['log_verified']}")
    else:
        print(f"\n   ✗ Test failed: {result.error}")


def example_coordinated_operation():
    """Example: Synchronized Air-Ground operation"""
    print("\n" + "=" * 60)
    print("Example 4: Coordinated Air-Ground Operation")
    print("=" * 60)

    dpm = DPMController()

    print("\n1. Coordinating Air-Side capture with Ground-Side verification...")
    print("   NOTE: Requires both Air-Side and Ground-Side to be connected")
    print("   Skipping actual execution (demonstration only)")

    # Example (would require actual devices):
    # result = dpm.multi_domain.coordinate_air_ground_operation(
    #     air_side_command='camera.capture',
    #     air_side_params={'quality': 95},
    #     ground_side_action='start_logcat',
    #     ground_side_params={'filter_tag': 'DPM'},
    #     verify_synchronization=True
    # )

    print("\n   Coordination workflow:")
    print("     1. Connect to both Air-Side and Ground-Side")
    print("     2. Execute Air-Side operation (e.g., camera.capture)")
    print("     3. Execute Ground-Side operation (e.g., start_logcat)")
    print("     4. Verify both operations in SystemTools logs")
    print("     5. Report synchronization status")


def example_test_export():
    """Example: Export test results with logs and analytics"""
    print("\n" + "=" * 60)
    print("Example 5: Export Test Results")
    print("=" * 60)

    dpm = DPMController()

    # Run a simple test to generate results
    print("\n1. Running test to generate results...")
    test_steps = [
        {
            'domain': 'system',
            'operation': 'get_system_status',
            'params': {},
            'verify': False
        }
    ]

    test_result = dpm.multi_domain.run_integration_test(
        test_name="export_test",
        test_steps=test_steps,
        verify_each_step=False
    )

    if test_result.success:
        print("   ✓ Test completed")

        # Export results
        print("\n2. Exporting test results...")
        output_path = '/tmp/dpm_test_results.json'

        export_result = dpm.multi_domain.export_test_results(
            test_results=[test_result.data],
            output_path=output_path,
            include_logs=True,
            include_analytics=False
        )

        if export_result.success:
            print(f"\n   ✓ Results exported to: {output_path}")
            print(f"   Test count: {export_result.data['test_count']}")
            print(f"   Log entries: {export_result.data['log_count']}")
            print(f"   Includes analytics: {export_result.data['includes_analytics']}")
        else:
            print(f"\n   ✗ Export failed: {export_result.error}")
    else:
        print(f"   ✗ Test failed: {test_result.error}")


def example_complete_workflow():
    """Example: Complete end-to-end automated testing workflow"""
    print("\n" + "=" * 60)
    print("Example 6: Complete Automated Testing Workflow")
    print("=" * 60)

    dpm = DPMController()

    print("\n1. Running complete automated test workflow...")

    # Step 1: Health check
    print("\n   Step 1: System health check...")
    health = dpm.multi_domain.run_health_check_workflow(include_ground_side=False)

    if not health.data.get('overall_healthy', False):
        print("   ✗ System unhealthy, aborting test")
        return

    print("   ✓ System healthy")

    # Step 2: Run integration tests
    print("\n   Step 2: Running integration tests...")

    test_suite = [
        # Test 1: Air-Side connectivity
        [
            {'domain': 'air_side', 'operation': 'connect', 'params': {}, 'verify': True},
            {'domain': 'air_side', 'operation': 'get_status', 'params': {}, 'verify': True},
            {'domain': 'air_side', 'operation': 'disconnect', 'params': {}, 'verify': False}
        ],
        # Test 2: Camera properties
        [
            {'domain': 'air_side', 'operation': 'connect', 'params': {}, 'verify': False},
            {'domain': 'air_side', 'operation': 'send_command', 'params': {
                'command': 'camera.get_properties', 'parameters': {}
            }, 'verify': True},
            {'domain': 'air_side', 'operation': 'disconnect', 'params': {}, 'verify': False}
        ],
        # Test 3: Log verification
        [
            {'domain': 'system', 'operation': 'query_logs', 'params': {
                'domain': 'air-side', 'limit': 50
            }, 'verify': False},
            {'domain': 'system', 'operation': 'get_system_status', 'params': {}, 'verify': False}
        ]
    ]

    test_results = []
    for idx, test_steps in enumerate(test_suite, 1):
        print(f"\n   Running Test {idx}...")
        result = dpm.multi_domain.run_integration_test(
            test_name=f"automated_test_{idx}",
            test_steps=test_steps,
            verify_each_step=True
        )

        if result.success:
            passed = result.data['passed']
            total = result.data['total']
            print(f"   ✓ Test {idx}: {passed}/{total} passed")
            test_results.append(result.data)
        else:
            print(f"   ✗ Test {idx} failed: {result.error}")

    # Step 3: Export results
    print("\n   Step 3: Exporting test results...")
    output_path = '/tmp/dpm_complete_test_results.json'

    export_result = dpm.multi_domain.export_test_results(
        test_results=test_results,
        output_path=output_path,
        include_logs=True,
        include_analytics=True
    )

    if export_result.success:
        print(f"\n   ✓ Complete workflow finished")
        print(f"   Tests run: {len(test_results)}")
        print(f"   Results exported to: {output_path}")
    else:
        print(f"\n   ✗ Export failed: {export_result.error}")


def main():
    """Run all Phase 5 examples"""
    print("\n" + "=" * 60)
    print("Phase 5: Multi-Domain Coordination")
    print("=" * 60)
    print("\nDemonstrates orchestrated operations across all domains\n")

    try:
        example_capture_workflow()
        example_health_check()
        example_integration_test()
        example_coordinated_operation()
        example_test_export()
        example_complete_workflow()

        print("\n" + "=" * 60)
        print("Phase 5 Examples Complete")
        print("=" * 60)
        print("\nPhase 5 provides:")
        print("- ✓ End-to-end workflow orchestration")
        print("- ✓ Multi-domain health checks")
        print("- ✓ Integration test framework")
        print("- ✓ Coordinated Air-Ground operations")
        print("- ✓ Test result export with logs/analytics")
        print("- ✓ Complete automated testing workflows")
        print("\n" + "=" * 60)
        print("DPM Remote Control API - ALL PHASES COMPLETE")
        print("=" * 60)
        print("\nPhase Summary:")
        print("  Phase 1: Air-Side Basic Operations")
        print("  Phase 2: Extended Air-Side (callbacks, file transfer)")
        print("  Phase 3: Ground-Side Control (ADB, H16 diagnostics)")
        print("  Phase 4: SystemTools (logs, analytics, database)")
        print("  Phase 5: Multi-Domain Coordination ✓")
        print("\nReady for PM automation and integration testing!")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
