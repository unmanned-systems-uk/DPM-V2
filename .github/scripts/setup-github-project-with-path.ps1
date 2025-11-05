# GitHub Project Setup Script for DPM-V2 (with explicit path)
# Run once to initialize GitHub project management
# This version uses full path to gh.exe

$ghPath = "C:\Program Files\GitHub CLI\gh.exe"

Write-Host "=== DPM-V2 GitHub Project Setup ===" -ForegroundColor Cyan
Write-Host ""

# Check if gh is installed at the expected location
if (Test-Path $ghPath) {
    Write-Host "GitHub CLI found at: $ghPath" -ForegroundColor Green
    $ghVersion = & $ghPath --version
    Write-Host "Version: $ghVersion" -ForegroundColor Green
} else {
    Write-Host "GitHub CLI not found at $ghPath" -ForegroundColor Red
    Write-Host "Please install from https://cli.github.com/" -ForegroundColor Red
    exit 1
}

# Check authentication
Write-Host "Checking GitHub authentication..." -ForegroundColor Yellow
$authStatus = & $ghPath auth status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Not authenticated. Please run:" -ForegroundColor Red
    Write-Host "  & `"$ghPath`" auth login" -ForegroundColor Yellow
    exit 1
}
Write-Host "Authenticated to GitHub" -ForegroundColor Green
Write-Host ""

# Repository info
$owner = "unmanned-systems-uk"
$repo = "DPM-V2"
Write-Host "Repository: $owner/$repo" -ForegroundColor Cyan
Write-Host ""

# Create labels
Write-Host "Creating domain labels..." -ForegroundColor Yellow
$domainLabels = @(
    @{name="air-side"; color="0E7490"; description="Air-Side (Pi 5 SBC) related"},
    @{name="ground-side"; color="059669"; description="Ground-Side (Android H16) related"},
    @{name="dev-tools"; color="7C3AED"; description="Development Tools (SystemTools) related"},
    @{name="all-domains"; color="EA580C"; description="Affects all domains"}
)

foreach ($label in $domainLabels) {
    $result = & $ghPath label create $label.name --repo "$owner/$repo" `
        --color $label.color `
        --description $label.description 2>&1

    if ($LASTEXITCODE -eq 0) {
        Write-Host "  Created label: $($label.name)" -ForegroundColor Green
    } else {
        Write-Host "  Label already exists: $($label.name)" -ForegroundColor Gray
    }
}

# Create priority labels
Write-Host "Creating priority labels..." -ForegroundColor Yellow
$priorityLabels = @(
    @{name="priority:critical"; color="B91C1C"; description="Critical - Must fix immediately"},
    @{name="priority:high"; color="DC2626"; description="High priority"},
    @{name="priority:medium"; color="F59E0B"; description="Medium priority"},
    @{name="priority:low"; color="3B82F6"; description="Low priority"}
)

foreach ($label in $priorityLabels) {
    $result = & $ghPath label create $label.name --repo "$owner/$repo" `
        --color $label.color `
        --description $label.description 2>&1

    if ($LASTEXITCODE -eq 0) {
        Write-Host "  Created label: $($label.name)" -ForegroundColor Green
    } else {
        Write-Host "  Label already exists: $($label.name)" -ForegroundColor Gray
    }
}

# Create status labels
Write-Host "Creating status labels..." -ForegroundColor Yellow
$statusLabels = @(
    @{name="status:in-progress"; color="FCD34D"; description="Currently being worked on"},
    @{name="status:blocked"; color="EF4444"; description="Blocked by dependency"},
    @{name="status:testing"; color="8B5CF6"; description="In testing phase"},
    @{name="status:ready"; color="10B981"; description="Ready for implementation"}
)

foreach ($label in $statusLabels) {
    $result = & $ghPath label create $label.name --repo "$owner/$repo" `
        --color $label.color `
        --description $label.description 2>&1

    if ($LASTEXITCODE -eq 0) {
        Write-Host "  Created label: $($label.name)" -ForegroundColor Green
    } else {
        Write-Host "  Label already exists: $($label.name)" -ForegroundColor Gray
    }
}

# Create type labels
Write-Host "Creating type labels..." -ForegroundColor Yellow
$typeLabels = @(
    @{name="bug"; color="D73027"; description="Something is not working"},
    @{name="enhancement"; color="0969DA"; description="New feature or request"},
    @{name="documentation"; color="0052CC"; description="Documentation improvements"},
    @{name="testing"; color="FBCA04"; description="Testing related"}
)

foreach ($label in $typeLabels) {
    $result = & $ghPath label create $label.name --repo "$owner/$repo" `
        --color $label.color `
        --description $label.description 2>&1

    if ($LASTEXITCODE -eq 0) {
        Write-Host "  Created label: $($label.name)" -ForegroundColor Green
    } else {
        Write-Host "  Label already exists: $($label.name)" -ForegroundColor Gray
    }
}

Write-Host ""

# Create milestones
Write-Host "Creating milestones..." -ForegroundColor Yellow
$milestones = @(
    @{title="Phase 1 - MVP"; description="Core functionality complete"; due="2025-11-15"},
    @{title="Phase 2 - Enhanced"; description="Additional features"; due="2025-11-30"},
    @{title="Phase 3 - Production"; description="Production ready"; due="2025-12-15"}
)

foreach ($milestone in $milestones) {
    $existing = & $ghPath api "repos/$owner/$repo/milestones" --jq ".[] | select(.title == \`"$($milestone.title)\`")" 2>$null
    if ($existing) {
        Write-Host "  Milestone already exists: $($milestone.title)" -ForegroundColor Gray
    } else {
        & $ghPath api "repos/$owner/$repo/milestones" `
            --method POST `
            -f title="$($milestone.title)" `
            -f description="$($milestone.description)" `
            -f due_on="$($milestone.due)T00:00:00Z" 2>$null
        Write-Host "  Created milestone: $($milestone.title)" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "=== Setup Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Run sync-todos-to-issues.ps1 to import existing TODOs"
Write-Host "2. Configure GitKraken to connect to this repository"
Write-Host "3. Use cc-start-session.ps1 when beginning work"
Write-Host ""
Write-Host "To add GitHub CLI to PATH permanently:" -ForegroundColor Yellow
Write-Host '  [Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Program Files\GitHub CLI", [EnvironmentVariableTarget]::User)' -ForegroundColor Gray
Write-Host ""