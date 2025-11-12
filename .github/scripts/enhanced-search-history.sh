#!/bin/bash

# Enhanced Historical Search for Claude Code
# Optimized for Claude's reactive nature and pattern recognition

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display usage
usage() {
    echo "Enhanced Historical Search for Claude Code"
    echo ""
    echo "Usage: $0 <search_term> [options]"
    echo ""
    echo "Options:"
    echo "  --show-failed       Show only failed attempts"
    echo "  --show-successful   Show only successful solutions"
    echo "  --analyze-patterns  Analyze failure patterns"
    echo "  --context-aware     Include context from WHO tags"
    echo "  --compression-safe  Output in compression-resistant format"
    echo "  --help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 'focus'                          # Search all issues for 'focus'"
    echo "  $0 'manual focus' --show-failed    # Show failed manual focus attempts"
    echo "  $0 'sony sdk' --analyze-patterns   # Analyze SDK-related patterns"
}

# Check if search term provided
if [ $# -eq 0 ] || [ "$1" == "--help" ]; then
    usage
    exit 0
fi

SEARCH_TERM="$1"
shift

# Parse options
SHOW_FAILED=false
SHOW_SUCCESSFUL=false
ANALYZE_PATTERNS=false
CONTEXT_AWARE=false
COMPRESSION_SAFE=false

while [ $# -gt 0 ]; do
    case "$1" in
        --show-failed)
            SHOW_FAILED=true
            ;;
        --show-successful)
            SHOW_SUCCESSFUL=true
            ;;
        --analyze-patterns)
            ANALYZE_PATTERNS=true
            ;;
        --context-aware)
            CONTEXT_AWARE=true
            ;;
        --compression-safe)
            COMPRESSION_SAFE=true
            ;;
        *)
            echo "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
    shift
done

echo -e "${BLUE}=== Enhanced Historical Search ===${NC}"
echo -e "Searching for: ${YELLOW}$SEARCH_TERM${NC}"
echo ""

# Search all issues (open and closed)
echo -e "${GREEN}Searching issues...${NC}"

# Get issues matching search term
ISSUES=$(gh issue list --repo unmanned-systems-uk/DPM-V2 --search "$SEARCH_TERM" --state all --limit 100 --json number,title,state,labels,createdAt,closedAt 2>/dev/null || echo "[]")

if [ "$ISSUES" == "[]" ]; then
    echo -e "${RED}No issues found matching '$SEARCH_TERM'${NC}"
    exit 0
fi

# Function to extract WHO tags from comments
extract_who_tags() {
    local issue_num=$1
    gh issue view $issue_num --repo unmanned-systems-uk/DPM-V2 --comments --json comments | \
        jq -r '.comments[].body' | \
        grep -o '\*\*WHO:\*\* [^[:space:]]*' | \
        sed 's/\*\*WHO:\*\* //' | \
        sort | uniq -c | sort -rn
}

# Function to check if issue contains failures
has_failures() {
    local issue_num=$1
    local failure_keywords="failed|didn't work|not working|broken|error|issue|problem|bug"

    gh issue view $issue_num --repo unmanned-systems-uk/DPM-V2 --comments --json body,comments | \
        jq -r '.body, .comments[].body' | \
        grep -iE "$failure_keywords" > /dev/null 2>&1
}

# Function to check if issue was successful
was_successful() {
    local issue_num=$1
    local success_keywords="fixed|working|success|complete|resolved|implemented"

    gh issue view $issue_num --repo unmanned-systems-uk/DPM-V2 --comments --json body,comments,labels | \
        jq -r '.labels[].name' | grep -E "status:fixed|status:complete" > /dev/null 2>&1
}

# Process issues based on filters
echo -e "${GREEN}Found $(echo $ISSUES | jq '. | length') issues${NC}"
echo ""

# Arrays to store patterns
declare -a FAILED_APPROACHES
declare -a SUCCESSFUL_APPROACHES
declare -a COMMON_ERRORS

