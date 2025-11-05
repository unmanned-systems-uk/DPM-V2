# Project Documentation Summary
## Air Side SBC Implementation - Ready for Claude Code

**Date:** October 22, 2025  
**Prepared for:** DPM Payload Manager Air Side Development

---

## What Has Been Prepared

I've created comprehensive structured instructions for Claude Code (CC) to implement the Air Side SBC connectivity layer. Here's what you now have:

### 1. Main Instructions Document
**File:** `CC_Air_Side_Implementation_Instructions.md`

This is the primary document Claude Code must read first. It contains:

- ✅ **Mandatory Documentation Review** - Complete checklist of all docs CC must read
- ✅ **Build Plan Requirements** - What CC must present before coding
- ✅ **Implementation Strategy Requirements** - Architecture decisions CC must discuss
- ✅ **Project Context** - Clear explanation of what we're building and why
- ✅ **Sony SDK Integration** - How to work with the camera SDK
- ✅ **Phase 1 Scope** - Precisely what to implement (connectivity only)
- ✅ **Project Structure** - Recommended directory layout
- ✅ **Dependencies** - All required libraries and tools
- ✅ **Protocol Details** - Complete message formats for Phase 1
- ✅ **Error Handling** - Error codes and response patterns
- ✅ **Build Requirements** - CMakeLists.txt guidance
- ✅ **Testing Requirements** - How to validate the implementation
- ✅ **Code Quality** - C++ best practices and standards
- ✅ **Success Criteria** - Clear definition of "done"
- ✅ **Workflow** - Step-by-step process for CC to follow

**Key Features:**
- Enforces "read-first" requirement - no coding until docs are reviewed
- Requires CC to present build and implementation plans for approval
- Clear phase boundaries (Phase 1 only - no camera control yet)
- Aligned with existing Android app (ground side)
- References Sony SDK documentation and examples

### 2. Updated Test Strategy
**File:** `Connectivity_Test_Strategy_v1.1.md`

Enhanced version of your original test strategy with additions:

- ✅ **Air Side Pre-Testing Checklist** - Verify build before testing
- ✅ **C++ Specific Testing** - Memory leaks, thread safety, profiling
- ✅ **Phase 1 MVP Priorities** - Which tests are critical vs nice-to-have
- ✅ **Stub Camera Testing** - How to test without real camera
- ✅ **Automated Test Script** - Bash script for automated testing
- ✅ **Android Integration** - How to test with real Android app
- ✅ **Build Verification** - How to verify compilation success
- ✅ **Service Startup Verification** - How to confirm service is running
- ✅ **Process Monitoring** - Resource usage validation

**Key Additions:**
- Practical build/deployment verification steps
- valgrind and thread sanitizer usage
- Automated testing bash script
- Clear test priorities for Phase 1
- Android LogCat integration

---

## What Claude Code Must Do (Summary)

### Step 1: Documentation Review (PAUSE - DO NOT CODE)
CC must read and understand:
1. CC_Air_Side_Implementation_Instructions.md (main instructions)
2. Air_Side_Implementation_Guide.md (your system architecture)
3. Connectivity_Test_Strategy_v1.1.md (testing approach)
4. Sony SDK README and PDFs
5. Sony SDK example code in the app/ directory

### Step 2: Build Plan Presentation (PAUSE - DO NOT CODE)
CC must present a detailed build plan covering:
- CMakeLists.txt approach
- Dependency management strategy
- Build steps and verification
- Platform-specific considerations

**CC must wait for your approval before proceeding.**

### Step 3: Implementation Strategy (PAUSE - DO NOT CODE)
CC must present:
- Component architecture design
- Threading model
- Error handling approach
- Sony SDK integration strategy (stub for Phase 1)
- Testing alignment

**CC must wait for your approval before proceeding.**

### Step 4: Implementation (START CODING)
Only after approval, CC implements:
- TCP server (port 5000)
- UDP broadcaster (port 5001)
- Heartbeat handler (port 5002)
- Message handling (JSON)
- Logging system
- System monitoring
- Camera stub (placeholder)

