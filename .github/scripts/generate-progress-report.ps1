# Generate Progress Report from GitHub Issues
# Creates a markdown report of project status

param(
    [string]$OutputFile = "docs/GITHUB_PROGRESS_REPORT.md"
)

Write-Host "=== Generating Progress Report ===" -ForegroundColor Cyan
Write-Host ""

$owner = "unmanned-systems-uk"
$repo = "DPM-V2"
$date = Get-Date -Format "yyyy-MM-dd"

# Fetch all issues
Write-Host "Fetching issues..." -ForegroundColor Yellow
$openIssues = gh issue list --repo "$owner/$repo" --state open --limit 1000 --json number,title,labels,assignees,createdAt,updatedAt
$closedIssues = gh issue list --repo "$owner/$repo" --state closed --limit 100 --json number,title,labels,assignees,createdAt,closedAt

$open = $openIssues | ConvertFrom-Json
$closed = $closedIssues | ConvertFrom-Json

# Calculate statistics
$totalOpen = $open.Count
$totalClosed = $closed.Count
$totalIssues = $totalOpen + $totalClosed

# Count by priority
$criticalCount = ($open | Where-Object { $_.labels.name -contains "priority:critical" }).Count
$highCount = ($open | Where-Object { $_.labels.name -contains "priority:high" }).Count
$mediumCount = ($open | Where-Object { $_.labels.name -contains "priority:medium" }).Count
$lowCount = ($open | Where-Object { $_.labels.name -contains "priority:low" }).Count

# Count by domain
$airCount = ($open | Where-Object { $_.labels.name -contains "air-side" }).Count
$groundCount = ($open | Where-Object { $_.labels.name -contains "ground-side" }).Count
$devCount = ($open | Where-Object { $_.labels.name -contains "dev-tools" }).Count

# In progress
$inProgress = $open | Where-Object { $_.labels.name -contains "status:in-progress" }
$blocked = $open | Where-Object { $_.labels.name -contains "status:blocked" }

# Recent activity (last 7 days)
$lastWeek = (Get-Date).AddDays(-7)
$recentClosed = $closed | Where-Object { [DateTime]$_.closedAt -gt $lastWeek }
$recentCreated = $open | Where-Object { [DateTime]$_.createdAt -gt $lastWeek }

# Calculate completion percentage
$completionPercent = if ($totalIssues -gt 0) { [math]::Round(($totalClosed / $totalIssues) * 100, 1) } else { 0 }

# Generate report
$report = @"
# GitHub Progress Report
*Generated: $date*
*Repository: $owner/$repo*

## Overall Progress

\`\`\`
Total Issues:    $totalIssues
Open:           $totalOpen
Closed:         $totalClosed
Completion:     $completionPercent%

Progress Bar:
$(if ($totalIssues -gt 0) {
    $filled = [math]::Floor($completionPercent / 2)
    $empty = 50 - $filled
    "█" * $filled + "░" * $empty + " $completionPercent%"
} else { "░" * 50 + " 0%" })
\`\`\`

## Priority Breakdown

| Priority | Count | Status |
|----------|-------|--------|
| 🔴 Critical | $criticalCount | $(if ($criticalCount -eq 0) { "✅ None" } else { "⚠️ Needs attention" }) |
| 🟡 High | $highCount | $(if ($highCount -eq 0) { "✅ Clear" } else { "📋 Active" }) |
| 🟢 Medium | $mediumCount | $(if ($mediumCount -eq 0) { "✅ Clear" } else { "📋 Active" }) |
| 🔵 Low | $lowCount | $(if ($lowCount -eq 0) { "✅ Clear" } else { "📋 Active" }) |

## Domain Distribution

| Domain | Open Issues | Percentage |
|--------|-------------|------------|
| Air-Side | $airCount | $(if ($totalOpen -gt 0) { [math]::Round(($airCount/$totalOpen)*100, 1) } else { 0 })% |
| Ground-Side | $groundCount | $(if ($totalOpen -gt 0) { [math]::Round(($groundCount/$totalOpen)*100, 1) } else { 0 })% |
| Dev-Tools | $devCount | $(if ($totalOpen -gt 0) { [math]::Round(($devCount/$totalOpen)*100, 1) } else { 0 })% |

## Current Status

### 🚀 In Progress ($($inProgress.Count))
$(foreach ($issue in $inProgress) {
"- #$($issue.number): $($issue.title) $(if ($issue.assignees) { "@$($issue.assignees[0].login)" })"
})

### 🚫 Blocked ($($blocked.Count))
$(foreach ($issue in $blocked) {
"- #$($issue.number): $($issue.title)"
})

## Recent Activity (Last 7 Days)

### ✅ Recently Closed ($($recentClosed.Count))
$(foreach ($issue in $recentClosed | Select-Object -First 10) {
"- #$($issue.number): $($issue.title)"
})

### 🆕 Recently Created ($($recentCreated.Count))
$(foreach ($issue in $recentCreated | Select-Object -First 10) {
"- #$($issue.number): $($issue.title)"
})

## Velocity Metrics

- **Issues Closed This Week:** $($recentClosed.Count)
- **Issues Created This Week:** $($recentCreated.Count)
- **Net Progress:** $(if (($recentClosed.Count - $recentCreated.Count) -ge 0) { "📈" } else { "📉" }) $($recentClosed.Count - $recentCreated.Count)

## Milestone Progress

\`\`\`
$(gh api "repos/$owner/$repo/milestones" --jq '.[] | "Milestone: \(.title)\nDue: \(.due_on // "No due date")\nOpen: \(.open_issues) | Closed: \(.closed_issues)\nProgress: \(if .open_issues + .closed_issues > 0 then ((.closed_issues / (.open_issues + .closed_issues)) * 100 | floor) else 0 end)%\n"')
\`\`\`

## Top Contributors (By Closed Issues)

\`\`\`
$(gh issue list --repo "$owner/$repo" --state closed --limit 100 --json assignees --jq '[.[] | .assignees[].login] | group_by(.) | map({user: .[0], count: length}) | sort_by(.count) | reverse | .[:5] | .[] | "\(.user): \(.count) issues closed"')
\`\`\`

## Links

- [Open Issues](https://github.com/$owner/$repo/issues)
- [Milestones](https://github.com/$owner/$repo/milestones)
- [Projects](https://github.com/$owner/$repo/projects)

---
*This report is generated automatically from GitHub Issues*
*Run \`.github\scripts\generate-progress-report.ps1\` to update*
"@

# Write report
Set-Content -Path $OutputFile -Value $report
Write-Host "✓ Report generated: $OutputFile" -ForegroundColor Green
Write-Host ""

# Display summary
Write-Host "=== Summary ===" -ForegroundColor Cyan
Write-Host "Total Issues: $totalIssues" -ForegroundColor White
Write-Host "Completion: $completionPercent%" -ForegroundColor $(if ($completionPercent -ge 75) { "Green" } elseif ($completionPercent -ge 50) { "Yellow" } else { "Red" })
Write-Host "Critical Issues: $criticalCount" -ForegroundColor $(if ($criticalCount -eq 0) { "Green" } else { "Red" })
Write-Host "In Progress: $($inProgress.Count)" -ForegroundColor Cyan
Write-Host "Blocked: $($blocked.Count)" -ForegroundColor $(if ($blocked.Count -eq 0) { "Green" } else { "Red" })
Write-Host ""