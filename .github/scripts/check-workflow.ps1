#!/usr/bin/env pwsh
# Workflow Compliance Checker - Run at start and end of session

param(
    [string]$IssueNumber = ""
)

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  GitHub Issue Workflow Compliance Check" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# Check if gh is available
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: GitHub CLI (gh) not found!" -ForegroundColor Red
    exit 1
}

# Get open issues
Write-Host "`nChecking open issues..." -ForegroundColor Yellow
$openIssues = gh issue list --repo unmanned-systems-uk/DPM-V2 --state open --json number,title,labels,assignees --limit 20 | ConvertFrom-Json

Write-Host "`nOpen Issues requiring attention:" -ForegroundColor Green
foreach ($issue in $openIssues) {
    $labels = $issue.labels | ForEach-Object { $_.name }
    $status = "unknown"

    if ($labels -contains "status:in-progress") {
        $status = "IN PROGRESS"
        Write-Host "  #$($issue.number): $($issue.title)" -ForegroundColor Yellow
        Write-Host "    Status: $status" -ForegroundColor Yellow
    }
    elseif ($labels -contains "status:testing") {
        $status = "TESTING"
        Write-Host "  #$($issue.number): $($issue.title)" -ForegroundColor Cyan
        Write-Host "    Status: $status - Needs testing!" -ForegroundColor Cyan
    }
    elseif ($labels -contains "status:needs-ground-impl") {
        $status = "NEEDS GROUND"
        Write-Host "  #$($issue.number): $($issue.title)" -ForegroundColor Magenta
        Write-Host "    Status: Ground-Side implementation needed!" -ForegroundColor Magenta
    }
    elseif ($labels -contains "status:needs-air-impl") {
        $status = "NEEDS AIR"
        Write-Host "  #$($issue.number): $($issue.title)" -ForegroundColor Magenta
        Write-Host "    Status: Air-Side implementation needed!" -ForegroundColor Magenta
    }
}

# If specific issue number provided, check it
if ($IssueNumber) {
    Write-Host "`n==================================================" -ForegroundColor Cyan
    Write-Host "  Checking Issue #$IssueNumber Specifically" -ForegroundColor Cyan
    Write-Host "==================================================" -ForegroundColor Cyan

    $issueData = gh issue view $IssueNumber --repo unmanned-systems-uk/DPM-V2 --json title,state,labels,comments

    if ($issueData) {
        $issue = $issueData | ConvertFrom-Json
        Write-Host "`nIssue #$IssueNumber: $($issue.title)" -ForegroundColor Green
        Write-Host "State: $($issue.state)" -ForegroundColor Green

        $labels = $issue.labels | ForEach-Object { $_.name }
        Write-Host "Labels: $($labels -join ', ')" -ForegroundColor Green

        # Check for recent comments
        $comments = $issue.comments
        if ($comments.Count -gt 0) {
            $lastComment = $comments[-1]
            Write-Host "`nLast comment by $($lastComment.author.login):" -ForegroundColor Yellow
            Write-Host ($lastComment.body -split "`n")[0..2] -join "`n" -ForegroundColor Gray
        }

        # Workflow compliance check
        Write-Host "`n📋 WORKFLOW CHECKLIST:" -ForegroundColor Cyan

        $hasInProgress = $labels -contains "status:in-progress"
        $hasTesting = $labels -contains "status:testing"
        $hasComments = $comments.Count -gt 0

        if ($hasInProgress) {
            Write-Host "  ✅ Has in-progress label" -ForegroundColor Green
        } else {
            Write-Host "  ⚠️  Missing in-progress label (add when starting work)" -ForegroundColor Yellow
        }

        if ($hasComments) {
            Write-Host "  ✅ Has progress comments" -ForegroundColor Green
        } else {
            Write-Host "  ❌ No comments! Must document progress!" -ForegroundColor Red
        }

        if ($hasTesting) {
            Write-Host "  ℹ️  In testing phase - provide test results" -ForegroundColor Cyan
        }
    }
}

Write-Host "`n==================================================" -ForegroundColor Cyan
Write-Host "  REMEMBER: Always update issues when working!" -ForegroundColor Yellow
Write-Host "==================================================" -ForegroundColor Cyan

Write-Host "`nQuick Commands:" -ForegroundColor Green
Write-Host "  Start work:  gh issue edit <#> --add-label 'status:in-progress'" -ForegroundColor White
Write-Host "  Add comment: gh issue comment <#> --body 'Progress update...'" -ForegroundColor White
Write-Host "  Testing:     gh issue edit <#> --add-label 'status:testing'" -ForegroundColor White
Write-Host "  Close:       gh issue close <#> --comment 'Fixed in...'" -ForegroundColor White