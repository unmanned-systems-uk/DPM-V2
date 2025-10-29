# Git Cheat Sheet for DPM Project

**Date:** October 25, 2025  
**Project:** Drone Payload Manager (DPM-V2)  
**Repository:** https://github.com/unmanned-systems-uk/DPM-V2.git

---

## 🚀 Initial Setup

### Configure Git (First Time Only)

```bash
# Set your name:
git config --global user.name "Your Name"

# Set your email:
git config --global user.email "your.email@example.com"

# Set default branch name:
git config --global init.defaultBranch main

# Set default editor:
git config --global core.editor "nano"
# Or: "vim", "code --wait" (VS Code), "notepad" (Windows)

# Check your config:
git config --list

# Check specific setting:
git config user.name
```

### Clone Repository

```bash
# Clone the DPM-V2 repository:
git clone https://github.com/unmanned-systems-uk/DPM-V2.git

# Clone to specific folder:
git clone https://github.com/unmanned-systems-uk/DPM-V2.git my-dpm

# Clone specific branch:
git clone -b branch-name https://github.com/unmanned-systems-uk/DPM-V2.git

# Clone with SSH (if SSH keys set up):
git clone git@github.com:unmanned-systems-uk/DPM-V2.git
```

---

## 📊 Check Status

### View Repository State

```bash
# Check current status:
git status

# Short status (compact view):
git status -s

# Show branch info:
git status -sb

# Check which files changed:
git status --short
```

### View Changes

```bash
# Show unstaged changes:
git diff

# Show staged changes:
git diff --staged
# Or:
git diff --cached

# Show changes in specific file:
git diff path/to/file.cpp

# Show changes between branches:
git diff main..feature-branch

# Show only file names that changed:
git diff --name-only

# Show statistics:
git diff --stat
```

---

## 📝 Making Changes

### Stage Files (Add to Commit)

```bash
# Stage specific file:
git add file.cpp

# Stage multiple files:
git add file1.cpp file2.h file3.java

# Stage all modified files:
git add .

# Stage all files (including deleted):
git add -A

# Stage all files in a directory:
git add src/

# Stage files matching pattern:
git add *.cpp

# Stage only modified files (not new):
git add -u

# Interactively stage parts of files:
git add -p
```

### Unstage Files

```bash
# Unstage specific file:
git restore --staged file.cpp
# Or (older Git):
git reset HEAD file.cpp

# Unstage all files:
git restore --staged .
# Or:
git reset HEAD .
```

### Discard Changes

```bash
# Discard changes in specific file (CAREFUL - can't undo):
git restore file.cpp
# Or:
git checkout -- file.cpp

# Discard all changes (CAREFUL):
git restore .

# Discard changes in directory:
git restore src/
```

---

## 💾 Commit Changes

### Create Commits

```bash
# Commit staged changes:
git commit -m "Add camera control feature"

# Commit with detailed message:
git commit -m "Add camera control" -m "Implemented shutter, aperture, and ISO controls"

# Stage and commit in one step:
git commit -am "Fix network timeout bug"

# Commit and open editor for message:
git commit

# Amend last commit (add forgotten files):
git add forgotten-file.cpp
git commit --amend --no-edit

# Amend and change message:
git commit --amend -m "New commit message"
```

### Commit Message Format

```bash
# Good commit message format:
git commit -m "[TYPE] Brief description

Detailed explanation of what changed and why.

- Bullet points for multiple changes
- Reference issue numbers if applicable"

# Common types:
[FEAT] - New feature
[FIX] - Bug fix
[DOCS] - Documentation changes
[STYLE] - Code formatting
[REFACTOR] - Code restructuring
[TEST] - Adding tests
[CHORE] - Maintenance tasks

# Examples:
git commit -m "[FEAT] Add TCP server for H16 communication"
git commit -m "[FIX] Resolve Sony SDK callback lifetime issue"
git commit -m "[DOCS] Update network topology to 10.0.1.x"
```

---

## 📜 View History

### View Commit Log

```bash
# View commit history:
git log

# Compact one-line view:
git log --oneline

# Show last 5 commits:
git log -5

# Show with file changes:
git log --stat

# Show with diff:
git log -p

# Show graph of branches:
git log --graph --oneline --all

# Pretty format:
git log --pretty=format:"%h - %an, %ar : %s"

# Show commits by author:
git log --author="Your Name"

# Show commits in date range:
git log --since="2025-10-01" --until="2025-10-25"

# Show commits affecting specific file:
git log -- path/to/file.cpp
```

