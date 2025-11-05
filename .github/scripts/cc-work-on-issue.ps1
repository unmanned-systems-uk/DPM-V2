# Claude Code - Work on Specific Issue
# Usage: cc-work-on-issue.ps1 <issue-number>

param(
    [Parameter(Mandatory=$true)]
    [int]$IssueNumber
)

Write-Host "=== Starting Work on Issue #$IssueNumber ===" -ForegroundColor Cyan
Write-Host ""

$owner = "unmanned-systems-uk"
$repo = "DPM-V2"

# Get issue details
Write-Host "Fetching issue details..." -ForegroundColor Yellow
$issue = gh issue view $IssueNumber --repo "$owner/$repo" --json title,body,labels,state,assignees

if (!$issue) {
    Write-Host "Issue #$IssueNumber not found" -ForegroundColor Red
    exit 1
}

$issueData = $issue | ConvertFrom-Json

# Display issue
Write-Host "Issue #$IssueNumber : $($issueData.title)" -ForegroundColor Cyan
Write-Host ""
Write-Host "Labels: $($issueData.labels.name -join ', ')" -ForegroundColor Gray
Write-Host "Status: $($issueData.state)" -ForegroundColor Gray
Write-Host ""
Write-Host "Description:" -ForegroundColor Yellow
Write-Host $issueData.body
Write-Host ""

# Check if already in progress
$hasInProgress = $issueData.labels.name -contains "status:in-progress"

if ($hasInProgress) {
    Write-Host "Issue is already marked as in-progress" -ForegroundColor Yellow
} else {
    # Mark as in-progress
    Write-Host "Marking issue as in-progress..." -ForegroundColor Yellow
    gh issue edit $IssueNumber --repo "$owner/$repo" --add-label "status:in-progress"

    # Add comment
    gh issue comment $IssueNumber --repo "$owner/$repo" --body "Started working on this issue via Claude Code session"

    Write-Host "Issue marked as in-progress" -ForegroundColor Green
}

# Assign to self if not assigned
if ($issueData.assignees.Count -eq 0) {
    Write-Host "Assigning issue to self..." -ForegroundColor Yellow
    gh issue edit $IssueNumber --repo "$owner/$repo" --add-assignee "@me"
    Write-Host "Issue assigned to you" -ForegroundColor Green
}

Write-Host ""

# Create feature branch
$branchName = "fix/issue-$IssueNumber"
$currentBranch = git branch --show-current

if ($currentBranch -eq $branchName) {
    Write-Host "Already on branch: $branchName" -ForegroundColor Green
} else {
    Write-Host "Creating feature branch: $branchName" -ForegroundColor Yellow

    # Check if branch exists
    $branchExists = git branch -r | Select-String "origin/$branchName"

    if ($branchExists) {
        # Checkout existing branch
        git checkout $branchName
        git pull origin $branchName
        Write-Host "Switched to existing branch: $branchName" -ForegroundColor Green
    } else {
        # Create new branch
        git checkout -b $branchName
        Write-Host "Created new branch: $branchName" -ForegroundColor Green
    }
}

Write-Host ""

# Determine domain from labels
$domain = "UPDATE"
if ($issueData.labels.name -contains "air-side") { $domain = "AIR" }
elseif ($issueData.labels.name -contains "ground-side") { $domain = "GROUND" }
elseif ($issueData.labels.name -contains "dev-tools") { $domain = "DEV" }
elseif ($issueData.labels.name -contains "all-domains") { $domain = "ALL" }

# Create tracking file content as array
$trackingLines = @()
$trackingLines += "# Working on Issue #$IssueNumber"
$trackingLines += "*Started: $(Get-Date -Format 'yyyy-MM-dd HH:mm')*"
$trackingLines += "*Branch: $branchName*"
$trackingLines += ""
$trackingLines += "## Issue"
$trackingLines += "$($issueData.title)"
$trackingLines += ""
$trackingLines += "## Tasks"
$trackingLines += "- [ ] Implement fix/feature"
$trackingLines += "- [ ] Test changes"
$trackingLines += "- [ ] Update documentation"
$trackingLines += "- [ ] Create PR"
$trackingLines += ""
$trackingLines += "## Notes"
$trackingLines += "Add notes here as you work..."
$trackingLines += ""
$trackingLines += "## Commit Template"
$trackingLines += '```'
$trackingLines += "[$domain][TYPE] $($issueData.title)"
$trackingLines += ""
$trackingLines += "- Add changes here"
$trackingLines += ""
$trackingLines += "Refs #$IssueNumber"
$trackingLines += '```'

$trackingContent = $trackingLines -join "`n"
$trackingFile = ".github/working-on-issue-$IssueNumber.md"

Set-Content -Path $trackingFile -Value $trackingContent
Write-Host "Created tracking file: $trackingFile" -ForegroundColor Green
Write-Host ""

# Show next steps
Write-Host "=== Ready to Code ===" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Make your changes"
Write-Host "2. Test thoroughly"
Write-Host "3. Commit with: git commit -m ""[$domain][FIX] Description"""
Write-Host "4. Reference issue: Add 'Refs #$IssueNumber' to commit message"
Write-Host "5. When done, run: .github\scripts\cc-complete-issue.ps1 $IssueNumber"
Write-Host ""
Write-Host "Tracking file: $trackingFile" -ForegroundColor Gray
Write-Host ""