#!/bin/bash

# Documentation Audit Script for DPM-V2
# Purpose: Quarterly review of documentation completeness and freshness
# Usage: ./.github/scripts/audit-documentation.sh

set -e

echo "======================================"
echo "DPM-V2 Documentation Audit"
echo "Date: $(date +%Y-%m-%d)"
echo "======================================"
echo ""

EXIT_CODE=0

# =============================================================================
# Check 1: Component Documentation Coverage
# =============================================================================
echo "1. Component Documentation Coverage"
echo "-----------------------------------"

echo ""
echo "   Air-Side Components (sbc/src/):"
MISSING_AIR_COMPONENTS=0

if [ -d "sbc/src" ]; then
    for dir in sbc/src/*/; do
        if [ -d "$dir" ]; then
            component=$(basename "$dir")
            if ! grep -q "$component" docs/architecture/view-logical.md 2>/dev/null; then
                echo "   ⚠️  Component '$component' not documented in view-logical.md"
                MISSING_AIR_COMPONENTS=$((MISSING_AIR_COMPONENTS + 1))
                EXIT_CODE=1
            fi
        fi
    done

    if [ $MISSING_AIR_COMPONENTS -eq 0 ]; then
        echo "   ✅ All Air-Side components documented"
    else
        echo "   ⚠️  Found $MISSING_AIR_COMPONENTS undocumented components"
    fi
else
    echo "   ℹ️  sbc/src/ directory not found (expected for Air-Side)"
fi

echo ""
echo "   Ground-Side Components (android/):"
MISSING_GROUND_COMPONENTS=0

if [ -d "android" ]; then
    # Check for ViewModels
    VIEWMODELS=$(find android -name "*ViewModel.kt" 2>/dev/null | wc -l)
    echo "   Found $VIEWMODELS ViewModel files"

    # Simple check: are ViewModels mentioned in docs?
    if [ $VIEWMODELS -gt 0 ]; then
        if ! grep -q "ViewModel" docs/architecture/view-logical.md 2>/dev/null; then
            echo "   ⚠️  ViewModels exist but not documented in view-logical.md"
            MISSING_GROUND_COMPONENTS=$((MISSING_GROUND_COMPONENTS + 1))
            EXIT_CODE=1
        else
            echo "   ✅ ViewModel documentation found"
        fi
    fi
else
    echo "   ℹ️  android/ directory not found (expected for Ground-Side)"
fi

echo ""

# =============================================================================
# Check 2: ADR Integration
# =============================================================================
echo "2. ADR Integration"
echo "-----------------------------------"

MISSING_ADR_REFS=0

if [ -d "docs/architecture/adr" ]; then
    for adr in docs/architecture/adr/ADR-*.md; do
        if [ -f "$adr" ]; then
            adr_num=$(basename "$adr" | grep -oP 'ADR-\d+' || echo "")
            if [ -n "$adr_num" ]; then
                if ! grep -q "$adr_num" docs/architecture/SOFTWARE_ARCHITECTURE_DOCUMENT.md 2>/dev/null; then
                    echo "   ⚠️  $adr_num not referenced in SOFTWARE_ARCHITECTURE_DOCUMENT.md"
                    MISSING_ADR_REFS=$((MISSING_ADR_REFS + 1))
                    EXIT_CODE=1
                fi
            fi
        fi
    done

    if [ $MISSING_ADR_REFS -eq 0 ]; then
        echo "   ✅ All ADRs referenced in SAD"
    else
        echo "   ⚠️  Found $MISSING_ADR_REFS unreferenced ADRs"
    fi
else
    echo "   ⚠️  docs/architecture/adr/ directory not found"
    EXIT_CODE=1
fi

echo ""

# =============================================================================
# Check 3: Cross-Reference Validation
# =============================================================================
echo "3. Cross-Reference Validation"
echo "-----------------------------------"

BROKEN_LINKS=0

for file in docs/architecture/*.md docs/architecture/adr/*.md; do
    if [ -f "$file" ]; then
        # Extract markdown links [text](path)
        while IFS= read -r link; do
            # Skip empty lines
            [ -z "$link" ] && continue

            # Skip external links (http/https)
            [[ "$link" =~ ^https?:// ]] && continue

            # Skip anchors only
            [[ "$link" =~ ^# ]] && continue

            # Determine target file path
            if [[ "$link" =~ ^\.\. ]]; then
                # Parent directory reference
                target_file="docs/$(echo $link | sed 's/\.\.\///')"
            elif [[ "$link" =~ ^\. ]]; then
                # Current directory reference
                target_file="docs/architecture/$(echo $link | sed 's/\.\///')"
            elif [[ "$link" =~ ^/ ]]; then
                # Absolute path from repo root
                target_file="${link:1}"
            else
                # Relative path
                target_file="docs/architecture/$link"
            fi

            # Remove anchor if present
            target_file=$(echo "$target_file" | cut -d'#' -f1)

            # Check if target exists
            if [ ! -f "$target_file" ] && [ ! -d "$target_file" ]; then
                echo "   ⚠️  Broken link in $(basename $file): $link"
                BROKEN_LINKS=$((BROKEN_LINKS + 1))
            fi
        done < <(grep -oP '\]\(\K[^)]+' "$file" 2>/dev/null || true)
    fi
done

if [ $BROKEN_LINKS -eq 0 ]; then
    echo "   ✅ No broken links detected"
else
    echo "   ⚠️  Found $BROKEN_LINKS potentially broken links"
    echo "   Note: Some warnings may be false positives (external references, anchors)"
fi

echo ""

# =============================================================================
# Check 4: Documentation Freshness
# =============================================================================
echo "4. Documentation Freshness"
echo "-----------------------------------"

# Get last update timestamps
if [ -d ".git" ]; then
    LAST_DOC_UPDATE=$(git log -1 --format=%ci docs/architecture/ 2>/dev/null || echo "Never")
    LAST_CODE_UPDATE_AIR=$(git log -1 --format=%ci sbc/ 2>/dev/null || echo "Never")
    LAST_CODE_UPDATE_GROUND=$(git log -1 --format=%ci android/ 2>/dev/null || echo "Never")
    LAST_CODE_UPDATE_TOOLS=$(git log -1 --format=%ci SystemTools/ 2>/dev/null || echo "Never")

    echo "   Last documentation update: $LAST_DOC_UPDATE"
    echo "   Last Air-Side code update: $LAST_CODE_UPDATE_AIR"
    echo "   Last Ground-Side code update: $LAST_CODE_UPDATE_GROUND"
    echo "   Last Tools code update: $LAST_CODE_UPDATE_TOOLS"

    # Check if code was updated more than 1 month after docs
    # (This is a simple heuristic - can be made more sophisticated)
    if command -v date >/dev/null 2>&1; then
        DOC_EPOCH=$(date -d "$LAST_DOC_UPDATE" +%s 2>/dev/null || echo "0")

        if [ "$LAST_CODE_UPDATE_AIR" != "Never" ]; then
            AIR_EPOCH=$(date -d "$LAST_CODE_UPDATE_AIR" +%s 2>/dev/null || echo "0")
            DIFF_DAYS=$(( (AIR_EPOCH - DOC_EPOCH) / 86400 ))
            if [ $DIFF_DAYS -gt 30 ]; then
                echo "   ⚠️  Air-Side code updated $DIFF_DAYS days after last doc update"
            fi
        fi
    fi
else
    echo "   ℹ️  Not a git repository - skipping freshness check"
fi

echo ""

# =============================================================================
# Check 5: Required Files Exist
# =============================================================================
echo "5. Required Files Existence"
echo "-----------------------------------"

REQUIRED_FILES=(
    "docs/architecture/SOFTWARE_ARCHITECTURE_DOCUMENT.md"
    "docs/architecture/view-logical.md"
    "docs/architecture/view-context.md"
    "docs/architecture/view-data.md"
    "docs/architecture/view-security-reliability.md"
    "docs/architecture/view-deployment.md"
    "docs/architecture/view-integration.md"
    "docs/architecture/c4-level1-context.puml"
    "docs/architecture/c4-level2-container.puml"
    "docs/architecture/c4-level3-air-side-components.puml"
    "docs/architecture/c4-level3-ground-side-components.puml"
    "docs/architecture/c4-level3-dev-tools-components.puml"
    "docs/architecture/c4-level4-deployment.puml"
    "docs/architecture/adr/README.md"
    "CONTRIBUTING.md"
    "docs/DOCUMENTATION_UPDATE_GUIDE.md"
)

MISSING_FILES=0

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "   ⚠️  Missing required file: $file"
        MISSING_FILES=$((MISSING_FILES + 1))
        EXIT_CODE=1
    fi
done

if [ $MISSING_FILES -eq 0 ]; then
    echo "   ✅ All required files present"
else
    echo "   ⚠️  Missing $MISSING_FILES required files"
fi

echo ""

# =============================================================================
# Check 6: PlantUML Syntax
# =============================================================================
echo "6. PlantUML Diagram Syntax"
echo "-----------------------------------"

if command -v plantuml >/dev/null 2>&1; then
    PLANTUML_ERRORS=0

    for file in docs/architecture/*.puml; do
        if [ -f "$file" ]; then
            if ! plantuml -checkonly "$file" >/dev/null 2>&1; then
                echo "   ⚠️  Syntax error in $(basename $file)"
                PLANTUML_ERRORS=$((PLANTUML_ERRORS + 1))
                EXIT_CODE=1
            fi
        fi
    done

    if [ $PLANTUML_ERRORS -eq 0 ]; then
        echo "   ✅ All PlantUML diagrams have valid syntax"
    else
        echo "   ⚠️  Found $PLANTUML_ERRORS diagrams with syntax errors"
    fi
else
    echo "   ℹ️  PlantUML not installed - skipping syntax check"
    echo "   Install: sudo apt-get install plantuml"
fi

echo ""

# =============================================================================
# Check 7: ADR Count
# =============================================================================
echo "7. Architecture Decision Records"
echo "-----------------------------------"

if [ -d "docs/architecture/adr" ]; then
    ADR_COUNT=$(find docs/architecture/adr -name "ADR-*.md" | wc -l)
    echo "   Total ADRs: $ADR_COUNT"

    if [ $ADR_COUNT -lt 15 ]; then
        echo "   ℹ️  Expected at least 15 ADRs (baseline from Issue #65)"
    else
        echo "   ✅ ADR count meets baseline"
    fi
fi

echo ""

# =============================================================================
# Summary
# =============================================================================
echo "======================================"
echo "Audit Summary"
echo "======================================"
echo ""

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Documentation audit PASSED"
    echo ""
    echo "All checks completed successfully. Documentation is complete and up-to-date."
else
    echo "⚠️  Documentation audit found ISSUES"
    echo ""
    echo "Review warnings above and update documentation as needed."
    echo "See CONTRIBUTING.md and docs/DOCUMENTATION_UPDATE_GUIDE.md for guidance."
fi

echo ""
echo "======================================"

exit $EXIT_CODE
