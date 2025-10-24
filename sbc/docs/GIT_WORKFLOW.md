# Git Workflow Guide
## DPM Payload Manager Project

**Version:** 1.0  
**Date:** October 24, 2025  
**For:** Claude Code and Human Developers

---

## 🎯 REPOSITORY INFORMATION

**Remote Repository:** `https://github.com/unmanned-systems-uk/DPM.git`

**Branch Strategy:**
- **Main branch:** `main` (all development happens here for now)
- **Future:** Feature branches when needed

**Local Repository:** `/home/dpm/DPM/sbc/`

---

## 📋 STANDARD WORKFLOW

### Session Start

```bash
# 1. Navigate to project
cd /home/dpm/DPM/sbc

# 2. Check current status
git status

# 3. Check recent history
git log --oneline -5

# 4. Pull latest changes (if working with others)
git pull origin main

# 5. Check for uncommitted changes from previous session
git diff

# If there are uncommitted changes, decide:
# - Complete and commit them
# - Stash them: git stash
# - Discard them: git checkout -- <file>
```

### During Work

```bash
# Check what's changed frequently
git status

# View specific changes
git diff                    # Unstaged changes
git diff --cached          # Staged changes
git diff HEAD              # All changes since last commit

# Stage files as you complete logical units
git add src/camera/camera_sony.cpp          # Specific file
git add src/camera/                         # Entire directory
git add docs/PROGRESS_AND_TODO.md          # Documentation
git add -A                                  # Everything (use carefully)

# Check what's staged
git status
git diff --cached

# Commit completed work
git commit -m "[TYPE] Component: Description

- Detail 1
- Detail 2"

# Continue working...
```

### Session End

```bash
# 1. Ensure all work is committed
git status
# Should show: "nothing to commit, working tree clean"

# 2. Push all commits
git push origin main

# 3. Verify push succeeded
git log --oneline -1
# Should match remote

# 4. Optional: Tag significant milestones
git tag -a v1.0-phase1-complete -m "Phase 1 MVP Complete"
git push origin --tags
```

---

## 📝 COMMIT MESSAGE STANDARDS

### Format

```
[TYPE] Component: Brief description (max 72 chars)

- Detailed point 1
- Detailed point 2
- Detailed point 3

Resolves: #issue-number (if applicable)
Related: #issue-number (if applicable)
```

### Commit Types

| Type | Purpose | Example |
|------|---------|---------|
| `[FEATURE]` | New functionality added | Adding camera control |
| `[FIX]` | Bug fixes | Fixing connection timeout |
| `[DOCS]` | Documentation only | Updating README |
| `[REFACTOR]` | Code improvement, no new features | Improving error handling |
| `[TEST]` | Adding/modifying tests | Adding unit tests |
| `[BUILD]` | Build system changes | CMake configuration |
| `[STYLE]` | Formatting, whitespace | Code formatting |
| `[PERF]` | Performance improvements | Optimizing loops |
| `[CHORE]` | Maintenance tasks | Updating dependencies |
| `[WIP]` | Work in progress | Incomplete feature |

### Good Commit Examples

```bash
# Feature implementation
git commit -m "[FEATURE] Camera: Implemented Sony SDK enumeration

- Added CameraDevice wrapper class
- Integrated USB and network camera detection
- Implemented callback-based connection handling
- Added error logging for SDK operations"

# Bug fix
git commit -m "[FIX] Docker: Resolved CrAdapter dynamic loading

- Root cause: Static linking prevented dynamic adapter loading
- Solution: Only link libCr_Core.so, copy CrAdapter/ directory
- Modified CMakeLists.txt (lines 145-150)
- Modified Dockerfile.prod (lines 32-38)
- Result: SDK now loads USB and IP adapters successfully

Resolves: #3"

# Documentation update
git commit -m "[DOCS] Updated PROGRESS_AND_TODO.md

- Added Docker deployment section (Phase 1.5)
- Documented libxml2 ABI resolution
- Updated overall completion to 68%
- Added connection error 0x8208 to Issue Tracker
- Updated Last Updated timestamp"

# Work in progress
git commit -m "[WIP] Camera: Debugging connection callback

- SDK::Connect() returns success
- OnConnected callback not firing (error 0x8208)
- Added detailed logging to connection sequence
- Next: Compare with RemoteCli implementation"

# Refactoring
git commit -m "[REFACTOR] Protocol: Improved JSON error handling

- Extracted JSON parsing to separate function
- Added comprehensive error messages
- Improved exception safety with try-catch blocks
- No functional changes, improved code quality"
```

