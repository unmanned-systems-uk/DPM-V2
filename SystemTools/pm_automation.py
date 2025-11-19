#!/usr/bin/env python3
"""
PM Automation Script - DPM Remote Control API
==============================================

Automated PM workflows for daily operations:
- Multi-domain health checks
- System diagnostics collection
- Error monitoring and alerting
- Status report generation
- Performance metrics collection

Usage:
    python3 pm_automation.py health        # Run health check
    python3 pm_automation.py diagnostics   # Collect diagnostics
    python3 pm_automation.py status        # Generate status report
    python3 pm_automation.py errors        # Check for errors
    python3 pm_automation.py daily         # Run daily workflow
"""

import sys
import json
import socket
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from api import DPMController


def _get_camera_status_from_broadcast(timeout=3.0):
    """
    Listen for Air-Side UDP status broadcast to get camera status

    Args:
        timeout: Seconds to wait for broadcast (default 3s, Air-Side broadcasts every 1s)

    Returns:
        dict: Camera status {'connected': bool, 'model': str} or None if no broadcast received
    """
    try:
        # Create UDP socket and bind to status port (5001)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('0.0.0.0', 5001))
        sock.settimeout(timeout)

        # Wait for one status broadcast
        data, addr = sock.recvfrom(65536)
        sock.close()

        # Parse JSON message
        message = json.loads(data.decode('utf-8'))

        # Extract camera status from payload
        if 'payload' in message and 'camera' in message['payload']:
            camera = message['payload']['camera']
            return {
                'connected': camera.get('connected', False),
                'model': camera.get('model', 'Unknown')
            }

        return None

    except socket.timeout:
        return None
    except Exception as e:
        print(f"    Warning: Could not get camera status from broadcast: {e}")
        return None


def pm_health_check(include_ground_side=False):
    """
    Run comprehensive health check across all domains

    Returns:
        dict: Health check results with status for each domain
    """
    print("\n" + "=" * 80)
    print("PM HEALTH CHECK - Multi-Domain System Status")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    with DPMController() as dpm:
        print("Running health check across all domains...")
        result = dpm.multi_domain.run_health_check_workflow(
            include_ground_side=include_ground_side
        )

        if not result.success:
            print(f"✗ Health check failed: {result.error}")
            return {'success': False, 'error': result.error}

        data = result.data
        overall_healthy = data.get('overall_healthy', False)

        # Check camera status on Air-Side via UDP status broadcast
        camera_status = {'connected': False, 'model': 'Unknown'}
        if data.get('domains', {}).get('air_side', {}).get('connected'):
            print("\n  Checking camera status (listening for broadcast)...")
            broadcast_status = _get_camera_status_from_broadcast(timeout=3.0)

            if broadcast_status:
                camera_status = broadcast_status
                if camera_status['connected']:
                    print(f"    ✓ Camera connected: {camera_status['model']}")
                else:
                    print(f"    ✗ Camera disconnected")
            else:
                print(f"    ⚠ No status broadcast received (Air-Side may not be running)")

        # Add camera status to air_side domain data
        if 'air_side' in data.get('domains', {}):
            data['domains']['air_side']['camera'] = camera_status

        # Print overall status
        print(f"\n{'='*80}")
        if overall_healthy:
            print("OVERALL STATUS: ✓ HEALTHY")
        else:
            print("OVERALL STATUS: ✗ UNHEALTHY - ATTENTION REQUIRED")
        print(f"{'='*80}\n")

        # Print domain status
        print("DOMAIN STATUS:")
        print("-" * 80)

        for domain, status in data.get('domains', {}).items():
            healthy = status.get('healthy', False)
            connected = status.get('connected', 'Unknown')

            health_icon = "✓" if healthy else "✗"
            print(f"\n  {domain.upper()}:")
            print(f"    Health: {health_icon} {'HEALTHY' if healthy else 'UNHEALTHY'}")

            if isinstance(connected, bool):
                conn_icon = "✓" if connected else "✗"
                print(f"    Connected: {conn_icon} {'YES' if connected else 'NO'}")

            if status.get('error'):
                print(f"    Error: {status['error']}")

            if status.get('status'):
                print(f"    Status: {status['status']}")

        print(f"\n{'='*80}\n")

        # Recommendations
        if not overall_healthy:
            print("RECOMMENDATIONS:")
            print("-" * 80)
            for domain, status in data.get('domains', {}).items():
                if not status.get('healthy', False):
                    print(f"  • Check {domain.upper()} connectivity and logs")
                    if status.get('error'):
                        print(f"    Error: {status['error']}")
            print()

        return {
            'success': True,
            'overall_healthy': overall_healthy,
            'domains': data.get('domains', {}),
            'timestamp': datetime.now().isoformat()
        }


