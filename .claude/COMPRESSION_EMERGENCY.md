# 🆘 COMPRESSION EMERGENCY - QUICK RESET
**Context lost? Rules forgotten? Start here. 50 lines max.**

---

## WHO ARE YOU?
```bash
pwd  # /home/anthony/DPM-V2
# Pick your role:
CC-Air-Side      # Pi 5 C++ (sbc/)
CC-Ground-Side   # Android (android/)
CC-Dev-Tools     # Python (SystemTools/)
CC-Project-Manager  # Coordination
```

## 5 RULES - NEVER BREAK
```
1. NEVER close issues (user closes)
2. Search history FIRST (don't repeat failures)
3. WHO tags ALWAYS (**WHO:** CC-[Domain])
4. Issue required (no work without issue)
5. Cross-domain = approval needed
```

## IMMEDIATE RECOVERY
```bash
# What needs work?
gh issue list --state open --label [your-domain]

# What was tried before?
gh issue list --search "keyword" --state all

# Start work:
gh issue edit <#> --title "[FIXING] Title"
gh issue comment <#> --body "**WHO:** CC-[Domain]\n\nStarting..."
```

## KEY PATHS
```
protocol/*.json    # Specs (truth)
sbc/              # Air-Side
android/          # Ground-Side
SystemTools/      # Dev-Tools
```

## FULL CONTEXT
```bash
cat .claude/RULES_CRITICAL.md      # 100 lines
cat .claude/SESSION_START.md        # 200 lines
cat docs/CC_READ_THIS_FIRST.md     # 250 lines
```

**Remember: Search history, use WHO tags, never close issues.**