### Bad Commit Examples (Don't Do This)

```bash
# ❌ Too vague
git commit -m "fixed stuff"
git commit -m "updates"
git commit -m "WIP"

# ❌ No type prefix
git commit -m "Added camera support"

# ❌ Too many unrelated changes
git commit -m "[FEATURE] Added camera, fixed networking, updated docs, refactored utils"

# ❌ No details
git commit -m "[FIX] Bug fix"

# ❌ Commit broken code without WIP tag
git commit -m "[FEATURE] Camera connection" # (but it doesn't compile)
```

---

## 🔄 BRANCHING STRATEGY (FUTURE)

**Current:** All work on `main` branch

**When to create feature branches (Phase 2+):**

```bash
# Create and switch to feature branch
git checkout -b feature/gimbal-integration

# Work on feature...
git add ...
git commit -m "[FEATURE] Gimbal: ..."

# When ready to merge
git checkout main
git pull origin main
git merge feature/gimbal-integration
git push origin main

# Delete feature branch (optional)
git branch -d feature/gimbal-integration
```

**Branch naming convention:**
- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation improvements
- `test/description` - Test additions
- `refactor/description` - Code improvements

---

## 🛠️ COMMON OPERATIONS

### Checking Status

```bash
# What's changed?
git status

# Detailed differences
git diff

# Show last N commits
git log --oneline -10

# Show commits by author
git log --author="name"

# Show commits affecting specific file
git log --oneline -- path/to/file

# Show commit details
git show <commit-hash>

# Graphical log
git log --graph --oneline --all
```

### Staging Changes

```bash
# Stage specific file
git add src/camera/camera_sony.cpp

# Stage all changes in directory
git add src/camera/

# Stage all modified files (not new files)
git add -u

# Stage everything (including new files)
git add -A

# Interactive staging (choose what to stage)
git add -p

# Unstage file
git reset HEAD src/camera/camera_sony.cpp
```

### Committing

```bash
# Standard commit
git commit -m "[TYPE] Message"

# Commit with editor for longer message
git commit

# Amend last commit (add forgotten files)
git add forgotten_file.cpp
git commit --amend --no-edit

# Amend last commit message
git commit --amend -m "[TYPE] New message"

# Note: Only amend commits that haven't been pushed!
```

### Pushing and Pulling

```bash
# Push to remote
git push origin main

# Pull from remote
git pull origin main

# Pull with rebase (cleaner history)
git pull --rebase origin main

# Force push (DANGEROUS - use only if certain)
git push --force origin main

# Push tags
git push origin --tags
```

### Undoing Changes

```bash
# Discard unstaged changes in file
git checkout -- path/to/file

# Discard all unstaged changes
git checkout -- .

# Unstage file (keep changes)
git reset HEAD path/to/file

# Undo last commit (keep changes staged)
git reset --soft HEAD~1

# Undo last commit (keep changes unstaged)
git reset HEAD~1

# Undo last commit (discard changes) - DANGEROUS
git reset --hard HEAD~1

# Revert commit (create new commit that undoes it)
git revert <commit-hash>
```

### Stashing Changes

```bash
# Save work temporarily
git stash

# Save with description
git stash save "Camera connection work in progress"

# List stashes
git stash list

# Apply most recent stash (keep in stash)
git stash apply

# Apply most recent stash (remove from stash)
git stash pop

# Apply specific stash
git stash apply stash@{2}

# Clear all stashes
git stash clear
```

---