### View Specific Commit

```bash
# Show commit details:
git show commit-hash

# Show specific file in commit:
git show commit-hash:path/to/file.cpp

# Show files changed in commit:
git show --name-only commit-hash
```

---

## 🌿 Branches

### Create & Switch Branches

```bash
# List all branches:
git branch

# List remote branches:
git branch -r

# List all branches (local + remote):
git branch -a

# Create new branch:
git branch feature-gimbal-control

# Create and switch to new branch:
git checkout -b feature-gimbal-control
# Or (newer Git):
git switch -c feature-gimbal-control

# Switch to existing branch:
git checkout main
# Or:
git switch main

# Create branch from specific commit:
git branch new-branch commit-hash
```

### Rename & Delete Branches

```bash
# Rename current branch:
git branch -m new-name

# Rename any branch:
git branch -m old-name new-name

# Delete branch (safe - won't delete if unmerged):
git branch -d branch-name

# Force delete branch:
git branch -D branch-name

# Delete remote branch:
git push origin --delete branch-name
```

---

## 🔄 Merge & Rebase

### Merge Branches

```bash
# Merge branch into current branch:
git merge feature-branch

# Merge with commit message:
git merge feature-branch -m "Merge gimbal control feature"

# Abort merge (if conflicts):
git merge --abort

# Continue merge after resolving conflicts:
git merge --continue
```

### Rebase

```bash
# Rebase current branch onto main:
git rebase main

# Interactive rebase (last 3 commits):
git rebase -i HEAD~3

# Abort rebase:
git rebase --abort

# Continue rebase after resolving conflicts:
git rebase --continue

# Skip current commit:
git rebase --skip
```

### Resolve Conflicts

```bash
# When conflicts occur:

# 1. View conflicted files:
git status

# 2. Open conflicted file and edit:
#    Look for conflict markers:
#    <<<<<<< HEAD
#    Your changes
#    =======
#    Their changes
#    >>>>>>> branch-name

# 3. After resolving, stage the file:
git add resolved-file.cpp

# 4. Continue merge/rebase:
git merge --continue
# Or:
git rebase --continue
```

---

## 🌐 Remote Repositories

### View Remotes

```bash
# List remotes:
git remote

# List remotes with URLs:
git remote -v

# Show remote details:
git remote show origin
```

### Add & Remove Remotes

```bash
# Add remote:
git remote add origin https://github.com/user/repo.git

# Change remote URL:
git remote set-url origin https://github.com/user/new-repo.git

# Remove remote:
git remote remove origin

# Rename remote:
git remote rename old-name new-name
```

### Fetch & Pull

```bash
# Fetch changes from remote (doesn't merge):
git fetch origin

# Fetch all remotes:
git fetch --all

# Pull changes (fetch + merge):
git pull origin main

# Pull with rebase instead of merge:
git pull --rebase origin main

# Pull specific branch:
git pull origin feature-branch
```

### Push Changes

```bash
# Push to remote:
git push origin main

# Push current branch:
git push

# Push and set upstream:
git push -u origin feature-branch

# Force push (CAREFUL - overwrites remote):
git push --force origin main
# Safer force push:
git push --force-with-lease origin main

# Push all branches:
git push --all origin

# Push tags:
git push --tags
```

---

## 🏷️ Tags

### Create Tags

```bash
# Create lightweight tag:
git tag v1.0.0

# Create annotated tag:
git tag -a v1.0.0 -m "Release version 1.0.0"

# Tag specific commit:
git tag -a v1.0.0 commit-hash -m "Release 1.0.0"

# List all tags:
git tag

# List tags matching pattern:
git tag -l "v1.*"

# Show tag details:
git show v1.0.0
```

### Delete & Push Tags

```bash
# Delete local tag:
git tag -d v1.0.0

# Delete remote tag:
git push origin --delete v1.0.0

# Push specific tag:
git push origin v1.0.0

# Push all tags:
git push --tags
```

---

## 🔙 Undo Changes

### Undo Commits

