# DPM-V2 Documentation Structure

**Purpose:** Guide to finding documentation across the project

**Referenced by:** `.claude/SESSION_START.md`

---

## Key Directory Paths

```
DPM-V2/
├── .claude/                    # Claude Code configuration
│   ├── commands/              # Slash commands (executable)
│   ├── agents/                # Agent definitions
│   ├── archive/               # Historical documents
│   ├── README.md              # This directory guide
│   └── *.md                   # Reference documentation
├── protocol/                   # Protocol specifications (JSON)
│   ├── commands.json          # Command definitions
│   ├── log_contexts.json      # Log context definitions
│   └── *.json                 # Other protocol files
├── sbc/                       # Air-Side (Pi 5 C++)
├── android/                   # Ground-Side (Android Kotlin)
├── SystemTools/               # SystemTools (Python)
└── docs/                      # Project documentation
    ├── ALL_DOMAINS/           # Cross-domain documentation
    ├── AIR_SIDE/              # Air-Side specific
    ├── GROUND_SIDE/           # Ground-Side specific
    ├── SYSTEMTOOLS/           # SystemTools specific
    └── architecture/          # Architecture docs
```

---

## Documentation Tiers

### Tier 1: MANDATORY (Read First)
```
docs/CC_READ_THIS_FIRST.md     # Critical rules and overview
.claude/RULES_CRITICAL.md      # Top-level critical rules
.claude/README.md              # .claude/ directory guide
```

### Tier 2: Domain-Specific (Your Domain)
```
# Air-Side
docs/AIR_SIDE/CrSDK_API_Reference_v2.00.00/  # Sony SDK (CHECK BEFORE camera features)
.claude/commands/start-air.md                # Air-Side session start

# Ground-Side
.claude/commands/start-ground.md             # Ground-Side session start
docs/GROUND_SIDE/                            # Ground-Side docs

# SystemTools
.claude/commands/start-tools.md              # SystemTools session start
SystemTools/README.md                        # SystemTools overview
```

### Tier 3: Cross-Domain (When Coordinating)
```
.claude/MULTI_DOMAIN_COORDINATION.md         # Multi-domain workflows
.claude/DOMAIN_AGENT_RULES.md                # Shared domain rules
docs/ALL_DOMAINS/LESSONS_LEARNED.md          # Historical lessons
protocol/*.json                               # Protocol specifications
```

### Tier 4: PM-Specific
```
.claude/PM_START.md                          # PM session start reference
.claude/PM_MONITORING_PROTOCOL.md            # PM monitoring procedures
.claude/PM_RULES_CRITICAL.md                 # PM-specific rules
.claude/commands/start-pm.md                 # PM session start (executable)
```

---

## Protocol Files (Single Source of Truth)

**Location:** `protocol/*.json`

**CRITICAL:** These are the single source of truth for cross-domain standards.

```
protocol/
├── commands.json              # All command definitions
├── log_contexts.json          # Log context tags (8 contexts)
├── camera_properties.json     # Camera property specifications
├── health_broadcast.json      # Health metrics format
├── log_request.json           # On-demand log request format
└── log_response.json          # Log response format
```

**Rule:** ALWAYS update protocol JSON BEFORE implementing features that use them.

---

## Domain-Specific Paths

### Air-Side (Pi 5 C++)
```
sbc/src/                       # C++ source code
sbc/include/                   # C++ headers
sbc/tests/                     # Unit tests
docs/AIR_SIDE/                 # Air-Side documentation
```

**CRITICAL:** Check Sony SDK docs BEFORE implementing camera features:
```
docs/AIR_SIDE/CrSDK_API_Reference_v2.00.00/index.html
```

### Ground-Side (Android Kotlin)
```
android/app/src/main/java/uk/unmannedsystems/dpm_android/
    ├── camera/                # Camera UI and logic
    ├── network/               # Network communication
    ├── ui/                    # UI components
    ├── diagnostics/           # Diagnostics
    └── settings/              # Settings management
```

### SystemTools (Python)
```
SystemTools/
├── DPM_Management_System.py   # Main GUI
├── log_aggregator.py          # Log aggregation
├── cli_interface.py           # CLI tool
├── config/                    # Configuration files
└── analytics/                 # Analytics tools
```

---

## Common Documentation

### Lessons Learned (CRITICAL)
**Location:** `docs/ALL_DOMAINS/LESSONS_LEARNED.md`

**When to read:**
- Before implementing similar functionality
- After encountering unexpected issues
- When debugging mysterious problems

**Search for:**
```bash
grep -i "camera" docs/ALL_DOMAINS/LESSONS_LEARNED.md
grep -i "focus" docs/ALL_DOMAINS/LESSONS_LEARNED.md
grep -i "[keyword]" docs/ALL_DOMAINS/LESSONS_LEARNED.md
```

### Architecture Documentation
```
docs/architecture/
├── SOFTWARE_ARCHITECTURE_DOCUMENT.md  # Main architecture doc
├── adr/                               # Architecture Decision Records
├── c4-*.puml                          # C4 diagrams
└── view-*.md                          # Architecture views
```

---

## Emergency/Quick Reference

### Lost Context?
```
.claude/COMPRESSION_EMERGENCY.md       # 52 lines - emergency recovery
.claude/RULES_CRITICAL.md              # 89 lines - critical rules
```

### Need Help?
```
.claude/commands/sos.md                # Emergency help command
.claude/README.md                      # Directory structure guide
```

### Session Start
```
.claude/commands/start-*.md            # Domain-specific session starts
.claude/SESSION_START.md               # General session guide
```

---

## Finding Specific Information

**Network configuration:**
```
.claude/CONNECTION_DETAILS.md          # Network details
protocol/*.json                        # Protocol specs
```

**Platform details:**
```
.claude/PLATFORM_VERIFICATION.md       # Platform checks
docs/AIR_SIDE/                         # Pi 5 specific
docs/GROUND_SIDE/                      # H16 specific
```

**Task completion:**
```
.claude/TASK_COMPLETION_PROTOCOL.md    # How to complete tasks
.claude/commands/eot-*.md              # End of task commands
```

**Git workflow:**
```
.claude/GIT_WORKFLOW.md                # Git procedures
```

---

**Last Updated:** 2025-11-22
**Maintained by:** CC-PM
