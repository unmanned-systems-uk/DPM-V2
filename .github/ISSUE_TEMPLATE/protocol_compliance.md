---
name: Protocol Compliance Issue
about: Report protocol compliance violations or non-enforcement (PM RULE 11)
title: '[DOMAIN][CRITICAL][PROTOCOL] '
labels: protocol, priority:critical
assignees: ''

---

## 🚨 Protocol Compliance Violation

**Discovered during:** [Phase 1 testing | Code review | PM startup checks | Other]
**Related Issue:** #___ *(if part of integration testing or feature work)*
**PM Rule:** See `.claude/PM_RULES_CRITICAL.md` - PM RULE 11

---

## Violation Summary

**Domain affected:**
- [ ] Air-Side (C++)
- [ ] Ground-Side (Kotlin/Android)
- [ ] SystemTools (Python)
- [ ] Multiple domains

**Protocol file violated:**
- [ ] `protocol/log_contexts.json` - Log context definitions
- [ ] `protocol/commands.json` - Command definitions
- [ ] Other: `protocol/___.json`

**Type of violation:**
- [ ] Hardcoded values instead of loading from protocol/*.json
- [ ] Missing runtime enforcement (no validation against protocol)
- [ ] Domain-specific implementation diverged from protocol
- [ ] Protocol file not used at all

**Violation count:** ___ *(how many instances)*

---

## Evidence

### Discovery Method

```bash
# Command used to detect violation:
[paste command here]

# Output:
[paste output showing violations]
```

### Specific Examples

**Example 1:**
```
File: path/to/file.ext:123
Code: [paste problematic code]
Problem: [hardcoded value | no validation | etc.]
```

**Example 2:**
```
File: path/to/file.ext:456
Code: [paste problematic code]
Problem: [hardcoded value | no validation | etc.]
```

---

## Root Cause Analysis

**What should be happening:**
- Protocol file `protocol/___.json` is single source of truth
- Domain should [load dynamically | generate enum | validate at runtime]
- Implementation notes in protocol file specify: [paste from protocol/*.json]

**What is actually happening:**
- Domain [hardcoded values | doesn't load protocol | custom implementation]
- No runtime enforcement or validation
- Divergence from protocol spec

**Why this matters:**
- [ ] Cross-domain compatibility broken
- [ ] Future protocol changes won't propagate
- [ ] Single-point-of-truth principle violated
- [ ] Manual synchronization required (error-prone)

---

## Required Fix

### ❌ INCORRECT Approach (Do NOT do this):
- [ ] ❌ Manual find/replace for all violations
- [ ] ❌ Individual file edits without architectural change
- [ ] ❌ "Good enough" fix that doesn't enforce protocol
- [ ] ❌ Partial fix leaving some violations

### ✅ CORRECT Approach (Architectural Fix):

**STEP 1: Fix Root Cause**
- [ ] Implement protocol loader/enforcer
- [ ] Add runtime validation against protocol/*.json
- [ ] OR: Generate code from protocol file at build time
- [ ] Ensure ALL new code must use protocol (fail if not compliant)

**Implementation suggestions:**
```
[Language-specific solution]

Air-Side (C++):
- Use LogContext enum (compile-time enforcement)
- Update enum when protocol changes

Ground-Side (Kotlin):
- Load LogContext enum from protocol JSON OR
- Generate enum at build time (Gradle task) OR
- Runtime validation in StructuredLogger

SystemTools (Python):
- Use ProtocolLogger wrapper
- Load contexts dynamically from protocol JSON
- ValueError if invalid context used
```

**STEP 2: Fix All Violations**
- [ ] Update all existing code to use protocol-compliant API
- [ ] Verify 0 violations remain

**STEP 3: Verify Cross-Domain Compatibility**
- [ ] Test logs flow between domains
- [ ] Test filtering works for all protocol contexts
- [ ] Verify all domains recognize same protocol values

---

## Protocol Compliance Verification

**Before closing this issue, run:**

```bash
echo "=== Protocol Compliance Check ==="

# 1. SystemTools log format compliance
echo "SystemTools violations:"
grep -r 'logger\.\(debug\|info\)(' SystemTools/ --include="*.py" | \
  grep -v '\[COMMAND\]' | grep -v '\[NETWORK\]' | grep -v '\[DISCOVERY\]' | \
  grep -v '\[CONFIG\]' | grep -v '\[SYSTEM\]' | grep -v '\[HEALTH\]' | \
  grep -v '\[CAMERA\]' | grep -v '\[STORAGE\]' | grep -v '\[SYNC\]' | \
  grep -v '\[UI\]' | wc -l
# Expected: 0

# 2. Air-Side LogContext enforcement (if accessible)
ssh dpm@10.0.1.53 "grep -r 'LOG_' ~/DPM-V2/sbc/src | grep -v 'LogContext::' | wc -l"
# Expected: 0

# 3. Ground-Side StructuredLogger usage
echo "Ground-Side raw Log violations:"
grep -r 'Log\.\(d\|i\|w\|e\)(' android/app/src --include="*.kt" | \
  grep -v "StructuredLogger.kt" | grep -v "DPMApplication.kt" | \
  grep -v "logging/" | wc -l
# Expected: 0

# 4. Verify protocol sync across domains
diff <(ssh dpm@10.0.1.53 "cat ~/DPM-V2/protocol/log_contexts.json | jq -S .contexts") \
     <(cat protocol/log_contexts.json | jq -S .contexts)
# Expected: No differences
```

---

## Impact Assessment

**What's broken/blocked:**
- [ ] Phase 1 Integration Testing (Issue #82)
- [ ] Cross-domain log filtering
- [ ] Protocol compliance across project
- [ ] Other: ___

**Risk if not fixed:**
- Future protocol changes won't propagate to this domain
- Cross-domain features will break
- Manual synchronization errors likely
- Technical debt accumulates

---

## Success Criteria

**This issue is resolved when:**
- [ ] Root cause fixed (protocol enforced at runtime OR code generation implemented)
- [ ] All violations corrected (0 violations in compliance check)
- [ ] Cross-domain compatibility verified (all domains use same protocol)
- [ ] Future protocol changes will auto-propagate (or clear process documented)
- [ ] Compliance check added to PM_START.md (prevent regression)

---

## Testing Verification

### Test 1: Protocol Enforcement
```bash
# Try to use invalid context (should fail/warn)
[Test code that uses invalid protocol value]
# Expected: Error/warning from enforcement layer
```

### Test 2: Cross-Domain Compatibility
```bash
# Verify all domains recognize all protocol values
# Example: Air-Side sends HEALTH log → Ground-Side receives → SystemTools filters
```

### Test 3: Regression Prevention
```bash
# Run compliance check (should pass with 0 violations)
[paste compliance check commands from above]
```

---

## Related Issues
- Blocks: #___ (what this blocks)
- Related: #___ (similar compliance issues)
- Discovered in: #___ (where this was found)

---

## PM Note

Per **PM RULE 11 - Protocol Enforcement & Cross-Domain Compliance**:
- Protocol violations require ARCHITECTURAL fixes, NOT manual edits
- PM MUST create compliance issues immediately
- PM MUST block Phase completion until compliance restored
- Protocol/*.json files are SINGLE SOURCE OF TRUTH

**Priority:** CRITICAL - Blocks integration work until resolved
