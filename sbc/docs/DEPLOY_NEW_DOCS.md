# Deploying New Documentation System
## DPM Payload Manager - Setup Instructions

**Date:** October 24, 2025  
**Purpose:** Deploy Claude Code workflow documentation  
**Time Required:** 15 minutes

---

## 📦 WHAT YOU'RE DEPLOYING

### New Documentation Files

1. **CC_READ_THIS_FIRST.md** - Mandatory workflow rules (~800 lines)
2. **CC_QUICK_REFERENCE.md** - One-page cheat sheet (~300 lines)
3. **PROGRESS_UPDATE_TEMPLATE.md** - Documentation update guide (~600 lines)
4. **GIT_WORKFLOW.md** - Git procedures and best practices (~700 lines)
5. **DOCUMENTATION_INDEX.md** - Master document index (~450 lines)
6. **DEPLOY_NEW_DOCS.md** - This file (~150 lines)

**Total:** ~3,000 lines of workflow documentation

---

## 🎯 DEPLOYMENT GOALS

1. ✅ Establish clear workflow for Claude Code
2. ✅ Ensure regular documentation updates
3. ✅ Enforce regular Git commits
4. ✅ Prevent orphaned documentation
5. ✅ Improve project maintainability
6. ✅ Reduce reading burden on CC (no more rereading 800-line planning docs)

---

## 📋 PRE-DEPLOYMENT CHECKLIST

**Before deploying, verify you have:**

- [ ] Downloaded all 6 new markdown files
- [ ] Access to project directory: `/home/dpm/DPM/sbc/`
- [ ] SSH access to Raspberry Pi (dpm@10.0.1.127)
- [ ] Git credentials available
- [ ] Current PROGRESS_AND_TODO.md backed up (optional safety)

---

## 🚀 DEPLOYMENT PROCEDURE

### Step 1: Access Project Directory

```bash
# SSH to Raspberry Pi
ssh dpm@10.0.1.127
# Password: 2350

# Navigate to docs directory
cd /home/dpm/DPM/sbc/docs

# Verify you're in the right place
pwd
# Should show: /home/dpm/DPM/sbc/docs

# Check current docs
ls -la
```

### Step 2: Upload New Documentation Files

**Option A: Upload from your local machine**

```bash
# On your local machine (where you downloaded the files)
scp CC_READ_THIS_FIRST.md dpm@10.0.1.127:/home/dpm/DPM/sbc/docs/
scp CC_QUICK_REFERENCE.md dpm@10.0.1.127:/home/dpm/DPM/sbc/docs/
scp PROGRESS_UPDATE_TEMPLATE.md dpm@10.0.1.127:/home/dpm/DPM/sbc/docs/
scp GIT_WORKFLOW.md dpm@10.0.1.127:/home/dpm/DPM/sbc/docs/
scp DOCUMENTATION_INDEX.md dpm@10.0.1.127:/home/dpm/DPM/sbc/docs/
scp DEPLOY_NEW_DOCS.md dpm@10.0.1.127:/home/dpm/DPM/sbc/docs/
```

**Option B: Copy-paste into files on Raspberry Pi**

```bash
# On Raspberry Pi
cd /home/dpm/DPM/sbc/docs

# Create each file
nano CC_READ_THIS_FIRST.md
# Paste content, Ctrl+O to save, Ctrl+X to exit

nano CC_QUICK_REFERENCE.md
# Paste content, save, exit

# Repeat for all 6 files...
```

**Option C: Use git to download (if already committed elsewhere)**

```bash
# If files are in a branch or different repo
git fetch origin
git checkout origin/docs-branch -- docs/CC_READ_THIS_FIRST.md
# etc.
```

### Step 3: Verify Files

```bash
# Check files were uploaded
cd /home/dpm/DPM/sbc/docs
ls -la

# Should see:
# CC_READ_THIS_FIRST.md
# CC_QUICK_REFERENCE.md
# PROGRESS_UPDATE_TEMPLATE.md
# GIT_WORKFLOW.md
# DOCUMENTATION_INDEX.md
# DEPLOY_NEW_DOCS.md
# (plus existing docs)

# Verify content of a file
head -20 CC_READ_THIS_FIRST.md
# Should show the header
```

