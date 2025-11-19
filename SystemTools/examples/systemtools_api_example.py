#!/usr/bin/env python3
"""
SystemTools API - Usage Examples (Phase 4)
===========================================

Demonstrates SystemTools controller operations:
- Log querying and export
- Performance analytics
- Database queries
- Filter management
- Configuration management
- System status monitoring

These examples enable PM automation for:
- Test result verification
- Performance monitoring
- Log analysis automation
- Test data export
"""

import sys
from pathlib import Path

# Add SystemTools to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api import DPMController


def example_log_querying():
    """Query aggregated logs with filters"""
    print("=" * 60)
    print("Example 1: Log Querying")
    print("=" * 60)

    dpm = DPMController()

    # Query logs by domain
    print("\n1. Querying Air-Side ERROR logs...")
    result = dpm.system.query_logs(
        domain='air-side',
        level='ERROR',
        limit=10
    )

    if result.success:
        print(f"   ✓ Found {result.data['count']} logs")
        for log in result.data['logs'][:3]:  # Show first 3
            print(f"     - {log.get('timestamp')}: {log.get('message')}")
    else:
        print(f"   ✗ Query failed: {result.error}")

    # Query logs by context
    print("\n2. Querying CAMERA context logs...")
    result = dpm.system.query_logs(
        context='CAMERA',
        limit=5
    )

    if result.success:
        print(f"   ✓ Found {result.data['count']} camera logs")

    # Search in message
    print("\n3. Searching for 'connection' in messages...")
    result = dpm.system.query_logs(
        message_filter='connection',
        limit=5
    )

    if result.success:
        print(f"   ✓ Found {result.data['count']} matching logs")


def example_log_export():
    """Export logs to file"""
    print("\n" + "=" * 60)
    print("Example 2: Log Export")
    print("=" * 60)

    dpm = DPMController()

    # Export to JSON
    print("\n1. Exporting ERROR logs to JSON...")
    result = dpm.system.export_logs(
        output_file='/tmp/error_logs.json',
        format='json',
        level='ERROR',
        limit=100
    )

    if result.success:
        print(f"   ✓ Exported {result.data['count']} logs to {result.data['output_file']}")
    else:
        print(f"   ✗ Export failed: {result.error}")

    # Export to CSV
    print("\n2. Exporting Air-Side logs to CSV...")
    result = dpm.system.export_logs(
        output_file='/tmp/air_side_logs.csv',
        format='csv',
        domain='air-side',
        limit=50
    )

    if result.success:
        print(f"   ✓ Exported {result.data['count']} logs to CSV")


def example_analytics():
    """Get performance analytics"""
    print("\n" + "=" * 60)
    print("Example 3: Performance Analytics")
    print("=" * 60)

    dpm = DPMController()

    # Get specific metric analytics
    print("\n1. Getting CPU usage analytics...")
    result = dpm.system.get_analytics(metric='cpu_percent')

    if result.success:
        stats = result.data['statistics']
        desc = stats.get('descriptive', {})
        print(f"   ✓ CPU Analytics:")
        print(f"     - Mean: {desc.get('mean', 0):.1f}%")
        print(f"     - Min: {desc.get('min', 0):.1f}%")
        print(f"     - Max: {desc.get('max', 0):.1f}%")
        print(f"     - Std Dev: {desc.get('std_dev', 0):.1f}")
    else:
        print(f"   ℹ {result.error}")

    # Get all metrics summary
    print("\n2. Getting all metrics summary...")
    result = dpm.system.get_analytics()

    if result.success:
        metrics = result.data.get('metrics', {})
        print(f"   ✓ Metrics Summary:")
        for metric_name, stats in metrics.items():
            print(f"     - {metric_name}: mean={stats.get('mean', 0):.1f}, max={stats.get('max', 0):.1f}")


def example_analytics_export():
    """Export analytics data"""
    print("\n" + "=" * 60)
    print("Example 4: Analytics Export")
    print("=" * 60)

    dpm = DPMController()

    # Export to CSV
    print("\n1. Exporting analytics to CSV...")
    result = dpm.system.export_analytics(
        output_file='/tmp/performance_metrics.csv',
        format='csv'
    )

    if result.success:
        print(f"   ✓ Exported {result.data['count']} snapshots to CSV")
    else:
        print(f"   ℹ {result.error}")

    # Export to JSON
    print("\n2. Exporting analytics to JSON...")
    result = dpm.system.export_analytics(
        output_file='/tmp/performance_metrics.json',
        format='json'
    )

    if result.success:
        print(f"   ✓ Exported {result.data['count']} snapshots to JSON")


def example_database_queries():
    """Execute database queries"""
    print("\n" + "=" * 60)
    print("Example 5: Database Queries")
    print("=" * 60)

    dpm = DPMController()

    # Query high CPU snapshots
    print("\n1. Querying high CPU usage snapshots (>80%)...")
    result = dpm.system.query_performance_db(
        sql="SELECT * FROM health_snapshots WHERE cpu_percent > 80 LIMIT 5"
    )

    if result.success:
        print(f"   ✓ Found {result.data['count']} high CPU snapshots")
        for row in result.data['results'][:3]:
            print(f"     - CPU: {row.get('cpu_percent', 0):.1f}% at {row.get('timestamp')}")
    else:
        print(f"   ℹ {result.error}")

    # Query camera latency spikes
    print("\n2. Querying camera latency spikes (>100ms)...")
    result = dpm.system.query_performance_db(
        sql="SELECT timestamp, camera_latency_ms FROM health_snapshots WHERE camera_latency_ms > 100 LIMIT 5"
    )

    if result.success:
        print(f"   ✓ Found {result.data['count']} latency spikes")


