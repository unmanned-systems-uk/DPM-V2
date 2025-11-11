# Git Hooks for DPM-V2

This directory contains git hooks to enforce documentation requirements.

## Installation

To enable the pre-commit hook:

```bash
git config core.hooksPath .githooks
```

This tells git to use hooks from `.githooks/` instead of `.git/hooks/`.

## Available Hooks

### pre-commit

**Purpose:** Ensure documentation is updated when code changes.

**What it checks:**
- If code files changed (`sbc/`, `android/`, `SystemTools/`, `docs/protocol/`)
- If documentation files changed (`docs/architecture/`)
- **CRITICAL:** If protocol changed, both PropertyLoader (C++ AND Kotlin) must be updated

**Behavior:**
- ✅ **PASS:** Code and docs both changed → commit allowed
- ✅ **PASS:** Docs-only change → commit allowed
- ⚠️ **WARNING:** Code changed but no docs → commit blocked
- 🔴 **CRITICAL:** Protocol changed but PropertyLoader not updated in both domains → commit blocked

**Bypass (use sparingly):**
```bash
git commit --no-verify
```

Only bypass if:
- Documentation update genuinely not needed (e.g., fixing typo in comment)
- You're working in progress and will update docs in next commit
- You understand the risk of stale documentation

## Why This Matters

Without automated enforcement, documentation becomes stale within months:
- Developers forget to update docs
- Code evolves but docs don't
- New team members get confused
- Architecture knowledge gets lost

The pre-commit hook makes it **easy to remember** by checking automatically.

## Troubleshooting

### Hook not running

Check if hooks path is configured:
```bash
git config core.hooksPath
```

Should output: `.githooks`

If not, run installation command above.

### Hook failing incorrectly

If hook is blocking a legitimate commit:

1. **Review the warning** - Did you actually forget to update docs?
2. **Check documentation requirements** - See `CONTRIBUTING.md`
3. **Still unsure?** - Ask in PR comments or create issue
4. **Absolutely sure it's wrong?** - Use `--no-verify` (document why in commit message)

### Disabling hooks

To temporarily disable:
```bash
git config core.hooksPath ""
```

To re-enable:
```bash
git config core.hooksPath .githooks
```

## Adding New Hooks

To add a new hook:

1. Create file in `.githooks/` (e.g., `pre-push`, `commit-msg`)
2. Make executable: `chmod +x .githooks/hook-name`
3. Test locally
4. Document in this README
5. Commit and push

## Testing Hooks

Test pre-commit hook without committing:
```bash
# Stage some code changes
git add sbc/src/camera/camera.cpp

# Run hook manually
./.githooks/pre-commit

# Should warn if no docs staged
```

Test with docs staged:
```bash
git add sbc/src/camera/camera.cpp
git add docs/architecture/view-logical.md

./.githooks/pre-commit
# Should pass
```

## Related

- **CONTRIBUTING.md** - Full documentation requirements
- **docs/DOCUMENTATION_UPDATE_GUIDE.md** - Quick reference for what to update
- **.github/workflows/documentation-check.yml** - CI/CD enforcement (runs on PR)
- **.github/scripts/audit-documentation.sh** - Quarterly audit script
