# DPM - Drone Payload Manager

Professional UAV payload management system for Sony camera control via SkyDroid H16 Pro.

## Architecture
- **Air-Side:** Raspberry Pi 5 + Sony Camera (C++17)
- **Ground-Side:** SkyDroid H16 (Android/Kotlin)
- **Link:** H16 R16 digital data-link

## Quick Start

### Requirements
- Raspberry Pi 5 8GB
- Ubuntu 24.04 LTS ARM64
- Sony Camera Remote SDK v2.00.00
- Docker

## 📋 SESSION START CHECKLIST FOR AIR-SIDE

**Every time you (Claude Code) start working, follow these steps in: `sbc/docs/CC_READ_THIS_FIRST.md` **
## 📋 SESSION START CHECKLIST FOR Ground-Side

**Every time you (Claude Code) start working, follow these steps in: `android/docs/CC_READ_THIS_FIRST.md` **

### Build
```bash
cd sbc
./build_container.sh
./run_container.sh prod
```

## Documentation
Air-Side See `sbc/docs/` for complete documentation.
Ground-Side See `android/docs/` for complete documentation
Common See `~/docs`
EOF