#!/usr/bin/env pwsh
# Add comment to issue with WHO tag and proper escaping

param(
    [Parameter(Mandatory=$true)]
    [int]$IssueNumber,

    [Parameter(Mandatory=$true)]
    [ValidateSet("CC-Air-Side", "CC-Ground-Side", "CC-SystemTools", "CC-Docs", "User")]
    [string]$Who,

    [Parameter(Mandatory=$true)]
    [string]$Comment,

    [string]$Repo = "unmanned-systems-uk/DPM-V2"
)

Write-Host "Commenting on issue #$IssueNumber as [$Who]" -ForegroundColor Cyan

# Build the full comment with WHO tag
$fullComment = @"
[$Who]

$Comment
"@

# Create temporary file for the comment to avoid escaping issues
$tempFile = [System.IO.Path]::GetTempFileName()
$tempFile = [System.IO.Path]::ChangeExtension($tempFile, ".md")

try {
    # Write comment to temp file
    $fullComment | Out-File -FilePath $tempFile -Encoding UTF8 -NoNewline

    Write-Host "Comment written to temp file" -ForegroundColor DarkGray

    # Execute gh command with file input
    $result = gh issue comment $IssueNumber `
        --repo $Repo `
        --body-file $tempFile

    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Comment added successfully!" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to add comment" -ForegroundColor Red
    }

} finally {
    # Clean up temp file
    if (Test-Path $tempFile) {
        Remove-Item $tempFile -Force
        Write-Host "Temp file cleaned up" -ForegroundColor DarkGray
    }
}

# Example usage displayed
Write-Host "`nExample usage:" -ForegroundColor Yellow
Write-Host '.\issue-comment-who.ps1 -IssueNumber 10 -Who "CC-Air-Side" -Comment "Starting work on focus implementation"' -ForegroundColor DarkGray