#!/usr/bin/env pwsh
# Create GitHub issue with proper escaping by using a temporary file

param(
    [Parameter(Mandatory=$true)]
    [string]$Title,

    [Parameter(Mandatory=$true)]
    [string]$Body,

    [string]$Labels = "",

    [string]$Repo = "unmanned-systems-uk/DPM-V2"
)

Write-Host "Creating issue: $Title" -ForegroundColor Cyan

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