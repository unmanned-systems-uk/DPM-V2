# GitHub Project Management Setup for DPM-V2
*Created: 2025-11-05*

## Prerequisites
1. Install GitHub CLI: https://cli.github.com/
   ```powershell
   # Windows (via Scoop)
   scoop install gh

   # Or via Chocolatey
   choco install gh

   # Or download installer from https://cli.github.com/
   ```

2. Authenticate GitHub CLI:
   ```bash
   gh auth login
   # Follow prompts to authenticate with GitHub
   ```

## Step 1: Create Project Structure

Run the setup script:
```bash
.github/scripts/setup-github-project.ps1
```

This will:
- Create labels for each domain (air-side, ground-side, dev-tools)
- Create priority labels (critical, high, medium, low)
- Create status labels (in-progress, blocked, testing)
- Create milestones for Phase 1, 2, 3
- Convert existing TODOs to GitHub Issues

## Step 2: GitKraken Setup

1. Open GitKraken
2. Connect to GitHub repository
3. Enable Issue Tracking:
   - File → Preferences → Issue Tracker
   - Select GitHub Issues
   - Connect to unmanned-systems-uk/DPM-V2

4. Enable GitKraken Boards:
   - Click Boards icon
   - Create board "DPM-V2 Sprint"
   - Connect to GitHub Project

## Step 3: Claude Code Workflow

When starting a session:
```bash
# Check assigned issues
.github/scripts/cc-start-session.ps1

# Pick an issue to work on
.github/scripts/cc-work-on-issue.ps1 123

# Complete an issue
.github/scripts/cc-complete-issue.ps1 123 "Fix message"
```

## Workflow Commands Reference

### Starting Work
```bash
# List open issues assigned to you
gh issue list --assignee @me --state open

# View issue details
gh issue view 123

# Mark as in-progress
gh issue edit 123 --add-label "in-progress"
gh issue comment 123 --body "Starting work on this issue"
```

### During Work
```bash
# Create feature branch
git checkout -b fix/issue-123

# Make changes and commit with issue reference
git add -A
git commit -m "[DOMAIN][TYPE] Description

Refs #123"
```

### Completing Work
```bash
# Push branch
git push -u origin fix/issue-123

# Create pull request
gh pr create --title "[DOMAIN][TYPE] Fix for issue #123" \
  --body "Fixes #123" \
  --base main

# After merge, close issue
gh issue close 123 --comment "Fixed in PR #456"
```

## Automation Scripts

All automation scripts are in `.github/scripts/`:
- `setup-github-project.ps1` - Initial project setup
- `cc-start-session.ps1` - Start CC work session
- `cc-work-on-issue.ps1` - Begin work on specific issue
- `cc-complete-issue.ps1` - Complete and close issue
- `sync-todos-to-issues.ps1` - Sync markdown TODOs to GitHub Issues
- `generate-progress-report.ps1` - Generate progress reports

## Integration with SystemTools

SystemTools Phase 3 will be simplified to:
- Read-only GitHub issue display
- Quick issue creation dialog
- Current sprint progress view
- Links to open in GitHub/GitKraken

## Benefits

1. **Professional Tools**: Use GitHub's proven project management
2. **Automation**: CC can manage everything via CLI
3. **Visibility**: GitKraken provides visual project status
4. **Integration**: Works with existing developer workflows
5. **History**: Full audit trail in GitHub