### Step 4: Update .gitignore (if needed)

```bash
# Check if .gitignore exists
cd /home/dpm/DPM/sbc
cat .gitignore

# If it doesn't exist or needs updates, create/edit it
nano .gitignore
```

**Recommended .gitignore contents:**
```
# Build artifacts
build/
*.o
*.so
*.a
payload_manager
test_camera
test_shutter

# Logs
logs/*.log
logs/*.txt

# IDE files
.vscode/
.idea/
*.swp
*~

# OS files
.DS_Store
Thumbs.db

# Temporary files
*.tmp
*.bak
```

### Step 5: Commit New Documentation

```bash
cd /home/dpm/DPM/sbc

# Check status
git status

# Stage new documentation files
git add docs/CC_READ_THIS_FIRST.md
git add docs/CC_QUICK_REFERENCE.md
git add docs/PROGRESS_UPDATE_TEMPLATE.md
git add docs/GIT_WORKFLOW.md
git add docs/DOCUMENTATION_INDEX.md
git add docs/DEPLOY_NEW_DOCS.md

# If you updated .gitignore
git add .gitignore

# Verify what's staged
git status

# Commit with descriptive message
git commit -m "[DOCS] Add Claude Code workflow documentation system

- CC_READ_THIS_FIRST.md: Mandatory workflow rules for CC
- CC_QUICK_REFERENCE.md: One-page cheat sheet
- PROGRESS_UPDATE_TEMPLATE.md: Documentation update guide
- GIT_WORKFLOW.md: Git procedures and best practices
- DOCUMENTATION_INDEX.md: Master documentation index
- DEPLOY_NEW_DOCS.md: Deployment instructions

Purpose:
- Enforce regular documentation updates
- Ensure regular Git commits
- Prevent orphaned documentation
- Streamline CC workflow
- Reduce redundant reading of large planning docs"

# Push to remote
git push origin main

# Verify push succeeded
git log --oneline -1
```

### Step 6: Test Documentation

```bash
# Try reading the main file
cat docs/CC_READ_THIS_FIRST.md | head -50

# Quick reference
cat docs/CC_QUICK_REFERENCE.md

# Check formatting
head -100 docs/DOCUMENTATION_INDEX.md
```

---

## ✅ POST-DEPLOYMENT VERIFICATION

### Verify Deployment Success

**Check 1: Files exist and are readable**
```bash
cd /home/dpm/DPM/sbc/docs
ls -lh CC_READ_THIS_FIRST.md
# Should show file size and permissions
cat CC_READ_THIS_FIRST.md | wc -l
# Should show ~800 lines
```

**Check 2: Git tracking**
```bash
git status
# Should show: "nothing to commit, working tree clean"

git log --oneline -1
# Should show your commit message
```

**Check 3: GitHub visibility**
```bash
# Visit: https://github.com/unmanned-systems-uk/DPM
# Navigate to: sbc/docs/
# Verify all 6 files are visible
```

**Check 4: Content integrity**
```bash
# Verify key sections exist
grep "SESSION START CHECKLIST" docs/CC_READ_THIS_FIRST.md
grep "COMMIT TYPES" docs/CC_QUICK_REFERENCE.md
grep "TEMPLATE SECTIONS" docs/PROGRESS_UPDATE_TEMPLATE.md
```

---

## 🎓 TRAINING CLAUDE CODE

### First Session After Deployment

**Tell Claude Code:**

```
New workflow documentation is deployed! 

Please start by reading CC_READ_THIS_FIRST.md - this is now your 
mandatory first read for every session. It contains all the rules 
for updating documentation and committing to git.

The key changes:
1. Read CC_READ_THIS_FIRST.md at start of every session
2. Read PROGRESS_AND_TODO.md for current status
3. Update PROGRESS_AND_TODO.md after significant changes
4. Commit regularly (every 30-60 min) without asking
5. Don't re-read Project_Summary_and_Action_Plan.md unless needed

Let's verify you can access the docs:
```

