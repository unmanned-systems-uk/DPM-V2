# Architecture Documentation Update Rules

**WHO:** CC-PM
**Date:** 2025-11-14
**Time:** 22:00 UTC
**Purpose:** Maintain architectural evolution history and enable PM master doc integration

---

## 🎯 Core Principle: DEPRECATE, Don't Delete

**Never delete deprecated architecture sections.** Comment them out to preserve system evolution history.

---

## 📋 Rule: Architecture Documentation Updates

### When Updating Architecture Documentation:

#### 1. Comment Out Deprecated Sections

**Format:**
```markdown
<!-- DEPRECATED: YYYY-MM-DD by WHO
     Reason: [Why this approach was replaced]
     Superseded by: [Reference to new section]

## [Old Section Title]

[Old architecture content preserved here...]
-->
```

**Example:**
```markdown
<!-- DEPRECATED: 2025-11-14 by CC-SystemTools
     Reason: File-based polling inefficient, no real-time capability
     Superseded by: § 3.2 Tri-Domain Log Aggregation (below)

## 3.1 File-Based Log Collection

### Architecture
Logs were collected by:
1. Polling log files every 5 minutes
2. Manual transfer via SCP
3. Local storage and review

### Limitations
- No real-time monitoring
- Manual intervention required
- 5-minute lag minimum
-->
```

#### 2. Add WHO/Date/Time Stamps to New Sections

**Format:**
```markdown
## [New Section Title]

**WHO:** CC-[Domain]
**Date:** YYYY-MM-DD
**Time:** HH:MM UTC
**Supersedes:** [What this replaces]
**Related Issue:** #[issue number]

### Architecture
[New architecture content...]
```

**Example:**
```markdown
## 3.2 Tri-Domain Log Aggregation

**WHO:** CC-SystemTools
**Date:** 2025-11-14
**Time:** 21:00 UTC
**Supersedes:** § 3.1 File-Based Log Collection
**Related Issue:** #74

### Architecture

Real-time log streaming from Air-Side (UDP) and Ground-Side (TCP) to SystemTools:

- **Air-Side → SystemTools:** UDP port 5007, always-on
- **Ground-Side → SystemTools:** TCP port 5008, always-on
- **Format:** JSON structured logs
- **Display:** Color-coded by domain (Blue [AIR], Magenta [GROUND])
```

#### 3. Create Architecture Update Issue

**Required for EVERY architecture documentation change.**

**Issue Template:**

**Title Format:**
```
[ARCHITECTURE][DOMAIN] Brief Description of Change
```

**Labels:**
- `architecture` (required)
- `{domain}` (air-side, ground-side, systemtools, or all-domains)
- `documentation` (required)

**Body Template:**
```markdown
## Architecture Change Summary

**Domain:** [Air-Side/Ground-Side/SystemTools/All-Domains]
**Component:** [Logging/Networking/Camera/etc.]
**Type:** [New Feature/Replacement/Enhancement/Deprecation]

## What Changed

[Brief description of architectural change]

## Deprecated

- **Old Approach:** [Description of what was deprecated]
- **Location in Docs:** [File path and section number/title]
- **Reason for Deprecation:** [Why it was replaced]

## New Architecture

- **New Approach:** [Description of new architecture]
- **Location in Docs:** [File path and section number/title]
- **Benefits:** [Why this is better - bullet points]

## Documentation Updates

- [ ] Domain-specific architecture doc updated
- [ ] Deprecated sections commented out with WHO/Date
- [ ] New sections added with WHO/Date/Time stamps
- [ ] PM notified for master architecture doc integration

## Files Modified

- `docs/[domain]/[file].md`
- [Other relevant documentation files]

## Related Issues

- Supersedes: #[old issue if applicable]
- Implements: #[feature issue that drove this change]
- Depends on: #[blocking issues if any]

---

**WHO:** CC-[Domain]
**Date:** YYYY-MM-DD
**Time:** HH:MM UTC
```

---

## 🔄 Workflow

### For Domain Agents (Air-Side, Ground-Side, SystemTools):

**When updating architecture documentation:**

1. **Edit Documentation:**
   ```bash
   # Open domain architecture doc
   vim docs/[domain]/architecture.md
   ```

2. **Comment Out Deprecated Section:**
   - Use `<!-- DEPRECATED: ... -->` format
   - Include WHO, Date, Reason, Superseded by

