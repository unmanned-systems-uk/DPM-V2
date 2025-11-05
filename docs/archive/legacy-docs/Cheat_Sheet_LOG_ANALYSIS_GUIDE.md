# Payload Manager Log Analysis Guide

**For Air-Side (SBC) - C++ Implementation**

This guide provides useful commands for analyzing payload_manager logs for troubleshooting, debugging, and monitoring.

---

## Table of Contents

1. [Basic Log Access](#basic-log-access)
2. [Filtering by Log Level](#filtering-by-log-level)
3. [Camera-Related Logs](#camera-related-logs)
4. [Network & Protocol Logs](#network--protocol-logs)
5. [Property & Command Logs](#property--command-logs)
6. [Performance & Timing](#performance--timing)
7. [Error Analysis](#error-analysis)
8. [Real-Time Monitoring](#real-time-monitoring)
9. [Log Export & Archival](#log-export--archival)

---

## Basic Log Access

### View recent logs (last 50 lines)
```bash
docker logs payload-manager --tail 50
```

### View all logs
```bash
docker logs payload-manager
```

### Follow logs in real-time
```bash
docker logs -f payload-manager
```

### View logs with timestamps
```bash
docker logs -t payload-manager
```

### View logs from specific time
```bash
# Since timestamp
docker logs --since 2025-10-29T10:00:00 payload-manager

# Last N minutes
docker logs --since 30m payload-manager

# Last N hours
docker logs --since 2h payload-manager
```

---

## Filtering by Log Level

### Show only ERROR messages
```bash
docker logs payload-manager 2>&1 | grep "\[ERROR\]"
```

### Show ERROR and WARN messages
```bash
docker logs payload-manager 2>&1 | grep -E "\[ERROR\]|\[WARN"
```

### Show INFO messages
```bash
docker logs payload-manager 2>&1 | grep "\[INFO \]"
```

### Show DEBUG messages
```bash
docker logs payload-manager 2>&1 | grep "\[DEBUG\]"
```

### Exclude DEBUG messages (cleaner output)
```bash
docker logs payload-manager 2>&1 | grep -v "\[DEBUG\]"
```

### Count messages by level
```bash
docker logs payload-manager 2>&1 | grep -o "\[ERROR\]\|\[WARN\]\|\[INFO \]\|\[DEBUG\]" | sort | uniq -c
```

---

## Camera-Related Logs

### Camera connection status
```bash
docker logs payload-manager 2>&1 | grep -i "camera" | grep -i -E "connect|disconnect|ready"
```

### Camera errors only
```bash
docker logs payload-manager 2>&1 | grep -i "camera" | grep "\[ERROR\]"
```

### Camera property changes
```bash
docker logs payload-manager 2>&1 | grep -i "property" | grep -i "camera"
```

### ISO-related logs
```bash
docker logs payload-manager 2>&1 | grep -i "iso"
```

### Shutter speed logs
```bash
docker logs payload-manager 2>&1 | grep -i "shutter"
```

### Aperture logs
```bash
docker logs payload-manager 2>&1 | grep -i "aperture"
```

### Camera health checks
```bash
docker logs payload-manager 2>&1 | grep "health check"
```

### Show camera property get/set operations
```bash
docker logs payload-manager 2>&1 | grep -E "Getting property|Setting property|Raw SDK value"
```

### Camera callback events
```bash
docker logs payload-manager 2>&1 | grep -i "callback\|OnConnected\|OnDisconnected\|OnPropertyChanged"
```

---

## Network & Protocol Logs

### TCP connection activity
```bash
docker logs payload-manager 2>&1 | grep -i "tcp\|connection\|accepted"
```

### Show client connections
```bash
docker logs payload-manager 2>&1 | grep "Accepted connection from"
```

### UDP status broadcasts (WARNING: Very verbose)
```bash
docker logs payload-manager 2>&1 | grep "Sent UDP status"
```

### Heartbeat activity
```bash
docker logs payload-manager 2>&1 | grep -i "heartbeat"
```

### Heartbeat warnings (connection loss)
```bash
docker logs payload-manager 2>&1 | grep "No heartbeat received"
```

### Show received commands
```bash
docker logs payload-manager 2>&1 | grep "Received from"
```

### Show sent responses
```bash
docker logs payload-manager 2>&1 | grep "Sent to"
```

### Network errors
```bash
docker logs payload-manager 2>&1 | grep -E "TCP|UDP" | grep "\[ERROR\]"
```

### Dynamic IP discovery events
```bash
docker logs payload-manager 2>&1 | grep -i "dynamic ip\|broadcaster.*updated"
```

---

## Property & Command Logs

### Show all commands executed
```bash
docker logs payload-manager 2>&1 | grep "Processing command:"
```

### Show specific command type
```bash
# camera.capture commands
docker logs payload-manager 2>&1 | grep "camera.capture"

# camera.set_property commands
docker logs payload-manager 2>&1 | grep "camera.set_property"

# camera.get_properties commands
docker logs payload-manager 2>&1 | grep "camera.get_properties"

# system.get_status commands
docker logs payload-manager 2>&1 | grep "system.get_status"
```

### Show command success/failure
```bash
docker logs payload-manager 2>&1 | grep -E "status.*success|status.*error"
```

### Show property mapping operations
```bash
docker logs payload-manager 2>&1 | grep -i "mapping\|converted\|decode"
```

### Show all property get operations with values
```bash
docker logs payload-manager 2>&1 | grep "Camera property .* ="
```

---

## Performance & Timing

### Show startup sequence
```bash
docker logs payload-manager 2>&1 | head -100 | grep "\[INFO \]"
```

### Time between events (with timestamps)
```bash
docker logs -t payload-manager 2>&1 | grep -E "pattern1|pattern2"
```

### Count messages per second (rough)
```bash
docker logs -t payload-manager 2>&1 | awk '{print $1" "$2}' | cut -d. -f1 | uniq -c
```

### Show sequence numbers for UDP/Heartbeat
```bash
# UDP status sequences
docker logs payload-manager 2>&1 | grep "Sent UDP status" | tail -20

# Heartbeat sequences
docker logs payload-manager 2>&1 | grep "Sent heartbeat" | tail -20
```

---

## Error Analysis

### Show all errors
```bash
docker logs payload-manager 2>&1 | grep "\[ERROR\]"
```

### Show errors with context (5 lines before and after)
```bash
docker logs payload-manager 2>&1 | grep -B 5 -A 5 "\[ERROR\]"
```

### Show unique error messages
```bash
docker logs payload-manager 2>&1 | grep "\[ERROR\]" | sort | uniq
```

### Count error occurrences
```bash
docker logs payload-manager 2>&1 | grep "\[ERROR\]" | sort | uniq -c | sort -rn
```

### Show Sony SDK error codes
```bash
docker logs payload-manager 2>&1 | grep -i "error code:\|error: 0x"
```

### Show camera-specific errors
```bash
docker logs payload-manager 2>&1 | grep "Camera error:"
```

### Failed command analysis
```bash
docker logs payload-manager 2>&1 | grep -B 3 '"status":"error"'
```

---

## Real-Time Monitoring

### Monitor camera connection status
```bash
docker logs -f payload-manager 2>&1 | grep -i --line-buffered "camera.*connect\|camera.*disconnect"
```

### Monitor incoming commands
```bash
docker logs -f payload-manager 2>&1 | grep --line-buffered "Processing command:"
```

### Monitor errors only
```bash
docker logs -f payload-manager 2>&1 | grep --line-buffered "\[ERROR\]"
```

### Monitor errors and warnings
```bash
docker logs -f payload-manager 2>&1 | grep --line-buffered -E "\[ERROR\]|\[WARN"
```

### Monitor specific property changes (e.g., ISO)
```bash
docker logs -f payload-manager 2>&1 | grep --line-buffered -i "iso"
```

### Monitor heartbeat health
```bash
docker logs -f payload-manager 2>&1 | grep --line-buffered -i "heartbeat"
```

### Clean output - hide DEBUG messages
```bash
docker logs -f payload-manager 2>&1 | grep --line-buffered -v "\[DEBUG\]"
```

### Monitor camera commands only
```bash
docker logs -f payload-manager 2>&1 | grep --line-buffered -E "camera\.(capture|set_property|get_properties)"
```

---

## Log Export & Archival

### Save logs to file
```bash
docker logs payload-manager > payload_manager_logs_$(date +%Y%m%d_%H%M%S).log
```

### Save recent logs (last 1000 lines)
```bash
docker logs --tail 1000 payload-manager > payload_manager_recent_$(date +%Y%m%d_%H%M%S).log
```

### Save logs from specific time period
```bash
docker logs --since "2025-10-29T10:00:00" --until "2025-10-29T12:00:00" payload-manager > payload_manager_period.log
```

### Create filtered log export (errors only)
```bash
docker logs payload-manager 2>&1 | grep "\[ERROR\]" > payload_manager_errors_$(date +%Y%m%d_%H%M%S).log
```

### Create summary report
```bash
{
  echo "=== Payload Manager Log Summary ==="
  echo "Generated: $(date)"
  echo ""
  echo "=== Log Level Counts ==="
  docker logs payload-manager 2>&1 | grep -o "\[ERROR\]\|\[WARN\]\|\[INFO \]\|\[DEBUG\]" | sort | uniq -c
  echo ""
  echo "=== Recent Errors (Last 10) ==="
  docker logs payload-manager 2>&1 | grep "\[ERROR\]" | tail -10
  echo ""
  echo "=== Camera Status ==="
  docker logs payload-manager 2>&1 | grep -i "camera" | grep -E "connect|disconnect|ready" | tail -5
  echo ""
  echo "=== Network Status ==="
  docker logs payload-manager 2>&1 | grep -i "tcp\|udp\|heartbeat" | grep "\[INFO \]" | tail -5
} > payload_manager_summary_$(date +%Y%m%d_%H%M%S).txt
```

---

## Advanced Grep Patterns

### Case-insensitive search
```bash
docker logs payload-manager 2>&1 | grep -i "pattern"
```

### Multiple patterns (OR)
```bash
docker logs payload-manager 2>&1 | grep -E "pattern1|pattern2|pattern3"
```

### Inverse match (exclude pattern)
```bash
docker logs payload-manager 2>&1 | grep -v "pattern_to_exclude"
```

### Context lines (before and after)
```bash
# 3 lines before
docker logs payload-manager 2>&1 | grep -B 3 "pattern"

# 3 lines after
docker logs payload-manager 2>&1 | grep -A 3 "pattern"

# 3 lines before and after
docker logs payload-manager 2>&1 | grep -C 3 "pattern"
```

### Show line numbers
```bash
docker logs payload-manager 2>&1 | grep -n "pattern"
```

### Count matches
```bash
docker logs payload-manager 2>&1 | grep -c "pattern"
```

### Show only matching part
```bash
docker logs payload-manager 2>&1 | grep -o "pattern"
```

### Regex patterns
```bash
# Match ISO values
docker logs payload-manager 2>&1 | grep -E "iso.*[0-9]+"

# Match error codes
docker logs payload-manager 2>&1 | grep -E "error.*0x[0-9a-f]+"

# Match timestamps
docker logs payload-manager 2>&1 | grep -E "\[20[0-9]{2}-[0-9]{2}-[0-9]{2}"
```

---

## Troubleshooting Common Issues

### ISO Auto Setting Issue
```bash
# Check ISO-related commands
docker logs payload-manager 2>&1 | grep -i "iso" | grep -E "set_property|Raw SDK value"

# Check if ISO Auto is being sent
docker logs payload-manager 2>&1 | grep -i "iso.*auto"

# Check for ISO property errors
docker logs payload-manager 2>&1 | grep -i "iso" | grep "\[ERROR\]"
```

### Camera Connection Lost
```bash
# Check disconnect events
docker logs payload-manager 2>&1 | grep -i "disconnect"

# Check reconnection attempts
docker logs payload-manager 2>&1 | grep -i "reconnect"

# Check health check failures
docker logs payload-manager 2>&1 | grep "health check"
```

### Ground Station Not Receiving Status
```bash
# Check UDP broadcaster
docker logs payload-manager 2>&1 | grep "UDP.*broadcaster\|Sent UDP status" | tail -20

# Check dynamic IP updates
docker logs payload-manager 2>&1 | grep -i "ground.*ip\|broadcaster.*updated"

# Check for network errors
docker logs payload-manager 2>&1 | grep "UDP" | grep "\[ERROR\]"
```

### Commands Not Working
```bash
# Check if commands are being received
docker logs payload-manager 2>&1 | grep "Received from"

# Check command processing
docker logs payload-manager 2>&1 | grep "Processing command:"

# Check command responses
docker logs payload-manager 2>&1 | grep "Sent to.*response"

# Check for command errors
docker logs payload-manager 2>&1 | grep "Processing command:" | grep -A 5 "\[ERROR\]"
```

---

## Quick Reference Card

```bash
# Most useful commands
docker logs -f payload-manager 2>&1 | grep -v "\[DEBUG\]"  # Clean real-time view
docker logs payload-manager 2>&1 | grep "\[ERROR\]"        # All errors
docker logs payload-manager 2>&1 | grep "Processing command:"  # Commands executed
docker logs payload-manager 2>&1 | grep -i "camera.*connect"  # Camera connection
docker logs payload-manager 2>&1 | grep "heartbeat" | tail -20  # Recent heartbeats

# Save important logs
docker logs payload-manager > logs_$(date +%Y%m%d_%H%M%S).log
docker logs payload-manager 2>&1 | grep "\[ERROR\]" > errors_$(date +%Y%m%d_%H%M%S).log

# Check container status
docker ps | grep payload
docker logs payload-manager --tail 30
```

---

## Tips

1. **Use `2>&1`** to capture both stdout and stderr when piping to grep
2. **Use `--line-buffered`** with grep when using `-f` (follow mode) for real-time output
3. **Combine with `tail`** to limit output: `docker logs payload-manager 2>&1 | grep pattern | tail -50`
4. **Save filtered logs** before running diagnostics for comparison
5. **Check timestamps** with `-t` flag when analyzing timing issues
6. **Use `less`** for interactive scrolling: `docker logs payload-manager 2>&1 | grep pattern | less`
7. **Color highlighting** is automatic in most terminals - errors show in red

---

## Related Documentation

- [PROGRESS_AND_TODO.md](./PROGRESS_AND_TODO.md) - Current development status
- [ISO_AUTO_INVESTIGATION.md](./ISO_AUTO_INVESTIGATION.md) - ISO Auto issue analysis
- [CC_READ_THIS_FIRST.md](./CC_READ_THIS_FIRST.md) - Claude Code session start guide

---

**Last Updated:** 2025-10-29
**Version:** 1.0.0
**Branch:** ISO-Set-Auto-Fix