```bash
# Undo last commit (keep changes):
git reset --soft HEAD~1

# Undo last commit (unstage changes):
git reset HEAD~1
# Or:
git reset --mixed HEAD~1

# Undo last commit (discard changes - CAREFUL):
git reset --hard HEAD~1

# Undo multiple commits:
git reset --soft HEAD~3

# Reset to specific commit:
git reset --hard commit-hash
```

### Revert Commits

```bash
# Create new commit that undoes changes:
git revert commit-hash

# Revert last commit:
git revert HEAD

# Revert without committing:
git revert -n commit-hash

# Revert merge commit:
git revert -m 1 merge-commit-hash
```

### Restore Files

```bash
# Restore file from last commit:
git restore file.cpp

# Restore file from specific commit:
git restore --source=commit-hash file.cpp

# Restore all files:
git restore .

# Restore staged file (unstage):
git restore --staged file.cpp
```

---

## 🧹 Clean Up

### Remove Untracked Files

```bash
# Show what would be deleted (dry run):
git clean -n

# Delete untracked files:
git clean -f

# Delete untracked files and directories:
git clean -fd

# Delete untracked and ignored files:
git clean -fdx

# Interactive clean:
git clean -i
```

### Prune & Optimize

```bash
# Remove remote-tracking branches that no longer exist:
git remote prune origin

# Optimize repository:
git gc

# Aggressive optimization:
git gc --aggressive --prune=now
```

---

## 🔍 Search & Find

### Search in Files

```bash
# Search for text in tracked files:
git grep "search-term"

# Search in specific files:
git grep "search-term" *.cpp

# Search showing line numbers:
git grep -n "search-term"

# Search case-insensitive:
git grep -i "search-term"

# Search in specific commit:
git grep "search-term" commit-hash
```

### Find Commits

```bash
# Find commits with message containing text:
git log --grep="bug fix"

# Find commits that changed specific text:
git log -S "function-name"

# Find who changed a line:
git blame file.cpp

# Show file history:
git log --follow -- file.cpp

# Find when file was deleted:
git log --all --full-history -- path/to/deleted/file.cpp
```

---

## 📦 Stash Changes

### Save Work in Progress

```bash
# Stash current changes:
git stash

# Stash with message:
git stash save "Work on camera feature"

# Stash including untracked files:
git stash -u

# Stash including ignored files:
git stash -a

# List all stashes:
git stash list

# Show stash contents:
git stash show
git stash show -p stash@{0}
```

### Apply Stashed Changes

```bash
# Apply most recent stash:
git stash apply

# Apply specific stash:
git stash apply stash@{2}

# Apply and remove stash:
git stash pop

# Apply stash to new branch:
git stash branch new-branch-name

# Drop specific stash:
git stash drop stash@{0}

# Clear all stashes:
git stash clear
```

---

## 🔀 Cherry-Pick

### Apply Specific Commits

```bash
# Apply commit from another branch:
git cherry-pick commit-hash

# Cherry-pick multiple commits:
git cherry-pick commit1-hash commit2-hash

# Cherry-pick without committing:
git cherry-pick -n commit-hash

# Abort cherry-pick:
git cherry-pick --abort

# Continue after resolving conflicts:
git cherry-pick --continue
```

---

## 🎯 DPM Project Workflows

### Daily Development Workflow

```bash
# 1. Start of day - update your branch:
git checkout main
git pull origin main

# 2. Create feature branch:
git checkout -b feature-camera-white-balance

# 3. Make changes and commit regularly:
git add src/camera/white_balance.cpp
git commit -m "[FEAT] Add white balance control"

# 4. Keep branch updated with main:
git fetch origin
git rebase origin/main

# 5. Push to remote:
git push -u origin feature-camera-white-balance

# 6. When ready, merge to main:
git checkout main
git merge feature-camera-white-balance
git push origin main
```

### Quick Commit Pattern

```bash
# Stage all, commit, and push (use during active development):
git add -A && git commit -m "[FEAT] Description" && git push
```

### Emergency Bug Fix

```bash
# 1. Create hotfix branch from main:
git checkout main
git pull origin main
git checkout -b hotfix-network-timeout

# 2. Fix the bug and commit:
git add src/network/tcp_client.cpp
git commit -m "[FIX] Resolve network timeout issue"

# 3. Merge back to main:
git checkout main
git merge hotfix-network-timeout
git push origin main

# 4. Delete hotfix branch:
git branch -d hotfix-network-timeout
```

