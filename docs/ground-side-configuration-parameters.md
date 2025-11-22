# Ground-Side Configuration Parameters

**WHO:** CC-Ground-Side
**DATE:** 2025-11-19
**PURPOSE:** Comprehensive documentation of all configurable parameters in Ground-Side (Android H16)
**RELATED:** Issue #170 - Phase 1: Configuration Management API

---

## Overview

Ground-Side manages two categories of configuration:

1. **Local Settings** - Ground-Side app settings stored in DataStore (persistent preferences)
2. **Air-Side Configuration** - Remote configuration managed via `system.get_config` / `system.update_config` commands

---

## 1. Ground-Side Local Settings

These settings are stored locally on the H16 device using AndroidX DataStore and managed by `SettingsRepository.kt`. All settings persist across app restarts.

### 1.1 Network Settings

Configuration for communication with Air-Side (Raspberry Pi).

| Parameter | Type | Default | Range/Validation | Description |
|-----------|------|---------|------------------|-------------|
| `targetIp` | String | `"192.168.144.10"` | Valid IPv4 | Air-Side Pi ethernet address |
| `commandPort` | Int | `5000` | 1024-65535 | TCP command channel port |
| `statusListenPort` | Int | `5001` | 1024-65535 | UDP status broadcast port |
| `heartbeatPort` | Int | `5002` | 1024-65535 | UDP heartbeat port |
| `connectionTimeoutMs` | Long | `5000` | > 0 | TCP connection timeout (ms) |
| `heartbeatIntervalMs` | Long | `1000` | > 0 | Heartbeat send interval (ms) |
| `statusBroadcastIntervalMs` | Long | `200` | > 0 | Expected status update interval (ms) |

**Data Model:** `NetworkSettings.kt`
**Storage:** DataStore preferences `network_settings`
**Access:** `SettingsRepository.networkSettingsFlow`

---

### 1.2 Video Stream Settings

RTSP video player configuration.

| Parameter | Type | Default | Options | Description |
|-----------|------|---------|---------|-------------|
| `enabled` | Boolean | `true` | - | Enable/disable video display |
| `rtspUrl` | String | `"rtsp://192.168.1.10:8554/H264Video"` | Valid RTSP URL | Camera RTSP stream URL |
| `aspectRatioMode` | Enum | `FILL` | AUTO, FILL, FIT | Video display mode |
| `bufferDurationMs` | Long | `500` | > 0 | ExoPlayer buffer duration (ms) |

**Data Model:** `VideoStreamSettings.kt`
**Storage:** DataStore preferences
**Access:** `SettingsRepository.videoSettingsFlow`

---

### 1.3 Camera Property Query Settings

Settings for periodic camera property querying.

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `propertyQueryFrequency` | Float | `0.5` Hz | > 0 | Property refresh rate (0.5Hz = every 2 seconds) |
| `propertyQueryEnabled` | Boolean | `true` | - | Enable/disable periodic property queries |

**Storage:** DataStore preferences
**Access:** `SettingsRepository.propertyQueryFrequencyFlow`, `propertyQueryEnabledFlow`

---

### 1.4 Connection Management Settings

Auto-connect and auto-reconnect behavior.

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `autoConnectEnabled` | Boolean | `true` | - | Connect to Air-Side on app startup |
| `autoReconnectEnabled` | Boolean | `true` | - | Auto-reconnect on connection loss |
| `autoReconnectIntervalSeconds` | Int | `5` | > 0 | Seconds between reconnect attempts |

**Storage:** DataStore preferences
**Access:** `SettingsRepository.autoConnectEnabledFlow`, `autoReconnectEnabledFlow`, `autoReconnectIntervalFlow`
**Behavior:** Managed by `NetworkManager.configureAutoReconnect()`

---

### 1.5 Protocol Settings

Protocol identification settings.

| Parameter | Type | Default | Options | Description |
|-----------|------|---------|---------|-------------|
| `clientId` | String | `"H16"` | Any string | Client identifier sent in protocol handshake |

**Storage:** DataStore preferences
**Access:** `SettingsRepository.clientIdFlow`
**Usage:** Passed to `NetworkManager.initialize(context, settings, clientId)`

---

### 1.6 SystemTools Logging Settings

Integration with SystemTools log aggregator.

