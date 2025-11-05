# Documentation Optimization Test Plan
*Comprehensive testing strategy for optimized DPM-V2 documentation*

## 🎯 Test Objectives

Verify that the documentation optimization:
1. Maintains all critical instructions for Claude Code
2. Provides clear navigation between domains
3. Enforces Git protocol correctly
4. Supports DevTools mode switching
5. Preserves all essential information

## 📋 Test Categories

### 1. Claude Code Context Test
**Goal**: Verify Claude Code can efficiently load and navigate documentation

#### Test 1.1: Initial Load Test
```
1. Start new Claude Code session
2. Load CC_READ_THIS_FIRST.md
3. Verify file loads quickly (137 lines vs old 1977)
4. Check all sections are readable
```
**Expected**: ✅ Fast load, all sections visible

#### Test 1.2: START Command Test
```
1. Type: START
2. Verify Claude Code recognizes command
3. Check if platform selection appears
4. Test each option: START AIR, START GROUND, START TOOLS, START DOCS
```
**Expected**: ✅ Each START variant works

#### Test 1.3: Context Limit Test
```
1. Load CC_READ_THIS_FIRST.md
2. Load a domain-specific PROGRESS.md
3. Load a TODO.md
4. Verify no context warnings
```
**Expected**: ✅ No "file too large" warnings

---

### 2. Domain Navigation Test
**Goal**: Verify domain structure is clear and navigable

#### Test 2.1: Domain Discovery
```
1. From CC_READ_THIS_FIRST.md, navigate to:
   - docs/ALL_DOMAINS/
   - docs/AIR_SIDE/
   - docs/GROUND_SIDE/
   - docs/DEVELOPMENT_SIDE/
```
**Expected**: ✅ All domains accessible

#### Test 2.2: File Structure Verification
```bash
# Run structure check
tree docs/ -L 2

# Verify structure matches:
docs/
├── ALL_DOMAINS/
│   ├── MASTER_STATUS.md
│   └── SYSTEM_METRICS.md
├── AIR_SIDE/
│   ├── PROGRESS.md
│   ├── TODO.md
│   └── CURRENT_STATUS.md
├── GROUND_SIDE/
│   ├── PROGRESS.md
│   ├── TODO.md
│   └── CURRENT_STATUS.md
├── DEVELOPMENT_SIDE/
│   ├── PROGRESS.md
│   ├── TODO.md
│   └── DEVTOOLS_MODE_GUIDE.md
├── archive/
├── CC_READ_THIS_FIRST.md
└── GIT_PROTOCOL_GUIDE.md
```
**Expected**: ✅ All files present

#### Test 2.3: Cross-Reference Test
```
1. Check references from CC_READ_THIS_FIRST.md work:
   - Line 137: DEVELOPMENT_SIDE/DEVTOOLS_MODE_GUIDE.md
   - Line 138: GIT_PROTOCOL_GUIDE.md
2. Verify files exist and contain referenced content
```
**Expected**: ✅ All references valid

---

### 3. Git Protocol Test
**Goal**: Verify Git hooks work correctly

#### Test 3.1: Pre-commit Hook Test
```bash
# Make a change in sbc/
touch sbc/test.cpp
git add sbc/test.cpp
git commit

# Verify pre-commit suggests [AIR] tag
```
**Expected**: ✅ Suggests [AIR] domain tag

#### Test 3.2: Commit Message Validation
```bash
# Test valid format
git commit -m "[AIR][TEST] Test Git protocol"
# Should succeed

# Test invalid format
git commit -m "Bad commit message"
# Should fail with helpful error
```
**Expected**: ✅ Valid passes, invalid fails

#### Test 3.3: Cross-Domain Commit Test
```bash
# Modify multiple domains
touch sbc/test.cpp android/test.kt
git add .

# Try single commit
git commit -m "[ALL][TEST] Cross-domain test"
# Should succeed but warn about separate commits
```
**Expected**: ✅ Accepts [ALL] tag

---

### 4. DevTools Mode Test
**Goal**: Verify DevTools modes work

#### Test 4.1: Mode Switching
```bash
cd SystemTools/

# Test development mode
python main.py --mode development --ui gui
# Should start with debug features

# Test deployment mode
python main.py --mode deployment --ui cli
# Should start in CLI mode

# Test auto detection
python main.py --mode deployment --ui auto
# Should detect environment
```
**Expected**: ✅ Each mode works correctly

#### Test 4.2: Configuration Persistence
```bash
# Run test suite
python test_modes.py

# All tests should pass:
# - Configuration creation
# - Mode switching
# - UI modes
# - Persistence
# - Mode-specific settings
# - CLI integration
```
**Expected**: ✅ All tests pass

