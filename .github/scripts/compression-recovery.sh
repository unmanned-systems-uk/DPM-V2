#!/bin/bash

# Compression Recovery Script for Claude Code
# Quickly restores context after compression detection

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# ASCII Art Header
echo -e "${RED}"
echo "╔══════════════════════════════════════════╗"
echo "║   COMPRESSION RECOVERY ACTIVATED        ║"
echo "╚══════════════════════════════════════════╝"
echo -e "${NC}"

# Function to show critical rules
show_critical_rules() {
    echo -e "${RED}=== CRITICAL RULES (MEMORIZE NOW) ===${NC}"
    echo ""
    echo "1. ${RED}NEVER${NC} close GitHub issues (user closes)"
    echo "2. ${RED}ALWAYS${NC} search history before implementing"
    echo "3. ${RED}WHO tags MANDATORY${NC} on every comment"
    echo "4. ${RED}NEVER${NC} work without GitHub issue"
    echo "5. ${RED}NEVER${NC} modify other domain's code without approval"
    echo ""
}

# Function to identify domain
identify_domain() {
    echo -e "${YELLOW}=== DOMAIN IDENTIFICATION ===${NC}"
    echo ""
    echo "Which domain are you working in?"
    echo "1) Air-Side (CC-Air-Side) - Pi 5 C++ in sbc/"
    echo "2) Ground-Side (CC-Ground-Side) - Android in android/"
    echo "3) Dev-Tools (CC-Dev-Tools) - Python in SystemTools/"
    echo "4) Project Manager (CC-Project-Manager) - Coordination"
    echo ""
    read -p "Enter domain number (1-4): " domain_choice

    case $domain_choice in
        1)
            DOMAIN="CC-Air-Side"
            DOMAIN_PATH="sbc/"
            echo -e "${GREEN}✅ Domain: Air-Side${NC}"
            ;;
        2)
            DOMAIN="CC-Ground-Side"
            DOMAIN_PATH="android/"
            echo -e "${GREEN}✅ Domain: Ground-Side${NC}"
            ;;
        3)
            DOMAIN="CC-Dev-Tools"
            DOMAIN_PATH="SystemTools/"
            echo -e "${GREEN}✅ Domain: Dev-Tools${NC}"
            ;;
        4)
            DOMAIN="CC-Project-Manager"
            DOMAIN_PATH="all"
            echo -e "${GREEN}✅ Domain: Project Manager${NC}"
            ;;
        *)
            echo -e "${RED}Invalid choice. Defaulting to PM role.${NC}"
            DOMAIN="CC-Project-Manager"
            DOMAIN_PATH="all"
            ;;
    esac
    echo ""
}

# Function to check current work
check_current_work() {
    echo -e "${YELLOW}=== CURRENT WORK STATUS ===${NC}"
    echo ""

    # Check for in-progress issues
    echo "In-progress issues:"
    gh issue list --repo unmanned-systems-uk/DPM-V2 --label "status:in-progress" --state open --json number,title | \
        jq -r '.[] | "  #\(.number): \(.title)"'

    echo ""
    echo "Issues marked [FIXING]:"
    gh issue list --repo unmanned-systems-uk/DPM-V2 --search "[FIXING]" --state open --json number,title | \
        jq -r '.[] | "  #\(.number): \(.title)"'

    echo ""
    echo "Recent commits:"
    git log --oneline -5

    echo ""
}

