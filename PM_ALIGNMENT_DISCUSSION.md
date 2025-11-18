# Phase 1 Cross-Domain Alignment Discussion

**Date:** 2025-11-15
**Issue:** #114 - Phase 1 Cross-Domain Integration & Alignment
**Participants:** PM, User

---

## Purpose

This document captures key architectural decisions needed to align all three domains (Air-Side, Ground-Side, SystemTools) for Phase 1 completion.

**Instructions:** Please respond to each question below. Your answers will guide PM in creating focused child issues and coordinating domain work.

---

# Discussion 1: Configuration Management (get_config / set_config)

## Background

**Current State:**
- ✅ **Ground-Side:** Already sending `get_config` TCP command to Air-Side
- ✅ **Air-Side:** ConfigManager implemented (loads from default.json, development.json)
- ❌ **Air-Side:** TCP protocol handlers NOT implemented (`get_config`, `update_config`)

**Problem:**
Ground-Side calls `get_config` but Air-Side doesn't respond, causing fallback to defaults with warning.

**Evidence:**
```kotlin
// Ground-Side AdvancedSettingsViewModel.kt
val result = NetworkManager.sendCommand("get_config", emptyMap())
// Falls back: "Air-Side does not support get_config command, using default config"
```

---

## Question 1.1: What configuration values should `get_config` expose to Ground-Side?

**Air-Side currently has (from default.json):**
- Network settings (tcp_port, udp ports, IPs)
- Logging configuration (levels, file paths, network streaming settings)
- Health monitoring settings (broadcast interval, thresholds)
- Camera settings (timeouts, retry attempts)
- Timing/sync settings (status intervals, heartbeat timeouts)
- Protocol version info

**Options:**
- [ ] **A)** All config - Expose everything from default.json
- [ ] **B)** Ground-relevant only - Just network IPs, ports, logging settings
- [ ] **C)** Specific subset - (Please list which values below)

**YOUR ANSWER:**
```
[Your response here]
A)** All config - Expose everything from default.json


```

---

## Question 1.2: Do we need `set_config` (update_config) or is `get_config` read-only?

**Options:**
- [ ] **A)** Read-only - Ground-Side just reads Air-Side config for display/diagnostics
- [ ] **B)** Bidirectional - Ground-Side can update Air-Side config remotely
- [ ] **C)** Hybrid - Some values read-only, some writable (please specify which)

**YOUR ANSWER:**
```
[Your response here]
Bidirectional - SystemTools can update Air-Side config remotely***
Bidirectional - SystemTools can update Ground-Side-Side config remotely***
Bidirectional - Ground-Side can update Air-Side config remotely




```

---

## Question 1.3: What's the primary use case for config sync?

**Examples:**
- Display Air-Side IP addresses in Advanced Settings?
- Show Air-Side logging configuration status?
- Allow Ground-Side to remotely enable/disable features?
- Verify protocol version compatibility?
- Something else?

**YOUR ANSWER:**
```
[Your response here]
 System-Tools Priority 1
 (Why, SystemTools is Python quicker and easier to implament / Test.)
 SystemTools Read / wright all Air-Side Configurations.
 SystemTools remotely enable/disable features.
 Ground-Side Priority 2
 Air-Side Read / wright all Air-Side Configurations.
 Air-Side remotely enable/disable features.
```

---

## Question 1.4: Should config changes (if set_config implemented) persist across Air-Side restarts?

**Options:**
- [ ] **A)** Yes - Write changes back to config file (default.json or development.json)
- [ ] **B)** No - Runtime only, reset to file values on restart
- [ ] **C)** Depends on the value (specify which should persist)

**YOUR ANSWER:**
```
[Your response here]
No - Runtime only, reset to file values on restart development.json unless SystemTools sends special command (NOT Ground-Side)
Yes - Write changes back to config file default.json


```

---

# Discussion 2: Logging Architecture

## Background

**We currently have FOUR logging modes/paths:**

### Mode 1: Debug/Development (Always-On)
```
Air-Side → UDP:5007 → SystemTools (Dev PC)
Status: ✅ WORKING NOW
Config: network_systemtools_enabled: true
Use case: Development - full Air-Side log visibility on dev machine
```

