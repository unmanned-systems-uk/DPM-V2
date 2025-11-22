# Common Commands Reference

**Purpose:** Frequently used commands across all domains

**Referenced by:** `.claude/SESSION_START.md`

---

## GitHub Issue Commands

### Checking Issues
```bash
# List open issues for your domain
gh issue list --state open --label air-side
gh issue list --state open --label ground-side
gh issue list --state open --label dev-tools

# Check in-progress issues
gh issue list --label status:in-progress --state open

# List all open issues
gh issue list --state open

# View specific issue with comments
gh issue view <#> --comments
```

### Historical Search
```bash
# Search all issues (open and closed)
gh issue list --search "camera focus" --state all
gh issue list --search "reconnect" --state all
gh issue list --search "[keyword]" --state all

# Search by label
gh issue list --search "label:air-side" --state all
gh issue list --search "label:priority:critical" --state all
```

### Updating Issues
```bash
# Change issue title
gh issue edit <#> --title "[FIXING] New title"
gh issue edit <#> --title "[FIXED] New title"

# Add comment
gh issue comment <#> --body "**WHO:** CC-[Domain]

Your comment here"

# Add comment from file
gh issue comment <#> --body-file comment.md
```

---

## Domain Workflow Commands

### Air-Side (Pi 5 C++)
```bash
# Navigate to domain
cd ~/DPM-V2/sbc

# Build
cmake -B build -S .
cmake --build build

# Run tests
cd build && ctest

# Check Docker container
docker ps
docker logs payload-manager
docker restart payload-manager

# Platform verification
cat /proc/device-tree/model
uname -m
```

### Ground-Side (Android Kotlin)
```bash
# Navigate to domain
cd ~/DPM-V2/android

# Build app
./gradlew assembleDebug

# Install app (via ADB)
adb devices
adb connect 10.0.1.92:5555
adb install -r app/build/outputs/apk/debug/app-debug.apk

# View logs
adb logcat -s DPM
adb logcat -s DPM | grep ERROR

# Clear app data
adb shell pm clear uk.unmannedsystems.dpm_android
```

### SystemTools (Python)
```bash
# Navigate to domain
cd ~/DPM-V2/SystemTools

# Run main GUI
python3 DPM_Management_System.py

# Run log aggregator
python3 log_aggregator.py

# Run CLI interface
python3 cli_interface.py

# Check Python version
python3 --version
```

---

## Git Commands

### Status & Log
```bash
# Check status
git status
git status --short

# View log
git log --oneline -10
git log --oneline --graph -20

# Check unpushed commits
git log origin/$(git branch --show-current)..HEAD

# View specific commit
git show <commit-hash>
```

### Working with Changes
```bash
# View changes
git diff
git diff --staged
git diff HEAD~1

# Stage files
git add .
git add <file>

# Commit
git commit -m "[DOMAIN][TYPE] Description"

# Push
git push
git push -u origin <branch>
```

### Branching
```bash
# List branches
git branch
git branch -a

# Create branch
git checkout -b feature/description

# Switch branch
git checkout <branch>

# Pull latest
git pull origin main
```

---

## Network & Connectivity

### Check Connectivity
```bash
# Check Pi 5 (Air-Side)
ping -c 1 10.0.1.53

# Check H16 (Ground-Side)
ping -c 1 10.0.1.92
adb devices | grep 10.0.1.92

# Check Jetson (future)
ping -c 1 10.0.1.113
```

### Network Status
```bash
# Check open ports
sudo netstat -tulpn | grep LISTEN

# Check UDP listeners
sudo netstat -ulpn

# Check TCP connections
sudo netstat -tnp
```

---

## File & Directory Commands

### Navigation
```bash
# Show current directory
pwd

# List files
ls -la
ls -lh

# Find files
find . -name "*.cpp"
find . -name "*.kt"
find . -name "*.py"
```

### Searching Content
```bash
# Search in files
grep -r "pattern" .
grep -r "LogContext" sbc/src/

# Search with line numbers
grep -rn "pattern" .

# Case insensitive
grep -ri "pattern" .
```

---

## Protocol & Documentation

### View Protocol Files
```bash
# List protocol files
ls -lh protocol/

# View specific protocol
cat protocol/log_contexts.json
cat protocol/commands.json
cat protocol/camera_properties.json
```

### Quick Documentation Lookup
```bash
# View critical rules
cat .claude/RULES_CRITICAL.md

# View domain rules
cat .claude/DOMAIN_AGENT_RULES.md

# View lessons learned
cat docs/ALL_DOMAINS/LESSONS_LEARNED.md

# Search lessons
grep -i "camera" docs/ALL_DOMAINS/LESSONS_LEARNED.md
```

---

## PM-Specific Commands

### tmux Monitoring
```bash
# List sessions
tmux list-sessions

# Capture pane output
tmux capture-pane -t DPM-AIR -p | tail -30
tmux capture-pane -t DPM-GROUND -p | tail -30
tmux capture-pane -t DPM-TOOLS -p | tail -30

# Send message to PM
tmux send-keys -t DPM-PM "Message" C-m
```

### Multi-Domain Status
```bash
# Check all domain issues
gh issue list --state open --label air-side
gh issue list --state open --label ground-side
gh issue list --state open --label dev-tools

# Check critical issues across all domains
gh issue list --label priority:critical --state open
```

---

## Quick Diagnostics

### System Info
```bash
# Check system
uname -a
uname -m

# Check uptime
uptime

# Check disk space
df -h

# Check memory
free -h

# Check processes
ps aux | grep python
ps aux | grep java
ps aux | grep cmake
```

### Check Services
```bash
# Docker
docker ps
docker ps -a

# ADB
adb devices
adb version

# Python
python3 --version
which python3

# Git
git --version
```

---

## Common Patterns

### Before Starting Work
```bash
cd ~/DPM-V2
git status
git pull origin main
gh issue list --state open --label [your-domain]
```

### After Completing Work
```bash
git status
git add .
git commit -m "[DOMAIN][TYPE] Description - Issue #XX"
git push
gh issue comment <#> --body "**WHO:** CC-[Domain]\n\nWork complete"
```

### When Stuck
```bash
# Search history
gh issue list --search "[keyword]" --state all

# Check lessons learned
grep -i "[keyword]" docs/ALL_DOMAINS/LESSONS_LEARNED.md

# Read domain docs
cat .claude/commands/start-[domain].md
```

---

**Last Updated:** 2025-11-22
**See Also:**
- `.claude/GIT_WORKFLOW.md` - Git procedures
- `.claude/DOC_STRUCTURE.md` - Documentation guide