# Function to show quick recovery
quick_recovery() {
    echo -e "${CYAN}=== QUICK RECOVERY PATHS ===${NC}"
    echo ""
    echo "Choose recovery level:"
    echo "1) Emergency (50 lines) - Bare minimum"
    echo "2) Critical (100 lines) - Essential rules"
    echo "3) Standard (200 lines) - Session start"
    echo "4) Full (250+ lines) - Complete context"
    echo ""
    read -p "Enter recovery level (1-4): " recovery_level

    case $recovery_level in
        1)
            echo -e "${YELLOW}Loading emergency recovery...${NC}"
            cat .claude/COMPRESSION_EMERGENCY.md
            ;;
        2)
            echo -e "${YELLOW}Loading critical rules...${NC}"
            cat .claude/RULES_CRITICAL.md
            ;;
        3)
            echo -e "${YELLOW}Loading session start...${NC}"
            cat .claude/SESSION_START.md
            ;;
        4)
            echo -e "${YELLOW}Loading full context...${NC}"
            cat .claude/SESSION_START.md
            echo ""
            echo -e "${YELLOW}=== ADDITIONAL CONTEXT ===${NC}"
            cat docs/CC_READ_THIS_FIRST.md
            ;;
        *)
            echo -e "${RED}Invalid choice. Loading emergency recovery...${NC}"
            cat .claude/COMPRESSION_EMERGENCY.md
            ;;
    esac
    echo ""
}

# Function to verify WHO tag knowledge
verify_who_tag() {
    echo -e "${YELLOW}=== WHO TAG VERIFICATION ===${NC}"
    echo ""
    echo "Your WHO tag is: ${GREEN}**WHO:** $DOMAIN${NC}"
    echo ""
    echo "Remember: EVERY GitHub comment must start with this WHO tag!"
    echo ""
}

# Function to show next steps
show_next_steps() {
    echo -e "${BLUE}=== NEXT STEPS ===${NC}"
    echo ""
    echo "1. Check open issues for your domain:"
    echo "   ${CYAN}gh issue list --state open --label ${DOMAIN_PATH}${NC}"
    echo ""
    echo "2. Search history before implementing:"
    echo "   ${CYAN}.github/scripts/enhanced-search-history.sh \"keyword\"${NC}"
    echo ""
    echo "3. When starting work on issue #N:"
    echo "   ${CYAN}gh issue edit N --title \"[FIXING] Original Title\"${NC}"
    echo "   ${CYAN}gh issue comment N --body \"**WHO:** $DOMAIN"
    echo "   "
    echo "   Starting work on [task]...\"${NC}"
    echo ""
    echo "4. Commit regularly:"
    echo "   ${CYAN}git add -A && git commit -m \"[DOMAIN][TYPE] Description\"${NC}"
    echo ""
}

# Function to create recovery checkpoint
create_checkpoint() {
    echo -e "${YELLOW}=== CREATING RECOVERY CHECKPOINT ===${NC}"
    echo ""

    # Create a recovery file with current context
    RECOVERY_FILE=".claude/recovery_$(date +%Y%m%d_%H%M%S).md"

    cat > "$RECOVERY_FILE" << EOF
# Recovery Checkpoint - $(date)

## Domain
$DOMAIN

## Current Directory
$(pwd)

## Git Status
$(git status --short)

## Last Commit
$(git log -1 --oneline)

## Open Issues
$(gh issue list --state open --label "status:in-progress" --json number,title | jq -r '.[] | "#\(.number): \(.title)"')

## Critical Rules Reminder
1. NEVER close GitHub issues
2. ALWAYS search history first
3. WHO tags MANDATORY
4. NEVER work without issue
5. Cross-domain approval required
EOF

    echo -e "${GREEN}✅ Recovery checkpoint created: $RECOVERY_FILE${NC}"
    echo ""
}

# Main execution
main() {
    # Show critical rules first
    show_critical_rules

    # Identify domain
    identify_domain

    # Check current work
    check_current_work

    # Verify WHO tag
    verify_who_tag

    # Ask if full recovery needed
    read -p "Do you need full context recovery? (y/n): " need_recovery
    if [[ "$need_recovery" == "y" ]]; then
        quick_recovery
    fi

    # Create checkpoint
    read -p "Create recovery checkpoint? (y/n): " create_check
    if [[ "$create_check" == "y" ]]; then
        create_checkpoint
    fi

    # Show next steps
    show_next_steps

    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║   RECOVERY COMPLETE - READY TO WORK     ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
    echo ""

    # Final reminder
    echo -e "${RED}REMEMBER:${NC}"
    echo "- Search history BEFORE implementing"
    echo "- Use WHO tags on EVERY comment"
    echo "- NEVER close issues"
    echo ""
}

# Run main function
main