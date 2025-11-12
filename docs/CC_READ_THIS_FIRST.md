# DPM-V2 Claude Code Guide - OPTIMIZED v3.0
*Compression-Resistant | Tiered Rules | Emergency Recovery*

---

## 🔴 TIER 1: CRITICAL (NEVER FORGET)
**These 5 rules survive ALL compressions:**

1. **NEVER close GitHub issues** - Only user closes
2. **ALWAYS search history first** - Don't repeat failures
3. **WHO tags MANDATORY** - Every comment starts with `**WHO:** CC-[Domain]`
4. **NEVER work without issue** - Create/find issue first
5. **Rule 11: Cross-domain approval** - Never modify other domain's code

**Compressed? Lost rules?** → `.claude/RULES_CRITICAL.md`

---

## 📋 COMPRESSION CHECKPOINT
**Reading after compression? Quick recovery:**
```bash
cat .claude/RULES_CRITICAL.md        # 100 lines max
cat .claude/COMPRESSION_EMERGENCY.md  # 50 lines max
gh issue list --state open           # What needs work?
```

---

## 🎯 TIER 2: DOMAIN ESSENTIALS

### Quick Domain Reference
| Domain | Platform | Code | Location | Port |
|--------|----------|------|----------|------|
| **Air-Side** | Pi 5 | C++/Sony SDK | `sbc/` | Send UDP 9002 |
| **Ground-Side** | H16 Android | Kotlin | `android/` | TCP 9001, UDP 9002 |
| **Dev-Tools** | Cross-platform | Python | `SystemTools/` | Diagnostics |
| **PM** | Coordination | N/A | All domains | GitHub/Docs |

### Quick Start Commands
```bash
START AIR     # Air-side session
START GROUND  # Ground-side session
START TOOLS   # Dev-tools session
START PM      # Project Manager session
EOD           # End-of-day reflection
```

---

## 🔄 TIER 3: WORKFLOWS

### Issue State Machine
```
[FIX] → [FIXING] → [FIXED] → CLOSED
      ↑ Start NOW  ↑ Tested  ↑ User only

# When starting (IMMEDIATELY, not EOD):
gh issue edit <#> --title "[FIXING] Title"
```

### Historical Search Protocol
```bash
# MANDATORY before ANY implementation:
gh issue list --search "keyword" --state all
gh issue view <#> --comments | grep "failed\|didn't work"

# Document findings:
"Found #1 tried X (failed), #2 tried Y (failed).
I'll try Z because [different approach]"
```

### WHO Tag Examples
```markdown
**WHO:** CC-Air-Side
Air-Side complete. Ground-Side needs to parse new field.

**WHO:** CC-Ground-Side
Parsing added. Testing with mock data.

**WHO:** User (Anthony)
Tested. Works perfectly.
```

---

## 📁 TIER 4: ARCHITECTURE

### Protocol Single Source
```
protocol/
├── commands.json          # Command definitions
└── camera_properties.json  # Property specs
```

### Critical Documentation
```
docs/ALL_DOMAINS/
├── LESSONS_LEARNED.md     # What failed/worked
├── WHO_TAG_GUIDE.md       # WHO tag reference
└── MASTER_STATUS.md       # Overall status

docs/AIR_SIDE/CrSDK_API_Reference_v2.00.00/  # Sony SDK
```

---

## 🏷️ TIER 5: CONVENTIONS

### Git Commits
```
[DOMAIN][TYPE] Description
[AIR][FIX] Focus distance calculation
[GROUND][FEATURE] Add gimbal UI
[PM][DOCS] Update lessons learned
```

### Testing Workflow
1. CC implements → provides test instructions
2. User tests → reports success/failure
3. CC asks → "Ready to mark [FIXED]?"
4. User confirms → CC updates labels
5. User decides → Close issue or keep open

---

## 🚨 PM ROLE SPECIAL RULES

### PM Can:
- ✅ Read any file in any domain
- ✅ Create/update GitHub issues
- ✅ Modify documentation
- ✅ Coordinate cross-domain work

### PM Cannot:
- ❌ Modify code without approval
- ❌ Close issues (user only)
- ❌ Override domain decisions

### PM Must:
- Check for duplicate issues
- Process lessons-learned issues
- Forward insights to CCPM Issue #69
- Update LESSONS_LEARNED.md after closures

---

## 📅 SCHEDULED TASKS

### Wednesday (Mid-week)
- Quick status update (15-30 min)
- Update domain CURRENT_STATUS.md

### Friday (End-week)
- Comprehensive update (45-90 min)
- Architecture docs review
- Lessons learned capture

### Every Session End (EOD)
```bash
EOD  # Triggers reflection
# Creates lessons-learned issue
# PM processes next session
```

---

## 🆘 EMERGENCY PROTOCOLS

### Lost Context Completely?
```bash
cat .claude/COMPRESSION_EMERGENCY.md
```

### Need Historical Context?
```bash
.github/scripts/search-history.ps1 "keyword"  # Windows
gh issue list --search "keyword" --state all   # Linux
```

### Unsure About Rule?
```bash
grep -r "rule name" docs/ALL_DOMAINS/
cat docs/ALL_DOMAINS/LESSONS_LEARNED.md
```

---

## 🔴 FAILURE EXAMPLES (LEARN FROM THESE)

### Issue #10 Failure
- **Problem:** Air/Ground didn't update GitHub
- **Result:** Workflow breakdown, confusion
- **Lesson:** ALWAYS update issues immediately

### Focus Issues #1, #2 Failure
- **Problem:** Repeated same failed attempts
- **Result:** Hours wasted on known failures
- **Lesson:** ALWAYS search history first

### Manual Focus Debugging
- **Problem:** Issues closed prematurely
- **Result:** Main branch unstable
- **Lesson:** NEVER close without user approval

---

## 📊 METRICS FOR SUCCESS

✅ **Good Session:**
- Searched history before implementing
- Used WHO tags on every comment
- Updated issue status immediately
- Documented what worked/failed
- Never closed issues

❌ **Bad Session:**
- Started coding without checking history
- Forgot WHO tags
- Delayed issue updates until EOD
- Repeated known failures
- Closed issues without permission

---

## 🎯 QUICK REFERENCE

**Start Session:**
```bash
pwd                          # Confirm location
gh issue list --state open   # Check work
git pull origin main         # Get latest
```

**During Work:**
```bash
gh issue edit <#> --title "[FIXING] Title"
gh issue comment <#> --body "**WHO:** CC-[Domain]\n\n..."
```

**End Session:**
```bash
EOD                          # Reflection
git add -A && git commit -m "[DOMAIN][TYPE] Message"
git push origin main
```

---

## 📋 FINAL CHECKPOINT

**Can you answer these?**
- [ ] Who closes issues? (User only)
- [ ] When to search history? (Before ANY implementation)
- [ ] What starts every comment? (WHO tag)
- [ ] When to change to [FIXING]? (IMMEDIATELY when starting)
- [ ] Who can modify other domain's code? (No one without approval)

**All yes? You're ready to work!**

---

*Version 3.0 - Optimized for compression resistance*
*Total: ~250 lines (vs 693 original)*