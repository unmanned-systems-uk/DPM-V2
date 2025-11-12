# Contributing to DPM-V2

Thank you for contributing to the Drone Payload Manager (DPM-V2) project! This guide will help you understand our development workflow and documentation requirements.

## Table of Contents

1. [Documentation Requirements](#documentation-requirements)
2. [Domain-Specific Guidelines](#domain-specific-guidelines)
3. [Pull Request Process](#pull-request-process)
4. [Architecture Decision Records](#architecture-decision-records)
5. [Commit Message Format](#commit-message-format)
6. [Code Style Guidelines](#code-style-guidelines)

---

## Documentation Requirements

### Golden Rule

**Every code change MUST include corresponding documentation updates.**

We maintain comprehensive architecture documentation (ISO/IEC/IEEE 42010 compliant) including:
- C4 diagrams (PlantUML)
- Architecture views (6 viewpoints)
- Architecture Decision Records (ADRs)
- Software Architecture Document (SAD)

When you change code, you must update the relevant documentation to maintain accuracy.

---

## Domain-Specific Guidelines

DPM-V2 is organized into domains. Each domain has specific documentation requirements.

### Air-Side (C++ in `sbc/`)

**Platform:** Raspberry Pi 5
**Language:** C++17
**Technologies:** Sony Camera Remote SDK, Docker

#### When you change Air-Side code, you MUST update:

1. **Code comments** - Inline C++ documentation for complex logic
2. **Component documentation** - `docs/architecture/view-logical.md` Section 4.2.3 (if component structure changed)
3. **C4 diagram** - `docs/architecture/c4-level3-air-side-components.puml` (if component added/removed)
4. **ADRs** - Update relevant ADR if architectural decision changed (see ADR index)
5. **Traceability matrix** - Update SAD Section 8.3 if component→code mapping changed

#### Triggers requiring Air-Side documentation update:

- ✅ Added/removed component (e.g., new Service class)
- ✅ Changed threading model (see ADR-006)
- ✅ Modified Docker deployment configuration (see ADR-004)
- ✅ Changed camera integration pattern (see ADR-012)
- ✅ Modified network protocol handling (see ADR-003)

#### Relevant ADRs:
- ADR-001: Three-Domain Architecture
- ADR-004: Docker Containerization
- ADR-006: Multi-Threaded Design
- ADR-007: Stateless Service
- ADR-012: C++ for Air-Side Performance

---

### Ground-Side (Kotlin in `android/`)

**Platform:** H16 Android Controller
**Language:** Kotlin
**Technologies:** Android SDK, Jetpack Compose

#### When you change Ground-Side code, you MUST update:

1. **Code comments** - KDoc for public APIs
2. **MVVM documentation** - `docs/architecture/view-logical.md` Section 4.2.4 (if layer changed)
3. **C4 diagram** - `docs/architecture/c4-level3-ground-side-components.puml` (if layer added)
4. **ADRs** - Update ADR-005 if MVVM pattern changed, ADR-013 if Compose pattern changed
5. **UI documentation** - Document new screens/flows in `view-logical.md`

#### Triggers requiring Ground-Side documentation update:

- ✅ Added/removed ViewModel
- ✅ New UI screen or navigation flow
- ✅ Changed state management pattern (StateFlow, etc.)
- ✅ Modified network layer (Repository pattern)
- ✅ Changed UI component structure

#### Relevant ADRs:
- ADR-005: MVVM Pattern for Ground-Side
- ADR-013: Jetpack Compose for Ground UI
- ADR-014: Auto-Reconnect Strategy

---

### Protocol Specification (JSON in `docs/protocol/`)

**Platform:** Cross-domain
**Language:** JSON
**Scope:** Affects BOTH Air-Side AND Ground-Side

#### When you change protocol specifications, you MUST update:

1. **Specification files** - `docs/protocol/commands.json` or `docs/protocol/camera_properties.json`
2. **Integration documentation** - `docs/architecture/view-integration.md` (protocol patterns)
3. **ADR-002** - If Specification-First pattern changed
4. **ADR-003** - If TCP/UDP protocol split changed
5. **PropertyLoader code** - BOTH `sbc/src/property_loader.cpp` (C++) AND `android/.../PropertyLoader.kt` (Kotlin) - **MANDATORY**

#### ⚠️ CRITICAL: Protocol Changes Affect Two Domains

Protocol changes require updates in **BOTH** Air-Side (C++) and Ground-Side (Kotlin):
- Update PropertyLoader in C++
- Update PropertyLoader in Kotlin
- Verify synchronization (Issue #22 lesson learned)
- Test both domains together

**Use issue label:** `[ALL-DOMAINS][PROTOCOL]`

#### Relevant ADRs:
- ADR-002: Specification-First Property Management
- ADR-003: TCP/UDP Protocol Split
- ADR-011: JSON-over-TCP/UDP Protocol

---

### Tools/Dev-Side (Python in `SystemTools/`)

**Platform:** Cross-platform (Windows/Linux)
**Language:** Python
**Technologies:** tkinter, paramiko, matplotlib

#### When you change diagnostic tools, you MUST update:

1. **Tool README** - Usage instructions in `SystemTools/README.md`
2. **Component documentation** - `docs/architecture/view-logical.md` Section 4.2.5
3. **C4 diagram** - `docs/architecture/c4-level3-dev-tools-components.puml`

#### Triggers requiring Tools documentation update:

- ✅ Added/removed diagnostic tool
- ✅ Changed tool UI or workflow
- ✅ New integration with Air-Side or Ground-Side

---

## Architecture Decision Records (ADRs)

ADRs document significant architectural decisions made during development.

### When to create a NEW ADR:

✅ You made a significant architectural decision (new pattern, technology choice, protocol change)
✅ You evaluated 2+ alternatives
✅ Decision has long-term impact (>6 months)
✅ Decision introduces new pattern or technology

### When to UPDATE an existing ADR:

✅ Decision consequences changed (new trade-off discovered)
✅ Alternative previously rejected is now chosen (supersede old ADR)
✅ Real-world validation data available (reference `LESSONS_LEARNED.md`)

### When NOT to create an ADR:

❌ Simple bug fix with no architectural impact
❌ Minor refactoring within single component
❌ Documentation-only change

### ADR Format:

Follow the template in `docs/architecture/adr/README.md`:

1. **Context** - Problem, requirements, constraints
2. **Decision** - What was decided and why
3. **Alternatives Considered** - 2-4 alternatives with pros/cons
4. **Consequences** - Positive benefits and negative trade-offs
5. **Related Decisions** - Cross-references to other ADRs
6. **References** - Links to code, docs, issues

**See existing ADRs for examples:** `docs/architecture/adr/ADR-*.md`

---

## Pull Request Process

### Before Creating a Pull Request

Run this checklist:

- [ ] Code changes complete and tested
- [ ] Inline comments added for complex logic
- [ ] Domain-specific documentation updated (see above)
- [ ] Architecture views updated if component structure changed
- [ ] C4 diagrams updated if components added/removed
- [ ] ADRs updated if decisions changed
- [ ] Traceability matrix updated if component→code mapping changed
- [ ] Cross-references valid (no broken links)
- [ ] Glossary updated if new terms introduced
- [ ] Commit messages follow format: `[DOMAIN][TYPE] Description`

### Pull Request Template

When you create a PR, fill out the template completely:
- Describe code changes
- Check domain-specific documentation checkboxes
- Indicate architecture impact (if any)
- Reference related issues

### Automated Checks

Your PR will be validated by GitHub Actions:
- ✅ Documentation modified when code changes
- ✅ PlantUML diagrams compile correctly
- ✅ Markdown links are valid
- ✅ ADR format is correct

**If checks fail:** Fix the issue and push updates.

### Code Review

Reviewers will verify:
- Code quality and correctness
- Documentation completeness and accuracy
- Adherence to architecture patterns
- Domain-specific requirements met

---

## Commit Message Format

Use the format: `[DOMAIN][TYPE] Description`

### Domain Tags:
- `[AIR]` - Air-Side (C++, Pi 5)
- `[GROUND]` - Ground-Side (Kotlin, Android)
- `[TOOLS]` - Tools/Dev-Side (Python)
- `[PROTOCOL]` - Protocol specifications
- `[DOCS]` - Documentation
- `[WORKFLOW]` - Development workflow
- `[ALL]` - All domains (cross-cutting)

### Type Tags:
- `[BUG]` - Bug report
- `[FIX]` - Bug fix implementation
- `[FEATURE]` - New functionality
- `[ENHANCEMENT]` - Improvement to existing functionality
- `[REFACTOR]` - Code improvement without behavior change
- `[TESTING]` - Test implementation
- `[DOCS]` - Documentation changes

### Examples:

```
[AIR][FEATURE] Add gimbal control support to camera service
[GROUND][FIX] Resolve focus commands not reaching Air-Side
[PROTOCOL][ENHANCEMENT] Add shutter_speed property to camera specs
[DOCS][ENHANCEMENT] Update architecture view with new component
[ALL][WORKFLOW] Implement documentation enforcement strategy
```

---

## Code Style Guidelines

### C++ (Air-Side)

- Follow C++17 standard
- Use `snake_case` for variables and functions
- Use `PascalCase` for class names
- Add header comments for all public classes
- Document complex algorithms inline
- Use smart pointers (avoid raw `new`/`delete`)
- Thread safety: Document mutex usage

**Example:**
```cpp
/**
 * CameraService manages Sony camera lifecycle and operations.
 * Thread-safe: All public methods protected by camera_mutex_.
 */
class CameraService {
public:
    /**
     * Initialize camera connection via USB.
     * @return true if successful, false otherwise
     */
    bool Initialize();

private:
    std::mutex camera_mutex_;  // Protects camera state
};
```

### Kotlin (Ground-Side)

- Follow Kotlin coding conventions
- Use `camelCase` for variables and functions
- Use `PascalCase` for class names
- Add KDoc for all public APIs
- Use StateFlow for reactive state
- Follow MVVM pattern (ADR-005)

**Example:**
```kotlin
/**
 * ViewModel for camera control screen.
 * Manages camera state and user interactions.
 */
class CameraViewModel(
    private val repository: CameraRepository
) : ViewModel() {

    /**
     * Current camera connection state.
     * Emits updates when connection status changes.
     */
    val connectionState: StateFlow<ConnectionState> = ...
}
```

### Python (Tools)

- Follow PEP 8 style guide
- Use `snake_case` for variables and functions
- Use `PascalCase` for class names
- Add docstrings for all public functions
- Type hints for function signatures

**Example:**
```python
def connect_to_air_side(host: str, port: int) -> bool:
    """
    Connect to Air-Side service via TCP.

    Args:
        host: IP address or hostname
        port: TCP port number

    Returns:
        True if connection successful, False otherwise
    """
    pass
```

---

## Quick Documentation Reference

### "What documentation do I update for...?"

**Component added:**
- Architecture view (logical/deployment/integration)
- C4 diagram (level 3)
- SAD traceability matrix (Section 8.3)

**Architectural decision made:**
- Create new ADR or update existing
- Update relevant architecture view
- Update SAD Section 5 summary

**Protocol changed:**
- Update `docs/protocol/*.json`
- Update PropertyLoader in C++ AND Kotlin (MANDATORY)
- Update `view-integration.md`
- Update ADR-002 or ADR-003

**Technology changed:**
- Update relevant ADR (e.g., ADR-012 for C++, ADR-013 for Compose)
- Update deployment view if infrastructure changed
- Update C4 level 2 container diagram if container tech changed

**Performance/Quality changed:**
- Update SAD Section 9 (Quality Attributes)
- Update ADR consequences if trade-off changed
- Update `view-security-reliability.md` if reliability changed

**For detailed guidance:** See `docs/DOCUMENTATION_UPDATE_GUIDE.md`

---

## Getting Help

- **Documentation questions:** See `docs/DOCUMENTATION_UPDATE_GUIDE.md`
- **Architecture questions:** Review `docs/architecture/SOFTWARE_ARCHITECTURE_DOCUMENT.md`
- **Domain questions:** Check `.github/domain-config.json`
- **Still unsure:** Ask in PR comments or create an issue

---

## Additional Resources

- **Architecture Documentation:** `docs/architecture/`
- **C4 Diagrams:** `docs/architecture/c4-level*.puml`
- **Architecture Views:** `docs/architecture/view-*.md`
- **ADRs:** `docs/architecture/adr/ADR-*.md`
- **SAD:** `docs/architecture/SOFTWARE_ARCHITECTURE_DOCUMENT.md`
- **Lessons Learned:** `LESSONS_LEARNED.md`
- **Domain Configuration:** `.github/domain-config.json`

---

Thank you for contributing to DPM-V2! Your attention to both code quality and documentation quality is what makes this project successful.
