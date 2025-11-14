# ADR-[NUMBER]: [SHORT TITLE]

**Status:** [Proposed | Accepted | Deprecated | Superseded]
**Date:** [YYYY-MM-DD] (Initial decision)
**Updated:** [YYYY-MM-DD] (Last update, if applicable)
**Deciders:** [List key people/roles involved in decision]
**Related Issues:** [#issue-numbers]
**Related Views:** [References to architecture views, e.g., `view-logical.md`]
**Supersedes:** [ADR-XXX if this replaces a previous decision]
**Superseded By:** [ADR-XXX if this has been replaced]

---

## Context

[Describe the forces at play, including technological, political, social, and project local. This is the "why" behind the decision.]

**Problem Statement:**
[What problem are we trying to solve? What is the current situation that requires a decision?]

**Key Requirements:**
1. [Requirement 1]
2. [Requirement 2]
3. [Requirement 3]

**Key Constraints:**
- [Constraint 1]: [Description]
- [Constraint 2]: [Description]

**Assumptions:**
- [Assumption 1]
- [Assumption 2]

---

## Decision

[State the architectural decision clearly and concisely. This should be actionable and specific.]

**We will [DECISION STATEMENT]**

**Rationale:**
[Why this decision was chosen. What factors led to this choice?]

**Implementation Details:**
- [Detail 1]: [Description]
- [Detail 2]: [Description]

**Scope:**
- **In Scope:** [What this decision applies to]
- **Out of Scope:** [What this decision does NOT apply to]

---

## Alternatives Considered

### Alternative 1: [Name]

**Approach:**
[Describe the alternative approach]

**Pros:**
- ✅ [Benefit 1]
- ✅ [Benefit 2]

**Cons:**
- ❌ [Drawback 1]
- ❌ [Drawback 2]

**Rejection Reason:**
[Why this alternative was not chosen]

---

### Alternative 2: [Name]

**Approach:**
[Describe the alternative approach]

**Pros:**
- ✅ [Benefit 1]
- ✅ [Benefit 2]

**Cons:**
- ❌ [Drawback 1]
- ❌ [Drawback 2]

**Rejection Reason:**
[Why this alternative was not chosen]

---

### Alternative 3: [Name]

[Add more alternatives as needed. It's important to show that multiple options were considered.]

---

## Consequences

### Positive Consequences

**Benefits:**
- ✅ [Benefit 1]: [Description and impact]
- ✅ [Benefit 2]: [Description and impact]

**Enables:**
- [What this decision enables or makes possible]

**Quality Attributes Improved:**
- [Performance | Reliability | Maintainability | etc.]: [How improved]

---

### Negative Consequences

**Costs:**
- ⚠️ [Cost 1]: [Description and impact]
- ⚠️ [Cost 2]: [Description and impact]

**Technical Debt:**
- [Any technical debt incurred by this decision]

**Risks:**
- [Risk 1]: [Description and mitigation]
- [Risk 2]: [Description and mitigation]

**Quality Attributes Degraded:**
- [Attribute]: [How degraded and why acceptable]

---

### Neutral Consequences

**Trade-offs:**
- [Trade-off 1]: [What was traded for what]

**Dependencies:**
- [Dependency 1]: [What this decision depends on]

---

## Implementation

**Affected Components:**
- [Component 1]: [How affected]
- [Component 2]: [How affected]

**Implementation Steps:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Validation:**
- [How to verify this decision is properly implemented]

**Migration Path:**
[If this replaces an existing approach, describe how to migrate]

---

## Compliance and Verification

**Compliance Checks:**
- [ ] [Check 1]: [How to verify compliance]
- [ ] [Check 2]: [How to verify compliance]

**Monitoring:**
- [What metrics or indicators show this decision is working]

**Review Criteria:**
- [When/why this decision should be reviewed or reconsidered]

---

## References

**Supporting Documents:**
- [Document 1]: [Location]
- [Document 2]: [Location]

**External References:**
- [Reference 1]: [URL]
- [Reference 2]: [URL]

**Related ADRs:**
- [ADR-XXX]: [Relationship description]
- [ADR-YYY]: [Relationship description]

**Standards Applied:**
- [Standard 1]: [How applied]

---

## Notes

**Discussion Points:**
- [Key point from discussion 1]
- [Key point from discussion 2]

**Open Questions:**
- [Question 1]: [Status]
- [Question 2]: [Status]

**Future Considerations:**
- [What might cause this decision to be revisited]

---

## Document History

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| [YYYY-MM-DD] | 1.0 | [Name] | Initial ADR |
| [YYYY-MM-DD] | 1.1 | [Name] | [Update description] |

---

## ADR Metadata

**Category:** [Architecture | Infrastructure | Security | Performance | Integration | Data | UI/UX | DevOps]
**Impact:** [High | Medium | Low]
**Effort:** [High | Medium | Low]
**Reversibility:** [Easily Reversible | Reversible with Effort | Irreversible]

---

**Document End**

---

# Template Usage Guide

## When to Create an ADR

Create an ADR for decisions that:
- Affect the system's structure or architecture
- Have significant consequences (positive or negative)
- Are difficult to reverse
- Require stakeholder consensus
- Will affect multiple teams or components
- Involve significant trade-offs

**Do NOT create ADRs for:**
- Routine implementation decisions
- Decisions easily reversed
- Obvious or trivial choices
- Decisions with no architectural impact

---

## ADR Numbering

- Use sequential numbers: ADR-001, ADR-002, etc.
- Never reuse numbers, even if an ADR is deprecated
- Maintain chronological order by decision date

---

## ADR Status Values

- **Proposed:** Decision is under discussion, not yet accepted
- **Accepted:** Decision has been approved and is being implemented
- **Deprecated:** Decision no longer applies but remains for historical context
- **Superseded:** Decision has been replaced by a newer ADR (reference it)

---

## Writing Quality Guidelines

**Context Section:**
- Provide enough background for future readers unfamiliar with the situation
- Include constraints and assumptions
- Reference related issues or documents

**Decision Section:**
- Be specific and actionable
- Avoid ambiguity
- State clearly what WILL be done

**Alternatives Section:**
- Show at least 2-3 alternatives considered
- Be fair to alternatives (don't strawman)
- Clearly state rejection reasons

**Consequences Section:**
- Be honest about both positive and negative impacts
- Consider long-term consequences
- Think about maintainability, evolution, and team impact

---

## Example ADR Filenames

- `ADR-001-three-domain-architecture.md`
- `ADR-015-use-postgresql-for-persistence.md`
- `ADR-027-adopt-microservices-pattern.md`

Use lowercase, hyphenated titles that are descriptive.

---

## Review Checklist

Before finalizing an ADR, verify:
- [ ] Problem/context is clear
- [ ] Decision is stated explicitly
- [ ] At least 2 alternatives are documented
- [ ] Consequences (positive and negative) are identified
- [ ] Implementation impact is described
- [ ] References are complete
- [ ] Status is appropriate
- [ ] Related issues/ADRs are linked