| Parameter | Type | Default | Validation | Description |
|-----------|------|---------|------------|-------------|
| `systemToolsLogHost` | String | `"localhost"` | Valid hostname/IP | SystemTools TCP host (use "localhost" with ADB reverse) |
| `systemToolsLogPort` | Int | `5008` | 1024-65535 | SystemTools TCP port |
| `systemToolsLogEnabled` | Boolean | `true` | - | Enable network logging to SystemTools |

**Storage:** DataStore preferences
**Access:** `SettingsRepository.systemToolsLogHostFlow`, `systemToolsLogPortFlow`, `systemToolsLogEnabledFlow`
**Setup:** Requires `adb reverse tcp:5008 tcp:5008` for localhost routing
**Alternative:** Set `systemToolsLogHost` to dev machine IP (e.g., `"10.0.1.83"`) for direct connection

**Related Components:**
- `NetworkSink.kt` - TCP client for log transmission
- `StructuredLogger.kt` - Multi-sink logging system

---

### 1.7 Logging Control Settings

Dynamic control of logging output destinations.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `androidLogcatEnabled` | Boolean | `true` | Enable Android Log.d() output (always safe) |
| `structuredLoggingEnabled` | Boolean | `true` | Enable Timber → SystemTools logging |

**Storage:** DataStore preferences
**Access:** `SettingsRepository.androidLogcatEnabledFlow`, `structuredLoggingEnabledFlow`
**Usage:** `LogHelper.kt` dynamically enables/disables logging sinks
**Safety:** Both enabled by default - disable Log.d() only after Timber proven reliable

---

## 2. Air-Side Configuration Management

Ground-Side can retrieve and update Air-Side configuration via the Configuration Manager API. These settings are stored on Air-Side and affect Air-Side behavior.

### 2.1 Configuration Manager API

**Implementation:** `NetworkClient.kt` (lines 323-351), `NetworkManager.kt` (lines 121-147)
**Protocol Commands:** `system.get_config`, `system.update_config`
**ViewModel:** `AdvancedSettingsViewModel.kt` - UI for config management
**Issue:** #170 - Phase 1: Configuration Management

**API Methods:**

```kotlin
// Retrieve complete Air-Side configuration
suspend fun NetworkClient.getConfig(): Result<ResponsePayload>
suspend fun NetworkManager.getConfig(): Result<ResponsePayload>

// Update Air-Side configuration (nested key format)
suspend fun NetworkClient.updateConfig(updates: Map<String, Any>): Result<ResponsePayload>
suspend fun NetworkManager.updateConfig(updates: Map<String, Any>): Result<ResponsePayload>
```

**Response Format (get_config):**
```json
{
  "status": "success",
  "result": {
    "config": {
      "network": { ... },
      "timing": { ... },
      "logging": { ... },
      "health": { ... }
    }
  }
}
```

**Request Format (update_config):**
```json
{
  "command": "system.update_config",
  "parameters": {
    "updates": {
      "network.tcp_port": 5001,
      "logging.level": "DEBUG"
    }
  }
}
```

---

### 2.2 Air-Side Network Configuration

Configuration for Air-Side network communication.

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `network.tcp_port` | Int | `9001` | 1024-65535 | Air-Side TCP command port |
| `network.udp_status_port` | Int | `9002` | 1024-65535 | Air-Side UDP status broadcast port |
| `network.udp_heartbeat_port` | Int | `9003` | 1024-65535 | Air-Side UDP heartbeat port |
| `network.ground_ip` | String | `"192.168.144.11"` | Valid IPv4 | Ground-Side IP address for targeting |

**Data Model:** `NetworkConfig` in `AirSideConfig.kt` (lines 53-105)
**Validation:** Port range 1024-65535, IPv4 format validation
**Restart Required:** Yes - network changes require Air-Side restart

---

### 2.3 Air-Side Timing Configuration

Timing intervals for Air-Side operations.

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `timing.status_interval_ms` | Int | `200` | 50-5000 | Status broadcast interval (ms) |
| `timing.heartbeat_interval_ms` | Int | `1000` | 500-5000 | Heartbeat send interval (ms) |
| `timing.heartbeat_timeout_sec` | Int | `5` | 1-60 | Heartbeat timeout (seconds) |
| `timing.reconnect_interval_ms` | Int | `1000` | 500-5000 | Reconnect attempt interval (ms) |

