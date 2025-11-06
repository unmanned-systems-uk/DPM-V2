#!/bin/bash
# Historical Issue Search Tool - Learn from past attempts (Linux/macOS version)
# Companion to search-history.ps1 for cross-platform support

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "Error: GitHub CLI (gh) is not installed"
    echo "Install: https://cli.github.com/"
    exit 1
fi

# Parse arguments
SEARCH_TERM="$1"
SHOW_FAILED=false
SHOW_COMMENTS=false

if [ -z "$SEARCH_TERM" ]; then
    echo "Usage: $0 <search_term> [--show-failed] [--show-comments]"
    echo ""
    echo "Examples:"
    echo "  $0 focus"
    echo "  $0 \"network timeout\" --show-failed"
    echo "  $0 camera --show-comments"
    exit 1
fi

# Check for flags
for arg in "$@"; do
    case $arg in
        --show-failed)
            SHOW_FAILED=true
            ;;
        --show-comments)
            SHOW_COMMENTS=true
            ;;
    esac
done

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

echo -e "${CYAN}==========================================================${NC}"
echo -e "${CYAN}  Historical Issue Search - Learning from Past Attempts${NC}"
echo -e "${CYAN}==========================================================${NC}"
echo ""
echo -e "${YELLOW}Searching for: '$SEARCH_TERM'${NC}"

# Search all issues (both open and closed)
ISSUES_JSON=$(gh issue list --repo unmanned-systems-uk/DPM-V2 \
    --search "$SEARCH_TERM" \
    --state all \
    --limit 100 \
    --json number,title,state,labels,createdAt,closedAt)

# Check if any issues found
ISSUE_COUNT=$(echo "$ISSUES_JSON" | jq '. | length')

if [ "$ISSUE_COUNT" -eq 0 ]; then
    echo -e "\n${RED}No issues found matching '$SEARCH_TERM'${NC}"
    echo -e "${YELLOW}Try broader search terms or check prefixes like [FOCUS], [CAMERA], [NETWORK]${NC}"
    exit 0
fi

echo -e "\n${GREEN}Found $ISSUE_COUNT related issues:${NC}"

# Separate open and closed issues
CLOSED_ISSUES=$(echo "$ISSUES_JSON" | jq -r '.[] | select(.state == "CLOSED")')
OPEN_ISSUES=$(echo "$ISSUES_JSON" | jq -r '.[] | select(.state == "OPEN")')

# Display closed issues first (likely contain solutions)
CLOSED_COUNT=$(echo "$ISSUES_JSON" | jq '[.[] | select(.state == "CLOSED")] | length')
if [ "$CLOSED_COUNT" -gt 0 ]; then
    echo -e "\n${GREEN}✅ SOLVED/CLOSED Issues (check these for working solutions):${NC}"
    echo "$ISSUES_JSON" | jq -r '.[] | select(.state == "CLOSED") |
        "  #\(.number): \(.title)\n    " +
        (if (.labels | length) > 0 then
            "Labels: " + ([.labels[].name] | join(", "))
         else
            "Labels: none"
         end) + "\n    Closed: \(.closedAt)"'
fi

# Display open issues
OPEN_COUNT=$(echo "$ISSUES_JSON" | jq '[.[] | select(.state == "OPEN")] | length')
if [ "$OPEN_COUNT" -gt 0 ]; then
    echo -e "\n${YELLOW}⚠️  OPEN Issues (may contain failed attempts):${NC}"
    echo "$ISSUES_JSON" | jq -r '.[] | select(.state == "OPEN") |
        "  #\(.number): \(.title)\n    " +
        (if (.labels | length) > 0 then
            "Labels: " + ([.labels[].name] | join(", "))
         else
            "Labels: none"
         end) + "\n    Created: \(.createdAt)"'
fi

# Show failed attempts if requested
if [ "$SHOW_FAILED" = true ]; then
    echo -e "\n${MAGENTA}🔍 Searching for failed attempts in comments...${NC}"

    # Get first 5 issue numbers
    ISSUE_NUMBERS=$(echo "$ISSUES_JSON" | jq -r '.[0:5] | .[].number')

    for issue_num in $ISSUE_NUMBERS; do
        # Get comments for this issue
        COMMENTS=$(gh issue view "$issue_num" --repo unmanned-systems-uk/DPM-V2 --json comments --jq '.comments[].body' 2>/dev/null)

        if [ -n "$COMMENTS" ]; then
            # Search for failure patterns
            FAILURES=$(echo "$COMMENTS" | grep -iE "didn't work|failed|tried|doesn't work|not working|broke|error" | head -5)

            if [ -n "$FAILURES" ]; then
                echo -e "\n${RED}❌ Failed attempts in #$issue_num:${NC}"
                echo "$FAILURES" | while IFS= read -r line; do
                    echo -e "  ${GRAY}$line${NC}"
                done
            fi
        fi
    done
fi

# Show comments if requested
if [ "$SHOW_COMMENTS" = true ]; then
    echo -e "\n${CYAN}📝 Detailed comments (first 3 issues):${NC}"

    # Get first 3 issue numbers
    ISSUE_NUMBERS=$(echo "$ISSUES_JSON" | jq -r '.[0:3] | .[].number')

    for issue_num in $ISSUE_NUMBERS; do
        echo -e "\n${CYAN}--- Issue #$issue_num ---${NC}"
        gh issue view "$issue_num" --repo unmanned-systems-uk/DPM-V2 --comments
    done
fi

# Provide actionable next steps
echo -e "\n${CYAN}==========================================================${NC}"
echo -e "${CYAN}  NEXT STEPS - Learn from History${NC}"
echo -e "${CYAN}==========================================================${NC}"

echo -e "\n${GREEN}1. Read closed issues for working solutions:${NC}"
echo "$ISSUES_JSON" | jq -r '.[0:3] | .[] | select(.state == "CLOSED") |
    "   gh issue view \(.number) --comments"'

echo -e "\n${YELLOW}2. Check open issues for failed attempts:${NC}"
echo "$ISSUES_JSON" | jq -r '.[0:3] | .[] | select(.state == "OPEN") |
    "   gh issue view \(.number) --comments | grep -i \"tried\\|failed\""'

echo -e "\n${MAGENTA}3. Document your approach based on lessons learned:${NC}"
echo -e '   gh issue comment <#> --body "Based on #X and #Y, I will NOT try [failed approach]. Instead I will [new approach]"'

echo -e "\n${CYAN}💡 TIP: Before implementing, always state:${NC}"
echo -e "   ${NC}- What previous attempts you found${NC}"
echo -e "   ${NC}- What failed and why${NC}"
echo -e "   ${NC}- What new approach you're taking${NC}"
echo -e "   ${NC}- Why this approach is different${NC}"

echo ""
