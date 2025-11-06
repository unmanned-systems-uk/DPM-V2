#!/usr/bin/env pwsh
# Historical Issue Search Tool - Learn from past attempts

param(
    [Parameter(Mandatory=$true)]
    [string]$SearchTerm,
    [switch]$ShowComments,
    [switch]$ShowFailed
)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  Historical Issue Search - Learning from Past Attempts" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

Write-Host "`nSearching for: '$SearchTerm'" -ForegroundColor Yellow

# Search all issues (both open and closed)
$allIssues = gh issue list --repo unmanned-systems-uk/DPM-V2 --search $SearchTerm --state all --limit 100 --json number,title,state,labels,createdAt,closedAt | ConvertFrom-Json

if ($allIssues.Count -eq 0) {
    Write-Host "`nNo issues found matching '$SearchTerm'" -ForegroundColor Red
    Write-Host "Try broader search terms or check prefixes like [FOCUS], [CAMERA], [NETWORK]" -ForegroundColor Yellow
    exit 0
}

Write-Host "`nFound $($allIssues.Count) related issues:" -ForegroundColor Green

# Group by state
$openIssues = $allIssues | Where-Object { $_.state -eq "OPEN" }
$closedIssues = $allIssues | Where-Object { $_.state -eq "CLOSED" }

# Display closed issues first (likely contain solutions)
if ($closedIssues.Count -gt 0) {
    Write-Host "`n✅ SOLVED/CLOSED Issues (check these for working solutions):" -ForegroundColor Green
    foreach ($issue in $closedIssues) {
        $labels = ($issue.labels | ForEach-Object { $_.name }) -join ", "
        Write-Host "  #$($issue.number): $($issue.title)" -ForegroundColor Green
        if ($labels) {
            Write-Host "    Labels: $labels" -ForegroundColor DarkGray
        }
        Write-Host "    Closed: $($issue.closedAt)" -ForegroundColor DarkGray
    }
}

# Display open issues
if ($openIssues.Count -gt 0) {
    Write-Host "`n⚠️ OPEN Issues (may contain failed attempts):" -ForegroundColor Yellow
    foreach ($issue in $openIssues) {
        $labels = ($issue.labels | ForEach-Object { $_.name }) -join ", "
        Write-Host "  #$($issue.number): $($issue.title)" -ForegroundColor Yellow
        if ($labels) {
            Write-Host "    Labels: $labels" -ForegroundColor DarkGray
        }
        Write-Host "    Created: $($issue.createdAt)" -ForegroundColor DarkGray
    }
}

# Show failed attempts if requested
if ($ShowFailed) {
    Write-Host "`n🔍 Searching for failed attempts in comments..." -ForegroundColor Magenta

    foreach ($issue in $allIssues[0..4]) {  # Check first 5 issues
        $comments = gh issue view $issue.number --repo unmanned-systems-uk/DPM-V2 --json comments --jq '.comments[].body' 2>$null

        if ($comments) {
            $failurePatterns = $comments | Select-String -Pattern "didn't work|failed|tried|doesn't work|not working|broke|error" -Context 2

            if ($failurePatterns) {
                Write-Host "`n❌ Failed attempts in #$($issue.number):" -ForegroundColor Red
                foreach ($match in $failurePatterns) {
                    Write-Host "  $($match.Line)" -ForegroundColor DarkRed
                }
            }
        }
    }
}

# Show comments if requested
if ($ShowComments) {
    Write-Host "`n📝 Detailed comments (first 3 issues):" -ForegroundColor Cyan

    foreach ($issue in $allIssues[0..2]) {  # Show first 3 issues
        Write-Host "`n--- Issue #$($issue.number) ---" -ForegroundColor Cyan
        gh issue view $issue.number --repo unmanned-systems-uk/DPM-V2 --comments
    }
}

# Provide actionable next steps
Write-Host "`n==========================================================" -ForegroundColor Cyan
Write-Host "  NEXT STEPS - Learn from History" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

Write-Host "`n1. Read closed issues for working solutions:" -ForegroundColor Green
foreach ($issue in $closedIssues[0..2]) {
    Write-Host "   gh issue view $($issue.number) --comments" -ForegroundColor White
}

Write-Host "`n2. Check open issues for failed attempts:" -ForegroundColor Yellow
foreach ($issue in $openIssues[0..2]) {
    Write-Host "   gh issue view $($issue.number) --comments | grep -i 'tried\|failed'" -ForegroundColor White
}

Write-Host "`n3. Document your approach based on lessons learned:" -ForegroundColor Magenta
Write-Host '   gh issue comment <#> --body "Based on #X and #Y, I will NOT try [failed approach]. Instead I will [new approach]"' -ForegroundColor White

Write-Host "`n💡 TIP: Before implementing, always state:" -ForegroundColor Cyan
Write-Host "   - What previous attempts you found" -ForegroundColor White
Write-Host "   - What failed and why" -ForegroundColor White
Write-Host "   - What new approach you're taking" -ForegroundColor White
Write-Host "   - Why this approach is different" -ForegroundColor White