# Documentation Optimization Test Script
# Automated testing for DPM-V2 documentation optimization

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DPM-V2 Documentation Test Suite" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$testResults = @()
$failCount = 0

# Function to run a test
function Run-Test {
    param(
        [string]$TestName,
        [scriptblock]$TestScript,
        [string]$ExpectedResult
    )

    Write-Host "[TEST] $TestName" -ForegroundColor Yellow
    try {
        $result = & $TestScript
        if ($result) {
            Write-Host "  [PASS] $ExpectedResult" -ForegroundColor Green
            $script:testResults += @{Name=$TestName; Status="PASS"}
            return $true
        } else {
            Write-Host "  [FAIL] Test did not meet expectations" -ForegroundColor Red
            $script:testResults += @{Name=$TestName; Status="FAIL"}
            $script:failCount++
            return $false
        }
    } catch {
        Write-Host "  [ERROR] $_" -ForegroundColor Red
        $script:testResults += @{Name=$TestName; Status="ERROR"}
        $script:failCount++
        return $false
    }
}

# Test 1: Check main documentation file size
Run-Test "Main doc optimization" {
    $file = Get-Item "docs\CC_READ_THIS_FIRST.md"
    $lineCount = (Get-Content $file.FullName | Measure-Object -Line).Lines
    Write-Host "    Lines: $lineCount (target: <200)" -ForegroundColor Gray
    $lineCount -lt 200
} "File under 200 lines"

# Test 2: Check domain structure
Run-Test "Domain structure" {
    $domains = @("ALL_DOMAINS", "AIR_SIDE", "GROUND_SIDE", "DEVELOPMENT_SIDE")
    $allExist = $true
    foreach ($domain in $domains) {
        $path = "docs\$domain"
        if (Test-Path $path) {
            Write-Host "    [OK] $domain exists" -ForegroundColor Gray
        } else {
            Write-Host "    [X] $domain missing" -ForegroundColor Red
            $allExist = $false
        }
    }
    $allExist
} "All domain directories exist"

# Test 3: Check PROGRESS and TODO files
Run-Test "Progress/TODO files" {
    $domains = @("AIR_SIDE", "GROUND_SIDE", "DEVELOPMENT_SIDE")
    $allExist = $true
    foreach ($domain in $domains) {
        $progress = "docs\$domain\PROGRESS.md"
        $todo = "docs\$domain\TODO.md"

        if ((Test-Path $progress) -and (Test-Path $todo)) {
            Write-Host "    [OK] $domain has both files" -ForegroundColor Gray
        } else {
            Write-Host "    [X] $domain missing files" -ForegroundColor Red
            $allExist = $false
        }
    }
    $allExist
} "All domains have PROGRESS and TODO"

# Test 4: Check Git hooks
Run-Test "Git hooks" {
    $preCommit = ".git\hooks\pre-commit"
    $commitMsg = ".git\hooks\commit-msg"

    $hooksExist = (Test-Path $preCommit) -and (Test-Path $commitMsg)
    if ($hooksExist) {
        Write-Host "    [OK] pre-commit exists" -ForegroundColor Gray
        Write-Host "    [OK] commit-msg exists" -ForegroundColor Gray
    }
    $hooksExist
} "Git hooks installed"

# Test 5: Check archive structure
Run-Test "Archive structure" {
    $optimizationArchive = "docs\archive\2025-11-04-optimization"
    $legacyArchive = "docs\archive\legacy-docs"

    $archivesExist = (Test-Path $optimizationArchive) -and (Test-Path $legacyArchive)
    if ($archivesExist) {
        $optimCount = (Get-ChildItem $optimizationArchive -Filter "*.md" | Measure-Object).Count
        $legacyCount = (Get-ChildItem $legacyArchive -Filter "*.md" | Measure-Object).Count
        Write-Host "    Optimization archive: $optimCount files" -ForegroundColor Gray
        Write-Host "    Legacy archive: $legacyCount files" -ForegroundColor Gray
        $legacyCount -gt 30
    } else {
        $false
    }
} "Archives contain expected files"

