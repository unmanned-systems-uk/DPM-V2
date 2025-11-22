# Domain Agent Rules - Shared Reference

**Purpose:** Common rules and protocols for all domain agents (Air-Side, Ground-Side, SystemTools)

**Referenced by:** `/start-air`, `/start-ground`, `/start-tools`

---

## Critical Rules (ALL DOMAINS)

1. ❌ **NEVER close GitHub issues** - Only user closes issues
2. ✅ **ALWAYS search history before implementing** - Check gh issue history
3. ✅ **WHO tags MANDATORY on every comment** - Format: `**WHO:** CC-[Domain]`
4. ✅ **NEVER work without GitHub issue** - All work tracked in issues
5. ❌ **NEVER modify other domain code without approval** - Stay in your lane
6. ✅ **ALWAYS update protocol/*.json BEFORE implementing** - Single source of truth

---

## Task Completion Protocol

**MANDATORY:** See `.claude/TASK_COMPLETION_PROTOCOL.md` for full details.

### Quick Summary - Use /eot Command

**When task is complete, use the domain-specific End of Task command:**

- **Air-Side:** `/eot-air`
- **Ground-Side:** `/eot-ground`
- **SystemTools:** `/eot-tools`

These commands will guide you through proper PM reporting via tmux.

### Manual Reporting (If /eot not available)

**When task is complete:**

1. ✅ **Update GitHub issue** with completion status and summary
2. ✅ **Report to PM** via tmux:
   ```bash
   tmux send-keys -t DPM-PM "
   **WHO:** CC-[Your-Domain]
   **Task Complete**

   **Issue:** #[number]
   **Summary:** [One sentence]
   **Status:** Complete and ready for review
   **Commit:** [git log -1 --oneline]
   " C-m
   ```
3. ✅ **Wait for PM acknowledgment** before starting new work

**DO NOT:**
- ❌ Close the issue yourself
- ❌ Mark issue as "done" without PM verification
- ❌ Start new work before PM acknowledges completion
- ❌ Forget to report to PM (use /eot commands to enforce this!)

---

## WHO Tags Reference

Use these exact formats in all GitHub comments:

- **Air-Side:** `**WHO:** CC-Air-Side`
- **Ground-Side:** `**WHO:** CC-Ground-Side`
- **SystemTools:** `**WHO:** CC-Dev-Tools`
- **PM:** `**WHO:** CC-PM`

---

## Common GitHub Commands

```bash
# Change issue to in-progress
gh issue edit <#> --title "[FIXING] Title"

# Add comment with WHO tag
gh issue comment <#> --body "**WHO:** CC-[Domain]

[Your message]"

# Search issue history
gh issue list --search "keyword" --state all

# View issue details
gh issue view <#>
```

---

## Protocol Compliance

**CRITICAL:** All domains MUST enforce `protocol/*.json` files at runtime.

**No hardcoded values allowed for:**
- Log contexts (use `protocol/log_contexts.json`)
- Commands (use `protocol/commands.json`)
- Network ports (use configuration files)

**Enforcement:**
- **Air-Side:** LogContext enum
- **Ground-Side:** StructuredLogger with context parameter
- **SystemTools:** ProtocolLogger wrapper

---

**Last Updated:** 2025-11-22
**Referenced by:** All domain start commands
