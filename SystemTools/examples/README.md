# DPM Remote Control API - Complete Documentation

Comprehensive programmatic interface for DPM Management System enabling PM automation, automated testing, and remote diagnostics.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Phase 1: Air-Side Basic Operations](#phase-1-air-side-basic-operations)
- [Phase 2: Extended Air-Side](#phase-2-extended-air-side)
- [Phase 3: Ground-Side Control](#phase-3-ground-side-control)
- [Phase 4: SystemTools](#phase-4-systemtools)
- [Phase 5: Multi-Domain Coordination](#phase-5-multi-domain-coordination)
- [Complete Examples](#complete-examples)
- [API Reference](#api-reference)

---

## Overview

The DPM Remote Control API provides programmatic access to all DPM domains:

- **Air-Side** (Raspberry Pi 5 + PayloadManager): Command execution, Docker management, file transfer
- **Ground-Side** (Android H16): ADB control, app lifecycle, input simulation, diagnostics
- **SystemTools**: Log aggregation, analytics, database queries, configuration
- **Multi-Domain**: Orchestrated workflows, integration testing, health checks

### Key Features

✓ **Fully Automated Testing** - Run complete test suites without GUI interaction
✓ **Cross-Domain Verification** - Verify operations in logs across all domains
✓ **Integration Test Framework** - Custom test workflows with step-by-step verification
✓ **Performance Analytics** - Query metrics, export data, analyze trends
✓ **Remote Diagnostics** - Access system health from Air-Side, Ground-Side, and SystemTools
✓ **Standardized Responses** - Consistent APIResponse format across all operations

---

## Installation

The API is part of the SystemTools package. No additional installation required.

```bash
cd /home/anthony/DPM-V2/SystemTools
python3 examples/phase1_airside_api_example.py
```

---

## Quick Start

```python
from api import DPMController

# Create controller
dpm = DPMController()

# Connect to Air-Side
result = dpm.air_side.connect()
if result.success:
    print(f"Connected to {result.data['host']}")

    # Send command
    cmd_result = dpm.air_side.send_command('camera.get_properties', {})
    if cmd_result.success:
        print(f"Command response: {cmd_result.data}")

    # Disconnect
    dpm.air_side.disconnect()
```

---

## Phase 1: Air-Side Basic Operations

**File**: `examples/phase1_airside_api_example.py`

### Capabilities

- TCP connection management
- Command execution (camera, storage, config, discovery, sync)
- Status queries
- SSH operations

### Example: Send Camera Command

```python
from api import DPMController

dpm = DPMController()

# Connect via TCP
dpm.air_side.connect(host='10.0.1.53', port=5010)

# Send camera.capture command
result = dpm.air_side.send_command(
    command='camera.capture',
    parameters={'quality': 95}
)

if result.success:
    print(f"Capture initiated: {result.data}")

dpm.air_side.disconnect()
```

### Methods

- `connect(host, port, timeout)` - Connect to Air-Side
- `disconnect()` - Disconnect from Air-Side
- `is_connected()` - Check connection status
- `send_command(command, parameters, timeout)` - Execute PayloadManager command
- `get_status()` - Get Air-Side status
- `execute_ssh_command(command, timeout)` - Run SSH command

---

## Phase 2: Extended Air-Side

**File**: `examples/phase2_extended_airside.py`

### Capabilities

- Response callbacks
- Status subscriptions
- Log streaming
- File transfer (SFTP)
- Camera file management
- Docker container management

### Example: Command with Callback

```python
def on_response(data):
    print(f"Response received: {data}")

def on_error(error):
    print(f"Error occurred: {error}")

result = dpm.air_side.send_command_with_callback(
    'camera.get_properties',
    {},
    on_response=on_response,
    on_error=on_error
)
```

### Example: File Transfer

```python
# Download file from Air-Side
result = dpm.air_side.transfer_file(
    remote_path='/tmp/logfile.txt',
    local_path='/tmp/downloaded_log.txt',
    direction='download'
)

if result.success:
    print(f"SCP command: {result.data['scp_command']}")
```

### Methods

- `send_command_with_callback()` - Command with response callback
- `subscribe_to_status()` / `unsubscribe_from_status()` - Real-time status updates
- `stream_logs()` - Docker log streaming
- `transfer_file()` - SFTP file transfer
- `get_camera_files()` - List camera files
- `download_camera_file()` - Download camera file
- `manage_docker_container()` - Docker control (start/stop/status/logs)

---

## Phase 3: Ground-Side Control

**File**: `examples/phase3_ground_side.py`

### Capabilities

- ADB connection management
- H16 diagnostics (battery, CPU, memory, temperature)
- App lifecycle control
- Input simulation (tap, swipe, key press)
- Screen capture
- Logcat streaming

### Example: H16 Diagnostics

```python
dpm = DPMController()

# Connect to H16 via ADB
dpm.ground_side.connect(host='10.0.1.92', port=5555)

# Get diagnostics
diag = dpm.ground_side.get_diagnostics()
if diag.success:
    print(f"Battery: {diag.data['battery']}")
    print(f"CPU: {diag.data['cpu']}")
    print(f"Memory: {diag.data['memory']}")
    print(f"Temperature: {diag.data['temperature']}")

dpm.ground_side.disconnect()
```

### Example: App Control

```python
# Start DPM app
dpm.ground_side.start_app('uk.unmannedsystems.dpm_android')

# Simulate tap
dpm.ground_side.tap(540, 960)

# Capture screenshot
dpm.ground_side.get_screen_capture('/tmp/screenshot.png')

# Stop app
dpm.ground_side.stop_app('uk.unmannedsystems.dpm_android')
```

### Methods

- `connect()` / `disconnect()` / `is_connected()` - ADB connection
- `execute_adb_command()` - Execute shell command
- `get_diagnostics()` - H16 health metrics
- `start_app()` / `stop_app()` / `install_app()` - App lifecycle
- `tap()` / `swipe()` / `press_key()` - Input simulation
- `get_screen_capture()` - Screenshot capture
- `start_logcat()` / `stop_logcat()` / `clear_logcat()` - Logcat operations

---

## Phase 4: SystemTools

**File**: `examples/systemtools_api_example.py`

### Capabilities

- Log aggregation queries
- Performance analytics
- Database operations (SQL queries)
- Filter management
- Configuration management
- System status

### Example: Query Logs

```python
# Query logs with filters
logs = dpm.system.query_logs(
    domain='air-side',
    level='ERROR',
    context='CAMERA',
    message_filter='capture',
    limit=50
)

if logs.success:
    print(f"Found {logs.data['count']} matching logs")
    for log in logs.data['logs']:
        print(f"[{log['timestamp']}] {log['message']}")
```

### Example: Performance Analytics

```python
# Get analytics for specific metric
analytics = dpm.system.get_analytics(
    metric='cpu_percent',
    time_range=3600  # Last hour
)

if analytics.success:
    stats = analytics.data['statistics']['descriptive']
    print(f"CPU - Mean: {stats['mean']:.1f}%, Max: {stats['max']:.1f}%")
```

### Example: Database Query

```python
# Run SQL query on performance database
result = dpm.system.query_performance_db(
    sql="SELECT * FROM snapshots WHERE cpu_percent > ? ORDER BY timestamp DESC LIMIT 10",
    params=(80.0,)
)

if result.success:
    print(f"Found {result.data['count']} high CPU snapshots")
```

### Methods

- `query_logs()` - Query aggregated logs with filters
- `export_logs()` - Export logs to file (JSON/CSV)
- `get_analytics()` - Get performance analytics
- `export_analytics()` - Export analytics to file
- `query_performance_db()` - Execute SQL queries
- `export_database()` - Export database to file
- `apply_filter()` / `save_filter()` / `load_filter()` - Filter management
- `get_config()` / `set_config()` / `reload_config()` - Configuration
- `get_system_status()` - SystemTools status

---

## Phase 5: Multi-Domain Coordination

**File**: `examples/phase5_multi_domain.py`

### Capabilities

- End-to-end workflow orchestration
- Multi-domain health checks
- Integration test framework
- Synchronized Air-Ground operations
- Test result export

### Example: Capture Workflow

```python
# Run complete capture workflow
result = dpm.multi_domain.run_capture_workflow(
    quality=95,
    verify_logs=True,
    verify_ground_side=True,
    capture_screenshot=True
)

if result.success:
    print(f"Workflow: {result.data['overall_success']}")
    print(f"Steps: {result.data['steps_completed']}")
    print(f"Duration: {result.data['total_duration_ms']}ms")
```

### Example: Health Check

```python
# Multi-domain health check
health = dpm.multi_domain.run_health_check_workflow(
    include_ground_side=True
)

if health.success:
    print(f"Overall Health: {health.data['overall_healthy']}")
    for domain, status in health.data['domains'].items():
        print(f"{domain}: {status['healthy']}")
```

### Example: Integration Test

```python
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
        'operation': 'send_command',
        'params': {
            'command': 'camera.capture',
            'parameters': {'quality': 95}
        },
        'verify': True
    },
    {
        'domain': 'system',
        'operation': 'query_logs',
        'params': {
            'message_filter': 'camera.capture',
            'limit': 10
        },
        'verify': False
    }
]

# Run integration test
result = dpm.multi_domain.run_integration_test(
    test_name="capture_verification_test",
    test_steps=test_steps,
    verify_each_step=True
)

print(f"Test Result: {result.data['passed']}/{result.data['total']} passed")
```

### Methods

- `run_capture_workflow()` - End-to-end capture with verification
- `run_health_check_workflow()` - System-wide health check
- `run_integration_test()` - Custom integration test execution
- `coordinate_air_ground_operation()` - Synchronized Air-Ground ops
- `export_test_results()` - Export results with logs/analytics

---

## Complete Examples

### Automated Testing Workflow

```python
from api import DPMController

with DPMController() as dpm:
    # Step 1: Health check
    health = dpm.multi_domain.run_health_check_workflow()
    if not health.data['overall_healthy']:
        print("System unhealthy, aborting")
        return

    # Step 2: Run capture workflow
    capture = dpm.multi_domain.run_capture_workflow(
        quality=95,
        verify_logs=True,
        verify_ground_side=True
    )

    # Step 3: Verify in logs
    logs = dpm.system.query_logs(
        message_filter='camera.capture',
        limit=50
    )

    # Step 4: Check performance
    analytics = dpm.system.get_analytics()

    # Step 5: Export everything
    dpm.multi_domain.export_test_results(
        test_results=[capture.data],
        output_path='/tmp/test_results.json',
        include_logs=True,
        include_analytics=True
    )
```

### PM Automation Script

```python
#!/usr/bin/env python3
"""PM Automation: Daily Health Check & Capture Test"""

from api import DPMController
import sys

def main():
    dpm = DPMController()

    # 1. Multi-domain health check
    print("Running health check...")
    health = dpm.multi_domain.run_health_check_workflow(include_ground_side=True)

    if not health.data['overall_healthy']:
        print("FAIL: System unhealthy")
        sys.exit(1)

    # 2. Run capture test
    print("Running capture test...")
    test_steps = [
        {'domain': 'air_side', 'operation': 'connect', 'params': {}, 'verify': True},
        {'domain': 'air_side', 'operation': 'send_command', 'params': {
            'command': 'camera.capture', 'parameters': {'quality': 95}
        }, 'verify': True},
        {'domain': 'air_side', 'operation': 'disconnect', 'params': {}, 'verify': False}
    ]

    test = dpm.multi_domain.run_integration_test("daily_capture_test", test_steps)

    if test.data['passed'] != test.data['total']:
        print(f"FAIL: {test.data['passed']}/{test.data['total']} passed")
        sys.exit(1)

    # 3. Export results
    dpm.multi_domain.export_test_results(
        [test.data],
        '/tmp/daily_test_results.json',
        include_logs=True,
        include_analytics=True
    )

    print("SUCCESS: All tests passed")

if __name__ == '__main__':
    main()
```

---

## API Reference

### APIResponse Format

All API methods return an `APIResponse` object:

```python
class APIResponse:
    success: bool           # Operation success status
    data: dict             # Response data (if successful)
    error: str             # Error message (if failed)
    timestamp: str         # ISO8601 timestamp
    domain: str            # Domain: 'air-side', 'ground-side', 'systemtools', 'multi-domain', 'all'
    operation: str         # Operation name
```

### DPMController Properties

```python
dpm = DPMController()

# Access domain controllers
dpm.air_side          # AirSideController
dpm.ground_side       # GroundSideController
dpm.system            # SystemController
dpm.multi_domain      # MultiDomainController

# High-level operations
dpm.connect_all()     # Connect to all domains
dpm.disconnect_all()  # Disconnect from all domains
dpm.get_system_status()  # Get status of all domains
```

### Context Manager Usage

```python
# Automatic cleanup
with DPMController() as dpm:
    # Your code here
    dpm.air_side.connect()
    result = dpm.air_side.send_command('camera.capture', {})
    # Automatic disconnect_all() on exit
```

---

## Running Examples

### Phase 1: Air-Side Basic
```bash
python3 examples/phase1_airside_api_example.py
```

### Phase 2: Extended Air-Side
```bash
python3 examples/phase2_extended_airside.py
```

### Phase 3: Ground-Side
```bash
python3 examples/phase3_ground_side.py
```

### Phase 4: SystemTools
```bash
python3 examples/systemtools_api_example.py
```

### Phase 5: Multi-Domain
```bash
python3 examples/phase5_multi_domain.py
```

---

## Best Practices

### Error Handling

```python
result = dpm.air_side.send_command('camera.capture', {})

if result.success:
    print(f"Success: {result.data}")
else:
    print(f"Error: {result.error}")
    print(f"Domain: {result.domain}")
    print(f"Operation: {result.operation}")
```

### Connection Management

```python
# Always disconnect after operations
try:
    dpm.air_side.connect()
    # Operations...
finally:
    dpm.air_side.disconnect()

# Or use context manager
with DPMController() as dpm:
    dpm.air_side.connect()
    # Operations...
    # Automatic cleanup
```

### Log Verification

```python
# Send command
cmd_result = dpm.air_side.send_command('camera.capture', {})

# Wait for log propagation
import time
time.sleep(0.5)

# Verify in logs
logs = dpm.system.query_logs(
    message_filter='camera.capture',
    limit=10
)

verified = logs.success and logs.data['count'] > 0
print(f"Command verified in logs: {verified}")
```

---

## Troubleshooting

### Connection Issues

```python
# Check connection status
if not dpm.air_side.is_connected():
    result = dpm.air_side.connect(host='10.0.1.53', port=5010, timeout=10.0)
    if not result.success:
        print(f"Connection failed: {result.error}")
```

### Command Timeout

```python
# Increase timeout for slow operations
result = dpm.air_side.send_command(
    'camera.capture',
    {'quality': 95},
    timeout=30.0  # 30 seconds
)
```

### Log Query No Results

```python
# Check if logs are being aggregated
status = dpm.system.get_system_status()
if status.success:
    log_queue_size = status.data['log_aggregator']['log_queue_size']
    print(f"Logs in queue: {log_queue_size}")
```

---

## Support

- **Issue Tracker**: [GitHub Issues](https://github.com/...)
- **Examples**: `/home/anthony/DPM-V2/SystemTools/examples/`
- **API Source**: `/home/anthony/DPM-V2/SystemTools/api/`

---

**Version**: 1.0.0
**Status**: ALL PHASES COMPLETE ✓
**Last Updated**: 2025-11-19
