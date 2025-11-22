---
description: Git repository health check and analysis
project: true
---

# Git Repository Health Check

**Purpose:** Comprehensive git repository status, local/remote comparison, and issue detection

---

## Step 1: Fetch Latest Remote State

```bash
echo "📡 Fetching latest from remote..."
git fetch origin --prune
```

---

## Step 2: Repository Status Overview

```bash
echo ""
echo "📊 REPOSITORY STATUS"
echo "===================="
echo ""
echo "Branch: $(git branch --show-current)"
echo "Repo: $(git remote get-url origin)"
echo ""
git status --short --branch
echo ""
```

---

## Step 3: Local vs Remote Comparison

```bash
echo "🔄 LOCAL VS REMOTE COMPARISON"
echo "=============================="
echo ""

CURRENT_BRANCH=$(git branch --show-current)

# Check if remote tracking branch exists
if git rev-parse --verify origin/$CURRENT_BRANCH >/dev/null 2>&1; then
    AHEAD=$(git rev-list --count origin/$CURRENT_BRANCH..HEAD)
    BEHIND=$(git rev-list --count HEAD..origin/$CURRENT_BRANCH)

    echo "Current branch: $CURRENT_BRANCH"
    echo "Ahead of remote: $AHEAD commits"
    echo "Behind remote: $BEHIND commits"
    echo ""

    if [ $AHEAD -gt 0 ]; then
        echo "📤 Commits to push:"
        git log --oneline origin/$CURRENT_BRANCH..HEAD
        echo ""
    fi

    if [ $BEHIND -gt 0 ]; then
        echo "📥 Commits to pull:"
        git log --oneline HEAD..origin/$CURRENT_BRANCH
        echo ""
    fi

    if [ $AHEAD -eq 0 ] && [ $BEHIND -eq 0 ]; then
        echo "✅ Local and remote are in sync"
        echo ""
    fi
else
    echo "⚠️ No remote tracking branch for: $CURRENT_BRANCH"
    echo "This is a local-only branch"
    echo ""
fi
```

---

## Step 4: Check for Conflicts

```bash
echo "⚔️ CONFLICT CHECK"
echo "================="
echo ""

# Check for merge conflicts
if git ls-files -u | grep -q '^'; then
    echo "❌ MERGE CONFLICTS DETECTED:"
    git ls-files -u | awk '{print $4}' | sort -u
    echo ""
    echo "🚨 Action required: Resolve conflicts before proceeding"
    echo ""
else
    echo "✅ No merge conflicts"
    echo ""
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo "⚠️ UNCOMMITTED CHANGES:"
    git status --short
    echo ""
else
    echo "✅ Working directory clean"
    echo ""
fi
```

---

## Step 5: GitHub Actions Status

```bash
echo "🔧 GITHUB ACTIONS STATUS"
echo "========================"
echo ""

# Check latest workflow runs
gh run list --limit 5 --json conclusion,name,headBranch,createdAt,displayTitle,url | \
    jq -r '.[] | "[\(.conclusion)] \(.name) - \(.headBranch) - \(.displayTitle) - \(.url)"'

echo ""

# Check for failed runs
FAILED_COUNT=$(gh run list --limit 20 --json conclusion | jq '[.[] | select(.conclusion=="failure")] | length')
if [ "$FAILED_COUNT" -gt 0 ]; then
    echo "⚠️ Found $FAILED_COUNT failed workflow runs in last 20"
    echo ""
fi
```

---

## Step 6: Branch Overview

```bash
echo "🌿 BRANCH OVERVIEW"
echo "=================="
echo ""

echo "Local branches:"
git branch -v
echo ""

echo "Remote branches (last 10):"
git branch -r --sort=-committerdate | head -10
echo ""
```

---

## Step 7: Recent Activity

```bash
echo "📜 RECENT COMMITS (last 10)"
echo "==========================="
echo ""
git log --oneline --graph --decorate -10
echo ""
```

---

## Step 8: Analysis & Recommendations

