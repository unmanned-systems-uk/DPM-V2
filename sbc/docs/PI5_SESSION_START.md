# Pi 5 Session Start Instructions

**FOR USER:** When you deploy Claude Code on the Raspberry Pi 5, tell Claude Code to run Issue #72.

---

## Quick Start Commands for Pi 5

When Claude Code is deployed on the Pi 5, it should execute:

```bash
# Navigate to project
cd ~/DPM-V2

# Sync with latest code
git pull origin main

# Verify we're on main branch
git branch --show-current

# Run automated validation (34 tests)
bash sbc/tests/validate_phase1.sh

# If all validation passes, proceed with deployment:
cd sbc
./build_container.sh
./run_container.sh prod

# Monitor logs
docker logs -f payload-manager

# Execute integration tests
# Follow: sbc/docs/PHASE1_TESTING_PLAN.md
```

---

## What to Tell Claude Code

**Option 1 (Simple):**
```
"Please continue work on Issue #72 - deploy and test Phase 1 on this Pi 5"
```

**Option 2 (Detailed):**
```
"START Air-Side
Work on Issue #72
You are now on the Raspberry Pi 5
All Phase 1 code is complete
Please deploy Docker and run integration tests"
```

---

## Expected Actions by Claude Code

1. ✅ Verify environment (Pi 5, Ubuntu, Docker)
2. ✅ Run automated validation tests (34 tests)
3. ✅ Build Docker image (payload-manager:latest)
4. ✅ Start Air-Side services
5. ✅ Verify all Phase 1 components initialize
6. ✅ Execute integration tests (13 tests from PHASE1_TESTING_PLAN.md)
7. ✅ Report results to Issue #72
8. ✅ Update issue status based on test results

---

## Files Ready on Pi 5 (after git pull)

- ✅ `sbc/docs/DEPLOYMENT_GUIDE.md` - Complete deployment steps
- ✅ `sbc/docs/PHASE1_TESTING_PLAN.md` - 13 integration tests
- ✅ `sbc/tests/validate_phase1.sh` - 34 automated validation tests
- ✅ All Phase 1 implementation code (ConfigManager, StructuredLogger, HealthMonitor)
- ✅ Protocol handlers for 3 new commands

---

## Success Criteria

**Claude Code should report:**
- Docker build: ✅ or ❌
- Service startup: ✅ or ❌
- Component initialization: ✅ or ❌
- Integration tests: X/13 PASSED
- Overall status: READY FOR PRODUCTION or NEEDS FIXES

---

**Issue to Continue:** #72 (Phase 1 Foundation Infrastructure)
**Session Type:** Air-Side deployment and testing on Pi 5
**WHO Tag Required:** CC-Air-Side
