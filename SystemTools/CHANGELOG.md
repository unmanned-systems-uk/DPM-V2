# DPM Diagnostic Tool - Changelog

All notable changes to the DPM Diagnostic Tool (SystemTools) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.7.0] - 2025-11-05

### Added
- **SFTP Log File Download**: New "Download Log File..." button in Log Inspector tab
  - Download application logs directly from Air-Side Pi to Windows PC
  - Background download with progress indication
  - File size reporting after successful download
- **SSH Client Enhancements**:
  - `download_file()` method for SFTP file transfer
  - `list_directory()` method for remote file listing
  - Progress callback support for future progress bar feature

### Changed
- Log Inspector tab now supports both Docker logs viewing and direct file download
- Enhanced SSH client with SFTP session support via paramiko

### Fixed
- Coordinated with Air-Side logging fix (see Air-Side CHANGELOG)
- Application log path corrected to enable file-based logging

### Documentation
- Added `/docs/LOG_DOWNLOAD_SOLUTION.md` - Complete technical guide
- Added `/docs/QUICK_START_LOG_DOWNLOAD.md` - Quick reference card

### Integration Notes
- Requires Air-Side container rebuild for logging to work
- Downloads from: `/home/dpm/DPM-V2/sbc/logs/payload_manager.log`
- Compatible with Air-Side v2.6+

---

## [1.6.0] - 2025-11-XX (Issue#5)

### Notes
- Version exists on deployed instances but not documented in repository
- Features and changes to be documented retroactively
- Likely includes enhancements between v1.5.4 and current release

---

## [1.5.4] - 2025-10-31

### Added
- Phase 3: H16 Logcat Search & Filter functionality
- Enhanced Android device diagnostics

### Status
- Phase 1: Complete (100%)
- Phase 2: Complete (100%)
- Overall Completion: 60%

---

## Version Numbering

**Format:** `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes or significant architecture changes
- **MINOR**: New features, backwards-compatible
- **PATCH**: Bug fixes, small improvements

**Current Protocol Version:** 1.1.0 (Heartbeat spec)

---

## Cross-Platform Coordination

### Air-Side Dependencies
- v1.7.0 requires Air-Side container rebuild for log file access
- Log path fix in `sbc/src/config.h` (see Air-Side commit 10ba985)

### Protocol Compatibility
- Heartbeat spec: v1.1.0
- Command protocol: v1.0
- Maintains backwards compatibility with earlier Air-Side versions (viewing only)

---

## Upcoming Features

### Planned for v1.8.0
- Progress bar for SFTP downloads
- Multi-file download support
- Automatic log archiving per-flight
- RTC battery status monitoring

### Planned for v2.0.0
- Real-time log streaming
- Enhanced camera control interface
- Flight mission planning integration
