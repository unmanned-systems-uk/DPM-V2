---
name: Bug Report with Historical Context
about: Report a bug with reference to previous attempts
title: '[DOMAIN][TYPE] '
labels: 'bug'
assignees: ''
---

<!--
📋 ISSUE TITLE FORMAT: [SCOPE][DOMAIN][TYPE] Description

Required Prefixes:

DOMAIN (pick one - REQUIRED):
- [AIR-SIDE] - Pi 5 C++ implementation
- [GROUND-SIDE] - H16 Android app
- [TOOLS] - SystemTools Python diagnostics
- [ALL-DOMAINS] - Affects multiple domains
- [WORKFLOW] - Development workflow/process
- [PROTOCOL] - Protocol specification changes
- [DOCS] - Documentation only

TYPE (pick one - REQUIRED):
- [BUG] - Something broken that should work
- [FIX] - Implementation of solution to a bug
- [FEATURE] - New functionality
- [ENHANCEMENT] - Improvement to existing functionality
- [REFACTOR] - Code improvement without behavior change
- [TESTING] - Test implementation or validation
- [DOCS] - Documentation changes

Optional SCOPE (prepend if needed):
- [MANDATORY] - All domains must implement immediately
- [URGENT] - Time-sensitive issue requiring quick attention
- [BLOCKED] - Cannot proceed without external action

Examples:
✅ [GROUND-SIDE][BUG] Focus commands not reaching Air-Side
✅ [MANDATORY][ALL-DOMAINS][WORKFLOW] New issue workflow requirements
✅ [AIR-SIDE][FEATURE] Add gimbal control support
✅ [TOOLS][ENHANCEMENT] Improve diagnostic dashboard performance

Format Order (General → Specific):
[SCOPE][DOMAIN][TYPE] - SCOPE is optional, DOMAIN and TYPE are required
-->

## Issue Description
<!-- Clear description of the problem -->

## Related Historical Issues
<!-- MANDATORY: List similar issues you found -->
- [ ] Searched for similar issues using: `gh issue list --search "keywords"`
- Related issues found:
  - #___ - [Issue title] - [Status: OPEN/CLOSED]
  - #___ - [Issue title] - [Status: OPEN/CLOSED]

## Previous Failed Attempts (from history)
<!-- What was tried before that didn't work? -->
1. **Issue #___**: Tried [approach] - Failed because [reason]
2. **Issue #___**: Tried [approach] - Failed because [reason]
3. **Not found in history** - This appears to be a new issue

## Proposed New Approach
<!-- Based on historical lessons, what will you try? -->
- Will NOT try: [Failed approach from history]
- Will try instead: [New approach]
- Why different: [Explanation of why this should work]

## Environment
- Domain: [Air-Side / Ground-Side / SystemTools]
- Platform: [Pi 5 / H16 Android / Windows]
- Version: [git commit hash]

## Steps to Reproduce
1.
2.
3.

## Expected Behavior
<!-- What should happen -->

## Actual Behavior
<!-- What actually happens -->

## Attempted Solutions Log
<!-- Update this as you try solutions -->

### Attempt 1: [Date/Time]
**What:**
**Code:** `specific function or line`
**Result:** ⬜ Pending / ❌ Failed / ✅ Success
**Lesson:**

### Attempt 2: [Date/Time]
**What:**
**Code:**
**Result:** ⬜ Pending / ❌ Failed / ✅ Success
**Lesson:**