## 🐛 TROUBLESHOOTING

### Problem: Git push fails with authentication error

**Symptoms:**
```
remote: Invalid username or password.
fatal: Authentication failed
```

**Solution:**
```bash

# Or configure credential helper
git config --global credential.helper store
git push origin main
# Enter credentials when prompted - they'll be saved
```

### Problem: Push rejected - non-fast-forward

**Symptoms:**
```
! [rejected]        main -> main (non-fast-forward)
error: failed to push some refs
```

**Solution:**
```bash
# Someone else pushed changes - pull first
git pull origin main

# If conflicts, resolve them:
# 1. Edit conflicted files
# 2. git add <resolved-files>
# 3. git commit

# Then push
git push origin main
```

### Problem: Merge conflict

**Symptoms:**
```
CONFLICT (content): Merge conflict in src/camera/camera_sony.cpp
Automatic merge failed; fix conflicts and then commit the result.
```

**Solution:**
```bash
# 1. Check which files have conflicts
git status

# 2. Open conflicted files, look for:
<<<<<<< HEAD
Your changes
=======
Their changes
>>>>>>> branch-name

# 3. Edit file to resolve conflict (remove markers)

# 4. Stage resolved files
git add src/camera/camera_sony.cpp

# 5. Complete merge
git commit -m "[MERGE] Resolved conflicts in camera_sony.cpp"

# 6. Push
git push origin main
```

### Problem: Accidentally committed to wrong branch

**Solution:**
```bash
# If not pushed yet:
git reset --soft HEAD~1    # Undo commit, keep changes
git stash                  # Save changes
git checkout correct-branch
git stash pop              # Apply changes
git add ...
git commit -m "..."

# If already pushed - contact team lead
```

### Problem: Committed sensitive data

**Solution:**
```bash
# If not pushed yet:
git reset --soft HEAD~1
# Remove sensitive data from files
git add ...
git commit -m "..."

# If already pushed:
# 1. Remove sensitive data from files
# 2. Commit the fix
# 3. Immediately change/revoke credentials
# 4. Consider: git filter-branch (advanced)
```

---

## 📊 COMMIT FREQUENCY GUIDELINES

### Ideal Commit Frequency

**Small commits frequently:**
- Every 30-60 minutes of productive work
- After completing logical unit (function, class, feature)
- Before switching tasks
- After fixing a bug
- Before lunch/breaks

**What constitutes a "logical unit":**
- ✅ One function implemented and tested
- ✅ One bug fixed and verified
- ✅ One configuration file updated
- ✅ One documentation section completed
- ❌ NOT: Half a function + documentation + unrelated fix

### Atomic Commits

