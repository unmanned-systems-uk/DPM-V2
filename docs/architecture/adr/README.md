# Architecture Decision Records (ADRs)

**Purpose:** Document major architectural decisions made during DPM-V2 development

**Standard:** Lightweight ADR format (Context, Decision, Alternatives, Consequences)

**Location:** `docs/architecture/adr/`

---

## What is an ADR?

An Architecture Decision Record (ADR) captures an important architectural decision made along with its context and consequences.

**When to create an ADR:**
- Choosing between multiple viable approaches
- Making a decision that affects multiple components
- Trade-offs that future developers should understand
- "Why did we do it this way?" questions

**When NOT to create an ADR:**
- Implementation details (code-level decisions)
- Obvious choices (e.g., "Use HTTP for web API")
- Temporary workarounds

---

## ADR Index

### Core Architecture (ADR-001 to ADR-005)

| ADR | Title | Status | Key Benefit | Trade-Off |
|-----|-------|--------|-------------|-----------|
| [ADR-001](ADR-001-three-domain-architecture.md) | Three-Domain Microservices Architecture | Accepted | Technology flexibility, independent deployment | Network overhead, protocol sync |
| [ADR-002](ADR-002-specification-first-property-management.md) | Specification-First Property Management | Accepted | Guaranteed Air/Ground sync, easy extensibility | Runtime JSON parsing, build-time sync |
| [ADR-003](ADR-003-tcp-udp-protocol-split.md) | TCP/UDP Protocol Split | Accepted | Optimal reliability + performance, no head-of-line blocking | Dual protocol complexity, 3 ports |
| [ADR-004](ADR-004-docker-containerization.md) | Docker Containerization for Air-Side | Accepted | Easy rollback, dependency isolation, auto-restart | Docker learning curve, host networking |
| [ADR-005](ADR-005-mvvm-pattern-ground-side.md) | MVVM Pattern for Ground-Side Android | Accepted | Testability, configuration change handling, reactive UI | Boilerplate, state sync complexity |

### Component Architecture (ADR-006 to ADR-010)

| ADR | Title | Status | Key Benefit | Trade-Off |
|-----|-------|--------|-------------|-----------|
| [ADR-006](ADR-006-multi-threaded-air-side-design.md) | Multi-Threaded Air-Side Design | Accepted | Non-blocking I/O, Sony SDK integration, timing precision | Synchronization complexity, thread overhead |
| [ADR-007](ADR-007-stateless-air-side-service.md) | Stateless Air-Side Service | Accepted | Fast recovery (<10 sec), simple deployment, idempotent | Camera reconnection delay, no command history |
| [ADR-008](ADR-008-udp-status-broadcast-rate.md) | UDP Status Broadcast Rate (5Hz) | Accepted | Smooth UX (200ms feels instant), network efficient (5KB/sec) | Packet loss visible if >2 consecutive |
| [ADR-009](ADR-009-heartbeat-timeout.md) | Heartbeat Timeout (10 Seconds) | Accepted | Fast failure detection, robust against false positives | 10 sec delay before reconnect |
| [ADR-010](ADR-010-propertyloader-pattern.md) | PropertyLoader Pattern | Accepted | Single responsibility, testable, reusable C++/Kotlin | Startup parsing (~50ms) |

### Protocol & Patterns (ADR-011 to ADR-015)

| ADR | Title | Status | Key Benefit | Trade-Off |
|-----|-------|--------|-------------|-----------|
| [ADR-011](ADR-011-json-over-tcp-udp-protocol.md) | JSON-over-TCP/UDP Protocol | Accepted | Human-readable, cross-language, debuggable (Wireshark) | Larger messages (2× binary), parsing overhead |
| [ADR-012](ADR-012-cpp-for-air-side-performance.md) | C++ for Air-Side Performance | Accepted | Native SDK integration, low latency (<30ms), memory efficient (50MB) | Manual memory management, longer dev time |
| [ADR-013](ADR-013-jetpack-compose-for-ground-ui.md) | Jetpack Compose for Ground UI | Accepted | Reactive UI (auto-updates), less code (30% reduction), reusable components | Learning curve, min SDK 21 |
| [ADR-014](ADR-014-auto-reconnect-strategy.md) | Auto-Reconnect Strategy | Accepted | Fast recovery (1sec), resource friendly (30sec max), self-healing | Max 30 sec wait, no manual retry |
| [ADR-015](ADR-015-closed-network-security-posture.md) | Closed Network Security Posture | Accepted | Fast development, easy debugging (plaintext), no key management | Not production-ready, security debt |

---

## ADR Relationships

### Dependency Graph

```
ADR-001 (Three-Domain Architecture)
  ├── ADR-002 (Spec-First) ──→ ADR-010 (PropertyLoader)
  ├── ADR-003 (TCP/UDP Split)
  │     ├── ADR-008 (5Hz Rate)
  │     ├── ADR-009 (10 Sec Timeout)
  │     └── ADR-011 (JSON Protocol)
  ├── ADR-004 (Docker) ──→ ADR-007 (Stateless)
  ├── ADR-005 (MVVM) ──→ ADR-013 (Jetpack Compose)
  ├── ADR-006 (Multi-Threaded)
  ├── ADR-012 (C++ Air-Side)
  └── ADR-014 (Auto-Reconnect)
        └── ADR-015 (Security Posture)
```

### Cross-Cutting Concerns

**Performance:**
- ADR-003: TCP/UDP split (no head-of-line blocking)
- ADR-006: Multi-threading (parallel processing)
- ADR-008: 5Hz rate (balance UX and bandwidth)
- ADR-012: C++ (native performance)

