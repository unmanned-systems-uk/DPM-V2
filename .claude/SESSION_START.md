# DPM-V2 Session Start Guide

**Read Time:** 1 minute | **Compression-Resistant**

---

## 🔴 CRITICAL RULES (MEMORIZE)

```
1. NEVER close GitHub issues (user closes)
2. ALWAYS search history before implementing
3. WHO tags MANDATORY on every comment
4. NEVER work without GitHub issue
5. NEVER modify other domain's code without approval
```

**Full rules:** `.claude/RULES_CRITICAL.md`

---

## ⚡ QUICK START

### Where am I?
```bash
pwd  # Should be: /home/anthony/DPM-V2
```

### What's my domain?
- **Air-Side** (CC-Air-Side) → Pi 5 C++ in `sbc/`
- **Ground-Side** (CC-Ground-Side) → Android in `android/`
- **Dev-Tools** (CC-Dev-Tools) → Python in `SystemTools/`
- **PM** (CC-PM) → Cross-domain coordination

### What needs work?
```bash
gh issue list --state open --label [air-side|ground-side|dev-tools]
gh issue list --label status:in-progress --state open
```

---

## 🎯 DOMAIN SESSION STARTS

**Use domain-specific slash commands:**
- `/start-air` - Air-Side (Pi 5 C++)
- `/start-ground` - Ground-Side (Android)
- `/start-tools` - SystemTools (Python)
- `/start-pm` - PM (Coordination)

**These commands load full domain context and procedures.**

---

## 🏷️ WHO TAGS (MANDATORY)

Every GitHub comment MUST start with WHO tag:

```
**WHO:** CC-Air-Side
**WHO:** CC-Ground-Side
**WHO:** CC-Dev-Tools
**WHO:** CC-PM
**WHO:** User (Anthony)
```

---

## 🔄 QUICK WORKFLOW

### 1. Historical Search (BEFORE implementing)
```bash
gh issue list --search "[keyword]" --state all
gh issue view <#> --comments
```

**See:** `.claude/GIT_WORKFLOW.md` for full Git procedures

### 2. Start Work
```bash
gh issue edit <#> --title "[FIXING] Title"
gh issue comment <#> --body "**WHO:** CC-[Domain]\n\nStarting..."
```

### 3. Complete Work
```bash
# Use domain-specific EOT command:
/eot-air        # Air-Side
/eot-ground     # Ground-Side
/eot-tools      # SystemTools
```

**These commands enforce proper PM reporting via tmux.**

---

## 📁 KEY REFERENCES

**Commands:** `.claude/COMMON_COMMANDS.md` - Frequently used commands
**Git:** `.claude/GIT_WORKFLOW.md` - Issue workflow, commit format
**Docs:** `.claude/DOC_STRUCTURE.md` - Where to find documentation
**Rules:** `.claude/DOMAIN_AGENT_RULES.md` - Shared domain rules

**Emergency:** `.claude/COMPRESSION_EMERGENCY.md` - Lost context recovery

---

## 🗂️ ESSENTIAL PATHS

```
protocol/*.json         # Protocol specs (single source of truth)
sbc/                   # Air-Side C++
android/               # Ground-Side Android
SystemTools/           # SystemTools Python
docs/ALL_DOMAINS/      # Cross-domain docs
.claude/               # Claude Code configuration
```

---

## 🚪 EXIT PROTOCOL

When user types "EXIT":
1. WHO tag yourself
2. Use `/eot-[domain]` to report completion
3. Check if Wed/Fri (architecture update due)

---

## 🆘 EMERGENCY

```bash
# Lost all context?
cat .claude/COMPRESSION_EMERGENCY.md

# Need full rules?
cat .claude/RULES_CRITICAL.md

# Need help?
/sos
```

---

**Ready to work!** User will specify domain and task.