```bash
echo "🔍 HEALTH ANALYSIS"
echo "=================="
echo ""

# Stale branches check
STALE_COUNT=$(git branch -r --merged origin/main | grep -v "main\|master" | wc -l)
if [ "$STALE_COUNT" -gt 5 ]; then
    echo "⚠️ Found $STALE_COUNT merged remote branches (consider cleanup)"
fi

# Large file check
LARGE_FILES=$(git ls-files | xargs du -h 2>/dev/null | sort -rh | head -5)
if [ ! -z "$LARGE_FILES" ]; then
    echo "📦 Largest tracked files:"
    echo "$LARGE_FILES"
    echo ""
fi

# Repo size
REPO_SIZE=$(du -sh .git | awk '{print $1}')
echo "💾 Repository size: $REPO_SIZE"
echo ""
```

---

## Step 9: Decision Tree & Next Actions

**Based on the checks above, PM should:**

### ✅ If Everything Clean
- Repository is healthy
- No action needed
- Safe to continue development

### ⚠️ If Local Ahead of Remote
- **Recommendation:** Push changes
- **Command:** `git push origin [branch]`
- **Check:** Review commits before pushing

### ⚠️ If Local Behind Remote
- **Recommendation:** Pull changes
- **Command:** `git pull origin [branch]`
- **Risk:** May cause merge conflicts if local changes exist

### 🔄 If Local Ahead AND Behind (Diverged)
- **STOP:** Do not proceed without analysis
- **Action:** Spawn Task agent for resolution strategy
- **Options:** Merge, rebase, or force push (dangerous)

### ❌ If Merge Conflicts Detected
- **STOP:** Must resolve conflicts first
- **Action:** Spawn Task agent for conflict resolution
- **Files:** Listed in Step 4 output

### 🔧 If GitHub Actions Failing
- **Action:** Review failure logs
- **Command:** `gh run view [run-id]`
- **Consider:** Spawn Task agent for CI/CD deep dive

### 🚨 If Complex Issues Detected
**Spawn Task agent with:**
```markdown
Analyze git repository health issues:

[Paste output from Steps 1-8]

Provide:
1. Root cause analysis
2. Resolution strategy
3. Step-by-step commands
4. Risk assessment
```

---

## Step 10: Summary Report

```bash
echo "📋 SUMMARY REPORT"
echo "================="
echo ""
echo "Repository: $(basename $(git rev-parse --show-toplevel))"
echo "Branch: $(git branch --show-current)"
echo "Status: [Review output above]"
echo "Next Action: [PM decides based on decision tree]"
echo ""
```

---

## When to Spawn Task Agent

**Spawn general-purpose Task agent for:**
- Divergent branch resolution (ahead AND behind)
- Complex merge conflict resolution
- CI/CD failure deep dive
- Repository cleanup strategy
- Large-scale refactoring needed
- Unusual git states (detached HEAD, corrupted refs, etc.)

**Example Task agent prompt:**
```markdown
I need help resolving a git repository health issue:

**Issue Type:** [Diverged branches / Merge conflicts / CI failures / etc.]

**Context:**
[Paste relevant output from /git command]

**Requirements:**
1. Analyze the situation
2. Recommend resolution strategy
3. Provide step-by-step commands
4. Assess risks of each approach
5. Recommend safest path forward
```

---

## Usage Notes

**For PM:**
- Run this command periodically (daily or before major work)
- Use decision tree to determine next action
- Spawn Task agent for complex issues only
- Simple issues (push/pull): Handle directly

**Quick Health Check:**
```bash
/git
```

**Before Starting New Work:**
```bash
/git  # Check status
# If clean: proceed
# If issues: resolve first
```

**Before End of Day:**
```bash
/git  # Check uncommitted work
# Push if ahead of remote
```

---

**Created:** 2025-11-22
**Type:** Hybrid (Slash command + optional Task agent spawn)
**Complexity:** Medium (handles 80% cases, escalates 20%)
