# GitHub Issue Prefix Taxonomy & Historical Learning System

## 🎯 Purpose: Prevent Repeating Failed Solutions

**Problem:** Claude Code keeps trying the same failed solutions because each session has no memory
**Solution:** Use GitHub issues as a persistent knowledge base with searchable prefixes

## 📋 Standard Issue Title Prefixes

### Feature/Problem Prefixes
- `[FOCUS]` - Focus control issues
- `[CAMERA]` - Camera control/properties
- `[NETWORK]` - TCP/UDP/connection issues
- `[PROTOCOL]` - Protocol implementation
- `[BUILD]` - Build/compilation issues
- `[DEPLOY]` - Deployment/installation issues
- `[UI]` - User interface issues
- `[SYNC]` - Cross-domain synchronization

### Domain Prefixes (always include)
- `[AIR]` - Air-Side specific
- `[GROUND]` - Ground-Side specific
- `[TOOLS]` - SystemTools specific
- `[CROSS]` - Affects multiple domains

### Status Prefixes (for clarity)
- `[SOLVED]` - Issue resolved, contains working solution
- `[PARTIAL]` - Partially working, some issues remain
- `[BLOCKED]` - Cannot proceed, external dependency
- `[INVESTIGATING]` - Still diagnosing root cause

## 📝 Example Issue Titles

Good examples with searchable prefixes:
- `[FOCUS][AIR] Focus distance always returns 0`
- `[FOCUS][GROUND] Manual focus slider not updating`
- `[NETWORK][CROSS] UDP packets dropping over 1KB`
- `[CAMERA][AIR][SOLVED] Shutter speed implementation via SDK`

## 🔍 MANDATORY: Search Before Implementation

### Claude Code MUST Run These Searches:

```bash
# Before working on ANY focus issue:
gh issue list --repo unmanned-systems-uk/DPM-V2 --search "[FOCUS]" --state all --limit 50

# Before working on specific problem:
gh issue list --repo unmanned-systems-uk/DPM-V2 --search "focus distance" --state all

# Check what solutions failed:
gh issue view <number> --comments | grep -i "tried\|didn't work\|failed"
```

## 📊 Failed Attempts Documentation Format

### Every Issue MUST Document:

```markdown
## Attempted Solutions Log

### Attempt 1: [Brief description]
**What:** [Exactly what was tried]
**Code:** `specific function or line`
**Result:** ❌ Failed - [why it failed]
**Lesson:** [What we learned]

### Attempt 2: [Brief description]
**What:** [Different approach]
**Code:** `different implementation`
**Result:** ❌ Failed - [why this also failed]
**Lesson:** [New insight gained]

### Attempt 3: [Brief description]
**What:** [Final working approach]
**Code:** `working implementation`
**Result:** ✅ Success - [what made it work]
**Key Insight:** [Why this worked when others didn't]
```

## 🧠 Learning From History Protocol

### Before Starting ANY Issue:

1. **Search for similar issues:**
   ```bash
   # Search by prefix
   gh issue list --repo unmanned-systems-uk/DPM-V2 --search "[PREFIX]" --state all

   # Search by keywords
   gh issue list --repo unmanned-systems-uk/DPM-V2 --search "problem keywords" --state all
   ```

2. **Read ALL related issues:**
   ```bash
   # Read issue with comments
   gh issue view <number> --comments
   ```

3. **Extract failed attempts:**
   ```bash
   # Look for failure patterns
   gh issue view <number> --comments | grep -A5 -B5 "didn't work\|failed\|tried"
   ```

4. **Document new approach:**
   ```bash
   gh issue comment <number> --body "Based on previous attempts in #X and #Y, I will NOT try:
   - [Failed approach 1] (failed in #X)
   - [Failed approach 2] (failed in #Y)

   Instead, I will try:
   - [New approach based on lessons learned]"
   ```

## 📌 Real Examples from DPM-V2

### Example: Focus Issues (#1, #2, #10)

**Pattern Recognition:**
- Multiple issues about focus control
- Common failed attempts:
  - ❌ Using getAvailableProperties (doesn't include focus)
  - ❌ Hardcoding focus values (camera rejects them)
  - ❌ Using wrong SDK functions (getFocusDistance vs getFocusArea)

**Lesson Learned:**
- ✅ Must use Sony SDK's specific focus functions
- ✅ Must check camera's focus mode first
- ✅ Different behavior in AF vs MF mode

### Example: Network Issues

**Pattern Recognition:**
- UDP packet size issues appear in multiple issues
- Common failed attempts:
  - ❌ Increasing buffer size (doesn't help fragmentation)
  - ❌ Compression (adds latency)

**Lesson Learned:**
- ✅ Keep UDP packets under 1KB
- ✅ Use TCP for large data transfers

## 🚀 Implementation in Workflow

### Modified CC_READ_THIS_FIRST.md Addition:

```markdown
## 🧠 MANDATORY: Check Historical Issues First

Before implementing ANYTHING:
1. Search for similar issues: `gh issue list --search "[PREFIX] keywords"`
2. Read failed attempts: `gh issue view <#> --comments`
3. Document what you WON'T try based on history
4. Explain your NEW approach based on lessons learned

**Example:**
"I found 3 previous focus issues (#1, #2, #10). They show that:
- Using getAvailableProperties doesn't work (tried in #1)
- Hardcoding values fails (tried in #2)
- Must use Sony SDK's getFocusDistance() (succeeded in #10)

Therefore, I will use the Sony SDK approach with proper error handling."
```

## 📈 Benefits of This System

1. **No repeated failures** - CC won't try what already failed
2. **Faster solutions** - Start with knowledge of what works
3. **Better debugging** - Understanding of why things fail
4. **Knowledge accumulation** - Each issue adds to collective knowledge
5. **Pattern recognition** - Identify systemic issues

## 🔧 Tools to Support This

### Quick Search Script (search-history.ps1):

```powershell
param(
    [Parameter(Mandatory=$true)]
    [string]$SearchTerm
)

Write-Host "Searching for historical issues related to: $SearchTerm" -ForegroundColor Cyan

# Search all issues
$issues = gh issue list --repo unmanned-systems-uk/DPM-V2 --search $SearchTerm --state all --limit 100 --json number,title,state,labels

Write-Host "`nFound issues:" -ForegroundColor Green
$issues | ConvertFrom-Json | ForEach-Object {
    $state = if ($_.state -eq "CLOSED") { "[SOLVED]" } else { "[OPEN]" }
    Write-Host "$state #$($_.number): $($_.title)"
}

Write-Host "`nTo read details: gh issue view <number> --comments" -ForegroundColor Yellow
```

## 📑 Issue Template with History Section

```markdown
## Issue Title: [PREFIX][DOMAIN] Clear description

## Related Historical Issues
- #X - [Similar issue title] - [SOLVED/FAILED]
- #Y - [Related issue] - [What was learned]

## Previous Failed Attempts (from history)
1. [What was tried in issue #X] - Failed because [reason]
2. [What was tried in issue #Y] - Failed because [reason]

## New Approach (based on lessons learned)
Will try [new approach] because:
- Avoids [problem from #X]
- Incorporates [success from #Y]
- Addresses [root cause identified]

## Implementation
[Actual work goes here]

## Results
[Document success or failure with lessons learned]
```

---

*This system turns GitHub issues into a searchable knowledge base, preventing Claude Code from repeating past mistakes.*