### Mode 2: Production (On-Demand via TCP)
```
Ground-Side → TCP: "logging.enable_streaming" → Air-Side
Air-Side → UDP:5005 → Ground-Side
Status: ⚠️ Air-Side ready, Ground-Side NOT implemented  <<< WRONG, Ground-Side is Ready, System-Tools NOT>>>
Config: Triggered by command, auto-timeout after duration
Use case: Production/Field - temporary diagnostics
```

### Mode 3: Ground-Side Logs to SystemTools
```
Ground-Side (H16) → TCP:5008 → SystemTools (Dev PC)
Status: ✅ WORKING (Issue #99)
Use case: Development - Ground-Side app logging to dev machine
```

### Mode 4: Field Deployment Relay (Future)
```
Air-Side → UDP:5005 → Ground-Side (H16) → TCP relay → SystemTools (Laptop)
Status: ⏳ Designed (Issue #95) but not implemented
Use case: Field/Aircraft - Air-Side isolated, H16 relays logs to laptop
```

---

## Question 2.1: What logging modes do we need RIGHT NOW for immediate testing?

**Context:** We need to validate Phase 1 is working. Which modes are critical to test NOW vs can be deferred?

**Options:**
- [ ] **A)** Mode 1 only - SystemTools direct from Air-Side (keep current)
- [ ] **B)** Mode 1 + Mode 3 - SystemTools receives both Air-Side and Ground-Side (validate current state)
- [ ] **C)** Mode 1 + Mode 2 + Mode 3 - All modes working
- [ ] **D)** Custom priority (please specify below)

**YOUR ANSWER:**
```
[Your response here]
d)
System-Tools Priority 1
(Why, SystemTools is Python quicker and easier to implament \ Test).
Mode 1 + Mode 2 + Mode 3 + Mode 4 All modes working
Ground-Side Priority 2
Mode 1 + Mode 2 + Mode 3 + Mode 4 All modes working



```

---

## Question 2.2: Does Ground-Side H16 app UI need to DISPLAY Air-Side logs?

**Context:** This determines if we implement Mode 2 (Air-Side → Ground-Side UDP streaming)

**If YES:**
- Need to implement UDP listener on H16 (port 5005)
- Need UI component to display Air-Side logs
- Need to send `logging.enable_streaming` TCP command

**If NO:**
- Ground-Side only sends its own logs to SystemTools
- Air-Side logs only visible via SystemTools
- Defer Mode 2 implementation

**Options:**
- [ ] **A)** Yes - H16 app should display Air-Side logs in UI (diagnostics screen, etc.)
- [ ] **B)** No - Air-Side logs only in SystemTools, H16 doesn't need them directly
- [ ] **C)** Future enhancement - Not needed for Phase 1 validation

**YOUR ANSWER:**
```
[Your response here]
B)** No - Air-Side logs only in SystemTools, H16 doesn't need them directly



```

---

## Question 2.3: For Mode 2 (on-demand streaming), when should Ground-Side request Air-Side logs?

**Context:** Assuming Mode 2 is needed, when should H16 send the `logging.enable_streaming` command?

**Options:**
- [ ] **A)** Automatically when app connects to Air-Side
- [ ] **B)** Only when user opens diagnostics/log viewer screen
- [ ] **C)** Manual toggle in Advanced Settings ("Enable Air-Side Log Streaming")
- [ ] **D)** Not needed yet - defer implementation

**YOUR ANSWER:**
```
[Your response here]
Already implamented !!! We have on demand logging from Air-Side to Ground-Side



```

---

## Question 2.4: What should we test FIRST to validate current Phase 1 architecture?

**Suggested test priority:**