**Then ask CC to:**
```bash
cat /home/dpm/DPM/sbc/docs/CC_READ_THIS_FIRST.md | head -100
```

### Subsequent Sessions

**Just tell CC:**
```
Please read CC_READ_THIS_FIRST.md and PROGRESS_AND_TODO.md 
to understand current status and workflow.
```

---

## 🔧 TROUBLESHOOTING

### Problem: Files won't upload

**Solution:**
```bash
# Check SSH connection
ssh dpm@10.0.1.127 "echo Connection works"

# Check directory exists
ssh dpm@10.0.1.127 "ls -la /home/dpm/DPM/sbc/docs"

# Check permissions
ssh dpm@10.0.1.127 "ls -la /home/dpm/DPM/sbc"

# If permission denied, fix it
ssh dpm@10.0.1.127
sudo chown -R dpm:dpm /home/dpm/DPM/sbc
```

### Problem: Git push fails

**Solution:**
```bash
# Check credentials
git config --global user.name
git config --global user.email

# Configure if needed
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Check remote
git remote -v

# Try pull first
git pull origin main

# Then push
git push origin main
```

### Problem: Files have Windows line endings

**Solution:**
```bash
# Convert line endings
dos2unix docs/CC_READ_THIS_FIRST.md
dos2unix docs/CC_QUICK_REFERENCE.md
dos2unix docs/PROGRESS_UPDATE_TEMPLATE.md
dos2unix docs/GIT_WORKFLOW.md
dos2unix docs/DOCUMENTATION_INDEX.md
dos2unix docs/DEPLOY_NEW_DOCS.md

# Or if dos2unix not available
sed -i 's/\r$//' docs/*.md
```

### Problem: Markdown formatting broken

**Solution:**
```bash
# Check if file is complete
wc -l docs/CC_READ_THIS_FIRST.md
# Should be ~800 lines

# Check for corruption
head -5 docs/CC_READ_THIS_FIRST.md
tail -5 docs/CC_READ_THIS_FIRST.md

# Re-upload if needed
```

---

## 📊 DEPLOYMENT VERIFICATION CHECKLIST

After deployment, verify:

**Files:**
- [ ] CC_READ_THIS_FIRST.md uploaded (~800 lines)
- [ ] CC_QUICK_REFERENCE.md uploaded (~300 lines)
- [ ] PROGRESS_UPDATE_TEMPLATE.md uploaded (~600 lines)
- [ ] GIT_WORKFLOW.md uploaded (~700 lines)
- [ ] DOCUMENTATION_INDEX.md uploaded (~450 lines)
- [ ] DEPLOY_NEW_DOCS.md uploaded (~150 lines)

**Git:**
- [ ] All files committed to git
- [ ] Commit message is descriptive
- [ ] Changes pushed to GitHub
- [ ] Files visible on GitHub web interface

**Testing:**
- [ ] Files readable with `cat` command
- [ ] Markdown formatting correct
- [ ] Line counts approximately correct
- [ ] No corruption or truncation

**Claude Code:**
- [ ] CC can access CC_READ_THIS_FIRST.md
- [ ] CC understands new workflow
- [ ] CC follows documentation update rules
- [ ] CC commits regularly

---

## 🎯 EXPECTED OUTCOMES

After successful deployment:

### Immediate Effects (Day 1)

1. **Claude Code behavior changes:**
   - Reads CC_READ_THIS_FIRST.md at session start
   - Updates PROGRESS_AND_TODO.md regularly
   - Commits every 30-60 minutes
   - Uses [TYPE] prefixes in commits
   - Doesn't ask permission to commit

2. **Documentation quality improves:**
   - PROGRESS_AND_TODO.md stays current
   - No orphaned documentation
   - Consistent formatting
   - Regular timestamps

3. **Git history improves:**
   - More frequent commits
   - Better commit messages
   - Clear project progression
   - Easier to review changes

### Long-term Effects (Week 1+)

1. **Workflow efficiency:**
   - Less time reading redundant docs
   - Faster session starts
   - Clear task priorities
   - Better project tracking

