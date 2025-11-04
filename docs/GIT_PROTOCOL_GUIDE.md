# Git Protocol Guide
*Domain-based commit standards for DPM-V2 project*
*Implemented: 2025-11-04*

## 🎯 Overview

This project enforces domain-based commit messages to:
- Track which platform is being modified
- Maintain clear change history
- Enable better cross-domain coordination
- Facilitate automated changelog generation

## 📝 Commit Message Format

### Required Format
```
[DOMAIN][TYPE] Brief description (max 72 chars)

Detailed explanation of changes (optional)
- Bullet point 1
- Bullet point 2

Affects: [Other domains impacted]
Tested: [How it was tested]
```

## 🏷️ Domain Tags

| Tag | Domain | Description |
|-----|--------|-------------|
| `[AIR]` | Air-Side | Pi 5 SBC, C++ code, Sony SDK |
| `[GROUND]` | Ground-Side | H16 Android app, Kotlin/Java |
| `[TOOLS]` | SystemTools | Python diagnostic tools |
| `[DOCS]` | Documentation | Markdown, protocol specs |
| `[ALL]` | All Domains | Changes affecting multiple domains |

## 🔧 Type Tags

| Tag | Purpose | Use When |
|-----|---------|----------|
| `[FEATURE]` | New functionality | Adding new capabilities |
| `[FIX]` | Bug fix | Resolving issues |
| `[REFACTOR]` | Code restructuring | Improving code quality |
| `[PROTOCOL]` | Protocol changes | Modifying communication specs |
| `[TEST]` | Testing | Adding/modifying tests |
| `[BUILD]` | Build system | CMake, Gradle, Docker changes |
| `[WIP]` | Work in progress | Incomplete changes |

## ✅ Good Examples

### Air-Side Feature
```
[AIR][FEATURE] Add thermal camera support via Sony SDK

- Implemented thermal imaging capture mode
- Added temperature data to UDP status broadcast
- Created thermal calibration routine

Affects: [GROUND] needs UI for thermal display
Tested: Sony thermal module on Pi 5
```

### Ground-Side Fix
```
[GROUND][FIX] Resolve touch gesture conflicts on H16

- Fixed pinch-zoom interfering with pan gestures
- Added gesture priority handling
- Improved touch responsiveness

Affects: None
Tested: H16 physical device
```

### Cross-Domain Protocol Change
```
[ALL][PROTOCOL] Update heartbeat to v1.2.0

- Added connection strength field
- Changed timeout from 10s to 15s
- Backward compatible with v1.1.0

Affects: All domains must update
Tested: Integration test with all platforms
```

### Documentation Update
```
[DOCS][REFACTOR] Optimize documentation structure

- Split monolithic files into domain-specific docs
- Reduced total size by 63%
- Improved navigation hierarchy

Affects: All developers
Tested: Claude Code context analysis
```

## ❌ Bad Examples

### Missing Domain Tag
```
Add camera feature  ❌

Should be: [AIR][FEATURE] Add camera feature
```

### Missing Type Tag
```
[AIR] Fix memory leak  ❌

Should be: [AIR][FIX] Fix memory leak
```

### Too Long First Line
```
[AIR][FEATURE] Implement comprehensive camera control system with multiple exposure modes, focus control, and advanced settings  ❌

Should be: [AIR][FEATURE] Add comprehensive camera control system
(Then add details in the body)
```

## 🔨 Automatic Enforcement

### Git Hooks Installed
1. **pre-commit** - Suggests appropriate domain tags based on changed files
2. **commit-msg** - Validates format and provides helpful feedback

### What Happens on Commit

1. **Pre-commit hook runs:**
   - Analyzes which files changed
   - Suggests appropriate domain tag
   - Shows type tag options

2. **You write commit message:**
   - Uses suggested format
   - Or opens template with guidelines

3. **Commit-msg hook validates:**
   - Checks for domain tag
   - Checks for type tag
   - Warns if line too long
   - Confirms success

## 🚀 Quick Start

### Using Command Line
```bash
git commit -m "[AIR][FEATURE] Add new feature"
```

### Using Template (Recommended)
```bash
git commit  # Opens template with guidelines
```

### Template Contents
The template (`.gitmessage`) includes:
- Format reminder
- All valid tags
- Example structure
- Cross-domain impact section

## 📊 Domain Detection

The pre-commit hook automatically detects:
- **Air-Side**: Changes in `sbc/` or `protocol/`
- **Ground-Side**: Changes in `android/`
- **SystemTools**: Changes in `SystemTools/`
- **Documentation**: Changes in `docs/` or `*.md` files

## 🔄 Multi-Domain Changes

When changes affect multiple domains:

### Option 1: Use [ALL] Tag
```
[ALL][PROTOCOL] Update command interface

Changes affect all platforms...
```

### Option 2: Multiple Commits (Preferred)
```bash
# Commit air-side changes
git add sbc/
git commit -m "[AIR][PROTOCOL] Implement new command"

# Commit ground-side changes
git add android/
git commit -m "[GROUND][PROTOCOL] Add UI for new command"
```

## 🛠️ Troubleshooting

### Hook Not Running
```bash
# Make hooks executable
chmod +x .git/hooks/pre-commit
chmod +x .git/hooks/commit-msg
```

### Bypass Hooks (Emergency Only)
```bash
git commit --no-verify -m "Emergency fix"
```

### View Current Configuration
```bash
git config --get commit.template  # Should show .gitmessage
ls -la .git/hooks/  # Should show executable hooks
```

## 📈 Benefits

### For Developers
- Clear guidance on commit format
- Automatic validation
- Helpful error messages
- Template with examples

### For Project Management
- Track work by domain
- Generate domain-specific changelogs
- Identify cross-domain impacts
- Measure activity per platform

### For CI/CD
- Trigger domain-specific builds
- Route notifications to teams
- Generate release notes
- Track deployment readiness

## 📋 Cheat Sheet

```
[AIR][FEATURE]    - New air-side feature
[AIR][FIX]        - Air-side bug fix
[GROUND][FEATURE] - New Android feature
[GROUND][FIX]     - Android bug fix
[TOOLS][FEATURE]  - New diagnostic tool
[TOOLS][FIX]      - Tool bug fix
[DOCS][REFACTOR]  - Documentation improvement
[ALL][PROTOCOL]   - Protocol affecting all
[ALL][BUILD]      - Build system for all
```

---
*Git hooks are in `.git/hooks/`*
*Template is in `.gitmessage`*
*This guide is in `docs/GIT_PROTOCOL_GUIDE.md`*