**Data Model:** `TimingConfig` in `AirSideConfig.kt` (lines 110-153)
**Validation:** Range validation enforced
**Restart Required:** Yes - timing changes require Air-Side restart

---

### 2.4 Air-Side Logging Configuration

Logging behavior on Air-Side.

| Parameter | Type | Default | Options | Description |
|-----------|------|---------|---------|-------------|
| `logging.log_level` | String | `"INFO"` | DEBUG, INFO, WARNING, ERROR | Minimum log level |
| `logging.file_logging_enabled` | Boolean | `true` | - | Enable file logging on Air-Side |
| `logging.file_max_size_mb` | Int | `50` | 10-500 | Max log file size (MB) |
| `logging.network_logging_enabled` | Boolean | `true` | - | Enable network log streaming |

**Data Model:** `LoggingConfig` in `AirSideConfig.kt` (lines 158-192)
**Validation:** Log level enum, file size range
**Restart Required:** Partial - `log_level` and `file_logging_enabled` require restart

---

### 2.5 Air-Side Health Configuration

Health monitoring settings on Air-Side.

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `health.broadcast_enabled` | Boolean | `true` | - | Enable health status broadcasts |
| `health.broadcast_interval_sec` | Int | `5` | 1-60 | Health broadcast interval (seconds) |
| `health.history_duration_min` | Int | `60` | 10-120 | Health history retention (minutes) |

**Data Model:** `HealthConfig` in `AirSideConfig.kt` (lines 197-228)
**Validation:** Interval and duration range validation
**Restart Required:** No - health settings can be changed at runtime

---

## 3. Configuration Persistence

### 3.1 Ground-Side Persistence

- **Technology:** AndroidX DataStore (Preferences)
- **File:** `/data/data/uk.unmannedsystems.dpm_android/files/datastore/network_settings.preferences_pb`
- **Scope:** Per-device, survives app restarts and updates
- **Access:** Via `SettingsRepository.kt` Kotlin Flows
- **Reset:** `SettingsRepository.resetToDefaults()`

### 3.2 Air-Side Persistence

- **Technology:** JSON configuration files
- **Files:**
  - `config/default.json` - Default configuration (read-only)
  - `config/development.json` - Runtime overrides (read/write)
- **Merge Strategy:** Development overrides default
- **Access:** Via `system.get_config` / `system.update_config` commands
- **Reset:** Delete `development.json` to revert to defaults

---

## 4. Configuration Validation

### 4.1 Ground-Side Validation

Ground-Side performs client-side validation before sending updates:

**Validation Rules:**
- All Air-Side config validated via `AirSideConfig.validate()` method
- Individual section validation: `NetworkConfig.validate()`, `TimingConfig.validate()`, etc.
- Validation errors displayed in UI before save
- Save operation blocked if validation fails

**Implementation:** `AdvancedSettingsViewModel.saveConfig()` (lines 192-265)

### 4.2 Air-Side Validation

Air-Side performs server-side validation on received updates:

**Validation Rules:**
- Type checking (int, string, bool)
- Range validation (ports, intervals, sizes)
- Format validation (IP addresses, log levels)
- Invalid updates rejected with error response

**Response Format (validation failure):**
```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid port range: 99999"
  }
}
```

---

## 5. Configuration UI

### 5.1 Basic Settings Screen

**File:** `SettingsScreen.kt`
**Settings:**
- Network connection (IP, ports)
- Auto-connect/reconnect
- Video stream settings
- Property query frequency

**Access:** Main menu → Settings

### 5.2 Advanced Settings Screen

**File:** `AdvancedSettingsScreen.kt`
**ViewModel:** `AdvancedSettingsViewModel.kt`
**Settings:**
- Air-Side configuration (network, timing, logging, health)
- SystemTools integration
- Configuration export/import
- Reset to defaults

**Features:**
- Real-time validation
- Unsaved changes tracking
- Restart required warnings
- JSON export/import

**Access:** Settings → Advanced Settings

---

## 6. Configuration Testing

### 6.1 Test Procedures

**Ground-Side Local Settings:**
1. Connect ADB: `adb connect 10.0.1.92:5555`
2. Open Settings UI
3. Modify settings
4. Verify persistence: Force-stop app and relaunch
5. Verify DataStore: `adb shell cat /data/data/uk.unmannedsystems.dpm_android/files/datastore/network_settings.preferences_pb`

