# Pull Request

## Description

<!-- Provide a clear and concise description of your changes -->

**What changed:**


**Why this change was needed:**


**Related Issues:**
<!-- Link related issues using #issue-number -->
Fixes #
Related to #

---

## Type of Change

<!-- Check all that apply -->

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Refactoring (code improvement without behavior change)
- [ ] Documentation update
- [ ] Testing (new or updated tests)

---

## Domain Impact

<!-- Check all domains affected by this PR -->

- [ ] Air-Side (`sbc/` - C++, Pi 5)
- [ ] Ground-Side (`android/` - Kotlin, H16)
- [ ] Protocol (`docs/protocol/` - JSON specifications)
- [ ] Tools/Dev-Side (`SystemTools/` - Python)
- [ ] Documentation (`docs/`)
- [ ] Workflow (`.github/`, development process)

---

## Documentation Updates

<!-- ⚠️ REQUIRED: Code changes MUST include documentation updates -->

### General Documentation

- [ ] Code comments added/updated for complex logic
- [ ] Architecture documentation updated (if component structure changed)
- [ ] C4 diagrams updated (if components added/removed)
- [ ] ADRs updated (if architectural decisions changed)
- [ ] Traceability matrices updated (if component→code mapping changed)
- [ ] Glossary updated (if new terms introduced)
- [ ] Cross-references validated (no broken links)

### Domain-Specific Documentation

#### If Air-Side Changed (`sbc/`)

- [ ] Updated `docs/architecture/view-logical.md` Section 4.2.3 (component structure)
- [ ] Updated `docs/architecture/view-deployment.md` (if Docker/Pi 5 config changed)
- [ ] Updated `docs/architecture/c4-level3-air-side-components.puml` (if components added/removed)
- [ ] Updated relevant ADR(s): ADR-001, ADR-004, ADR-006, ADR-007, ADR-012
- [ ] Updated SAD Section 8.3 traceability matrix (if component→code mapping changed)

#### If Ground-Side Changed (`android/`)

- [ ] Updated `docs/architecture/view-logical.md` Section 4.2.4 (MVVM layers)
- [ ] Updated `docs/architecture/c4-level3-ground-side-components.puml` (if layers added)
- [ ] Updated relevant ADR(s): ADR-005, ADR-013, ADR-014
- [ ] Updated UI documentation in `view-logical.md` (if screens added)

#### If Protocol Changed (`docs/protocol/`)

<!-- ⚠️ CRITICAL: Protocol changes affect BOTH Air-Side AND Ground-Side -->

- [ ] Updated `docs/protocol/commands.json` or `docs/protocol/camera_properties.json`
- [ ] Updated PropertyLoader in C++ (`sbc/src/property_loader.cpp`) - **MANDATORY**
- [ ] Updated PropertyLoader in Kotlin (`android/.../PropertyLoader.kt`) - **MANDATORY**
- [ ] Verified Air-Side and Ground-Side synchronization (tested both domains)
- [ ] Updated `docs/architecture/view-integration.md` (protocol patterns)
- [ ] Updated ADR-002 (if Specification-First pattern changed)
- [ ] Updated ADR-003 (if TCP/UDP protocol changed)

#### If Tools/Dev-Side Changed (`SystemTools/`)

- [ ] Updated `SystemTools/README.md` (usage instructions)
- [ ] Updated `docs/architecture/view-logical.md` Section 4.2.5 (tool components)
- [ ] Updated `docs/architecture/c4-level3-dev-tools-components.puml`

### Architecture Impact Assessment

**Does this PR change the architecture?**
<!-- Check one -->

- [ ] No architecture impact (bug fix, minor enhancement)
- [ ] Minor architecture impact (new component within existing pattern)
- [ ] Major architecture impact (new pattern, technology, or cross-domain change)

**If major architecture impact:**

- [ ] Created new ADR documenting the decision
- [ ] Updated relevant architecture views
- [ ] Updated C4 diagrams at appropriate levels
- [ ] Updated SAD summary sections

---

## Testing

<!-- Describe testing performed -->

### Test Coverage

- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed
- [ ] Tested on target hardware (if applicable)

### Test Description

**What was tested:**


**Test results:**


**Test environment:**
<!-- e.g., Pi 5, H16, development machine -->


---

## Checklist

<!-- Complete before requesting review -->

### Before Submitting

- [ ] Code follows project style guidelines (see `CONTRIBUTING.md`)
- [ ] Self-review of code completed
- [ ] Comments added for complex/non-obvious code
- [ ] No new compiler warnings introduced
- [ ] Commit messages follow format: `[DOMAIN][TYPE] Description`
- [ ] All automated checks passing (CI/CD green)

### Documentation Completeness

- [ ] I have updated ALL required documentation per domain (see above)
- [ ] I have validated cross-references (no broken links)
- [ ] I have reviewed `docs/DOCUMENTATION_UPDATE_GUIDE.md` for guidance
- [ ] If unsure about documentation requirements, I asked in PR comments

### Review Readiness

- [ ] PR title follows format: `[DOMAIN][TYPE] Description`
- [ ] PR description is clear and complete
- [ ] Related issues are linked
- [ ] Ready for code review

---

## Additional Notes

<!-- Any additional information for reviewers -->


---

## For Reviewers

### Documentation Review Checklist

- [ ] Code changes are clear and well-tested
- [ ] Architecture documentation updated if component structure changed
- [ ] C4 diagrams updated if components added/removed
- [ ] ADRs updated if decisions changed
- [ ] Traceability matrices updated if mappings changed
- [ ] Cross-references are valid (no broken links)
- [ ] Domain-specific requirements met (see CONTRIBUTING.md)
- [ ] All automated checks passed (CI/CD green)
- [ ] Documentation reads well (no obvious errors)
- [ ] Changes maintain ISO/IEC/IEEE 42010 compliance

---

**Documentation Guide:** See `docs/DOCUMENTATION_UPDATE_GUIDE.md` for quick reference on what to update.
