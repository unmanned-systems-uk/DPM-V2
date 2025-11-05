# Claude Code Session Start Script
# Shows available issues and helps select work

Write-Host "=== Claude Code Session Starting ===" -ForegroundColor Cyan
Write-Host "Session Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm')" -ForegroundColor Gray
Write-Host ""

$owner = "unmanned-systems-uk"
$repo = "DPM-V2"

# Show current branch
$branch = git branch --show-current
Write-Host "Current Branch: $branch" -ForegroundColor Yellow

if ($branch -ne "main") {
    Write-Host "Warning: Not on main branch" -ForegroundColor Yellow
}

Write-Host ""

# Pull latest changes
Write-Host "Pulling latest changes..." -ForegroundColor Yellow
git pull origin main
Write-Host ""

# Show open issues by priority
Write-Host "=== Open Issues by Priority ===" -ForegroundColor Cyan
Write-Host ""

# Critical issues
Write-Host "CRITICAL Issues:" -ForegroundColor Red
gh issue list --repo "$owner/$repo" --label "priority:critical" --state open --limit 5
Write-Host ""

# High priority issues
Write-Host "HIGH Priority Issues:" -ForegroundColor Yellow
gh issue list --repo "$owner/$repo" --label "priority:high" --state open --limit 5
Write-Host ""

# In-progress issues
Write-Host "In Progress:" -ForegroundColor Cyan
gh issue list --repo "$owner/$repo" --label "status:in-progress" --state open --limit 5
Write-Host ""

# Show my assigned issues
Write-Host "Assigned to Me:" -ForegroundColor Magenta
gh issue list --repo "$owner/$repo" --assignee "@me" --limit 10
Write-Host ""

# Quick stats
$openCount = (gh issue list --repo "$owner/$repo" --state open --json id --jq 'length')
$closedToday = (gh issue list --repo "$owner/$repo" --state closed --search "closed:>$(Get-Date -Format 'yyyy-MM-dd')" --json id --jq 'length')

Write-Host "=== Statistics ===" -ForegroundColor Cyan
Write-Host "Open Issues: $openCount" -ForegroundColor Yellow
Write-Host "Closed Today: $closedToday" -ForegroundColor Green
Write-Host ""

# Session setup
$sessionId = "$(Get-Date -Format 'yyyyMMdd-HHmm')"
$sessionFile = ".claude/sessions/$sessionId-session.md"

# Create session file
$sessionContent = @"
# Claude Code Session
*Session ID: $sessionId*
*Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm')*
*Branch: $branch*

## Issues Worked On
- [ ] Issue #___ - Title

## Changes Made
-

## Files Modified
-

## Notes
-

---
*Session Start: $(Get-Date -Format 'HH:mm')*
"@

if (!(Test-Path ".claude/sessions")) {
    New-Item -ItemType Directory -Path ".claude/sessions" -Force | Out-Null
}

New-Item -Path $sessionFile -Value $sessionContent -Force | Out-Null
Write-Host "Session file created: $sessionFile" -ForegroundColor Green
Write-Host ""

Write-Host "=== Ready to Work ===" -ForegroundColor Green
Write-Host "To work on an issue, run:" -ForegroundColor Cyan
Write-Host "  .github\scripts\cc-work-on-issue.ps1 [issue-number]" -ForegroundColor White
Write-Host ""
Write-Host "To create a new issue, run:" -ForegroundColor Cyan
Write-Host "  gh issue create --title ""Title"" --body ""Description"" --label ""domain,priority""" -ForegroundColor White
Write-Host ""