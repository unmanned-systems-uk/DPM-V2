# Claude Code - Complete Issue
# Usage: cc-complete-issue.ps1 <issue-number> ["commit message"]

param(
    [Parameter(Mandatory=$true)]
    [int]$IssueNumber,
    [string]$CommitMessage = ""
)

Write-Host "=== Completing Issue #$IssueNumber ===" -ForegroundColor Cyan
Write-Host ""

$owner = "unmanned-systems-uk"
$repo = "DPM-V2"

# Check for uncommitted changes
$status = git status --porcelain
if ($status) {
    Write-Host "📝 Uncommitted changes detected" -ForegroundColor Yellow

    if ($CommitMessage) {
        # Commit with provided message
        git add -A
        git commit -m "$CommitMessage`n`nFixes #$IssueNumber"
        Write-Host "✓ Changes committed" -ForegroundColor Green
    } else {
        Write-Host "Please commit your changes first or provide a commit message" -ForegroundColor Red
        Write-Host "Usage: cc-complete-issue.ps1 $IssueNumber `"Commit message`"" -ForegroundColor Gray
        exit 1
    }
}

Write-Host ""

# Get current branch
$branch = git branch --show-current
$isFeatureBranch = $branch -match "issue-$IssueNumber"

if ($isFeatureBranch) {
    Write-Host "🌿 On feature branch: $branch" -ForegroundColor Cyan

    # Push branch
    Write-Host "Pushing branch to remote..." -ForegroundColor Yellow
    git push -u origin $branch
    Write-Host "✓ Branch pushed" -ForegroundColor Green
    Write-Host ""

    # Create PR
    Write-Host "Creating Pull Request..." -ForegroundColor Yellow

    # Get issue title for PR
    $issueTitle = gh issue view $IssueNumber --repo "$owner/$repo" --json title --jq '.title'

    # Determine domain from branch or issue
    $domain = "UPDATE"
    $issueLabels = gh issue view $IssueNumber --repo "$owner/$repo" --json labels --jq '.labels[].name'
    if ($issueLabels -match "air-side") { $domain = "AIR" }
    elseif ($issueLabels -match "ground-side") { $domain = "GROUND" }
    elseif ($issueLabels -match "dev-tools") { $domain = "DEV" }

    $prTitle = "[$domain][FIX] $issueTitle (#$IssueNumber)"
    $prBody = @"
## Summary
Fixes issue #$IssueNumber

## Changes
- See commits for detailed changes

## Testing
- Tested locally
- All existing tests pass

## Issue Reference
Fixes #$IssueNumber
"@

    $pr = gh pr create `
        --repo "$owner/$repo" `
        --title "$prTitle" `
        --body "$prBody" `
        --base main `
        --head $branch 2>&1

    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Pull Request created: $pr" -ForegroundColor Green

        # Get PR number
        $prNumber = $pr -match "#(\d+)" | Out-Null; $matches[1]

        # Add comment to issue
        gh issue comment $IssueNumber --repo "$owner/$repo" `
            --body "🔗 Pull Request #$prNumber created for this issue"

        Write-Host ""
        Write-Host "=== Next Steps ===" -ForegroundColor Cyan
        Write-Host "1. Wait for PR review" -ForegroundColor Yellow
        Write-Host "2. After approval, merge PR" -ForegroundColor Yellow
        Write-Host "3. Issue will auto-close when PR is merged" -ForegroundColor Yellow
    } else {
        Write-Host "⚠ PR may already exist or there was an error" -ForegroundColor Yellow
        Write-Host "Output: $pr" -ForegroundColor Gray
    }

} else {
    Write-Host "📍 On branch: $branch (not a feature branch)" -ForegroundColor Yellow
    Write-Host ""

    # Direct completion (for hotfixes on main)
    $confirm = Read-Host "Close issue #$IssueNumber directly without PR? (y/n)"

    if ($confirm -eq "y") {
        # Remove in-progress label
        gh issue edit $IssueNumber --repo "$owner/$repo" --remove-label "status:in-progress"

        # Close issue
        gh issue close $IssueNumber --repo "$owner/$repo" `
            --comment "✅ Issue completed via direct commit to $branch"

        Write-Host "✓ Issue #$IssueNumber closed" -ForegroundColor Green
    }
}

# Clean up tracking file
$trackingFile = ".github/working-on-issue-$IssueNumber.md"
if (Test-Path $trackingFile) {
    Remove-Item $trackingFile
    Write-Host "✓ Removed tracking file" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== Issue #$IssueNumber Complete ===" -ForegroundColor Green
Write-Host ""

# Show summary
Write-Host "Summary:" -ForegroundColor Cyan
gh issue view $IssueNumber --repo "$owner/$repo"
Write-Host ""