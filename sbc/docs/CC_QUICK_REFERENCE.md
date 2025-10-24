# Claude Code Quick Reference Card
## DPM Payload Manager - Essential Info

**Version:** 1.0 | **Date:** October 24, 2025

---

## 🚀 SESSION START (30 SECONDS)

```bash
# 1. Read rules
cat CC_READ_THIS_FIRST.md  # Full workflow rules

# 2. Check status
cat PROGRESS_AND_TODO.md   # Current phase, blockers, next tasks

# 3. Check git
git status                 # Uncommitted changes?
git log --oneline -5       # Recent commits

# 4. Start work!
```

---

## 📋 MANDATORY UPDATES

### After Every Significant Change:
1. Update `PROGRESS_AND_TODO.md`:
   - Mark tasks [x]
   - Update "Last Updated" timestamp
   - Add to "Recent Updates" if major
   - Update completion %

2. Commit to git:
   ```bash
   git add -A
   git commit -m "[TYPE] Component: Description"
   git push origin main
   ```

---

## 🎯 COMMIT TYPES

| Type | When to Use | Example |
|------|-------------|---------|
| `[FEATURE]` | New functionality | `[FEATURE] Camera: Added Sony SDK enumeration` |
| `[FIX]` | Bug fixes | `[FIX] Docker: Resolved adapter loading issue` |
| `[DOCS]` | Documentation only | `[DOCS] Updated PROGRESS with Docker status` |
| `[WIP]` | Incomplete work | `[WIP] Camera: Working on connection callback` |
| `[REFACTOR]` | Code cleanup | `[REFACTOR] Protocol: Improved error handling` |
| `[TEST]` | Test additions | `[TEST] Added camera connection test suite` |

---

## 📁 FILE PRIORITIES

### 🔴 Update Every Session
- `PROGRESS_AND_TODO.md` - Current status

### 🟡 Update When Relevant
- `BUILD_AND_IMPLEMENTATION_PLAN.md` - Architecture changes
- `DOCKER_SETUP.md` - Docker/build process changes

### 🟢 Read Once, Reference Later
- `Project_Summary_and_Action_Plan.md` - Initial overview (800+ lines)
- Protocol specs - When implementing protocol
- Sony SDK docs - When working on camera

---

## 🔑 QUICK ACCESS

**Git:**
```bash
# Standard workflow
git pull origin main
git add -A
git commit -m "[TYPE] Message"
git push origin main
```

**SSH:**
```bash
# Raspberry Pi access
ssh dpm@10.0.1.127
# Password: 2350
# Sudo: 2350
```

**Docker:**
```bash
# Quick commands
sudo docker exec -it payload-manager bash  # Shell access
./build_container.sh                       # Rebuild image
./run_container.sh prod                    # Run container
./shell.sh                                 # Helper script
```

---

## 📊 CURRENT PROJECT STATUS

**Phase:** 1.5 - Docker Deployment + Camera Integration  
**Overall:** 68% Complete  
**Status:** Docker ✅ | Camera 🐛 Debugging  
**Blocker:** Connection error 0x8208 (OnConnected callback)

**Key Paths:**
```
/home/dpm/DPM/sbc/              # Project root
/home/dpm/SonySDK/...           # Sony SDK
/app/sbc/build/                 # Container build
```

---

## ⚡ EFFICIENCY RULES

### DO ✅
- Commit every 30-60 minutes
- Update docs before committing code
- Use [TYPE] prefixes in commits
- Keep commits focused and atomic
- Read PROGRESS_AND_TODO.md each session

### DON'T ❌
- Re-read large docs every session
- Commit without updating docs
- Make large multi-purpose commits
- Leave work without WIP commit
- Ask permission to commit (just do it)

---

## 🆘 COMMON ISSUES

**"What do I work on?"**
→ Check PROGRESS_AND_TODO.md, first unchecked [ ] task

**"Should I read this doc?"**
→ CC_READ_THIS_FIRST.md has decision tree

**"Git push failed"**
→ Check credentials, try `git pull` first

**"Docker not running"**
→ `sudo docker start payload-manager`

**"Can't compile"**
→ Inside container: `cd /app/sbc && ./rebuild.sh`

---

## 📝 DOCUMENTATION UPDATE TEMPLATE

```markdown
## RECENT UPDATES (October XX, 2025)

### [Feature/Fix Name]
- ✅ Completed: [what was done]
- ✅ Result: [what works now]
- 🐛 Issue: [if any blocker]

## [Current Phase Section]
- [x] Task completed
- [ ] Task pending
- 🐛 Task blocked: reason

**Last Updated:** October XX, 2025 HH:MM - After [what change]
```

---

## 🎯 SESSION END CHECKLIST

- [ ] PROGRESS_AND_TODO.md updated
- [ ] All checkboxes accurate
- [ ] Completion % updated
- [ ] Last Updated timestamp current
- [ ] All code committed
- [ ] Commits pushed
- [ ] No orphaned documentation

**All checked? You're done! 🎉**

---

## 🔄 WORKFLOW VISUALIZATION

```
SESSION START
     ↓
Read CC_READ_THIS_FIRST.md
     ↓
Read PROGRESS_AND_TODO.md
     ↓
git status & git log
     ↓
┌────────────────────┐
│   DO WORK          │
│   (30-60 min)      │
└────────────────────┘
     ↓
Update PROGRESS_AND_TODO.md
     ↓
git commit -m "[TYPE] ..."
     ↓
Continue? ─YES→ DO WORK
     ↓
    NO
     ↓
git push origin main
     ↓
SESSION END
```

---

**🔴 REMEMBER: Follow CC_READ_THIS_FIRST.md for complete rules! 🔴**

**This is just a quick reference - not a replacement for the full rules document.**