### Step 5: Testing (VALIDATE)
CC tests against Connectivity_Test_Strategy_v1.1.md:
- Network layer tests
- Protocol layer tests
- Application layer tests
- Error handling tests
- Performance tests

### Step 6: Documentation (FINALIZE)
CC documents:
- Build instructions
- Deployment guide
- Any deviations from spec
- Known limitations

---

## Key Constraints and Boundaries

### ✅ IN SCOPE (Phase 1 - Current Focus)
- Network communication (TCP/UDP)
- Handshake and basic commands
- Status broadcasting
- Heartbeat mechanism
- Logging infrastructure
- System monitoring
- Camera stub (not real SDK)

### ❌ OUT OF SCOPE (Phase 1)
- Sony Camera SDK integration (Phase 2)
- Camera property control (Phase 2)
- Image capture (Phase 2)
- Video recording (Phase 3)
- Gimbal control (Phase 3)
- Content download (Phase 3)

---

## Critical Success Factors

### 1. Documentation First
CC **must** read all documentation before writing any code. This is enforced through the instruction document.

### 2. Approval Gates
CC **must** present plans and wait for approval at two key checkpoints:
- Build plan approval
- Implementation strategy approval

### 3. Phase 1 Only
CC **must not** implement camera control or advanced features. Phase 1 is connectivity validation only.

### 4. Test-Driven
Implementation **must** pass the tests defined in Connectivity_Test_Strategy_v1.1.md.

### 5. Sony SDK Patterns
When Phase 2 begins, CC **must** follow the patterns from Sony's example code, not invent new approaches.

---

## How to Use These Documents