**Reliability:**
- ADR-004: Docker (auto-restart)
- ADR-007: Stateless (fast recovery)
- ADR-009: Heartbeat timeout (failure detection)
- ADR-014: Auto-reconnect (self-healing)

**Maintainability:**
- ADR-002: Spec-First (single source of truth)
- ADR-005: MVVM (separation of concerns)
- ADR-010: PropertyLoader (reusable pattern)
- ADR-011: JSON (human-readable)

**Extensibility:**
- ADR-001: Three-Domain (independent evolution)
- ADR-002: Spec-First (add properties without code changes)
- ADR-013: Jetpack Compose (reusable components)

---

## ADR Template

When creating new ADRs, use this format:

```markdown
# ADR-XXX: Title

**Status:** Proposed | Accepted | Deprecated | Superseded
**Date:** YYYY-MM-DD
**Updated:** YYYY-MM-DD
**Deciders:** Who made this decision
**Related Issues:** #123, #456
**Related Views:** view-xxx.md

---

## Context

What is the issue we're facing? What are the requirements and constraints?

---

## Decision

What did we decide? Why did we choose this approach?

---

## Alternatives Considered

### Alternative 1: Name

**Approach:** Brief description

**Pros:**
- Advantage 1
- Advantage 2

**Cons:**
- ❌ Disadvantage 1 (with reason for rejection)
- ❌ Disadvantage 2

**Rejection Reason:** Why we didn't choose this

---

## Consequences

### Positive

✅ Benefit 1
✅ Benefit 2

### Negative

⚠️ Trade-off 1
- Mitigation: How we address this

---

## Related Decisions

- **ADR-XXX:** Brief relationship description

---

## References

- Links to code, docs, external resources
```

---

## ADR Workflow

### Creating a New ADR

1. **Identify Decision:** Recognize a choice that affects architecture
2. **Draft ADR:** Use template above
3. **Number ADR:** Next sequential number (ADR-016, ADR-017, ...)
4. **Review:** Team reviews draft, suggests alternatives
5. **Update Status:** Mark as "Accepted" once finalized
6. **Commit:** Add to git with descriptive commit message
7. **Update Index:** Add to this README.md table

### Modifying an ADR

**ADRs are immutable once accepted.** If a decision changes:

1. **Deprecate Old ADR:** Change status to "Deprecated by ADR-XXX"
2. **Create New ADR:** Explain new decision, reference old ADR
3. **Update Status:** Mark new ADR as "Accepted"

**Example:**
- ADR-003 (TCP/UDP) → ADR-020 (Switch to gRPC)
- ADR-003 status: "Deprecated by ADR-020"

---

## Viewing ADRs

### By Topic

**Network & Communication:**
- ADR-003 (TCP/UDP Split)
- ADR-008 (5Hz Broadcast)
- ADR-009 (Heartbeat Timeout)
- ADR-011 (JSON Protocol)
- ADR-014 (Auto-Reconnect)

**Air-Side Implementation:**
- ADR-004 (Docker)
- ADR-006 (Multi-Threaded)
- ADR-007 (Stateless)
- ADR-012 (C++)

**Ground-Side Implementation:**
- ADR-005 (MVVM)
- ADR-013 (Jetpack Compose)

**Data Management:**
- ADR-002 (Spec-First)
- ADR-010 (PropertyLoader)

**Architecture Patterns:**
- ADR-001 (Three-Domain)
- ADR-015 (Security Posture)

---

### By Issue

**Focus & Camera Control (Issues #1, #2, #10, #22):**
- ADR-002 (Spec-First prevents property mismatch)
- ADR-010 (PropertyLoader validates commands)
- ADR-012 (C++ for Sony SDK integration)

**Network Monitoring (Issue #11):**
- ADR-003 (TCP/UDP for different needs)
- ADR-008 (5Hz status rate)
- ADR-009 (10 sec heartbeat timeout)

**Deployment (Issues #33, #46, #50, #51):**
- ADR-004 (Docker prevents deployment bugs)
- ADR-007 (Stateless simplifies recovery)

**UI Implementation (Issues #10, #20):**
- ADR-005 (MVVM for reactive UI)
- ADR-013 (Compose for quick screens)

---

## ADR Statistics

**Total ADRs:** 15
**Accepted:** 15
**Deprecated:** 0
**Superseded:** 0

**By Category:**
- Core Architecture: 5 (33%)
- Component Architecture: 5 (33%)
- Protocol & Patterns: 5 (33%)

**Key Metrics:**
- Average ADR length: ~300 lines
- Total documentation: ~4,500 lines
- Alternatives considered: 2-4 per ADR

---

## Further Reading

- **Architecture Views:** `docs/architecture/view-*.md` (How decisions manifest in system)
- **C4 Diagrams:** `docs/architecture/c4-*.puml` (Visual representation)
- **Lessons Learned:** `docs/ALL_DOMAINS/LESSONS_LEARNED.md` (Real-world validation)
- **Integration Points:** `docs/ALL_DOMAINS/INTEGRATION_POINTS.md` (Protocol implementation)

---

## External ADR Resources

- **ADR GitHub:** https://adr.github.io/ (ADR best practices)
- **Michael Nygard's ADRs:** Original ADR concept
- **ThoughtWorks Tech Radar:** ADR as "Adopt" technique

---

**Maintained by:** DPM-V2 Development Team
**Last Updated:** 2025-11-11
**Version:** 1.0
