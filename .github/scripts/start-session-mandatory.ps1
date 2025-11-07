#!/usr/bin/env pwsh
# MANDATORY Session Startup - Enforces New Workflow

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("Air-Side", "Ground-Side", "SystemTools", "Docs")]
    [string]$Domain
)

$ErrorActionPreference = "Stop"

Write-Host @"
==============================================================
  MANDATORY WORKFLOW COMPLIANCE CHECK
==============================================================
"@ -ForegroundColor Red

Write-Host "Domain: $Domain" -ForegroundColor Cyan
Write-Host "Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm')" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check for latest changes
Write-Host "📥 Pulling latest changes..." -ForegroundColor Yellow
git pull origin main

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to pull latest changes. Fix conflicts first!" -ForegroundColor Red
    exit 1
}

# Step 2: Check if announcement has been read
Write-Host "`n📋 Checking mandatory announcement..." -ForegroundColor Yellow
$announcement = gh issue view 26 --repo unmanned-systems-uk/DPM-V2 --json comments --jq '.comments[].body' | Select-String "\[CC-$Domain\].*understood"

if (-not $announcement) {
    Write-Host @"
❌ YOU HAVE NOT ACKNOWLEDGED THE MANDATORY WORKFLOW UPDATE!

Required Action:
1. Read Issue #26 completely
2. Comment with: [CC-$Domain] ✅ Workflow updates received and understood.

"@ -ForegroundColor Red

    Write-Host "Opening Issue #26 in browser..." -ForegroundColor Yellow
    Start-Process "https://github.com/unmanned-systems-uk/DPM-V2/issues/26"

    Write-Host "`n⏸️  Session BLOCKED until you acknowledge the workflow update." -ForegroundColor Red
    exit 1
}

Write-Host "✅ Workflow acknowledgment found" -ForegroundColor Green

# Step 3: Display workflow reminders
Write-Host @"

==============================================================
  WORKFLOW REMINDERS - MANDATORY
==============================================================

1. BEFORE ANY IMPLEMENTATION:
   .\scripts\search-history.ps1 "keyword"

2. ALL COMMENTS MUST HAVE WHO TAG:
   [CC-$Domain]

3. USE FILE-BASED UPDATES FOR COMPLEX COMMENTS:
   .\scripts\issue-comment-who.ps1 -IssueNumber <#> -Who "CC-$Domain" -Comment "..."

4. DOCUMENT WHAT YOU WON'T REPEAT FROM HISTORY

==============================================================
"@ -ForegroundColor Cyan

# Step 4: Check open issues
Write-Host "`n📊 Open Issues Status:" -ForegroundColor Yellow
gh issue list --repo unmanned-systems-uk/DPM-V2 --state open --label $Domain.ToLower() --limit 5

# Step 5: Run workflow compliance check
Write-Host "`n🔍 Running workflow compliance check..." -ForegroundColor Yellow
& "$PSScriptRoot\check-workflow.ps1"

# Step 6: Final confirmation
Write-Host @"

==============================================================
  SESSION READY - WORKFLOW COMPLIANCE ACTIVE
==============================================================

Domain: CC-$Domain
Remember:
- Search history BEFORE implementing
- Use WHO tags on EVERY comment
- Document failed attempts
- Never repeat past failures

Type 'YES' to confirm you will follow the mandatory workflow:
"@ -ForegroundColor Green

$confirmation = Read-Host

if ($confirmation -ne "YES") {
    Write-Host "`n❌ Session terminated. You must agree to follow the workflow." -ForegroundColor Red
    exit 1
}

Write-Host @"

✅ SESSION STARTED - CC-$Domain
Workflow enforcement is ACTIVE. Non-compliance = termination.

"@ -ForegroundColor Green

# Create session marker
$sessionId = [Guid]::NewGuid().ToString().Substring(0, 8)
Write-Host "Session ID: $sessionId" -ForegroundColor DarkGray
Write-Host "All issue comments should start with: [CC-$Domain]" -ForegroundColor Yellow