2. **Maintainability:**
   - Always know project status
   - Easy to onboard new developers
   - Clear development history
   - Professional documentation

3. **Quality:**
   - Fewer bugs from poor documentation
   - Better coordination
   - Easier debugging
   - Clear audit trail

---

## 🔄 ROLLBACK PROCEDURE (If Needed)

**If deployment causes problems:**

```bash
# Revert the commit
cd /home/dpm/DPM/sbc
git log --oneline -5
# Identify the commit hash of the documentation deployment

git revert <commit-hash>
# Or
git reset --hard HEAD~1  # If not pushed yet

# Remove files
rm docs/CC_READ_THIS_FIRST.md
rm docs/CC_QUICK_REFERENCE.md
rm docs/PROGRESS_UPDATE_TEMPLATE.md
rm docs/GIT_WORKFLOW.md
rm docs/DOCUMENTATION_INDEX.md
rm docs/DEPLOY_NEW_DOCS.md

# Push if needed
git push origin main
```

**Then:** Review what went wrong, fix issues, redeploy.

---

## 📈 MEASURING SUCCESS

### Week 1 Metrics

Track these to measure improvement:

- [ ] Git commits per day (should increase)
- [ ] Days since PROGRESS_AND_TODO.md updated (should be < 1)
- [ ] Commit message quality (should have [TYPE] prefix)
- [ ] Documentation-code sync (should be perfect)
- [ ] Time to session start (should decrease)

### Success Indicators

**Good signs:**
- ✅ PROGRESS_AND_TODO.md updated daily
- ✅ 5-10 commits per work day
- ✅ All commits have [TYPE] prefixes
- ✅ No "orphaned" code/docs
- ✅ CC session starts in < 5 minutes

**Warning signs:**
- ⚠️ PROGRESS_AND_TODO.md not updated in 2+ days
- ⚠️ < 2 commits per work day
- ⚠️ Vague commit messages
- ⚠️ Code without documentation
- ⚠️ CC confused about what to work on

---

## 🎉 DEPLOYMENT COMPLETE

**Congratulations!** You've deployed the Claude Code workflow documentation system.

**Next Steps:**

1. **For your next Claude Code session, say:**
   ```
   Please read CC_READ_THIS_FIRST.md and PROGRESS_AND_TODO.md 
   to understand the new workflow, then continue with current tasks.
   ```

2. **Monitor for first few days:**
   - Check PROGRESS_AND_TODO.md updates
   - Review commit history
   - Verify workflow is being followed

3. **Adjust if needed:**
   - Update rules in CC_READ_THIS_FIRST.md
   - Clarify confusing sections
   - Add examples if needed

4. **Enjoy the benefits:**
   - Better documentation
   - Regular commits
   - Clear project status
   - Efficient workflow

---

## 📞 SUPPORT

**If you encounter issues:**

1. Check TROUBLESHOOTING section above
2. Review DOCUMENTATION_INDEX.md for document relationships
3. Verify all files uploaded correctly
4. Test Git operations
5. Restart Claude Code session with clear instructions

**Common first-session issues:**
- CC doesn't know new docs exist → Tell CC explicitly
- CC asks permission to commit → Remind about workflow rules
- CC doesn't update docs → Remind to read CC_READ_THIS_FIRST.md

---

## ✅ FINAL CHECKLIST

Before considering deployment complete:

- [ ] All 6 files uploaded
- [ ] Files committed to git
- [ ] Changes pushed to GitHub
- [ ] Files readable and formatted correctly
- [ ] .gitignore updated (if needed)
- [ ] Tested with `cat` command
- [ ] Verified on GitHub web interface
- [ ] Informed Claude Code about new workflow
- [ ] CC successfully read CC_READ_THIS_FIRST.md
- [ ] First session after deployment successful

**All checked? Deployment successful! 🎉**

---

**Deployment Guide Version:** 1.0  
**Last Updated:** October 24, 2025  
**Deployed By:** [Your name]  
**Deployment Date:** [Date deployed]

**Status:** Ready for deployment ✅

---

**🚀 Deploy with confidence! These docs will improve your development workflow significantly.**
