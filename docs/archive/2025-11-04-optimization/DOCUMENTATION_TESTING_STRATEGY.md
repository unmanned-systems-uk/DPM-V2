# Documentation Testing Strategy
*Ensuring optimized structure works effectively with Claude Code*

## Test Objectives
1. Verify context usage reduction (target: <50% of previous)
2. Ensure all critical information is accessible
3. Validate domain separation effectiveness
4. Test quick navigation to specific information
5. Confirm no loss of essential project knowledge

---

## Test 1: Context Usage Comparison

### Before Optimization
```
Files loaded:
- CC_READ_THIS_FIRST.md: 1977 lines
- SystemTools/PROGRESS_AND_TODO.md: 896 lines
- Total: 2873 lines
```

### After Optimization
```
Files loaded:
- CC_READ_THIS_FIRST.md: 137 lines
- Domain-specific TODO: ~150 lines (estimated)
- Total: ~287 lines
```

**Expected Result:** 90% reduction in initial context load

---

## Test 2: Domain-Specific Session Start

### Test Scenarios

#### A. Air-Side Session
```
User: START AIR
Expected Claude behavior:
1. Read CC_READ_THIS_FIRST.md (137 lines)
2. Navigate to sbc/docs/PROGRESS_AND_TODO.md
3. Check protocol/commands.json for air-side items
4. Ready to work with <300 lines context
```

#### B. Ground-Side Session
```
User: START GROUND
Expected Claude behavior:
1. Read CC_READ_THIS_FIRST.md (137 lines)
2. Navigate to android/docs/PROGRESS_AND_TODO.md
3. Check protocol/camera_properties.json for ground-side items
4. Ready to work with <300 lines context
```

#### C. SystemTools Session
```
User: START TOOLS
Expected Claude behavior:
1. Read CC_READ_THIS_FIRST.md (137 lines)
2. Navigate to SystemTools/PROGRESS_AND_TODO.md
3. Understand 10 functional tabs available
4. Ready to work with <300 lines context
```

---

## Test 3: Information Retrieval Speed

### Quick Access Tests

| Query | Expected Location | Target Time |
|-------|------------------|-------------|
| "What port for commands?" | CC_READ_THIS_FIRST.md line 47 | <5 seconds |
| "Git commit format?" | CC_READ_THIS_FIRST.md line 74 | <5 seconds |
| "Air-side build command?" | CC_READ_THIS_FIRST.md line 99 | <5 seconds |
| "Current air-side tasks?" | docs/AIR_SIDE/TODO.md | <10 seconds |
| "Integration issues?" | docs/ALL_DOMAINS/BLOCKERS.md | <10 seconds |

---

## Test 4: Cross-Domain Work

### Scenario: Implementing new camera property
```
1. Check docs/ALL_DOMAINS/INTEGRATION_POINTS.md
2. Implement in air-side (docs/AIR_SIDE/)
3. Implement in ground-side (docs/GROUND_SIDE/)
4. Update integration status
```

**Success Criteria:**
- Can track implementation across domains
- No duplication of information
- Clear synchronization status

---

## Test 5: New Developer Onboarding

### Test Process
1. Start with only CC_READ_THIS_FIRST.md
2. Follow structure to understand project
3. Time to productive work

**Target:** <15 minutes to understand and start contributing

---

## Validation Checklist

### Essential Information Preserved
- [ ] Quick start commands work
- [ ] Network configuration accessible
- [ ] Git workflow clear
- [ ] Domain separation understood
- [ ] Protocol location known
- [ ] Build commands available

### Navigation Efficiency
- [ ] Can find any information in <3 jumps
- [ ] Domain docs clearly separated
- [ ] Master status provides overview
- [ ] No circular references

### Context Efficiency
- [ ] Initial load <200 lines
- [ ] Working session <500 lines total
- [ ] Can complete tasks without overload
- [ ] Incremental loading works

---

## Test Execution Plan

### Phase 1: Structure Test (Now)
1. ✅ Verify CC_READ_THIS_FIRST.md is 137 lines
2. Simulate START commands
3. Check navigation paths

### Phase 2: Content Migration (Next)
1. Split PROGRESS_AND_TODO files
2. Create domain folders
3. Test domain isolation

### Phase 3: Real Usage (After Migration)
1. Perform actual development task
2. Measure context usage
3. Track time to complete
4. Gather feedback

---

## Success Metrics

| Metric | Target | Actual |
|--------|--------|--------|
| CC_READ_THIS_FIRST.md size | <200 lines | ✅ 137 lines |
| Context reduction | >50% | Pending |
| Time to find info | <10 sec | Pending |
| Domain separation | Clear | Pending |
| No information loss | 100% | Pending |

---

## Rollback Plan
If testing reveals issues:
1. Original files backed up as *.backup
2. Can restore with: `cp *.backup *.md`
3. Git history preserves all versions
4. Incremental improvements possible

---

*This testing strategy ensures the optimized structure maintains functionality while dramatically reducing context overhead.*