# Process each issue
echo "$ISSUES" | jq -c '.[]' | while read -r issue; do
    NUMBER=$(echo "$issue" | jq -r '.number')
    TITLE=$(echo "$issue" | jq -r '.title')
    STATE=$(echo "$issue" | jq -r '.state')

    # Apply filters
    if [ "$SHOW_FAILED" = true ]; then
        if ! has_failures $NUMBER; then
            continue
        fi
    fi

    if [ "$SHOW_SUCCESSFUL" = true ]; then
        if ! was_successful $NUMBER; then
            continue
        fi
    fi

    # Display issue
    if [ "$STATE" = "closed" ]; then
        STATE_COLOR="${GREEN}[CLOSED]${NC}"
    else
        STATE_COLOR="${YELLOW}[OPEN]${NC}"
    fi

    echo -e "${BLUE}Issue #$NUMBER${NC} $STATE_COLOR: $TITLE"

    # Show WHO context if requested
    if [ "$CONTEXT_AWARE" = true ]; then
        echo "  Contributors:"
        extract_who_tags $NUMBER | while read -r line; do
            echo "    $line"
        done
    fi

    # Extract key information
    echo "  Key findings:"
    gh issue view $NUMBER --repo unmanned-systems-uk/DPM-V2 --comments --json body,comments | \
        jq -r '.body, .comments[].body' | \
        grep -iE "tried|attempted|failed|working|fixed|solution" | \
        head -3 | \
        sed 's/^/    /'

    echo ""
done

# Analyze patterns if requested
if [ "$ANALYZE_PATTERNS" = true ]; then
    echo -e "${YELLOW}=== Pattern Analysis ===${NC}"
    echo ""

    # Analyze failure patterns
    echo "Common failure indicators:"
    echo "$ISSUES" | jq -c '.[]' | while read -r issue; do
        NUMBER=$(echo "$issue" | jq -r '.number')
        gh issue view $NUMBER --repo unmanned-systems-uk/DPM-V2 --comments --json comments | \
            jq -r '.comments[].body' | \
            grep -ioE "(tried .{0,50}|failed because .{0,50}|didn't work .{0,50})" | \
            sed 's/tried/TRIED:/i' | \
            sed 's/failed because/FAILED:/i' | \
            sed "s/didn't work/DIDN'T WORK:/i"
    done | sort | uniq -c | sort -rn | head -10

    echo ""
    echo "Success patterns:"
    echo "$ISSUES" | jq -c '.[]' | while read -r issue; do
        NUMBER=$(echo "$issue" | jq -r '.number')
        if was_successful $NUMBER; then
            gh issue view $NUMBER --repo unmanned-systems-uk/DPM-V2 --comments --json comments | \
                jq -r '.comments[].body' | \
                grep -ioE "(fixed by .{0,50}|solution was .{0,50}|working after .{0,50})" | \
                sed 's/fixed by/FIXED BY:/i' | \
                sed 's/solution was/SOLUTION:/i' | \
                sed 's/working after/WORKING:/i'
        fi
    done | sort | uniq -c | sort -rn | head -10
fi

# Compression-safe output
if [ "$COMPRESSION_SAFE" = true ]; then
    echo ""
    echo -e "${GREEN}=== COMPRESSION-SAFE SUMMARY ===${NC}"
    echo "SEARCH: $SEARCH_TERM"
    echo "ISSUES: $(echo $ISSUES | jq '. | length')"
    echo ""
    echo "KEY LESSONS:"

    # Extract most important lessons
    echo "$ISSUES" | jq -c '.[]' | while read -r issue; do
        NUMBER=$(echo "$issue" | jq -r '.number')
        if was_successful $NUMBER; then
            echo "✅ #$NUMBER: WORKED"
            gh issue view $NUMBER --repo unmanned-systems-uk/DPM-V2 --comments --json comments | \
                jq -r '.comments[].body' | \
                grep -i "solution\|fixed\|working" | \
                head -1 | \
                sed 's/^/   /'
        elif has_failures $NUMBER; then
            echo "❌ #$NUMBER: FAILED"
            gh issue view $NUMBER --repo unmanned-systems-uk/DPM-V2 --comments --json comments | \
                jq -r '.comments[].body' | \
                grep -i "failed\|didn't work" | \
                head -1 | \
                sed 's/^/   /'
        fi
    done | head -10

    echo ""
    echo "REMEMBER: Don't repeat failed approaches!"
fi

echo ""
echo -e "${GREEN}Search complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Review relevant issues with: gh issue view <number> --comments"
echo "2. Learn from past failures before implementing"
echo "3. Document your approach based on history"