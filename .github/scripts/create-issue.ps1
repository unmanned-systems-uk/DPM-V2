#!/usr/bin/env pwsh
# Create GitHub issue with proper escaping by using a temporary file

param(
    [Parameter(Mandatory=$true)]
    [string]$Title,

    [Parameter(Mandatory=$true)]
    [string]$Body,

    [string]$Labels = "",

    [string]$Repo = "unmanned-systems-uk/DPM-V2",

    [switch]$SkipValidation
)

# Validation function for issue title format
function Test-IssueTitleFormat {
    param([string]$Title)

    $validDomains = @('AIR-SIDE', 'GROUND-SIDE', 'TOOLS', 'ALL-DOMAINS', 'WORKFLOW', 'PROTOCOL', 'DOCS')
    $validTypes = @('BUG', 'FIX', 'FEATURE', 'ENHANCEMENT', 'REFACTOR', 'TESTING', 'DOCS')
    $validScopes = @('MANDATORY', 'URGENT', 'BLOCKED')

    # Extract all bracketed prefixes
    $prefixes = [regex]::Matches($Title, '\[([^\]]+)\]') | ForEach-Object { $_.Groups[1].Value }

    if ($prefixes.Count -lt 2) {
        Write-Host "`n⚠️  TITLE FORMAT WARNING" -ForegroundColor Yellow
        Write-Host "Expected format: [DOMAIN][TYPE] Description" -ForegroundColor Yellow
        Write-Host "Your title: $Title" -ForegroundColor Red
        Write-Host "`nValid DOMAINS: $($validDomains -join ', ')" -ForegroundColor Cyan
        Write-Host "Valid TYPES: $($validTypes -join ', ')" -ForegroundColor Cyan
        Write-Host "Optional SCOPES (prepend): $($validScopes -join ', ')" -ForegroundColor Cyan
        Write-Host "`nExamples:" -ForegroundColor Green
        Write-Host "  [GROUND-SIDE][BUG] Focus commands not working" -ForegroundColor Gray
        Write-Host "  [MANDATORY][ALL-DOMAINS][WORKFLOW] New workflow requirements" -ForegroundColor Gray
        Write-Host "  [AIR-SIDE][FEATURE] Add gimbal control" -ForegroundColor Gray
        return $false
    }

    # Check if at least one domain and one type are present
    $hasDomain = $false
    $hasType = $false

    foreach ($prefix in $prefixes) {
        if ($validDomains -contains $prefix) { $hasDomain = $true }
        if ($validTypes -contains $prefix) { $hasType = $true }
    }

    if (-not $hasDomain) {
        Write-Host "`n⚠️  MISSING DOMAIN PREFIX" -ForegroundColor Yellow
        Write-Host "Valid domains: $($validDomains -join ', ')" -ForegroundColor Cyan
        return $false
    }

    if (-not $hasType) {
        Write-Host "`n⚠️  MISSING TYPE PREFIX" -ForegroundColor Yellow
        Write-Host "Valid types: $($validTypes -join ', ')" -ForegroundColor Cyan
        return $false
    }

    Write-Host "✅ Title format validated" -ForegroundColor Green
    return $true
}

Write-Host "Creating issue: $Title" -ForegroundColor Cyan

# Validate title format unless skipped
if (-not $SkipValidation) {
    if (-not (Test-IssueTitleFormat $Title)) {
        Write-Host "`nDo you want to create the issue anyway? (Y/N): " -ForegroundColor Yellow -NoNewline
        $response = Read-Host
        if ($response -ne 'Y' -and $response -ne 'y') {
            Write-Host "❌ Issue creation cancelled" -ForegroundColor Red
            exit 1
        }
    }
}

# Create temporary file for the body to avoid escaping issues
$tempFile = [System.IO.Path]::GetTempFileName()
$tempFile = [System.IO.Path]::ChangeExtension($tempFile, ".md")

try {
    # Write body to temp file
    $Body | Out-File -FilePath $tempFile -Encoding UTF8 -NoNewline

    Write-Host "Body written to temp file: $tempFile" -ForegroundColor DarkGray

    # Build gh command
    $ghArgs = @(
        "issue", "create",
        "--repo", $Repo,
        "--title", $Title,
        "--body-file", $tempFile
    )

    # Add labels if provided
    if ($Labels) {
        $ghArgs += "--label"
        $ghArgs += $Labels
    }

    # Execute gh command
    $result = & gh $ghArgs

    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Issue created successfully!" -ForegroundColor Green
        Write-Host $result -ForegroundColor Cyan
    } else {
        Write-Host "❌ Failed to create issue" -ForegroundColor Red
    }

} finally {
    # Clean up temp file
    if (Test-Path $tempFile) {
        Remove-Item $tempFile -Force
        Write-Host "Temp file cleaned up" -ForegroundColor DarkGray
    }
}

# Return the issue URL
return $result