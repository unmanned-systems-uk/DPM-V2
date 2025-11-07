---
name: Feature Request
about: Propose a new feature or enhancement for DPM-V2
title: '[DOMAIN][FEATURE] '
labels: enhancement
assignees: ''

---

## WHO Tag (REQUIRED)
**WHO:** [CC-Air-Side | CC-Ground-Side | CC-Dev-Tools | CC-Project-Manager | User (name)]

## Historical Search (REQUIRED)
**Did you search for similar historical features/requests?**
- [ ] Yes - Found similar: #___, #___
- [ ] Yes - No similar requests found
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

## Domain & Scope
**Target Domain(s):**
- [ ] Air-Side (Pi 5 C++)
- [ ] Ground-Side (H16 Android)
- [ ] Dev-Tools (SystemTools Python)
- [ ] Cross-domain (requires multiple domains)
- [ ] Protocol (changes to protocol/*.json)

**Feature Category:**
- [ ] Camera control/property
- [ ] Network/communication
- [ ] UI/UX enhancement
- [ ] Monitoring/diagnostics
- [ ] Protocol extension
- [ ] Workflow improvement
- [ ] Other: ___

## Feature Description
**One-sentence summary:**
[Clear, concise description]

**Detailed description:**
[Full explanation of the proposed feature]

**Problem it solves:**
[What user problem or pain point does this address?]

## Use Case
**Who needs this?**
- [ ] Air-Side operator
- [ ] Ground-Side pilot/operator
- [ ] Developer/maintainer
- [ ] System administrator

**When would it be used?**
[Describe the scenario/workflow where this feature is needed]

**Example workflow:**
1. User does X
2. System responds with Y
3. User can now accomplish Z

## Implementation Scope
**Estimated complexity:**
- [ ] Small - Single file, < 2 hours
- [ ] Medium - Multiple files, single domain, 2-8 hours
- [ ] Large - Cross-domain, 8-24 hours
- [ ] Very Large - Architectural change, > 24 hours

**Required changes:**

### Air-Side (C++)
- [ ] Not required
- [ ] Required - Files: `___`
- [ ] Required - Sony SDK integration needed

### Ground-Side (Android/Kotlin)
- [ ] Not required
- [ ] Required - Files: `___`
- [ ] Required - UI changes needed

### Dev-Tools (Python)
- [ ] Not required
- [ ] Required - Files: `___`
- [ ] Required - New tab/panel needed

### Protocol
- [ ] Not required
- [ ] Required - commands.json changes
- [ ] Required - camera_properties.json changes
- [ ] New protocol file needed

## Protocol Impact
**Does this require protocol changes?**
- [ ] No - Uses existing protocol
- [ ] Yes - Extends existing command/property
- [ ] Yes - New command/property needed

**Protocol specification:**
```json
{
  "command_name": {
    "description": "...",
    "parameters": {},
    "response": {}
  }
}
```

## Dependencies
**Blocks or depends on:**
- Blocks: [List issues this must complete before others can proceed]
- Depends on: [List issues that must be completed first]
- Related to: [List related issues]

**External dependencies:**
- [ ] Sony SDK functionality
- [ ] Android API version
- [ ] Python library: ___
- [ ] Network infrastructure
- [ ] None

## Cross-Domain Coordination
**If cross-domain, specify implementation order:**
1. [Domain] - [What to implement first]
2. [Domain] - [What depends on step 1]
3. [Domain] - [Final integration]

**Handoff points:**
- After [Domain] completes X, [Domain] needs to implement Y
- See [cross-domain doc] for details

## Testing Requirements
**How should this feature be tested?**

**Unit tests:**
- [Domain]: [What to test]

**Integration tests:**
- [How to test cross-domain interaction]

**Manual testing:**
1. [Step 1]
2. [Step 2]
3. [Expected result]

**Test environment:**
- [ ] Can test in simulation
- [ ] Requires actual camera
- [ ] Requires full Air-Side + Ground-Side setup

## Acceptance Criteria
**Feature is complete when:**
- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [Criterion 3]
- [ ] All tests pass
- [ ] Documentation updated
- [ ] PROGRESS_AND_TODO.md updated

## Alternatives Considered
**Other approaches:**
1. [Alternative 1] - Pros: ___ | Cons: ___
2. [Alternative 2] - Pros: ___ | Cons: ___

**Why this approach?**
[Rationale for chosen approach]

## Additional Context
[Screenshots, mockups, examples, or other relevant information]

## Priority
**User priority:**
- [ ] Must have - Critical for operations
- [ ] Should have - Important but not blocking
- [ ] Nice to have - Quality of life improvement
- [ ] Future - Low priority

**Project Manager assessment:**
[PM to fill in: feasibility, timeline, dependencies]

---
**Remember:** Use WHO tags in all comments on this issue!