def example_database_export():
    """Export entire database"""
    print("\n" + "=" * 60)
    print("Example 6: Database Export")
    print("=" * 60)

    dpm = DPMController()

    print("\n1. Exporting performance database...")
    result = dpm.system.export_database('/tmp/performance_backup.db')

    if result.success:
        print(f"   ✓ Database exported to {result.data['output_file']}")
    else:
        print(f"   ℹ {result.error}")


def example_filter_management():
    """Manage log filters"""
    print("\n" + "=" * 60)
    print("Example 7: Filter Management")
    print("=" * 60)

    dpm = DPMController()

    # Apply filter
    print("\n1. Applying filter (Air-Side ERRORS only)...")
    filter_config = {
        "domain": "air-side",
        "level": ["ERROR", "CRITICAL"],
        "context": ["CAMERA", "NETWORK"]
    }

    result = dpm.system.apply_filter(filter_config)

    if result.success:
        print(f"   ✓ Filter applied")
    else:
        print(f"   ✗ Failed: {result.error}")

    # Save filter
    print("\n2. Saving filter to file...")
    result = dpm.system.save_filter(filter_config, '/tmp/test_filter.json')

    if result.success:
        print(f"   ✓ Filter saved to {result.data['output_file']}")

    # Load filter
    print("\n3. Loading filter from file...")
    result = dpm.system.load_filter('/tmp/test_filter.json')

    if result.success:
        print(f"   ✓ Filter loaded")


def example_configuration():
    """Configuration management"""
    print("\n" + "=" * 60)
    print("Example 8: Configuration Management")
    print("=" * 60)

    dpm = DPMController()

    # Get specific config
    print("\n1. Getting tcp_port configuration...")
    result = dpm.system.get_config('tcp_port')

    if result.success:
        print(f"   ✓ tcp_port = {result.data.get('tcp_port')}")

    # Get all config
    print("\n2. Getting all configuration...")
    result = dpm.system.get_config()

    if result.success:
        config_keys = list(result.data.keys())
        print(f"   ✓ Configuration has {len(config_keys)} keys")
        print(f"     Keys: {', '.join(config_keys[:5])}...")

    # Set config
    print("\n3. Setting configuration value...")
    result = dpm.system.set_config('test_key', 'test_value')

    if result.success:
        print(f"   ✓ Config set: {result.data['key']} = {result.data['value']}")


def example_system_status():
    """Get system status"""
    print("\n" + "=" * 60)
    print("Example 9: System Status")
    print("=" * 60)

    dpm = DPMController()

    print("\n1. Getting SystemTools status...")
    result = dpm.system.get_system_status()

    if result.success:
        status = result.data
        print(f"   ✓ System Status:")
        print(f"     - Log queue available: {status['log_queue']['available']}")
        print(f"     - Log count: {status['log_queue']['count']}")
        print(f"     - Data storage available: {status['data_storage']['available']}")
        print(f"     - Filter manager available: {status['filter_manager']['available']}")


def example_automated_test_with_verification():
    """Complete automated test with log verification"""
    print("\n" + "=" * 60)
    print("Example 10: Automated Test with Log Verification")
    print("=" * 60)

    with DPMController() as dpm:
        test_results = []

        # Test 1: Send command to Air-Side
        print("\nTest 1: Send camera command")
        cmd_result = dpm.air_side.send_command('camera.get_properties', {})
        test_results.append(("Send Command", cmd_result.success))
        print(f"   {'✓ PASS' if cmd_result.success else '✗ FAIL'}")

        # Test 2: Verify command in logs
        print("\nTest 2: Verify command appears in logs")
        log_result = dpm.system.query_logs(
            message_filter='camera.get_properties',
            limit=10
        )
        verified = log_result.success and log_result.data['count'] > 0
        test_results.append(("Log Verification", verified))
        print(f"   {'✓ PASS' if verified else '✗ FAIL'}")

        # Test 3: Check performance metrics
        print("\nTest 3: Check performance metrics available")
        analytics_result = dpm.system.get_analytics()
        has_metrics = analytics_result.success and 'metrics' in analytics_result.data
        test_results.append(("Performance Metrics", has_metrics))
        print(f"   {'✓ PASS' if has_metrics else '✗ FAIL'}")

        # Test 4: Export test results
        print("\nTest 4: Export test results")
        export_result = dpm.system.export_logs(
            output_file='/tmp/test_results.json',
            format='json',
            limit=100
        )
        test_results.append(("Export Results", export_result.success))
        print(f"   {'✓ PASS' if export_result.success else '✗ FAIL'}")

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
    """Run all SystemTools API examples"""
    print("\n" + "=" * 60)
    print("SystemTools API Examples (Phase 4)")
    print("=" * 60)
    print("\nDemonstrates programmatic control of SystemTools operations")
    print("for automated testing, log analysis, and performance monitoring.\n")

    try:
        # Run examples
        example_log_querying()
        example_log_export()
        example_analytics()
        example_analytics_export()
        example_database_queries()
        example_database_export()
        example_filter_management()
        example_configuration()
        example_system_status()
        example_automated_test_with_verification()

        print("\n" + "=" * 60)
        print("SystemTools Examples Complete")
        print("=" * 60)
        print("\nPhase 4 capabilities enable:")
        print("- ✓ Automated test verification via log queries")
        print("- ✓ Performance monitoring and analytics export")
        print("- ✓ Database queries for test result analysis")
        print("- ✓ Filter management for focused testing")
        print("- ✓ Complete PM automation with verification")

    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