**Each commit should:**
1. **Build successfully** (unless marked [WIP])
2. **Have a single purpose** (one feature, one fix, one doc update)
3. **Be self-contained** (doesn't depend on uncommitted changes)
4. **Have a clear message** (explains what and why)

**Example of good commit sequence:**
```bash
[FEATURE] Camera: Add CameraDevice wrapper class
[FEATURE] Camera: Implement USB detection
[FEATURE] Camera: Implement network detection
[TEST] Camera: Add enumeration tests
[DOCS] Updated PROGRESS with camera integration
```

**Example of bad commit:**
```bash
[FEATURE] Added camera support and fixed networking and updated docs
# ❌ Too many unrelated changes
```

---

## 🔍 REVIEWING COMMITS

### Before Committing

```bash
# Review what you're committing
git status                  # High-level overview
git diff                    # Detailed differences (unstaged)
git diff --cached          # Detailed differences (staged)

# Check for common issues:
# - Debug print statements
# - Commented-out code
# - TODO markers
# - Hardcoded paths/credentials
# - Whitespace errors

# Fix issues before committing
```

### After Committing (Before Pushing)

```bash
# Review last commit
git show

# Check commit message format
git log --oneline -1

# If issues found:
git commit --amend         # Fix the commit
```

---

## 📈 BEST PRACTICES

### DO ✅

1. **Commit early and often** - Small, frequent commits
2. **Write descriptive messages** - Future you will thank you
3. **Use [TYPE] prefixes** - Makes log readable
4. **Review before committing** - `git diff --cached`
5. **Pull before pushing** - Avoid conflicts
6. **Document in commit messages** - Explain "why", not just "what"
7. **Keep commits atomic** - One logical change per commit
8. **Test before committing** - Ensure code compiles (unless [WIP])
9. **Update docs with code** - Keep them in sync
10. **Use branches for experiments** - Keep main stable (Phase 2+)

### DON'T ❌

1. **Don't commit commented-out code** - Use git history instead
2. **Don't commit credentials** - Use environment variables/config files
3. **Don't commit generated files** - Add to .gitignore
4. **Don't commit broken code** - Unless marked [WIP]
5. **Don't use generic messages** - "fixed stuff" tells nothing
6. **Don't commit massive changes** - Break into smaller commits
7. **Don't mix changes** - Separate features/fixes/docs
8. **Don't force push** - Unless you really know what you're doing
9. **Don't commit without testing** - At least verify it compiles
10. **Don't forget to push** - Local commits aren't backed up

---

## 🎓 GIT COMMAND QUICK REFERENCE

### Essential Commands

```bash
# Setup
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
git clone https://github.com/unmanned-systems-uk/DPM.git

# Daily workflow
git status                      # Check status
git add <file>                  # Stage file
git add -A                      # Stage all
git commit -m "message"         # Commit
git push origin main            # Push
git pull origin main            # Pull

# History
git log                         # Full log
git log --oneline              # Compact log
git log -p                     # Log with diffs
git show <commit>              # Show commit details

# Undoing
git checkout -- <file>         # Discard changes
git reset HEAD <file>          # Unstage
git reset --soft HEAD~1        # Undo last commit
git revert <commit>            # Revert commit

# Branching
git branch                     # List branches
git branch <name>              # Create branch
git checkout <name>            # Switch branch
git merge <branch>             # Merge branch

# Remote
git remote -v                  # Show remotes
git fetch origin               # Fetch updates
git push origin <branch>       # Push branch
```

---

## 📋 PRE-COMMIT CHECKLIST

Before every commit, verify:

- [ ] Code compiles (or marked [WIP])
- [ ] Tests pass (when tests exist)
- [ ] No debug/test code left in
- [ ] No commented-out code
- [ ] No hardcoded credentials/paths
- [ ] PROGRESS_AND_TODO.md updated (if relevant)
- [ ] Commit message has [TYPE] prefix
- [ ] Commit message is descriptive
- [ ] Changes are related (atomic commit)
- [ ] Reviewed diff: `git diff --cached`

---

## 🔐 SECURITY REMINDERS

### Never Commit:
- Passwords or tokens (except in this documented case)
- API keys
- Private keys
- Database credentials
- Hardcoded IP addresses of private systems
- Personal information

### If Accidentally Committed:
1. **Don't panic**
2. If not pushed: `git reset --soft HEAD~1` and remove
3. If pushed: Change/revoke credentials immediately
4. Consider: `git filter-branch` to remove from history (advanced)
5. Document incident

---

## 🎯 SUMMARY

**Key Takeaways:**

1. **Commit frequently** - Every 30-60 minutes
2. **Use [TYPE] prefixes** - Readable history
3. **Write good messages** - Explain what and why
4. **Review before committing** - `git diff --cached`
5. **Push regularly** - End of session minimum
6. **Keep commits atomic** - One purpose per commit
7. **Update docs with code** - Never orphan documentation
8. **Follow the workflow** - Start → Work → Commit → Push → End

**Remember:** Git is your safety net. Use it well!

---

**Document Version:** 1.0  
**Last Updated:** October 24, 2025  
**Maintained By:** Project Team

**Related Documents:**
- `CC_READ_THIS_FIRST.md` - Overall workflow rules
- `CC_QUICK_REFERENCE.md` - Quick reference card
- `PROGRESS_UPDATE_TEMPLATE.md` - Documentation update guide