def pm_collect_diagnostics(include_ground_side=True):
    """
    Collect comprehensive diagnostics from all domains

    Returns:
        dict: Diagnostic data from all domains
    """
    print("\n" + "=" * 80)
    print("PM DIAGNOSTICS COLLECTION")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    diagnostics = {
        'timestamp': datetime.now().isoformat(),
        'air_side': {},
        'ground_side': {},
        'system': {}
    }

    with DPMController() as dpm:
        # Air-Side diagnostics
        print("Collecting Air-Side diagnostics...")
        air_result = dpm.air_side.connect()
        if air_result.success:
            print("  ✓ Connected to Air-Side (10.0.1.53:5000)")

            # Get status
            status_result = dpm.air_side.get_status()
            diagnostics['air_side']['connected'] = True
            diagnostics['air_side']['status'] = status_result.data if status_result.success else None

            dpm.air_side.disconnect()
        else:
            print(f"  ✗ Failed to connect to Air-Side: {air_result.error}")
            diagnostics['air_side']['connected'] = False
            diagnostics['air_side']['error'] = air_result.error

        # Ground-Side diagnostics
        if include_ground_side:
            print("\nCollecting Ground-Side diagnostics...")
            ground_result = dpm.ground_side.connect()
            if ground_result.success:
                print("  ✓ Connected to Ground-Side (10.0.1.92:5555)")

                # Get H16 diagnostics
                diag_result = dpm.ground_side.get_diagnostics()
                if diag_result.success:
                    diag_data = diag_result.data
                    print(f"  ✓ H16 Diagnostics collected:")
                    print(f"    Battery: {diag_data.get('battery', 'N/A')}%")
                    print(f"    CPU Usage: {diag_data.get('cpu_usage', 'N/A')}%")
                    print(f"    Memory: {diag_data.get('memory_used', 'N/A')} / {diag_data.get('memory_total', 'N/A')}")
                    print(f"    Temperature: {diag_data.get('temperature', 'N/A')}°C")

                    diagnostics['ground_side']['connected'] = True
                    diagnostics['ground_side']['diagnostics'] = diag_data
                else:
                    print(f"  ✗ Failed to get diagnostics: {diag_result.error}")
                    diagnostics['ground_side']['connected'] = True
                    diagnostics['ground_side']['error'] = diag_result.error

                dpm.ground_side.disconnect()
            else:
                print(f"  ✗ Failed to connect to Ground-Side: {ground_result.error}")
                diagnostics['ground_side']['connected'] = False
                diagnostics['ground_side']['error'] = ground_result.error

        # SystemTools diagnostics
        print("\nCollecting SystemTools diagnostics...")
        system_result = dpm.system.get_system_status()
        if system_result.success:
            print("  ✓ SystemTools status collected")
            diagnostics['system'] = system_result.data
        else:
            print(f"  ✗ Failed to get SystemTools status: {system_result.error}")
            diagnostics['system']['error'] = system_result.error

    print(f"\n{'='*80}\n")

    return diagnostics


