# DPM-V2 Session Start Guide - OPTIMIZED v3.0
**Read Time: 2 minutes | Critical Rules: 5 | Compression-Resistant**

---

## 🔴 CRITICAL RULES (MEMORIZE NOW)
```bash
# If compressed, these 5 rules MUST survive:
1. NEVER close GitHub issues (user closes)
2. ALWAYS search history before implementing
3. WHO tags MANDATORY on every comment
4. NEVER work without GitHub issue
5. NEVER modify other domain's code without approval
```

**Lost rules?** → Read `.claude/RULES_CRITICAL.md`

---

## ⚡ QUICK START (30 seconds)

### Where am I?
```bash
pwd  # Should be: /home/anthony/DPM-V2
```

### What's my domain?
- **Air-Side** (CC-Air-Side) → Pi 5 C++ in `sbc/`
- **Ground-Side** (CC-Ground-Side) → Android in `android/`
- **Dev-Tools** (CC-Dev-Tools) → Python in `SystemTools/`
- **PM** (CC-Project-Manager) → Cross-domain coordination

### What needs work?
```bash
# Check open issues for your domain
gh issue list --state open --label [air-side|ground-side|dev-tools]

# Check in-progress from last session
gh issue list --label status:in-progress --state open
```

---

## 📋 COMPRESSION CHECKPOINT #1
**If reading after compression, you MUST:**
1. ✅ Confirmed location (`pwd`)
2. ✅ Identified your domain
3. ✅ Checked open issues
4. ✅ Remember: NEVER close issues
5. ✅ Remember: WHO tags required

---

## 🎯 DOMAIN WORKFLOWS

### Air-Side (Pi 5 C++)
```bash
cd sbc/
# CRITICAL: Check Sony SDK docs before implementing
# Location: docs/AIR_SIDE/CrSDK_API_Reference_v2.00.00/
```

### Ground-Side (Android)
```bash
cd android/
# Key: TCP commands (9001), UDP status (9002)
```

### Dev-Tools (Python)
```bash
cd SystemTools/
python main.py  # Diagnostic GUI
```

### PM (Coordination)
```bash
# Check ALL domains, coordinate handoffs
gh issue list --state open
cat docs/ALL_DOMAINS/LESSONS_LEARNED.md

# CRITICAL: Setup tmux monitoring sessions
# This gives PM real-time visibility into all domain activities
tmux list-sessions  # Should see: Air-Side-PI, Ground-Side, SystemTools
```

**PM REQUIRES TMUX SESSIONS:**
User must have these tmux sessions active:
1. **Air-Side-PI**: SSH to Pi 5 (10.0.1.53) running Claude Code
2. **Ground-Side**: Local session working on Android
3. **SystemTools**: Local session for Python tools

Without these, PM cannot monitor real-time progress!

---

## 🔄 ISSUE WORKFLOW
```bash
# Start work (change IMMEDIATELY, not at EOD):
gh issue edit <#> --title "[FIXING] Title"
gh issue comment <#> --body "**WHO:** CC-[Domain]\n\nStarting..."

# Complete work:
gh issue comment <#> --body "**WHO:** CC-[Domain]\n\nComplete. Test?"

# User confirms:
gh issue edit <#> --title "[FIXED] Title"
# NEVER close - user closes
```

---

## 📋 COMPRESSION CHECKPOINT #2
**Critical workflows to remember:**
- ✅ Historical search BEFORE implementing
- ✅ Issue state: [FIX] → [FIXING] → [FIXED]
- ✅ WHO tags on EVERY comment
- ✅ Cross-domain needs approval (Rule 11)

---

## 🔍 HISTORICAL SEARCH (MANDATORY)
```bash
# BEFORE any implementation:
gh issue list --search "focus" --state all  # Example
gh issue view <#> --comments  # Read what failed

# Document your approach:
"Found #1, #2 tried X and failed. I'll try Y because..."
```

---

## 🏷️ WHO TAGS (MANDATORY)
```markdown
**WHO:** CC-Air-Side
**WHO:** CC-Ground-Side
**WHO:** CC-Dev-Tools
**WHO:** CC-Project-Manager
**WHO:** User (Anthony)
```

Every GitHub comment MUST start with WHO tag.

---

## 📋 COMPRESSION CHECKPOINT #3
**If heavily compressed:**
1. Read `.claude/RULES_CRITICAL.md` (100 lines)
2. Read `.claude/COMPRESSION_EMERGENCY.md` (50 lines)
3. WHO tag yourself
4. Check open issues
5. Never close issues

---

## 🗂️ KEY PATHS
```
protocol/*.json         # Command/property specs
sbc/                   # Air-Side C++
android/               # Ground-Side Android
SystemTools/           # Dev-Tools Python
docs/ALL_DOMAINS/      # Cross-domain docs
docs/AIR_SIDE/CrSDK_*  # Sony SDK reference
```

---

## 🚀 COMMIT FORMAT
```
[AIR][FIX] Description
[GROUND][FEATURE] Description
[TOOLS][FIX] Description
[PM][DOCS] Description
```

---

## 📅 ARCHITECTURE UPDATES
**Wednesday:** Quick status update (15-30 min)
**Friday:** Comprehensive update (45-90 min)
- Check with: `date +%A`
- See Issue #62 for checklist

---

## 🚪 EXIT PROTOCOL
When user types "EXIT":
1. **WHO tag yourself**
2. **Check day** (Wed/Fri updates?)
3. **Run EOD** (End of Day reflection)
4. **Create lessons-learned issue**

---

## 📋 FINAL CHECKPOINT
**Core memory intact?**
- [ ] Never close issues
- [ ] Search history first
- [ ] WHO tags always
- [ ] Issue-first workflow
- [ ] Cross-domain approval

**Ready to work!**

---

## 🆘 EMERGENCY RECOVERY
```bash
# Lost all context?
cat .claude/COMPRESSION_EMERGENCY.md

# Need full context?
cat docs/CC_READ_THIS_FIRST.md
```

**Next:** User tells you domain and task.