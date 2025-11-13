#!/bin/bash
# validate_phase1.sh - Automated validation tests for Phase 1 implementation
# Can be run on any platform (Windows/Linux) without requiring Docker or Pi 5
# Usage: ./tests/validate_phase1.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PASS_COUNT=0
FAIL_COUNT=0
TOTAL_TESTS=0

# Test result tracking
pass_test() {
    PASS_COUNT=$((PASS_COUNT + 1))
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -e "${GREEN}✅ PASS${NC}: $1"
}

fail_test() {
    FAIL_COUNT=$((FAIL_COUNT + 1))
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -e "${RED}❌ FAIL${NC}: $1"
}

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Phase 1 Validation Tests${NC}"
echo -e "${BLUE}Automated checks without Docker/Pi 5${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Change to project root
cd "$(dirname "$0")/../.."

echo -e "${YELLOW}Test Suite 1: JSON Validation${NC}"
echo "---"

# Test 1: Validate commands.json
if python -m json.tool protocol/commands.json > /dev/null 2>&1; then
    pass_test "protocol/commands.json is valid JSON"
else
    fail_test "protocol/commands.json has syntax errors"
fi

# Test 2: Validate config files
for config_file in sbc/config/*.json; do
    if python -m json.tool "$config_file" > /dev/null 2>&1; then
        pass_test "$(basename $config_file) is valid JSON"
    else
        fail_test "$(basename $config_file) has syntax errors"
    fi
done

echo ""
echo -e "${YELLOW}Test Suite 2: Source File Verification${NC}"
echo "---"

# Test 3: Check Phase 1 sources in CMakeLists.txt
PHASE1_SOURCES=(
    "src/config/config_manager.cpp"
    "src/logging/structured_logger.cpp"
    "src/logging/sinks/console_sink.cpp"
    "src/logging/sinks/file_sink.cpp"
    "src/logging/sinks/network_sink.cpp"
    "src/health/health_monitor.cpp"
)

for src in "${PHASE1_SOURCES[@]}"; do
    if grep -q "$src" sbc/CMakeLists.txt; then
        pass_test "$src listed in CMakeLists.txt"
    else
        fail_test "$src MISSING from CMakeLists.txt"
    fi
done

echo ""
echo -e "${YELLOW}Test Suite 3: Protocol Integration${NC}"
echo "---"

# Test 4: Verify protocol commands exist
COMMANDS=("logging.enable_streaming" "logging.disable_streaming" "health.get_snapshot")
for cmd in "${COMMANDS[@]}"; do
    if grep -q "\"$cmd\"" protocol/commands.json; then
        pass_test "$cmd documented in protocol/commands.json"
    else
        fail_test "$cmd MISSING from protocol/commands.json"
    fi
done

# Test 5: Verify command handlers exist
HANDLERS=("handleEnableLogStreaming" "handleDisableLogStreaming" "handleGetHealth")
for handler in "${HANDLERS[@]}"; do
    if grep -q "$handler" sbc/src/protocol/tcp_server.cpp; then
        pass_test "$handler implemented in tcp_server.cpp"
    else
        fail_test "$handler MISSING from tcp_server.cpp"
    fi
done

# Test 6: Verify handler declarations
for handler in "${HANDLERS[@]}"; do
    if grep -q "$handler" sbc/src/protocol/tcp_server.h; then
        pass_test "$handler declared in tcp_server.h"
    else
        fail_test "$handler MISSING from tcp_server.h"
    fi
done

# Test 7: Verify command routing
for cmd in "${COMMANDS[@]}"; do
    if grep -q "$cmd" sbc/src/protocol/tcp_server.cpp; then
        pass_test "$cmd routed in processCommand()"
    else
        fail_test "$cmd NOT routed in processCommand()"
    fi
done

echo ""
echo -e "${YELLOW}Test Suite 4: Include Verification${NC}"
echo "---"

# Test 8: Check main.cpp includes
MAIN_INCLUDES=("config/config_manager.h" "logging/structured_logger.h" "health/health_monitor.h")
for inc in "${MAIN_INCLUDES[@]}"; do
    if grep -q "$inc" sbc/src/main.cpp; then
        pass_test "main.cpp includes $inc"
    else
        fail_test "main.cpp MISSING include: $inc"
    fi
done

# Test 9: Check tcp_server.cpp includes
TCP_INCLUDES=("logging/structured_logger.h" "health/health_monitor.h")
for inc in "${TCP_INCLUDES[@]}"; do
    if grep -q "$inc" sbc/src/protocol/tcp_server.cpp; then
        pass_test "tcp_server.cpp includes $inc"
    else
        fail_test "tcp_server.cpp MISSING include: $inc"
    fi
done

echo ""
echo -e "${YELLOW}Test Suite 5: Header Guards${NC}"
echo "---"

# Test 10: Check header guards
HEADERS=(
    "sbc/src/logging/structured_logger.h"
    "sbc/src/health/health_monitor.h"
    "sbc/src/logging/log_sink.h"
    "sbc/src/config/config_manager.h"
)

for header in "${HEADERS[@]}"; do
    if grep -q "#ifndef.*_H" "$header" && grep -q "#define.*_H" "$header" && grep -q "#endif" "$header"; then
        pass_test "$(basename $header) has proper include guards"
    else
        fail_test "$(basename $header) MISSING or malformed include guards"
    fi
done

echo ""
echo -e "${YELLOW}Test Suite 6: Documentation Consistency${NC}"
echo "---"

# Test 11: Check documented TODOs are tracked
TODO_COUNT=$(grep -r "TODO" sbc/src/main.cpp | wc -l)
if [ "$TODO_COUNT" -eq 4 ]; then
    pass_test "All 4 known TODOs present in main.cpp"
else
    fail_test "TODO count mismatch (expected 4, found $TODO_COUNT)"
fi

# Test 12: Check testing plan exists
if [ -f "sbc/docs/PHASE1_TESTING_PLAN.md" ]; then
    pass_test "Phase 1 testing plan exists"
else
    fail_test "Phase 1 testing plan MISSING"
fi

# Test 13: Check protocol version consistency
PROTOCOL_VERSION=$(grep -oP '"version":\s*"\K[^"]+' protocol/commands.json | head -1)
if [ "$PROTOCOL_VERSION" = "1.0.0" ]; then
    pass_test "Protocol version is 1.0.0"
else
    fail_test "Protocol version mismatch (expected 1.0.0, found $PROTOCOL_VERSION)"
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Test Results Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Total Tests:  ${TOTAL_TESTS}"
echo -e "Passed:       ${GREEN}${PASS_COUNT}${NC}"
echo -e "Failed:       ${RED}${FAIL_COUNT}${NC}"
echo ""

if [ $FAIL_COUNT -eq 0 ]; then
    echo -e "${GREEN}✅ ALL VALIDATION TESTS PASSED!${NC}"
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "1. Build Docker image on Pi 5: cd sbc && ./build_container.sh"
    echo "2. Run integration tests: Follow sbc/docs/PHASE1_TESTING_PLAN.md"
    echo "3. Report results on Issue #72"
    exit 0
else
    echo -e "${RED}❌ VALIDATION FAILED - Fix errors before testing on Pi 5${NC}"
    echo ""
    echo -e "${YELLOW}Action Required:${NC}"
    echo "Review failed tests above and fix issues"
    echo "Re-run this script after fixes"
    exit 1
fi
