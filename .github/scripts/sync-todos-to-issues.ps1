# Sync TODOs from Markdown to GitHub Issues
# Parses MASTER_TODO.md and creates GitHub issues for items not already tracked

param(
    [string]$DryRun = "false"
)

Write-Host "=== Syncing TODOs to GitHub Issues ===" -ForegroundColor Cyan
Write-Host ""

$owner = "unmanned-systems-uk"
$repo = "DPM-V2"
$todoFile = "docs/MASTER_TODO.md"

if (!(Test-Path $todoFile)) {
    Write-Host "✗ MASTER_TODO.md not found at $todoFile" -ForegroundColor Red
    exit 1
}

# Parse TODO file
Write-Host "Parsing $todoFile..." -ForegroundColor Yellow
$content = Get-Content $todoFile -Raw
$lines = $content -split "`n"

$todos = @()
$currentSection = ""
$currentPriority = "medium"

foreach ($line in $lines) {
    # Detect sections
    if ($line -match "^##.*CRITICAL") {
        $currentSection = "Critical"
        $currentPriority = "critical"
    }
    elseif ($line -match "^##.*HIGH PRIORITY") {
        $currentSection = "High Priority"
        $currentPriority = "high"
    }
    elseif ($line -match "^##.*MEDIUM PRIORITY") {
        $currentSection = "Medium Priority"
        $currentPriority = "medium"
    }
    elseif ($line -match "^##.*LOW PRIORITY") {
        $currentSection = "Low Priority"
        $currentPriority = "low"
    }

    # Parse TODO items
    if ($line -match "^- \[ \] \*\*(.*?)\*\*(.*)") {
        $title = $matches[1].Trim()
        $description = $matches[2].Trim()

        # Extract domain tags
        $domains = @()
        if ($line -match "\[AIR\]") { $domains += "air-side" }
        if ($line -match "\[GROUND\]") { $domains += "ground-side" }
        if ($line -match "\[DEV\]") { $domains += "dev-tools" }
        if ($line -match "\[ALL\]") { $domains += "all-domains" }
        if ($line -match "\[AIR\+GROUND\]") {
            $domains += "air-side"
            $domains += "ground-side"
        }

        $todos += @{
            title = $title
            description = $description
            section = $currentSection
            priority = $currentPriority
            domains = $domains
        }
    }
}

Write-Host "Found $($todos.Count) TODO items" -ForegroundColor Green
Write-Host ""

# Get existing issues to avoid duplicates
Write-Host "Checking existing issues..." -ForegroundColor Yellow
$existingIssues = gh issue list --repo "$owner/$repo" --limit 1000 --json title --jq '.[].title'

$created = 0
$skipped = 0

foreach ($todo in $todos) {
    if ($existingIssues -contains $todo.title) {
        Write-Host "  ⚬ Skipping (exists): $($todo.title)" -ForegroundColor Gray
        $skipped++
        continue
    }

    if ($DryRun -eq "true") {
        Write-Host "  🔸 Would create: $($todo.title)" -ForegroundColor Yellow
        Write-Host "      Priority: $($todo.priority)" -ForegroundColor DarkGray
        Write-Host "      Domains: $($todo.domains -join ', ')" -ForegroundColor DarkGray
        $created++
        continue
    }

    # Build labels
    $labels = @("priority:$($todo.priority)")
    $labels += $todo.domains
    $labelString = $labels -join ","

    # Build body
    $body = @"
## Description
$($todo.description)

## Section
$($todo.section)

## Source
Imported from MASTER_TODO.md

---
*Auto-imported by sync-todos-to-issues.ps1*
"@

    # Create issue
    try {
        $result = gh issue create `
            --repo "$owner/$repo" `
            --title "$($todo.title)" `
            --body "$body" `
            --label "$labelString" 2>&1

        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ Created: $($todo.title)" -ForegroundColor Green
            $created++
        } else {
            Write-Host "  ✗ Failed: $($todo.title)" -ForegroundColor Red
            Write-Host "    Error: $result" -ForegroundColor DarkRed
        }
    } catch {
        Write-Host "  ✗ Error creating issue: $($todo.title)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=== Summary ===" -ForegroundColor Cyan
Write-Host "Created: $created issues" -ForegroundColor Green
Write-Host "Skipped: $skipped (already exist)" -ForegroundColor Gray
Write-Host ""

if ($DryRun -eq "true") {
    Write-Host "This was a dry run. To actually create issues, run without -DryRun parameter" -ForegroundColor Yellow
}