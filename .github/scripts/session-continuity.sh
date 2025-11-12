#!/bin/bash

# Session Continuity Checker for Claude Code
# Verifies persistent artifacts to ensure session integrity

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Claude Code Session Continuity Check ===${NC}"
echo ""

# Function to check git status
check_git_status() {
    echo -e "${YELLOW}Checking Git Status...${NC}"

    # Check if we're in the right directory
    CURRENT_DIR=$(pwd)
    if [[ "$CURRENT_DIR" != */DPM-V2 ]]; then
        echo -e "${RED}❌ Not in DPM-V2 directory!${NC}"
        echo "   Current: $CURRENT_DIR"
        echo "   Expected: */DPM-V2"
        return 1
    else
        echo -e "${GREEN}✅ Correct directory${NC}"
    fi

    # Check branch
    BRANCH=$(git branch --show-current)
    if [[ "$BRANCH" != "main" ]]; then
        echo -e "${YELLOW}⚠️  Not on main branch (currently on: $BRANCH)${NC}"
    else
        echo -e "${GREEN}✅ On main branch${NC}"
    fi

    # Check for uncommitted changes
    if [[ -n $(git status --porcelain) ]]; then
        echo -e "${YELLOW}⚠️  Uncommitted changes detected:${NC}"
        git status --short | head -5
    else
        echo -e "${GREEN}✅ No uncommitted changes${NC}"
    fi

    # Check last commit
    echo "   Last commit: $(git log -1 --oneline)"
    echo ""
}

# Function to check GitHub issues
check_github_issues() {
    echo -e "${YELLOW}Checking GitHub Issues...${NC}"

    # Check for in-progress issues
    IN_PROGRESS=$(gh issue list --repo unmanned-systems-uk/DPM-V2 --label "status:in-progress" --state open --json number,title 2>/dev/null || echo "[]")

    if [[ "$IN_PROGRESS" != "[]" ]]; then
        COUNT=$(echo "$IN_PROGRESS" | jq '. | length')
        echo -e "${YELLOW}⚠️  $COUNT issue(s) in progress:${NC}"
        echo "$IN_PROGRESS" | jq -r '.[] | "   #\(.number): \(.title)"'
    else
        echo -e "${GREEN}✅ No issues currently in progress${NC}"
    fi

    # Check for issues with FIXING in title
    FIXING=$(gh issue list --repo unmanned-systems-uk/DPM-V2 --search "[FIXING]" --state open --json number,title 2>/dev/null || echo "[]")

    if [[ "$FIXING" != "[]" ]]; then
        COUNT=$(echo "$FIXING" | jq '. | length')
        echo -e "${YELLOW}⚠️  $COUNT issue(s) marked [FIXING]:${NC}"
        echo "$FIXING" | jq -r '.[] | "   #\(.number): \(.title)"'
    else
        echo -e "${GREEN}✅ No issues marked [FIXING]${NC}"
    fi

    echo ""
}

# Function to check recent WHO tags
check_who_tags() {
    echo -e "${YELLOW}Checking Recent WHO Tags...${NC}"

    # Get recent comments (last 24 hours)
    RECENT_ISSUES=$(gh issue list --repo unmanned-systems-uk/DPM-V2 --state all --updated ">$(date -d '24 hours ago' '+%Y-%m-%d')" --json number 2>/dev/null || echo "[]")

    if [[ "$RECENT_ISSUES" != "[]" ]]; then
        WHO_TAGS_FOUND=0
        WHO_TAGS_MISSING=0

        echo "$RECENT_ISSUES" | jq -r '.[].number' | while read -r issue_num; do
            # Get last comment
            LAST_COMMENT=$(gh issue view "$issue_num" --repo unmanned-systems-uk/DPM-V2 --comments --json comments | \
                jq -r '.comments[-1].body' 2>/dev/null || echo "")

            if [[ -n "$LAST_COMMENT" ]]; then
                if [[ "$LAST_COMMENT" == "**WHO:"* ]]; then
                    ((WHO_TAGS_FOUND++)) || true
                else
                    ((WHO_TAGS_MISSING++)) || true
                    echo -e "${RED}   ❌ Issue #$issue_num: Last comment missing WHO tag${NC}"
                fi
            fi
        done

        if [[ $WHO_TAGS_MISSING -eq 0 ]]; then
            echo -e "${GREEN}✅ All recent comments have WHO tags${NC}"
        fi
    else
        echo -e "${BLUE}ℹ️  No recent issue activity${NC}"
    fi

    echo ""
}