### For Claude Code:
1. Start by reading `CC_Air_Side_Implementation_Instructions.md` top to bottom
2. Review all referenced documents in order
3. Examine Sony SDK example code
4. Present build plan (don't code yet!)
5. Present implementation strategy (don't code yet!)
6. Implement after approval
7. Test against Connectivity_Test_Strategy_v1.1.md
8. Document results

### For You (Human):
1. Give these documents to Claude Code
2. Review CC's build plan when presented
3. Approve or request changes
4. Review CC's implementation strategy
5. Approve or request changes
6. Monitor CC's implementation progress
7. Review test results
8. Verify against your Android app (ground side)

---

## File Locations

All documents have been saved to `/mnt/user-data/outputs/`:

1. **CC_Air_Side_Implementation_Instructions.md** - Main instructions for Claude Code
2. **Connectivity_Test_Strategy_v1.1.md** - Updated test strategy with Air Side additions

Original documents remain at `/mnt/user-data/uploads/`:
- Air_Side_Implementation_Guide.md
- Connectivity_Test_Strategy.md (original version)
- README.md (Sony SDK)
- Camera_Remote_SDK_Readme_v2_00_00.pdf
- RemoteSampleApp_IM_v2_00_00.pdf

---

## What Happens Next

### Immediate Next Steps:
1. **You:** Provide these documents to Claude Code
2. **Claude Code:** Reads all documentation (may take a while)
3. **Claude Code:** Asks clarifying questions if needed
4. **Claude Code:** Presents build plan for your review
5. **You:** Review and approve (or request changes)
6. **Claude Code:** Presents implementation strategy
7. **You:** Review and approve (or request changes)
8. **Claude Code:** Begins implementation

### Timeline Expectations:
- Documentation review: 30-60 minutes (CC reading)
- Build plan development: 30-60 minutes
- Implementation strategy: 30-60 minutes
- Implementation: 4-8 hours (depending on complexity)
- Testing: 2-4 hours
- Total: ~1-2 days for Phase 1 complete

---

## Key Design Decisions Made

### 1. Phased Approach
- Phase 1: Connectivity only (current)
- Phase 2: Camera control (future)
- Phase 3: Advanced features (future)

### 2. Technology Stack
- C++17 (modern C++ features)
- nlohmann/json for JSON parsing
- POSIX sockets for networking
- Standard threading library
- Sony CrSDK v2.00.00

### 3. Testing Strategy
- Manual testing with scripts
- Integration with Android app
- Memory leak detection (valgrind)
- Thread safety verification
- Performance profiling

### 4. Code Quality
- RAII for resource management
- Smart pointers (no raw pointers)
- Const correctness
- Exception safety
- Comprehensive logging

---

## Alignment with Your Existing Work

### Ground Side (Android App)
Your Android app is already complete and tested. The Air Side implementation will:
- Use the exact same protocol (JSON messages)
- Respond to the same ports (5000, 5001, 5002)
- Implement the same message formats
- Handle the same commands (handshake, system.get_status)

### Testing Compatibility
The test strategy is designed to work with your existing Android app:
- Manual connection testing
- Status update verification
- Error handling validation
- Performance measurement

### Future Integration
Phase 2 will add:
- Sony Camera SDK integration (using provided SDK)
- Camera property control (matching Android UI)
- Image capture (coordinated with Android)

---

## Questions Claude Code Might Ask

Based on the documentation, CC might ask:

1. **Build Questions:**
   - "Should I use system nlohmann-json or bundle it?"
   - "What CMake version should I target?"
   - "Should I set up cross-compilation or native build?"

2. **Implementation Questions:**
   - "Should I use boost::asio or raw POSIX sockets?"
   - "How should I structure the thread pool for TCP clients?"
   - "Should I implement log rotation or just append?"

3. **Testing Questions:**
   - "Do you want unit tests or just integration tests?"
   - "Should I create mock objects for testing?"
   - "What's the priority for memory leak testing?"

4. **Sony SDK Questions:**
   - "For Phase 1 stub, what interface should I define?"
   - "Should I structure code to make Phase 2 integration easy?"
   - "Do you have the actual Sony SDK files available?"

You should be prepared to answer these or guide CC based on your preferences.

---

## Success Metrics

Phase 1 is successful when:

### Functionality ✅
- Service compiles without warnings
- Service runs without crashes
- Accepts TCP connections
- Handshake works correctly
- System status command works
- Status broadcasts at 5 Hz
- Heartbeat exchanges at 1 Hz
- JSON parsing works perfectly

### Testing ✅
- All Network Layer tests pass
- All Protocol Layer tests pass
- All Application Layer tests pass
- 80%+ Error Handling tests pass
- Performance metrics met
- Android app can connect
- No memory leaks
- Resource usage within limits

### Code Quality ✅
- Follows C++17 best practices
- No compiler warnings
- Thread-safe implementation
- Graceful shutdown works
- Documentation complete

---

## Important Reminders

### For Claude Code:
- 🛑 **DO NOT** start coding until you've read all documentation
- 🛑 **DO NOT** implement camera features (Phase 2)
- 🛑 **DO NOT** proceed without approval on build plan
- 🛑 **DO NOT** proceed without approval on implementation strategy
- ✅ **DO** ask questions when unclear
- ✅ **DO** follow Sony SDK patterns
- ✅ **DO** align with test strategy
- ✅ **DO** focus on Phase 1 only

### For You:
- Review CC's plans carefully before approval
- Test with your Android app when ready
- Provide the Sony SDK files when CC needs them
- Be prepared to iterate on designs
- Phase 1 is foundation for Phase 2/3

---

## Document Status

- ✅ Instructions created: CC_Air_Side_Implementation_Instructions.md
- ✅ Test strategy updated: Connectivity_Test_Strategy_v1.1.md  
- ✅ All reference documents verified
- ✅ Sony SDK structure understood
- ✅ Android app integration planned
- ✅ Phase boundaries defined
- ✅ Success criteria established

**Ready to proceed with Claude Code implementation!**

---

**Prepared by:** Claude (Documentation Assistant)  
**Date:** October 22, 2025  
**Status:** Complete and ready for handoff to Claude Code