# Test 6: Check DevTools configuration
Run-Test "DevTools config" {
    $configFile = "SystemTools\devtools_config.py"
    $testFile = "SystemTools\test_modes.py"

    $filesExist = (Test-Path $configFile) -and (Test-Path $testFile)
    if ($filesExist) {
        Write-Host "    [OK] devtools_config.py exists" -ForegroundColor Gray
        Write-Host "    [OK] test_modes.py exists" -ForegroundColor Gray
    }
    $filesExist
} "DevTools configuration files exist"

# Test 7: Check critical patterns documented
Run-Test "Critical patterns" {
    $devGuide = Get-Content "docs\DEVELOPMENT_SIDE\DEVTOOLS_MODE_GUIDE.md" -Raw
    $gitGuide = Get-Content "docs\GIT_PROTOCOL_GUIDE.md" -Raw

    $callbackPattern = $devGuide -match "Callback Chaining Pattern"
    $crossDomain = $gitGuide -match "Cross-Domain Implementation"

    if ($callbackPattern) {
        Write-Host "    [OK] Callback pattern documented" -ForegroundColor Gray
    }
    if ($crossDomain) {
        Write-Host "    [OK] Cross-domain instructions documented" -ForegroundColor Gray
    }

    $callbackPattern -and $crossDomain
} "Critical patterns documented"

# Test 8: Check file references
Run-Test "File references" {
    $mainDoc = Get-Content "docs\CC_READ_THIS_FIRST.md" -Raw

    # Check if referenced files exist
    $ref1 = $mainDoc -match "DEVELOPMENT_SIDE/DEVTOOLS_MODE_GUIDE.md"
    $ref2 = $mainDoc -match "GIT_PROTOCOL_GUIDE.md"

    if ($ref1 -and $ref2) {
        Write-Host "    [OK] DevTools guide referenced" -ForegroundColor Gray
        Write-Host "    [OK] Git protocol referenced" -ForegroundColor Gray
        $true
    } else {
        $false
    }
} "Important references included"

# Test 9: Run Python mode tests
Run-Test "Python mode tests" {
    Push-Location SystemTools
    try {
        $output = python test_modes.py 2>&1
        $success = $output -match "All tests passed"
        if ($success) {
            Write-Host "    [OK] All Python tests passed" -ForegroundColor Gray
        } else {
            Write-Host "    X Some Python tests failed" -ForegroundColor Red
        }
        Pop-Location
        $success
    } catch {
        Pop-Location
        $false
    }
} "DevTools mode switching works"

# Test 10: Check documentation metrics
Run-Test "Documentation metrics" {
    $oldSize = 1977  # Original CC_READ_THIS_FIRST.md lines
    $newSize = (Get-Content "docs\CC_READ_THIS_FIRST.md" | Measure-Object -Line).Lines
    $reduction = [math]::Round((($oldSize - $newSize) / $oldSize) * 100, 1)

    Write-Host "    Original: $oldSize lines" -ForegroundColor Gray
    Write-Host "    Current: $newSize lines" -ForegroundColor Gray
    Write-Host "    Reduction: $reduction%" -ForegroundColor Gray

    $reduction -gt 60
} "60%+ size reduction achieved"

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$passCount = ($testResults | Where-Object {$_.Status -eq "PASS"}).Count
$totalCount = $testResults.Count

foreach ($test in $testResults) {
    $color = switch ($test.Status) {
        "PASS" { "Green" }
        "FAIL" { "Red" }
        "ERROR" { "Magenta" }
    }
    Write-Host "$($test.Status): $($test.Name)" -ForegroundColor $color
}

Write-Host ""
Write-Host "Results: $passCount/$totalCount tests passed" -ForegroundColor $(if ($failCount -eq 0) {"Green"} else {"Yellow"})

if ($failCount -eq 0) {
    Write-Host ""
    Write-Host "SUCCESS: ALL TESTS PASSED! Documentation optimization successful!" -ForegroundColor Green
    exit 0
} else {
    Write-Host ""
    Write-Host "WARNING: $failCount tests failed. Review issues above." -ForegroundColor Yellow
    exit 1
}