### Before Important Changes

```bash
# Create backup branch:
git checkout -b backup-before-refactor

# Make changes on new branch:
git checkout -b refactor-network-stack

# If everything works, delete backup:
git branch -D backup-before-refactor
```

---

## 🔧 Configuration

### Useful Aliases

```bash
# Create shortcuts for common commands:

# Status alias:
git config --global alias.st status

# Commit alias:
git config --global alias.ci commit

# Checkout alias:
git config --global alias.co checkout

# Branch alias:
git config --global alias.br branch

# Pretty log:
git config --global alias.lg "log --oneline --graph --all"

# Undo last commit:
git config --global alias.undo "reset --soft HEAD~1"

# Now use them:
git st
git ci -m "message"
git co main
git lg
```

### Useful Settings

```bash
# Set default push behavior:
git config --global push.default current

# Enable color output:
git config --global color.ui auto

# Set merge tool:
git config --global merge.tool vimdiff

# Set diff tool:
git config --global diff.tool vimdiff

# Cache credentials (1 hour):
git config --global credential.helper 'cache --timeout=3600'

# Line ending settings (Windows):
git config --global core.autocrlf true

# Line ending settings (Linux/Mac):
git config --global core.autocrlf input
```

---

## 📁 .gitignore

### Common Patterns for DPM Project

Create `.gitignore` file in project root:

```gitignore
# Build directories
build/
bin/
obj/
out/

# C++ compiled files
*.o
*.obj
*.exe
*.dll
*.so
*.dylib
*.a
*.lib

# CMake
CMakeCache.txt
CMakeFiles/
cmake_install.cmake
Makefile

# Android
*.apk
*.ap_
*.dex
*.class
local.properties
.gradle/
.idea/
*.iml
captures/
.externalNativeBuild/
.cxx/

# Android Studio
.DS_Store
/build
/captures
.externalNativeBuild
.cxx

# Gradle
.gradle
/local.properties

# IDE
.vscode/
.vs/
*.swp
*.swo
*~

# Logs
*.log

# Temporary files
*.tmp
*.temp
*.bak

# OS files
.DS_Store
Thumbs.db

# Sony SDK (if externalized)
sony_sdk/

# Credentials and secrets
*.key
*.pem
credentials.json
secrets.txt

# Documentation builds
docs/_build/
docs/html/

# Personal notes
TODO.txt
NOTES.md
```

### Add .gitignore

```bash
# Create .gitignore:
nano .gitignore
# (Add patterns above)

# Add to git:
git add .gitignore
git commit -m "[CHORE] Add .gitignore"

# Remove already-tracked files:
git rm --cached file-to-ignore
git commit -m "[CHORE] Remove tracked file from git"
```

---

## 🚨 Emergency Commands

### Recover Lost Work

```bash
# Show reflog (history of HEAD):
git reflog

# Recover deleted branch:
git checkout -b recovered-branch commit-hash

# Recover deleted commit:
git cherry-pick commit-hash

# Find lost commits:
git fsck --lost-found
```

### Fix Mistakes

```bash
# Committed to wrong branch:
git reset --soft HEAD~1  # Undo commit
git stash                # Save changes
git checkout correct-branch
git stash pop            # Apply changes
git commit               # Commit to correct branch

# Pushed sensitive data:
# 1. Remove from history:
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch path/to/file" \
  --prune-empty --tag-name-filter cat -- --all
# 2. Force push:
git push --force --all origin

# Made commit on main instead of branch:
git branch feature-branch  # Create branch at current commit
git reset --hard HEAD~1    # Move main back
git checkout feature-branch
```

### Sync Fork with Upstream

```bash
# Add upstream remote:
git remote add upstream https://github.com/original/repo.git

# Fetch upstream:
git fetch upstream

# Merge upstream changes:
git checkout main
git merge upstream/main

# Push to your fork:
git push origin main
```

---

## 📊 Advanced Commands

### Submodules

```bash
# Add submodule:
git submodule add https://github.com/user/repo.git path/to/submodule

# Clone repo with submodules:
git clone --recurse-submodules https://github.com/user/repo.git

# Initialize submodules after clone:
git submodule init
git submodule update

# Update all submodules:
git submodule update --remote

# Remove submodule:
git submodule deinit path/to/submodule
git rm path/to/submodule
```

