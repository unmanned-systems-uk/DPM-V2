# PM Automation Guide - DPM Remote Control API

**Date**: 2025-11-19
**Status**: Production Ready
**API Version**: Issue #144 Implementation

---

## Overview

The PM Automation system provides comprehensive automated workflows for daily Project Manager operations across all DPM domains (Air-Side, Ground-Side, SystemTools).

**Key Benefits:**
- ✅ Automated health monitoring across all domains
- ✅ Comprehensive diagnostics collection
- ✅ Real-time error detection and alerting
- ✅ Daily status report generation
- ✅ Scheduled automation support

---

## Prerequisites

1. **DPM Remote Control API** installed (Issue #144)
2. **Network connectivity** to Air-Side (10.0.1.53:5000) and Ground-Side (10.0.1.92:5555)
3. **Python 3.x** with required dependencies
4. **Optional**: DPM_Management_System running for log queries

---

## Quick Start

### Installation

```bash
cd /home/anthony/DPM-V2/SystemTools
chmod +x pm_automation.py
```

### Basic Usage

```bash
# Run health check
python3 pm_automation.py health

# Collect diagnostics
python3 pm_automation.py diagnostics

# Check for errors
python3 pm_automation.py errors

# Generate status report
python3 pm_automation.py status

# Run complete daily workflow
python3 pm_automation.py daily
```

---

## Available Workflows

### 1. Health Check (`health`)

**Purpose**: Verify all domains are operational and healthy

**What it checks:**
- Air-Side TCP connectivity (10.0.1.53:5000)
- Ground-Side ADB connectivity (10.0.1.92:5555)
- SystemTools availability
- Overall system health

**Example Output:**
```
================================================================================
PM HEALTH CHECK - Multi-Domain System Status
================================================================================
Timestamp: 2025-11-19 15:25:20

OVERALL STATUS: ✓ HEALTHY

DOMAIN STATUS:
--------------------------------------------------------------------------------

  AIR_SIDE:
    Health: ✓ HEALTHY
    Connected: ✓ YES

  GROUND_SIDE:
    Health: ✓ HEALTHY
    Connected: ✓ YES

  SYSTEM_TOOLS:
    Health: ✓ HEALTHY
```

**When to use:**
- Start of day verification
- After system restarts
- Before critical operations
- Hourly monitoring (via cron)

---

### 2. Diagnostics Collection (`diagnostics`)

**Purpose**: Gather comprehensive system diagnostics from all domains

**What it collects:**

**Air-Side:**
- Connection status
- System status (if available)

**Ground-Side (H16):**
- Battery level
- CPU usage
- Memory usage
- Temperature

**SystemTools:**
- Log queue status
- Database status
- Filter manager status

**Example Output:**
```
================================================================================
PM DIAGNOSTICS COLLECTION
================================================================================

Collecting Air-Side diagnostics...
  ✓ Connected to Air-Side (10.0.1.53:5000)

Collecting Ground-Side diagnostics...
  ✓ Connected to Ground-Side (10.0.1.92:5555)
  ✓ H16 Diagnostics collected:
    Battery: 100%
    CPU Usage: 45%
    Memory: 512MB / 2GB
    Temperature: 62°C

Collecting SystemTools diagnostics...
  ✓ SystemTools status collected
```

**Output Format:** JSON (can be piped to file)

**When to use:**
- Troubleshooting performance issues
- Before/after major operations
- Regular monitoring intervals
- Performance baseline collection

---

### 3. Error Monitoring (`errors`)

**Purpose**: Scan recent logs across all domains for ERROR level entries

**What it monitors:**
- Air-Side ERROR logs (last 50 entries)
- Ground-Side ERROR logs (last 50 entries)
- SystemTools ERROR logs (last 50 entries)

**Example Output:**
```
================================================================================
PM ERROR MONITORING - Recent Log Analysis
================================================================================
Checking last 50 log entries per domain

Checking air-side logs...
  ✗ Found 3 ERROR entries
  Most recent errors:
    - 2025-11-19 15:20:15: Camera connection timeout
    - 2025-11-19 15:18:32: Focus command failed
    - 2025-11-19 15:15:10: Network disconnection detected

TOTAL ERRORS FOUND: 3
```

**Requirements:**
- DPM_Management_System must be running for log queries
- Log aggregation active

**When to use:**
- After testing sessions
- Debugging failures
- Daily error summary
- Incident investigation

---

### 4. Status Report (`status`)

**Purpose**: Generate comprehensive PM status report combining all workflows

**What it includes:**
1. Complete health check results
2. Full diagnostics from all domains
3. Error summary and analysis
4. Automated recommendations

**Usage:**
```bash
# Display report
python3 pm_automation.py status

# Save report to file
python3 pm_automation.py status /tmp/pm_report.json
```

**Output:** JSON format with:
- Timestamp
- Health check results
- Diagnostics data
- Error summary
- Recommendations

**When to use:**
- End of day summary
- Handoff documentation
- Issue investigation
- Performance tracking

---

### 5. Daily Workflow (`daily`)

**Purpose**: Complete automated daily PM workflow

**What it does:**
1. Runs health check
2. Collects diagnostics
3. Monitors for errors
4. Generates comprehensive report
5. Archives report with timestamp

**Usage:**
```bash
# Use default location (/tmp/pm_reports)
python3 pm_automation.py daily

# Specify custom directory
python3 pm_automation.py daily /path/to/reports
```

**Output:**
- Report file: `pm_daily_report_YYYYMMDD_HHMMSS.json`
- Console summary
- Recommendations

**Automation Example (cron):**
```bash
# Run daily at 6 AM
0 6 * * * cd /home/anthony/DPM-V2/SystemTools && python3 pm_automation.py daily /home/anthony/pm_reports

# Run every 4 hours
0 */4 * * * cd /home/anthony/DPM-V2/SystemTools && python3 pm_automation.py health
```

---

## Integration with PM Session

### Real-Time Monitoring from PM Session

```bash
# From PM tmux session, monitor TOOLS automation
watch -n 300 'cd /home/anthony/DPM-V2/SystemTools && python3 pm_automation.py health'

# Or run periodically
while true; do
  python3 pm_automation.py health
  sleep 300  # 5 minutes
done
```

### Automated Alerting

```bash
#!/bin/bash
# pm_health_alert.sh - Alert if system unhealthy

cd /home/anthony/DPM-V2/SystemTools
RESULT=$(python3 pm_automation.py health 2>&1)

if echo "$RESULT" | grep -q "UNHEALTHY"; then
  echo "ALERT: DPM System Unhealthy"
  echo "$RESULT"
  # Send notification (email, Slack, etc.)
fi
```

---

## API Usage Examples

### Python Integration

```python
from SystemTools.pm_automation import (
    pm_health_check,
    pm_collect_diagnostics,
    pm_check_errors,
    pm_status_report
)

# Run health check
health = pm_health_check(include_ground_side=True)
if not health['overall_healthy']:
    print("System unhealthy!")

# Collect diagnostics
diag = pm_collect_diagnostics(include_ground_side=True)
battery = diag['ground_side']['diagnostics']['battery']

# Check errors
errors = pm_check_errors(domains=['air-side'], limit=100)
if errors['total_errors'] > 10:
    print(f"Warning: {errors['total_errors']} errors detected")

# Generate report
report = pm_status_report(output_file='/tmp/report.json')
```

### Custom Workflows

```python
from SystemTools.api import DPMController

def custom_pm_workflow():
    """Custom PM workflow example"""
    with DPMController() as dpm:
        # Step 1: Verify Air-Side
        result = dpm.air_side.connect()
        if not result.success:
            return {"error": "Air-Side unavailable"}

        # Step 2: Run camera test
        result = dpm.air_side.send_command(
            'camera.get_properties',
            {}
        )

        # Step 3: Verify in logs
        logs = dpm.system.query_logs(
            message_filter='camera',
            limit=10
        )

        dpm.air_side.disconnect()

        return {"success": True, "logs": logs.data}
```

---

## Troubleshooting

### Issue: "Log queue not available"

**Cause**: DPM_Management_System not running
**Solution**:
```bash
# Start DPM_Management_System in SYSTEM tmux session
tmux attach -t SYSTEM
cd /home/anthony/DPM-V2/SystemTools
python3 DPM_Management_System.py
```

### Issue: "Failed to connect to Air-Side"

**Cause**: Pi 5 offline or network issue
**Solution**:
```bash
# Verify network
ping 10.0.1.53

# SSH to Pi 5 and check payload-manager
ssh dpm@10.0.1.53
docker ps | grep payload-manager
```

### Issue: "Failed to connect to Ground-Side"

**Cause**: H16 ADB not connected
**Solution**:
```bash
# Check ADB connection
adb devices

# Reconnect if needed
adb connect 10.0.1.92:5555
```

---

## Performance Metrics

**Typical Execution Times:**
- Health Check: ~3 seconds
- Diagnostics Collection: ~5 seconds
- Error Monitoring: ~2 seconds (with DPM_Management_System)
- Status Report: ~10 seconds
- Daily Workflow: ~15 seconds

**Resource Usage:**
- Memory: ~50MB peak
- CPU: <5% average
- Network: Minimal (command/response only)

---

## Best Practices

1. **Run health check** at start of each PM session
2. **Collect diagnostics** before major operations
3. **Monitor errors** after testing sessions
4. **Generate status report** at end of day
5. **Archive reports** for historical tracking
6. **Automate daily workflow** via cron for continuous monitoring

---

## Future Enhancements

Potential additions:
- [ ] Email/Slack notifications on health failures
- [ ] Performance trending and analytics
- [ ] Automated recovery actions
- [ ] Web dashboard for report visualization
- [ ] Integration with CI/CD pipeline
- [ ] Historical comparison reports

---

## Related Documentation

- **API Documentation**: `SystemTools/examples/README.md`
- **Test Results**: `SystemTools/API_TEST_RESULTS.md`
- **Example Workflows**: `SystemTools/examples/phase5_multi_domain.py`
- **Issue Tracking**: GitHub Issue #144

---

## Support

**For issues or questions:**
1. Check troubleshooting section above
2. Review API documentation
3. Check SystemTools logs: `SystemTools/logs/`
4. Create GitHub issue with label `pm-automation`

---

**Status**: ✅ PRODUCTION READY
**Last Updated**: 2025-11-19
**Version**: 1.0