#### Test 4.3: CLI Interface Test
```bash
# Start CLI mode
python main.py --mode deployment --ui cli

# Test commands:
help     # Should show commands
status   # Should show status
list     # Should list protocol commands
quit     # Should exit cleanly
```
**Expected**: ✅ CLI commands work

---

### 5. Archive Integrity Test
**Goal**: Verify archived files are accessible

#### Test 5.1: Archive Structure
```bash
# Check archive exists
dir docs\archive\

# Should show:
# - 2025-11-04-optimization/
# - legacy-docs/
```
**Expected**: ✅ Archive folders present

#### Test 5.2: Backup Recovery Test
```bash
# Verify backup files exist
dir docs\archive\2025-11-04-optimization\*.back*

# Should list:
# - CC_READ_THIS_FIRST.back
# - SystemTools_PROGRESS_AND_TODO.backup
# - android_PROGRESS_AND_TODO.backup
# - sbc_PROGRESS_AND_TODO.backup
```
**Expected**: ✅ All backups present

#### Test 5.3: Legacy File Access
```bash
# Count legacy files
dir docs\archive\legacy-docs\*.md | measure

# Should show 35+ .md files
```
**Expected**: ✅ 35+ legacy files archived

---

### 6. Critical Pattern Test
**Goal**: Verify critical patterns are documented

#### Test 6.1: Callback Pattern Check
```
1. Open docs/DEVELOPMENT_SIDE/DEVTOOLS_MODE_GUIDE.md
2. Search for "Callback Chaining Pattern"
3. Verify complete example present
```
**Expected**: ✅ Pattern documented with examples

#### Test 6.2: Cross-Domain Instructions
```
1. Open docs/GIT_PROTOCOL_GUIDE.md
2. Search for "Cross-Domain Implementation"
3. Verify detailed instructions present
```
**Expected**: ✅ Instructions complete

---

## 🔄 Regression Tests

### Quick Regression Checklist
```
□ CC_READ_THIS_FIRST.md loads < 200 lines
□ START command recognized
□ All 3 domains have PROGRESS.md
□ All 3 domains have TODO.md
□ Git hooks executable
□ DevTools config.py runs without errors
□ Archive folders intact
□ No broken references in main docs
```

---

## 📊 Test Execution Matrix

| Test Category | Tests | Priority | Time | Status |
|--------------|-------|----------|------|--------|
| Claude Context | 3 | HIGH | 5 min | ⏳ Ready |
| Domain Navigation | 3 | HIGH | 5 min | ⏳ Ready |
| Git Protocol | 3 | HIGH | 10 min | ⏳ Ready |
| DevTools Modes | 3 | MEDIUM | 10 min | ⏳ Ready |
| Archive Integrity | 3 | LOW | 5 min | ⏳ Ready |
| Critical Patterns | 2 | HIGH | 5 min | ⏳ Ready |

**Total Test Time**: ~40 minutes

---

## 🎯 Test Commands Summary

### Quick Test Suite
```bash
# 1. Test documentation structure
tree docs/ -L 2

# 2. Test Git hooks
git commit -m "test" --dry-run

# 3. Test DevTools
cd SystemTools && python test_modes.py

# 4. Check file counts
echo "Main docs:" && dir docs\*.md | measure
echo "Archive:" && dir docs\archive\legacy-docs\*.md | measure

# 5. Test START simulation
cat docs/CC_READ_THIS_FIRST.md | head -20
```

### Full Test Suite
```bash
# Run all tests systematically
powershell -File test_documentation.ps1
```

---

## ✅ Success Criteria

The optimization is successful if:
1. ✅ All START commands work
2. ✅ Domain navigation is clear
3. ✅ Git hooks enforce protocol
4. ✅ DevTools modes switch correctly
5. ✅ No critical information lost
6. ✅ File sizes reduced >60%
7. ✅ No broken references
8. ✅ Callback pattern documented
9. ✅ Cross-domain instructions clear
10. ✅ All tests pass

---

## 🚨 Rollback Plan

If critical issues found:
```bash
# Restore original documentation
cp docs/archive/2025-11-04-optimization/CC_READ_THIS_FIRST.back docs/CC_READ_THIS_FIRST.md
cp docs/archive/2025-11-04-optimization/SystemTools_PROGRESS_AND_TODO.backup SystemTools/PROGRESS_AND_TODO.md
cp docs/archive/2025-11-04-optimization/android_PROGRESS_AND_TODO.backup android/docs/PROGRESS_AND_TODO.md
cp docs/archive/2025-11-04-optimization/sbc_PROGRESS_AND_TODO.backup sbc/docs/PROGRESS_AND_TODO.md

# Restore legacy docs
cp -r docs/archive/legacy-docs/* docs/
```

---

*Test plan ready for execution!*