1. ✅ Verify Mode 1 still working (Air-Side → SystemTools UDP:5007)
2. ✅ Verify Mode 3 still working (Ground-Side → SystemTools TCP:5008)
3. Test tri-domain log aggregation (SystemTools receives both Air + Ground logs)
4. Test Ground-Side logging migration (Issue #113 - LogHelper with toggles)
5. Test health monitoring broadcasts (Air-Side → Ground-Side)
6. Test config sync (get_config) after implementing Air-Side handlers
7. Later: Implement Mode 2 if needed
8. Later: Implement Mode 4 (field relay) per Issue #95

**Do you agree with this priority order, or would you change it?**

**YOUR ANSWER:**
```
[Your response here]
agree



```

---

## Question 2.5: Logging in Production vs Development - Clarification

**Current understanding:**
- **Development mode:** Always-on UDP streaming to SystemTools (network_systemtools_enabled: true)
- **Production mode:** On-demand UDP streaming to Ground-Side (via logging.enable_streaming command)

**Questions:**
- A) Is this distinction correct?
- B) In production (aircraft), will SystemTools even be available? Or is it Ground-Side only?
- C) Should we have different config files (development.json vs production.json) that change which mode is active?

**YOUR ANSWER:**
```
[Your response here]

A) Yes
B) Veriable
C) YES


```

---

# Discussion 3: Integration Testing Priorities

## Question 3.1: What is the MINIMUM set of features that must work to consider Phase 1 "complete"?

**Candidates:**
- [ ] Air-Side structured logging to SystemTools (Mode 1)
- [ ] Ground-Side structured logging to SystemTools (Mode 3)
- [ ] Air-Side health monitoring broadcasts
- [ ] Ground-Side receives health broadcasts
- [ ] Air-Side ConfigManager (internal)
- [ ] Air-Side get_config TCP command (expose config to Ground-Side)
- [ ] Air-Side set_config TCP command (allow remote config updates)
- [ ] UDP Discovery (SystemTools auto-detection)
- [ ] Ground-Side UDP log listener (Mode 2)
- [ ] Ground-Side log relay to SystemTools (Mode 4 / Issue #95)

**YOUR ANSWER (check all that are REQUIRED for Phase 1):**
```
[Your response here - list which features are MUST-HAVE vs NICE-TO-HAVE]

Re-Arange 
Priority 1 Keep our SystemTools main.py as is. COPY log_viewer_gui.py to > DPM_Managment_System.py < We will build on this.
✅ we HAVE now, ❌ we DON'T have now.
*** Implament on Air-Side and SystemTools TEST then mograte to Ground-Side***
1. ✅ (LOG) Air-Side    <> SystemTools passive logging UPD (Development Mode)
1. ✅ (LOG) Ground-Side <> SystemTools passive logging UPD (Development Mode)

2. ❌ (REMOTE) [Air-Side] Configurator get_config Set_config
2. ❌ (REMOTE) [Air-Side] Configurator set_config Set_config
2. ❌ (REMOTE) [SystemTools] <> [Air-Side] Configurator get_config 
2. ❌ (REMOTE) [SystemTools] <> [Air-Side] configurator set_config 

3. ❌ (REMOTE) [Ground-Side] Configurator get_config Set_config
3. ❌ (REMOTE) [Ground-Side] Configurator set_config Set_config
3. ❌ (REMOTE) [SystemTools] <> [Ground-Side] Configurator get_config 
3. ❌ (REMOTE) [SystemTools] <> [Ground-Side] configurator set_config 
 < Like a PC H16 dashboard / helper allowing to set ALL settings in H16>

Once he have above in place we then then FULLY remote configure Air-Side and Ground-Side from PC SystemTools
We can then remotly disable UDP log streaming and fully test Log on demand.

4. ✅ (LOG) Air-Side TCP Log on Demand for X seconds
4. ❌ (LOG) SystemTools Send TCP Log demand to Air-Side, Display UDP log <Same Screen as we have but with new TCP Requester> 

5. ❌ (LOG) Ground-Side to SystemTools TCP Log on Demand
5. ❌ (LOG) SystemTools Send TCP Log demand to Ground-Side, Display UDP log <Same Screen as we have but with new TCP Requester> 

Priority 2
Implament into Ground-Side (H16)
1. ✅ (LOG) Ground-Side Send TCP Log demand to Air-Side
1. ✅ (LOG) Display Air-Side Log stream for X seconds
2. ✅ (REMOTE) [Air-Side] <> [Ground-Side] Configurator get_config
2. ❌ (REMOTE) [Air-Side] <> Configurator set_config Set_config
3. ❌ (LOG) Relay Air-Side Log to SystemTools DEVELOPMENT UDP Streaming mode.
4. ❌ (LOG) Save Air-Side and Ground-Side logs to SD / USB

