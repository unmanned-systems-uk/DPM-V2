---
name: Bug Report
about: Report a bug or issue in the DPM-V2 system
title: '[DOMAIN][BUG] '
labels: bug
assignees: ''

---

## WHO Tag (REQUIRED)
**WHO:** [CC-Air-Side | CC-Ground-Side | CC-Dev-Tools | CC-Project-Manager | User (name)]

## Historical Search (REQUIRED)
**Did you search for similar historical issues?**
- [ ] Yes - Found similar issues: #___, #___
- [ ] Yes - No similar issues found
- [ ] No - Need to perform search

**Search command used:**
```bash
# Linux/macOS/Air-Side
.github/scripts/search-history.sh "keywords"

# Windows/Dev-Side
.github\scripts\search-history.ps1 "keywords"
```

**Related historical issues:**
- Issue #___ - [Brief description of relevance]

## Domain & Priority
**Affected Domain(s):**
- [ ] Air-Side (Pi 5 C++)
- [ ] Ground-Side (H16 Android)
- [ ] Dev-Tools (SystemTools Python)
- [ ] Cross-domain (multiple domains)

**Priority:**
- [ ] Critical - System unusable
- [ ] High - Major functionality broken
- [ ] Medium - Feature partially working
- [ ] Low - Minor issue or cosmetic

## Bug Description
**Brief description:**
[Clear one-sentence description]

**Detailed description:**
[Full description of the bug and its impact]

## Steps to Reproduce
1. [First step]
2. [Second step]
3. [Third step]
...

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happens]

## Environment
**Platform:**
- [ ] Air-Side (Pi 5, which branch: ___)
- [ ] Ground-Side (H16 Android, APK version: ___)
- [ ] Dev-Tools (Python version: ___, OS: ___)

**Network Configuration:**
- Air-Side IP: `192.168.___`
- Connection status: [Connected | Disconnected | Intermittent]

## Logs & Error Messages
```
[Paste relevant logs here]
```

**Log sources:**
- Air-Side: Container logs via SystemTools or `docker logs payload_manager`
- Ground-Side: `adb logcat -s NetworkClient`
- Dev-Tools: SystemTools console output

## Protocol Status
**Protocol version:** [Check protocol/*.json files]

**Relevant protocol files:**
- [ ] commands.json - Command: `___`
- [ ] camera_properties.json - Property: `___`
- [ ] Not protocol-related

## Attempted Solutions
**What have you tried? (Document to help future sessions)**

**Attempt 1:**
- What: [What you tried]
- Code: [File:line or specific change]
- Result: [❌ Failed | ⏳ Pending | ✅ Partial success]
- Lesson: [What you learned]

**Attempt 2:**
- What:
- Code:
- Result:
- Lesson:

[Add more attempts as needed]

## Additional Context
[Any other relevant information, screenshots, or context]

## Cross-Domain Impact
**Does this bug affect multiple domains?**
- [ ] No - Single domain issue
- [ ] Yes - Requires coordination:
  - Air-Side: [What needs to be done]
  - Ground-Side: [What needs to be done]
  - Dev-Tools: [What needs to be done]

## Testing Plan (When Fixed)
**How should this fix be tested?**
1. [Test step 1]
2. [Test step 2]
3. [Expected result]

---
**Remember:** Use WHO tags in all comments on this issue!