# Function to check for compression indicators
check_compression_risk() {
    echo -e "${YELLOW}Checking Compression Risk...${NC}"

    # Check session start time (from git log or last issue comment)
    LAST_COMMIT_TIME=$(git log -1 --format="%ar" 2>/dev/null || echo "unknown")
    echo "   Last commit: $LAST_COMMIT_TIME"

    # Count total commits today
    TODAY_COMMITS=$(git log --since="midnight" --oneline 2>/dev/null | wc -l)
    echo "   Commits today: $TODAY_COMMITS"

    # Estimate session length
    if [[ $TODAY_COMMITS -gt 20 ]]; then
        echo -e "${YELLOW}⚠️  High activity session (${TODAY_COMMITS} commits) - compression risk increased${NC}"
    elif [[ $TODAY_COMMITS -gt 10 ]]; then
        echo -e "${YELLOW}ℹ️  Moderate activity session (${TODAY_COMMITS} commits)${NC}"
    else
        echo -e "${GREEN}✅ Normal activity level${NC}"
    fi

    echo ""
}

# Function to verify critical files exist
check_critical_files() {
    echo -e "${YELLOW}Checking Critical Files...${NC}"

    CRITICAL_FILES=(
        ".claude/RULES_CRITICAL.md"
        ".claude/SESSION_START.md"
        ".claude/COMPRESSION_EMERGENCY.md"
        "docs/CC_READ_THIS_FIRST.md"
        "protocol/commands.json"
    )

    ALL_EXIST=true
    for file in "${CRITICAL_FILES[@]}"; do
        if [[ -f "$file" ]]; then
            echo -e "${GREEN}✅ $file exists${NC}"
        else
            echo -e "${RED}❌ $file missing!${NC}"
            ALL_EXIST=false
        fi
    done

    if [[ "$ALL_EXIST" = false ]]; then
        echo -e "${RED}⚠️  Some critical files are missing!${NC}"
    fi

    echo ""
}

# Function to generate recovery recommendations
generate_recommendations() {
    echo -e "${BLUE}=== Session Continuity Recommendations ===${NC}"
    echo ""

    # Check if recovery needed
    if [[ -n $(git status --porcelain) ]]; then
        echo "1. Commit or stash uncommitted changes:"
        echo "   git add -A && git commit -m '[DOMAIN][WIP] Session continuity checkpoint'"
        echo ""
    fi

    # Check for in-progress work
    if [[ "$IN_PROGRESS" != "[]" ]]; then
        echo "2. Resume in-progress issues before starting new work"
        echo ""
    fi

    # Compression prevention
    if [[ $TODAY_COMMITS -gt 15 ]]; then
        echo "3. Consider session break to prevent compression:"
        echo "   - Run EOD reflection"
        echo "   - Create lessons-learned issue"
        echo "   - Start fresh session"
        echo ""
    fi

    echo "4. If context feels lost, immediately run:"
    echo "   cat .claude/COMPRESSION_EMERGENCY.md"
    echo ""
}

# Main execution
main() {
    check_git_status
    check_github_issues
    check_who_tags
    check_compression_risk
    check_critical_files
    generate_recommendations

    echo -e "${GREEN}Session continuity check complete!${NC}"
    echo ""

    # Return status based on critical issues
    if [[ "$ALL_EXIST" = false ]]; then
        exit 1
    fi

    exit 0
}

# Run main function
main