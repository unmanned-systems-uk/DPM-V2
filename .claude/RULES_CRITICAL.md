# 🔴 CRITICAL RULES - SURVIVE COMPRESSION
**If context compressed, these rules MUST survive. Max 100 lines.**

## 🚨 NEVER VIOLATE THESE (INSTANT FAILURE)

### 1. NEVER CLOSE ISSUES
```bash
# ❌ NEVER run: gh issue close
# ✅ Only user closes issues
# ✅ You can suggest: "Ready to close?"
```

### 2. ALWAYS SEARCH HISTORY FIRST
```bash
# Before ANY implementation:
gh issue list --search "[keyword]" --state all
# Learn from past failures - don't repeat
```

### 3. WHO TAGS MANDATORY
```markdown
**WHO:** CC-[Domain]

Every GitHub comment starts with WHO tag.
No exceptions.
```

### 4. ISSUE-FIRST WORKFLOW
```bash
# ❌ NEVER start work without issue
# ✅ Check/create issue first
gh issue list --state open
gh issue create --title "[TYPE] Task"
```

### 5. CROSS-DOMAIN APPROVAL (Rule 11)
```bash
# ❌ NEVER modify other domain's code
# ✅ Get user approval for cross-domain changes
"Need to modify Ground-Side. Approve?"
```

## 📍 DOMAIN IDENTIFICATION
```
Air-Side = Pi 5 C++ (sbc/)
Ground-Side = H16 Android (android/)
Dev-Tools = Python (SystemTools/)
PM = Coordination (all domains)
```

## 🔄 ISSUE STATE TRANSITIONS
```
[FIX] → [FIXING] → [FIXED] → CLOSED
      ↑ Start work  ↑ After test  ↑ User only

# When starting work (IMMEDIATELY):
gh issue edit # --title "[FIXING] Title"
```

## 📁 KEY PATHS
```
protocol/*.json     # Single source truth
sbc/               # Air-Side C++
android/           # Ground-Side Kotlin
SystemTools/       # Dev-Tools Python
docs/ALL_DOMAINS/  # Cross-domain docs
```

## 🎯 COMMIT FORMAT
```
[DOMAIN][TYPE] Description
[AIR][FIX] Focus distance bug
[GROUND][FEATURE] Add UI element
[PM][DOCS] Update workflow
```

## ⚠️ COMPRESSION CHECKPOINT
**If you see this after compression:**
1. Read `.claude/SESSION_START.md`
2. Read `docs/CC_READ_THIS_FIRST.md`
3. Check open issues: `gh issue list --state open`
4. WHO tag yourself: `**WHO:** CC-[Domain]`

## 🆘 EMERGENCY RECOVERY
**Lost context? Run:**
```bash
cat .claude/COMPRESSION_EMERGENCY.md
```

**Remember: Search history, don't close issues, use WHO tags.**