# Issue Consolidation Guide - PM Workflow

**WHO:** CC-Project-Manager

**Purpose:** Systematic detection and consolidation of overlapping/duplicate issues

**Status:** Active (Step 4 of PM Session Checklist)

**Related:** CCPM PM Confidence-Based Autonomy System

---

## Overview

During PM sessions, systematically detect overlapping or duplicate issues across all domains and consolidate them to maintain a clean, clear issue tracker for domain teams.

**Why this matters:**
- Prevents workflow confusion (which issue to track work against?)
- Reduces duplicate effort (don't investigate same problem twice)
- Maintains single source of truth per problem
- Applies Historical Learning System (Issue #37 - catch duplicates early)

---

## When This Runs

**Frequency:** Every PM session start (Step 4 of PM checklist)

**Timing:** Start-of-day and EOD PM sessions
- PM does consolidation during coordination windows
- Domains see clean issues when they start work
- GitHub notifications automatic

**Duration:** 5-10 minutes per PM session

**Expected finds:** 1-3 overlapping issue pairs per week (based on historical rate)

---

## Process Overview

**5-Phase Process:**
1. **Detection** (2-3 min) - Find potentially overlapping issues
2. **Review** (2-3 min) - Evaluate each flagged pair
3. **Decision** (1-2 min) - Use 15 criteria to score and recommend
4. **User Approval** (1 min) - Ask user if confident <90%
5. **Execute & Log** (2-3 min) - Close duplicate, log decision to CCPM

---

## Phase 1: Automated Detection

### Commands to Run

```bash
# Get all open issues
gh issue list --state open --limit 50 --json number,title,labels,createdAt

# Review for patterns manually or grep for keywords
gh issue list --state open | grep -i "focus"
gh issue list --state open | grep -i "camera"
```

### Detection Heuristics

**1. Title Keyword Overlap**
- Extract key nouns from titles (focus, AF Hold, camera, network, etc.)
- Flag if 2+ issues share 2+ keywords
- Example: "focus distance" appears in #1 and #42

**2. Label Overlap with Similar Titles**
- Same domain label (air-side) + similar title words
- Example: Both #2 and #41 have `air-side` + mention "AF Hold"

**3. Related Issue Mentions**
- Check if issues reference each other in comments
- "Related to #X" or "Duplicate of #Y"

**4. Age Gap Pattern**
- Old issue (auto-imported, early days) + new issue (recent, detailed)
- Often indicates duplicate with better scoping

**Output:** List of potentially overlapping issue pairs

Example:
```
Potential Overlaps Detected:
- Issues #1, #42: Both mention "focus distance" (air-side)
- Issues #2, #41: Both mention "AF Hold" (air-side)
```

---

## Phase 2: Manual Review

For each flagged pair, PM reviews:

1. **Read both issue titles and descriptions**
2. **Check for:**
   - Same problem scope?
   - Same component/area?
   - One issue more detailed than other?
   - One issue has work done (investigation, code, testing)?
   - Different priorities (CRITICAL vs MEDIUM)?

3. **Classify:**
   - **Duplicate:** Same problem → consolidate
   - **Related but separate:** Different aspects → keep both, link them
   - **False positive:** Different problems → ignore

---

## Phase 3: Consolidation Decision Using 15 Criteria

### Criteria Framework

**Which issue to keep?** Score both issues using 15 criteria:

#### Category 1: Work & Progress (40% weight)

**1. work_done (weight: 0.25)**
- Investigation completed
- Code implemented
- Testing performed
- Documentation written
- Score: 0.0 (none) → 1.0 (comprehensive)

**2. testing_status (weight: 0.10)**
- Has test plan
- Tests written
- Tests passing
- Coverage documented
- Score: 0.0 (no tests) → 1.0 (comprehensive testing)

**3. documentation_quality (weight: 0.05)**
- README updated
- Code comments
- User-facing docs
- Architecture docs
- Score: 0.0 (none) → 1.0 (comprehensive)

---

#### Category 2: Issue Quality (25% weight)

**4. priority (weight: 0.15)**
- CRITICAL = 1.0
- HIGH = 0.75
- MEDIUM = 0.5
- LOW = 0.25
- NONE = 0.0

**5. detail (weight: 0.10)**
- Problem description depth
- Reproduction steps
- Expected vs actual behavior
- Context provided
- Score: 0.0 (minimal) → 1.0 (comprehensive)

---

#### Category 3: Structure & Metadata (20% weight)

**6. structure (weight: 0.08)**
- Uses issue template
- Has acceptance criteria
- Labels present
- Milestone assigned
- Score: 0.0 (unstructured) → 1.0 (template-compliant)

**7. status_clarity (weight: 0.07)**
- Current state documented
- BLOCKED/IN PROGRESS/TESTING clear
- Blockers identified
- Next steps defined
- Score: 0.0 (unclear) → 1.0 (crystal clear)

**8. affected_component (weight: 0.05)**
- Component identified
- Code area specified
- Architecture layer noted
- Dependencies listed
- Score: 0.0 (unknown) → 1.0 (fully specified)

---

#### Category 4: Activity & Timeliness (10% weight)

**9. recent_activity (weight: 0.05)**
- Comments in last 7 days = 1.0
- Comments in last 30 days = 0.75
- Comments in last 90 days = 0.5
- Older = 0.25
- No activity = 0.0

**10. recency (weight: 0.05)**
- Created in last 7 days = 1.0
- Created in last 30 days = 0.75
- Created in last 90 days = 0.5
- Older but referenced = 0.25
- Stale = 0.0

---

#### Category 5: Cross-Domain (5% weight)

**11. requester (weight: 0.02)**
- Project owner = 1.0
- Domain lead = 0.8
- Contributor = 0.6
- External = 0.4

**12. cross_domain_impact (weight: 0.03)**
- Multiple domains affected = 1.0
- Single domain + dependencies = 0.7
- Single domain isolated = 0.3

---

#### Category 6: Technical Context (bonus)

**13. root_cause_identified (weight: 0.02)**
- Root cause analysis complete = 1.0
- Theory documented = 0.7
- Investigation ongoing = 0.4
- Unknown = 0.0

**14. regression_vs_new (weight: 0.02)**
- Regression (was working) = 1.0
- Never worked (blocked) = 0.6
- New feature = 0.4
- Enhancement = 0.2

**15. reversibility (weight: 0.01)**
- Changes reversible = 1.0
- Partially reversible = 0.5
- Irreversible = 0.0

---

### Scoring Example

**Issue #42 vs Issue #1 (focus distance readback)**

**Issue #42 scores:**
```
work_done: 1.0          (investigation complete)
testing_status: 0.4     (theory, no tests yet)
documentation_quality: 0.7  (issue well-documented)
priority: 0.75          (HIGH)
detail: 1.0             (comprehensive)
structure: 1.0          (template-compliant)
status_clarity: 1.0     (BLOCKED clearly stated)
affected_component: 1.0 (camera_sony.cpp specified)
recent_activity: 1.0    (active)
recency: 1.0            (recent)
requester: 1.0          (project owner)
cross_domain_impact: 0.3 (air-side only)
root_cause_identified: 0.7 (LiveView theory)
regression_vs_new: 0.6  (never worked)
reversibility: 1.0      (just investigation)

Weighted Score: 0.88
```

**Issue #1 scores:**
```
work_done: 0.0          (no work)
testing_status: 0.0     (no tests)
documentation_quality: 0.2  (minimal)
priority: 1.0           (CRITICAL)
detail: 0.2             (minimal description)
structure: 0.3          (old format)
status_clarity: 0.0     (unclear)
affected_component: 0.5 (focus mentioned, not specific)
recent_activity: 0.0    (closed, no activity)
recency: 0.0            (old, auto-imported)
requester: 0.6          (contributor)
cross_domain_impact: 0.3 (air-side only)
root_cause_identified: 0.0 (unknown)
regression_vs_new: 0.0  (unclear)
reversibility: 1.0      (no work done)

Weighted Score: 0.31
```

**Conclusion:** Keep #42, close #1 (score: 0.88 vs 0.31)

---

## Phase 4: User Approval

### PM Asks User (If Confidence <90%)

```
PM: "Issue Consolidation Detected

Issue #1 vs Issue #42 (both: focus distance readback)

Analysis:
- #42 has investigation work completed (score: 1.0)
- #42 has detailed analysis (score: 1.0)
- #42 specifies affected component camera_sony.cpp (score: 1.0)
- #1 has no work done, minimal detail (scores: 0.0, 0.2)

Weighted Scores: #42 = 0.88, #1 = 0.31

Recommendation: Keep #42, close #1 with reference

PM Confidence: 65% (bootstrap phase, 3/10 decisions)

Approve? [Y/N]"
```

### Autonomous Action (If Confidence ≥90%)

```
PM: "Issue Consolidation - Autonomous Action

Closed Issue #1 as duplicate of #42

Rationale:
- Weighted scores: #42=0.88, #1=0.31
- #42 has investigation complete, #1 has no work
- Both about focus distance readback

PM Confidence: 92% (23/25 decisions approved)

Action is reversible - can reopen #1 if needed.

See consolidation comment: [GitHub URL]"
```

---

## Phase 5: Execute & Log

### 5a. Close Duplicate Issue

**Add comment to issue being closed:**

```markdown
**WHO:** CC-Project-Manager

## Issue Consolidation - Closing as Duplicate

This issue overlaps with Issue #42: Focus distance readback not working.

Closing in favor of #42 because:
- #42 has investigation work completed
- #42 has higher detail (comprehensive analysis)
- #42 specifies affected component (camera_sony.cpp)
- #42 has BLOCKED status clearly documented

**What this issue contributed:**
- Identified focus distance as CRITICAL priority

**All future work should reference Issue #42.**

Consolidation detected during PM session startup (Step 4 of PM checklist).

**Weighted Scores:** #42=0.88, #1=0.31 (15 criteria framework)
**PM Confidence:** 65% (bootstrap phase)
**User Approval:** APPROVED
```

**Close the issue:**
```bash
gh issue close 1 --comment "[comment above]"
```

---

### 5b. Add Reference to Issue Being Kept

**Add comment to primary issue:**

```markdown
**WHO:** CC-Project-Manager

## Related Issue Reference

Note: Issue #1 was a duplicate/overlapping issue that has been closed.

Issue #1 identified this as CRITICAL priority, which is noted.

All work continues here in #42.
```

---

### 5c. Log Decision to CCPM Training Data

**Append to:** `/home/anthony/cc-project-management/model-training-data/pm-decisions/issue-consolidation/decisions.jsonl`

```json
{
  "domain": "pm-decisions",
  "decision_type": "issue_consolidation",
  "decision_id": "IC-2025-11-09-001",
  "timestamp": "2025-11-09T10:30:00Z",
  "context": {
    "issue_a": 42,
    "issue_b": 1,
    "domain": "air-side",
    "keywords_overlap": ["focus", "distance", "readback"],
    "age_gap_days": 180
  },
  "pm_analysis": {
    "criteria_scores": {
      "work_done": {"a": 1.0, "b": 0.0, "weight": 0.25},
      "testing_status": {"a": 0.4, "b": 0.0, "weight": 0.10},
      "documentation_quality": {"a": 0.7, "b": 0.2, "weight": 0.05},
      "priority": {"a": 0.75, "b": 1.0, "weight": 0.15},
      "detail": {"a": 1.0, "b": 0.2, "weight": 0.10},
      "structure": {"a": 1.0, "b": 0.3, "weight": 0.08},
      "status_clarity": {"a": 1.0, "b": 0.0, "weight": 0.07},
      "affected_component": {"a": 1.0, "b": 0.5, "weight": 0.05},
      "recent_activity": {"a": 1.0, "b": 0.0, "weight": 0.05},
      "recency": {"a": 1.0, "b": 0.0, "weight": 0.05},
      "requester": {"a": 1.0, "b": 0.6, "weight": 0.02},
      "cross_domain_impact": {"a": 0.3, "b": 0.3, "weight": 0.03},
      "root_cause_identified": {"a": 0.7, "b": 0.0, "weight": 0.02},
      "regression_vs_new": {"a": 0.6, "b": 0.0, "weight": 0.02},
      "reversibility": {"a": 1.0, "b": 1.0, "weight": 0.01}
    },
    "weighted_score": {"a": 0.88, "b": 0.31},
    "recommendation": "keep_a_close_b",
    "reasoning": [
      "#42 has investigation work completed",
      "#42 has more detailed analysis",
      "#42 has BLOCKED status properly documented",
      "#42 specifies affected component (camera_sony.cpp)",
      "#1 already closed with no work done",
      "#1 has minimal detail and unclear status"
    ]
  },
  "pm_confidence_metadata": {
    "confidence_before_decision": 0.65,
    "asked_user": true,
    "threshold_at_time": "transitional"
  },
  "user_response": {
    "decision": "APPROVED",
    "feedback": "Correct - #42 is clearly better"
  },
  "outcome": {
    "action_taken": "CLOSED issue #1 with reference to #42",
    "reversible": true,
    "github_urls": [
      "https://github.com/unmanned-systems-uk/DPM-V2/issues/1",
      "https://github.com/unmanned-systems-uk/DPM-V2/issues/42"
    ]
  },
  "learning_metadata": {
    "confidence_after_decision": 0.68,
    "total_decisions_to_date": 4,
    "approved_decisions_to_date": 4,
    "notes": "First decision with full 15 criteria framework"
  }
}
```

---

### 5d. Update Confidence History

**Append to:** `/home/anthony/cc-project-management/model-training-data/pm-decisions/issue-consolidation/confidence-history.csv`

```csv
2025-11-09T10:30:00,IC-2025-11-09-001,issue_consolidation,4,4,1.00,transitional,APPROVED,"Full 15 criteria - user approved"
```

---

### 5e. Commit to CCPM Repo

```bash
cd /home/anthony/cc-project-management
git add model-training-data/pm-decisions/issue-consolidation/
git commit -m "[ML][DATA] Log PM decision IC-2025-11-09-001 - Issue consolidation

Logged issue consolidation decision (#42 vs #1).

User approved: Keep #42, close #1
Weighted scores: #42=0.88, #1=0.31 (15 criteria)
Confidence after: 100% (4/4 approved in bootstrap phase)

🚀 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"

git push origin main
```

---

## Confidence-Based Autonomy

### Bootstrap Phase (First 10 Decisions)

**Behavior:** Always ask user before action

**Why:** Need baseline approval rate before granting autonomy

**Current:** Decisions 1-10

---

### Supervised Phase (Confidence <75%)

**Behavior:** Always ask user before action

**Message:** "PM Confidence: 65% - Asking for approval"

---

### Transitional Phase (Confidence 75-89%)

**Behavior:** Ask user, but note PM confidence

**Message:** "PM Confidence: 82% - Fairly confident, but asking for approval"

---

### Semi-Autonomous Phase (Confidence 90-94%)

**Behavior:** Act autonomously, notify user after

**Message:** "PM Confidence: 92% - Acted autonomously (reversible). Approve retroactively? [Y/N]"

**Safety:** All actions reversible, user can override

---

### Fully Autonomous Phase (Confidence ≥95%)

**Behavior:** Fully autonomous, log for retrospective review

**Message:** "PM acted autonomously (95%+ confidence). See consolidation in Issue #X"

**Review:** User can audit in weekly retrospectives

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Overlap detection rate | 100% | PM catches all overlaps |
| Time to consolidation | <48 hours | From issue creation to consolidation |
| Consolidation accuracy | 90%+ | User approval rate |
| PM confidence growth | 75% by week 4 | Approval rate tracking |
| User workload reduction | 70% | Autonomous decisions / total |

---

## Common Patterns

### Pattern: Old Auto-Imported + New Detailed

**Example:** Issue #1 (old, minimal) + Issue #42 (new, detailed)

**Decision:** Almost always keep new detailed issue

**Criteria winners:** work_done, detail, structure, status_clarity, recency

---

### Pattern: Bug Report + Feature Request (Same Problem)

**Example:** Issue #2 (bug: AF Hold broken) + Issue #41 (feature: implement AF Hold)

**Decision:** Keep bug issue if has investigation, otherwise feature issue

**Criteria winners:** work_done, priority, root_cause_identified

---

### Pattern: Different Domains, Same Component

**Example:** Air-Side #10 (implementation) + Ground-Side #22 (UI)

**Decision:** Usually keep both, link them (not duplicates, different aspects)

**Criteria:** cross_domain_impact = 1.0 → separate issues

---

## Troubleshooting

### Issue: PM recommends wrong consolidation

**Symptom:** User rejects PM recommendation

**Cause:** Criteria weights don't match user preferences

**Solution:**
1. Review user feedback in decision log
2. Identify which criterion PM weighted wrong
3. Adjust weights in next decision
4. ML will learn from rejection

---

### Issue: False positive (not actually duplicates)

**Symptom:** Keyword overlap but different problems

**Example:** "focus distance" in camera vs "focus distance" in UI

**Solution:**
1. Check affected_component criterion
2. Use domain labels to distinguish
3. Mark as "not_duplicate" in decision log

---

### Issue: Confidence not increasing

**Symptom:** Stuck at 60-70% approval rate

**Cause:** PM criteria don't align with user priorities

**Solution:**
1. Error analysis (see USAGE_GUIDE.md Use Case #3)
2. Feature importance analysis
3. Ask user: "Which criteria should I weight more?"

---

## Related Documentation

**DPM-V2:**
- `docs/CC_READ_THIS_FIRST.md` - PM Session Checklist (Step 4)
- `docs/ALL_DOMAINS/LESSONS_LEARNED.md` - Consolidation patterns

**CCPM:**
- `model-training-data/README.md` - Dataset overview
- `model-training-data/USAGE_GUIDE.md` - ML usage examples
- `model-training-data/pm-decisions/issue-consolidation/schema.json` - Decision format
- `docs/pm-confidence-system/OVERVIEW.md` - System description
- `docs/pm-confidence-system/THOUGHT-PROCESS.md` - Genesis conversation

**CCPM Issues:**
- #72: Umbrella issue (PM Confidence-Based Autonomy System)
- #74: Repository structure
- #75: Schema design (15 criteria)
- #76: Confidence tracking algorithm

---

## Quick Reference

**15 Criteria Weights:**
```
Work & Progress (40%):     work_done=0.25, testing=0.10, docs=0.05
Issue Quality (25%):       priority=0.15, detail=0.10
Structure & Metadata (20%): structure=0.08, status=0.07, component=0.05
Activity & Time (10%):     recent_activity=0.05, recency=0.05
Cross-Domain (5%):         requester=0.02, cross_domain=0.03
Technical Context (bonus): root_cause=0.02, regression=0.02, reversible=0.01
```

**Confidence Thresholds:**
- <75%: Always ask
- 75-89%: Ask with confidence note
- 90-94%: Act, notify after
- 95%+: Fully autonomous

**Files to Update:**
- CCPM: `decisions.jsonl`, `confidence-history.csv`
- DPM-V2: GitHub issues (close with comments)

---

**Document Version:** 1.0.0
**Last Updated:** 2025-11-09
**Author:** CC-Project-Manager (DPM-V2)
**Status:** Active - Ready for first PM session execution
