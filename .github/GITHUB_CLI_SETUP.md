# GitHub CLI Setup Instructions
*Created: 2025-11-05*

## Installation Complete! ✅

You've already installed GitHub CLI and GitKraken. Now let's set them up:

## Step 1: Authenticate GitHub CLI

Open a new PowerShell/Terminal window and run:

```powershell
# Authenticate with GitHub
gh auth login

# Follow the prompts:
# 1. Choose: GitHub.com
# 2. Choose: HTTPS
# 3. Authenticate with: Browser (easiest)
# 4. It will open browser for authentication
```

## Step 2: Verify Authentication

```powershell
# Check authentication status
gh auth status

# Should show: ✓ Logged in to github.com
```

## Step 3: Initial Project Setup

Run our setup script to create all labels and milestones:

```powershell
# Navigate to project
cd D:\DPM\DPM-V2

# Run setup (creates labels, milestones)
.\.github\scripts\setup-github-project.ps1
```

## Step 4: Import Existing TODOs (Optional)

Convert our existing TODO items to GitHub Issues:

```powershell
# Dry run first (preview what will be created)
.\.github\scripts\sync-todos-to-issues.ps1 -DryRun true

# If looks good, run for real
.\.github\scripts\sync-todos-to-issues.ps1
```

## Step 5: GitKraken Setup

1. **Open GitKraken**

2. **Connect Repository:**
   - File → Open → Navigate to D:\DPM\DPM-V2
   - Or File → Clone → Clone from GitHub

3. **Enable GitHub Integration:**
   - File → Preferences → Integrations
   - Connect to GitHub (OAuth)
   - Authorize GitKraken

4. **Enable Issue Tracking:**
   - Click the Issues icon (left sidebar)
   - Select GitHub Issues
   - It will auto-detect the repository

5. **View Project Board:**
   - Click Boards icon
   - Create new board or connect to GitHub Projects

## Daily Workflow

### Starting Work:
```powershell
# 1. Start your session
.\.github\scripts\cc-start-session.ps1

# 2. Pick an issue to work on
.\.github\scripts\cc-work-on-issue.ps1 123
```

### During Work:
- Make your changes
- Commit with issue references: `git commit -m "[DOMAIN][TYPE] Fix thing. Refs #123"`

### Completing Work:
```powershell
# Complete and create PR
.\.github\scripts\cc-complete-issue.ps1 123 "Your commit message"
```

### Quick Commands:

```powershell
# List your assigned issues
gh issue list --assignee @me

# Create new issue
gh issue create --title "Fix focus distance" --body "Description" --label "air-side,bug,priority:high"

# View issue
gh issue view 123

# Add comment
gh issue comment 123 --body "Working on this now"

# Close issue
gh issue close 123 --comment "Fixed in PR #456"
```

## Benefits of This System

1. **Professional Tools:** GitHub's proven issue tracking
2. **Visual Management:** GitKraken shows project status visually
3. **Automation:** Scripts handle repetitive tasks
4. **Integration:** Works with existing GitHub features (Projects, Milestones, Labels)
5. **Audit Trail:** Complete history in GitHub
6. **Collaboration:** Multiple people can work simultaneously

## Troubleshooting

### "gh: command not found"
- Restart your terminal/PowerShell
- Or add to PATH manually: `C:\Program Files\GitHub CLI\`

### "Not authenticated"
- Run: `gh auth login`
- Choose browser authentication

### "Repository not found"
- Check you're in the right directory
- Verify remote: `git remote -v`

## Next Steps

1. ✅ GitHub CLI installed
2. ✅ GitKraken installed
3. ⏳ Authenticate GitHub CLI (`gh auth login`)
4. ⏳ Run setup script (`.github\scripts\setup-github-project.ps1`)
5. ⏳ Configure GitKraken integration
6. ⏳ Start using the workflow!

---

*Once setup is complete, task management becomes much more professional and scalable!*