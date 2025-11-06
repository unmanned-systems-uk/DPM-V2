#!/usr/bin/env pwsh
# Setup GitHub CLI in PATH for current session

$ghPath = "C:\Program Files\GitHub CLI"

if (Test-Path $ghPath) {
    # Add to PATH for current session
    $env:PATH = "$ghPath;$env:PATH"
    Write-Host "✅ GitHub CLI added to PATH for this session" -ForegroundColor Green
    Write-Host "You can now use 'gh' commands directly" -ForegroundColor Cyan
} else {
    Write-Host "❌ GitHub CLI not found at $ghPath" -ForegroundColor Red
    exit 1
}