3. **Add New Section:**
   - Include WHO/Date/Time stamps
   - Reference what it supersedes
   - Include related issue number

4. **Create Architecture Update Issue:**
   ```bash
   gh issue create \
     --title "[ARCHITECTURE][DOMAIN] Description" \
     --body-file architecture_update_template.md \
     --label "architecture,{domain},documentation"
   ```

5. **Notify PM:**
   - Add comment to issue: `@CC-PM Architecture documentation updated. Please integrate into master docs.`
   - PM will be automatically notified via architecture label

### For PM (Project Manager):

**Monitoring Architecture Changes:**

1. **Daily Check:**
   ```bash
   gh issue list --label architecture --state open
   ```

2. **Review Process:**
   - Read architecture update issue
   - Review domain-specific doc changes
   - Verify deprecated sections properly commented
   - Verify new sections have WHO/Date/Time stamps

3. **Master Doc Integration:**
   - Update `docs/architecture/SOFTWARE_ARCHITECTURE_DOCUMENT.md`
   - Update `docs/ALL_DOMAINS/INTEGRATION_POINTS.md` (if applicable)
   - Cross-reference domain-specific changes
   - Maintain architectural evolution timeline

4. **Close Issue:**
   ```bash
   gh issue close [number] --comment "Integrated into master architecture docs: [commit hash]"
   ```

---

## 📁 Documentation Structure

### Domain-Specific Architecture Docs:
```
docs/
├── air-side/
│   └── architecture.md          # Air-Side specific
├── ground-side/
│   └── architecture.md          # Ground-Side specific
├── systemtools/
│   └── architecture.md          # SystemTools specific
└── architecture/
    ├── SOFTWARE_ARCHITECTURE_DOCUMENT.md  # Master doc (PM-maintained)
    └── view-context.md          # System-wide views
```

### Update Flow:
1. Domain updates `docs/{domain}/architecture.md`
2. Domain creates architecture update issue
3. PM integrates into `docs/architecture/SOFTWARE_ARCHITECTURE_DOCUMENT.md`

---

## ✅ Benefits

1. **Preserved History:**
   - Can see what approaches were tried
   - Understand why decisions were made
   - Avoid repeating failed patterns

2. **PM Tracking:**
   - Architecture label provides clear signal
   - Easy to find what needs master doc integration
   - No changes slip through unnoticed

3. **Accountability:**
   - WHO stamps show who made changes
   - Date/Time stamps show when
   - Clear evolution timeline

4. **Master Doc Accuracy:**
   - PM knows exactly what changed
   - Can integrate with full context
   - Master docs stay synchronized

5. **Future Sessions:**
   - Claude Code can see architectural evolution
   - Understand rationale for current design
   - Learn from deprecated approaches

---

## 🚨 Critical Notes

1. **NEVER delete deprecated sections** - Always comment out
2. **ALWAYS create architecture update issue** - No exceptions
3. **ALWAYS include WHO/Date/Time stamps** - Mandatory for new sections
4. **ALWAYS notify PM** - Tag issue with architecture label
5. **ALWAYS explain superseding** - Future sessions need context

---

## 📋 Quick Reference Checklist

**Before committing architecture doc changes:**

- [ ] Deprecated sections commented out (not deleted)
- [ ] DEPRECATED tag includes: WHO, Date, Reason, Superseded by
- [ ] New sections include: WHO, Date, Time, Supersedes, Related Issue
- [ ] Architecture update issue created
- [ ] Issue has correct labels: architecture, {domain}, documentation
- [ ] Issue body follows template
- [ ] PM notified via issue tag

**PM Integration Checklist:**

- [ ] Reviewed domain-specific changes
- [ ] Verified deprecation format correct
- [ ] Verified new section stamps present
- [ ] Updated master architecture document
- [ ] Committed master doc changes
- [ ] Closed architecture update issue with commit reference

---

## 🔗 Related Documents

- `.claude/PM_RULES_CRITICAL.md` - Rule 10: Architecture Documentation Updates
- `docs/architecture/SOFTWARE_ARCHITECTURE_DOCUMENT.md` - Master architecture doc
- `docs/ALL_DOMAINS/LESSONS_LEARNED.md` - Lessons from architectural changes

---

**Review this file before ANY architecture documentation update!**