**Air-Side Configuration:**
1. Connect to Air-Side
2. Fetch config: `ground_side.get_config()`
3. Verify response contains all sections
4. Update config: `ground_side.update_config({"logging.level": "DEBUG"})`
5. Verify changes persist: Check `config/development.json` on Air-Side
6. Test restart required flag: Update network settings

### 6.2 Test Coverage

**Test Categories:**
- [ ] Ground-Side settings persistence across app restarts
- [ ] Air-Side config get/update roundtrip
- [ ] Validation error handling (client and server)
- [ ] Restart required detection
- [ ] SystemTools logging integration
- [ ] Configuration export/import

**Status:** Implementation complete, testing blocked by H16 device offline (ADB connection failed)

---

## 7. Related Files

### Ground-Side Implementation

| File | Purpose |
|------|---------|
| `NetworkClient.kt` | Config API methods (lines 323-351) |
| `NetworkManager.kt` | Config API wrappers (lines 121-147) |
| `AdvancedSettingsViewModel.kt` | Config management logic |
| `AdvancedSettingsScreen.kt` | Config UI |
| `SettingsRepository.kt` | DataStore persistence |
| `NetworkSettings.kt` | Network settings model |
| `AirSideConfig.kt` | Air-Side config model + validation |

### Air-Side Implementation

| File | Purpose |
|------|---------|
| `protocol/commands.json` | Command specifications (lines 279, 370) |
| `air_side/config/default.json` | Default Air-Side configuration |
| `air_side/config/development.json` | Runtime configuration overrides |

### Documentation

| File | Purpose |
|------|---------|
| `docs/ground-side-configuration-parameters.md` | This document |
| `docs/architecture/view-logical.md` | Architecture overview |
| `docs/architecture/c4-level3-ground-side-components-UPDATED-20251118.puml` | Component diagram |

---

## 8. Future Enhancements

### Planned Features (Issue #170 - Future Phases)

1. **Configuration Profiles**
   - Save/load named configuration profiles
   - Quick switch between development/production/testing configs

2. **Configuration Sync**
   - Automatic sync on connection
   - Conflict resolution strategies

3. **Configuration History**
   - Track configuration changes over time
   - Rollback to previous configurations

4. **Configuration Validation UI**
   - Real-time validation feedback
   - Suggested values for common scenarios

5. **Bulk Configuration Management**
   - Multi-device configuration deployment
   - Configuration templates

---

## Appendix A: Default Values Summary

### Ground-Side Defaults

```kotlin
// Network
targetIp = "192.168.144.10"
commandPort = 5000
statusListenPort = 5001
heartbeatPort = 5002
connectionTimeoutMs = 5000L
heartbeatIntervalMs = 1000L
statusBroadcastIntervalMs = 200L

// Video
videoEnabled = true
rtspUrl = "rtsp://192.168.1.10:8554/H264Video"
aspectRatioMode = FILL
bufferDurationMs = 500L

// Camera
propertyQueryFrequency = 0.5f Hz
propertyQueryEnabled = true

// Connection
autoConnectEnabled = true
autoReconnectEnabled = true
autoReconnectIntervalSeconds = 5

// Protocol
clientId = "H16"

// SystemTools
systemToolsLogHost = "localhost"
systemToolsLogPort = 5008
systemToolsLogEnabled = true

// Logging Control
androidLogcatEnabled = true
structuredLoggingEnabled = true
```

### Air-Side Defaults

```json
{
  "network": {
    "tcp_port": 9001,
    "udp_status_port": 9002,
    "udp_heartbeat_port": 9003,
    "ground_ip": "192.168.144.11"
  },
  "timing": {
    "status_interval_ms": 200,
    "heartbeat_interval_ms": 1000,
    "heartbeat_timeout_sec": 5,
    "reconnect_interval_ms": 1000
  },
  "logging": {
    "log_level": "INFO",
    "file_logging_enabled": true,
    "file_max_size_mb": 50,
    "network_logging_enabled": true
  },
  "health": {
    "broadcast_enabled": true,
    "broadcast_interval_sec": 5,
    "history_duration_min": 60
  }
}
```

---

**END OF DOCUMENT**
