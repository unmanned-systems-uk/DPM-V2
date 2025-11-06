# 🚀 Workflow Rollout Instructions

## For Human Users

### Immediate Actions Required:

1. **Pull latest changes:**
   ```bash
   git pull origin main
   ```

2. **Read Issue #26** (PINNED):
   - https://github.com/unmanned-systems-uk/DPM-V2/issues/26
   - This is the mandatory announcement

3. **For each Claude Code session**, start with:
   ```powershell
   # Air-Side sessions:
   .github\scripts\start-session-mandatory.ps1 -Domain "Air-Side"

   # Ground-Side sessions:
   .github\scripts\start-session-mandatory.ps1 -Domain "Ground-Side"

   # SystemTools sessions:
   .github\scripts\start-session-mandatory.ps1 -Domain "SystemTools"
   ```

## For Claude Code Sessions

### At Session Start, You MUST:

1. **Read these files:**
   - `docs/CC_READ_THIS_FIRST.md`
   - `docs/GITHUB_ISSUE_WORKFLOW_ENFORCEMENT.md`
   - Issue #26 (pinned announcement)

2. **Acknowledge compliance:**
   ```bash
   gh issue comment 26 --body "[CC-YourDomain] ✅ Workflow updates received and understood. Will comply with all requirements."
   ```

3. **Use WHO tags on EVERY comment:**
   - `[CC-Air-Side]` for Air-Side work
   - `[CC-Ground-Side]` for Ground-Side work
   - `[CC-SystemTools]` for SystemTools work

4. **Search history before ANY implementation:**
   ```powershell
   .github\scripts\search-history.ps1 "keyword"
   ```

## Enforcement Active

Starting NOW:
- ❌ No WHO tag = Invalid comment
- ❌ No historical search = Wasted work
- ❌ Repeated past failure = Session terminated

## Quick Test

Test the new workflow:
```powershell
# 1. Search for focus issues
.github\scripts\search-history.ps1 "focus"

# 2. Add a test comment with WHO tag
.github\scripts\issue-comment-who.ps1 -IssueNumber 26 -Who "CC-SystemTools" -Comment "Testing WHO tag system"

# 3. Check compliance
.github\scripts\check-workflow.ps1
```

---

**This is MANDATORY. Not optional. Effective immediately.**