### Bisect (Find Bug)

```bash
# Start bisect:
git bisect start

# Mark current commit as bad:
git bisect bad

# Mark known good commit:
git bisect good commit-hash

# Test commit, mark as good or bad:
git bisect good  # If works
git bisect bad   # If broken

# Git will binary search to find the bad commit

# End bisect:
git bisect reset
```

### Worktrees

```bash
# Create new worktree:
git worktree add ../dpm-hotfix hotfix-branch

# List worktrees:
git worktree list

# Remove worktree:
git worktree remove ../dpm-hotfix
```

---

## 💡 Best Practices

### Commit Guidelines

✅ **DO:**
- Commit often (every 30-60 minutes of work)
- Write clear, descriptive commit messages
- Use present tense ("Add feature" not "Added feature")
- Keep commits focused on single changes
- Test before committing
- Use branches for features

❌ **DON'T:**
- Commit broken code to main
- Use generic messages ("fix", "update", "changes")
- Commit credentials or secrets
- Make huge commits with many changes
- Force push to shared branches
- Commit generated files (build artifacts)

### Branch Strategy

```
main (production-ready)
  ├─ develop (integration branch)
  │   ├─ feature-camera-control
  │   ├─ feature-gimbal-integration
  │   └─ feature-mavlink-support
  └─ hotfix-critical-bug
```

### Git Workflow for DPM

```bash
# Feature development:
1. git checkout main
2. git pull origin main
3. git checkout -b feature-name
4. [Make changes and commit]
5. git push -u origin feature-name
6. [Create pull request]
7. [After review] git checkout main && git merge feature-name

# Bug fixes:
1. git checkout -b fix-bug-name
2. [Fix and commit]
3. git push -u origin fix-bug-name
4. [Merge to main]

# Regular commits during development:
git add -A
git commit -m "[TYPE] Clear description"
git push
```

---

## 📞 Quick Reference Card

### Essential Commands

```bash
# Check status
git status

# Stage all changes
git add -A

# Commit
git commit -m "message"

# Push
git push

# Pull
git pull

# Create branch
git checkout -b branch-name

# Switch branch
git checkout branch-name

# Merge branch
git merge branch-name

# View history
git log --oneline

# Undo last commit
git reset --soft HEAD~1

# Discard changes
git restore file.cpp

# Stash changes
git stash

# Apply stash
git stash pop
```

---

## 🎓 Git Terminology

- **Repository (Repo):** Project folder tracked by Git
- **Commit:** Snapshot of changes
- **Branch:** Independent line of development
- **Remote:** Repository hosted on server (GitHub)
- **Origin:** Default name for remote repository
- **Main/Master:** Primary branch
- **HEAD:** Pointer to current commit
- **Staging Area (Index):** Files ready to commit
- **Working Directory:** Your project files
- **Clone:** Copy remote repository locally
- **Fork:** Copy repository to your account
- **Pull Request (PR):** Request to merge changes
- **Merge:** Combine branches
- **Rebase:** Move commits to new base
- **Cherry-pick:** Apply specific commit
- **Stash:** Temporarily save changes
- **Tag:** Mark specific commit (version)

---

## 🆘 Help Commands

```bash
# General help:
git help

# Help for specific command:
git help commit
git help branch

# Quick help:
git commit --help

# List all commands:
git help -a

# Git manual:
man git
```

---

## 📚 Additional Resources

- **Git Documentation:** https://git-scm.com/doc
- **GitHub Guides:** https://guides.github.com/
- **Git Cheat Sheet (Official):** https://training.github.com/downloads/github-git-cheat-sheet/
- **Learn Git Branching:** https://learngitbranching.js.org/
- **Oh Shit, Git!?!:** https://ohshitgit.com/

---

**Document Version:** 1.0  
**Last Updated:** October 25, 2025  
**Project:** Drone Payload Manager (DPM-V2)  
**Repository:** unmanned-systems-uk/DPM-V2

---

## 🎉 You're Now a Git Master!

Keep this cheat sheet handy during development. For daily work, the "Quick Reference Card" section has everything you need most often.

Happy committing! 🚀