def pm_check_errors(domains=None, limit=50):
    """
    Check for errors across all domains in recent logs

    Args:
        domains: List of domains to check (None = all)
        limit: Number of log entries to check per domain

    Returns:
        dict: Error summary by domain
    """
    print("\n" + "=" * 80)
    print("PM ERROR MONITORING - Recent Log Analysis")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Checking last {limit} log entries per domain")
    print()

    domains_to_check = domains or ['air-side', 'ground-side', 'system']
    error_summary = {
        'timestamp': datetime.now().isoformat(),
        'domains': {},
        'total_errors': 0
    }

    with DPMController() as dpm:
        for domain in domains_to_check:
            print(f"Checking {domain} logs...")

            # Query ERROR level logs
            result = dpm.system.query_logs(
                domain=domain,
                level='ERROR',
                limit=limit
            )

            if result.success:
                logs = result.data.get('logs', [])
                error_count = len(logs)
                error_summary['domains'][domain] = {
                    'error_count': error_count,
                    'recent_errors': logs[:5] if logs else []  # Store last 5 errors
                }
                error_summary['total_errors'] += error_count

                if error_count > 0:
                    print(f"  ✗ Found {error_count} ERROR entries")
                    print(f"  Most recent errors:")
                    for log in logs[:3]:
                        print(f"    - {log.get('timestamp', 'N/A')}: {log.get('message', 'N/A')}")
                else:
                    print(f"  ✓ No errors found")
            else:
                print(f"  ✗ Failed to query logs: {result.error}")
                error_summary['domains'][domain] = {
                    'error_count': 0,
                    'query_failed': True,
                    'error': result.error
                }

            print()

    # Summary
    print(f"{'='*80}")
    print(f"TOTAL ERRORS FOUND: {error_summary['total_errors']}")
    print(f"{'='*80}\n")

    return error_summary


def pm_status_report(output_file=None):
    """
    Generate comprehensive PM status report

    Args:
        output_file: Optional path to save report as JSON

    Returns:
        dict: Complete status report
    """
    print("\n" + "=" * 80)
    print("PM STATUS REPORT - Complete System Overview")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Collect all data
    print("Step 1/3: Running health check...")
    health = pm_health_check(include_ground_side=True)

    print("\nStep 2/3: Collecting diagnostics...")
    diagnostics = pm_collect_diagnostics(include_ground_side=True)

    print("\nStep 3/3: Checking for errors...")
    errors = pm_check_errors(limit=50)

    # Compile report
    report = {
        'timestamp': datetime.now().isoformat(),
        'health_check': health,
        'diagnostics': diagnostics,
        'error_summary': errors,
        'recommendations': []
    }

    # Generate recommendations
    if not health.get('overall_healthy', False):
        report['recommendations'].append("CRITICAL: System health check failed - investigate immediately")

    if errors.get('total_errors', 0) > 10:
        report['recommendations'].append(f"WARNING: {errors['total_errors']} errors found in recent logs")

    # Print summary
    print("\n" + "=" * 80)
    print("STATUS REPORT SUMMARY")
    print("=" * 80)
    print(f"Overall Health: {'✓ HEALTHY' if health.get('overall_healthy') else '✗ UNHEALTHY'}")
    print(f"Total Errors: {errors.get('total_errors', 0)}")
    print(f"Domains Checked: {len(health.get('domains', {}))}")

    if report['recommendations']:
        print(f"\nRECOMMENDATIONS:")
        for rec in report['recommendations']:
            print(f"  • {rec}")

    print(f"{'='*80}\n")

    # Save to file if requested
    if output_file:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"Report saved to: {output_path}\n")

    return report


def pm_daily_workflow(report_dir='/tmp/pm_reports'):
    """
    Complete daily PM workflow

    Runs:
    1. Health check
    2. Diagnostics collection
    3. Error monitoring
    4. Status report generation
    5. Report archival

    Args:
        report_dir: Directory to save daily reports
    """
    print("\n" + "=" * 80)
    print("PM DAILY WORKFLOW - Automated System Monitoring")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Generate timestamp for filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = Path(report_dir) / f"pm_daily_report_{timestamp}.json"

    # Run complete workflow
    report = pm_status_report(output_file=report_file)

    # Print completion
    print(f"\n{'='*80}")
    print("DAILY WORKFLOW COMPLETE")
    print(f"{'='*80}")
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Report: {report_file}")
    print()

    return report


def main():
    """Main entry point for PM automation"""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1].lower()

    try:
        if command == 'health':
            pm_health_check(include_ground_side=True)

        elif command == 'diagnostics':
            result = pm_collect_diagnostics(include_ground_side=True)
            print("\nDiagnostics collected successfully")
            print(f"Export to file: {json.dumps(result, indent=2)}")

        elif command == 'status':
            output = sys.argv[2] if len(sys.argv) > 2 else None
            pm_status_report(output_file=output)

        elif command == 'errors':
            pm_check_errors(limit=50)

        elif command == 'daily':
            report_dir = sys.argv[2] if len(sys.argv) > 2 else '/tmp/pm_reports'
            pm_daily_workflow(report_dir=report_dir)

        else:
            print(f"Unknown command: {command}")
            print(__doc__)
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
