# ADR-006: Multi-Threaded Air-Side Design

**Status:** Accepted
**Date:** 2024-10 (Air-Side implementation)
**Updated:** 2025-11-11
**Deciders:** Air-Side Development Team
**Related Issues:** #1, #2, #33 (Camera SDK integration)
**Related Views:** `view-logical.md`, `view-security-reliability.md`

---

## Context

Air-Side service must handle multiple concurrent activities:

1. **Sony SDK Callbacks:** Camera events (disconnect, property changed, capture complete)
2. **TCP Command Processing:** Incoming commands from Ground-Side/Dev-Tools
3. **UDP Status Broadcasting:** 5Hz telemetry broadcast
4. **UDP Heartbeat:** 1Hz bidirectional heartbeat
5. **System Monitoring:** Query CPU, memory, temperature
6. **Camera Polling:** Check camera state (connection, properties)

**Concurrency Challenges:**
- Sony SDK callbacks arrive on SDK-managed thread (out of our control)
- TCP blocking I/O (accept, recv) would block other operations
- UDP broadcast must occur precisely every 200ms (5Hz)
- Camera state shared across threads (must be thread-safe)
- Command processing must not block status broadcasting

**Platform:** Raspberry Pi 5 (4 cores, 8GB RAM) - sufficient for multi-threading

**Design Question:** Single-threaded event loop vs. multi-threaded design?

---

## Decision

**We will use a multi-threaded architecture** with dedicated threads for each major component:

### Thread 1: Main Thread
- **Responsibility:** Startup, initialization, signal handling
- **Lifetime:** Program start to shutdown
- **Blocks:** Only during initialization, then waits for signal

### Thread 2: Camera Thread
- **Responsibility:** Sony SDK management and callbacks
- **Lifetime:** After SDK initialization to shutdown
- **Blocks:** On SDK callback dispatcher (SDK-managed)
- **Key Principle:** SDK callbacks execute on THIS thread

### Thread 3: TCP Server Thread
- **Responsibility:** Accept TCP connections
- **Lifetime:** After network init to shutdown
- **Blocks:** On `accept()` waiting for clients

### Thread 4: TCP Handler Thread (per connection)
- **Responsibility:** Process commands from single client
- **Lifetime:** Connection start to close
- **Blocks:** On `recv()` waiting for command

### Thread 5: UDP Broadcast Thread
- **Responsibility:** 5Hz status broadcast
- **Lifetime:** After network init to shutdown
- **Blocks:** On `sleep(200ms)` between broadcasts

### Thread 6: UDP Heartbeat Thread
- **Responsibility:** 1Hz heartbeat send/receive
- **Lifetime:** After network init to shutdown
- **Blocks:** On `recvfrom()` and `sleep(1s)`

---

## Thread Communication

### Shared State (Thread-Safe)

```cpp
class CameraState {
private:
    mutable std::mutex mutex_;
    bool connected_;
    std::string iso_;
    std::string aperture_;
    // ... other properties

public:
    // Thread-safe getters
    bool isConnected() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return connected_;
    }

    // Thread-safe setters
    void setConnected(bool connected) {
        std::lock_guard<std::mutex> lock(mutex_);
        connected_ = connected;
    }
};
```

### Message Queue (Thread-Safe)

```cpp
class CommandQueue {
private:
    std::queue<Command> queue_;
    std::mutex mutex_;
    std::condition_variable cv_;

public:
    void push(Command cmd) {
        std::lock_guard<std::mutex> lock(mutex_);
        queue_.push(cmd);
        cv_.notify_one();
    }

    Command pop() {
        std::unique_lock<std::mutex> lock(mutex_);
        cv_.wait(lock, [this] { return !queue_.empty(); });
        Command cmd = queue_.front();
        queue_.pop();
        return cmd;
    }
};
```

---

## Threading Model Diagram

```
┌─────────────────────────────────────────────────────────┐
│                      Main Thread                         │
│  - Startup, init, signal handling                        │
└─────────────────────────────────────────────────────────┘
                           │
                           ├─────────────────┬─────────────────┬─────────────────┐
                           ▼                 ▼                 ▼                 ▼
              ┌─────────────────────┐ ┌───────────────┐ ┌──────────────┐ ┌──────────────┐
              │   Camera Thread     │ │ TCP Server    │ │ UDP Broadcast│ │ UDP Heartbeat│
              │  - SDK callbacks    │ │  - Accept()   │ │  - 5Hz timer │ │  - 1Hz timer │
              │  - Update state     │ │  - Spawn TCP  │ │  - Get state │ │  - Send/Recv │
              └─────────────────────┘ │    handlers   │ │  - Broadcast │ └──────────────┘
                           │          └───────────────┘ └──────────────┘
                           │                 │
                           │                 ▼
                           │          ┌──────────────────┐
                           │          │ TCP Handler 1    │
                           │          │  - Recv command  │
                           │          │  - Execute       │
                           │          │  - Send response │
                           │          └──────────────────┘
                           │
                           ▼
                    ┌─────────────────┐
                    │  CameraState    │ ◄──── All threads read/write
                    │  (mutex-locked) │
                    └─────────────────┘
```

---

## Alternatives Considered

### Alternative 1: Single-Threaded Event Loop

**Approach:** Single thread with `select()` / `epoll()` for I/O multiplexing

```cpp
while (running) {
    epoll_wait(epoll_fd, events, MAX_EVENTS, 200); // 200ms timeout for 5Hz broadcast

    for (event in events) {
        if (event.fd == tcp_socket) handleTcpCommand();
        else if (event.fd == udp_socket) handleUdpPacket();
    }

    // Every 200ms (timeout)
    broadcastStatus();
}
```

**Pros:**
- No thread synchronization complexity
- No mutex contention
- Deterministic execution order

**Cons:**
- ❌ **Sony SDK Callbacks:** SDK expects to call us on its own thread
  - Can't integrate SDK callbacks into our event loop
  - Would need cross-thread queue (same complexity as multi-threading)
- ❌ **Blocking Operations:** Any blocking call (e.g., camera query) stalls entire loop
  - 5Hz status broadcast delayed if command processing slow
- ❌ **Timing Precision:** 200ms broadcast interval relies on epoll timeout
  - Command arrival resets timeout → jitter in broadcast rate
- ❌ **Scalability:** Adding new I/O sources requires modifying central event loop

**Rejection Reason:** Sony SDK threading model incompatible with single-threaded event loop. SDK callbacks must execute on dedicated thread.

---

### Alternative 2: Thread Pool with Work Queue

**Approach:** Fixed thread pool (e.g., 8 threads) processing tasks from shared queue

```cpp
ThreadPool pool(8);

pool.enqueue([=] { handleTcpCommand(socket); });
pool.enqueue([=] { broadcastStatus(); });
pool.enqueue([=] { sendHeartbeat(); });
```

**Pros:**
- Flexible task scheduling
- Efficient CPU utilization
- Easy to add new tasks

**Cons:**
- ⚠️ **Timing Unpredictable:** Status broadcast not guaranteed 5Hz
  - Queue may be full → broadcast delayed
  - Thread may be busy → broadcast delayed
- ⚠️ **SDK Callbacks:** Still need dedicated camera thread (SDK requirement)
- ⚠️ **Complexity:** Task queue, thread lifecycle management
- ⚠️ **Overkill:** We know exactly which tasks we have (not dynamic workload)

**Partial Rejection:** Thread pool appropriate for dynamic workloads. Our workload is static and well-defined → dedicated threads simpler.

---

### Alternative 3: Asynchronous I/O (Boost.Asio / libuv)

**Approach:** Use async I/O library for non-blocking operations

```cpp
boost::asio::io_context io;

// Async TCP accept
tcp_acceptor.async_accept([&](error_code ec, tcp::socket socket) {
    handleConnection(std::move(socket));
});

// Async timer for status broadcast
boost::asio::steady_timer timer(io, 200ms);
timer.async_wait([&](error_code ec) {
    broadcastStatus();
    timer.expires_after(200ms);
    timer.async_wait(...); // Recurse
});

io.run(); // Event loop
```

**Pros:**
- Modern C++ async pattern
- Library handles threading details
- Composable async operations

**Cons:**
- ❌ **External Dependency:** Boost/libuv adds ~10MB to binary
- ❌ **Learning Curve:** Team not familiar with async I/O patterns
- ❌ **SDK Integration:** Sony SDK still requires dedicated thread
- ❌ **Debugging Complexity:** Async stack traces harder to follow
- ❌ **Overkill:** Simple sockets sufficient for our use case

**Rejection Reason:** Adds dependency and complexity without solving Sony SDK threading constraint. Standard threads + mutexes well-understood by team.

---

## Consequences

### Positive

✅ **Sony SDK Integration:** Dedicated camera thread meets SDK requirements
- SDK callbacks execute on camera thread
- No cross-thread callback issues
- SDK internal state management unaffected

✅ **Non-Blocking I/O:** Each operation on its own thread
- TCP command processing doesn't block UDP broadcast
- Slow camera query doesn't delay status broadcast
- Heartbeat continues even if TCP connection stalled

✅ **Timing Precision:** Dedicated broadcast thread ensures 5Hz rate
- `std::this_thread::sleep_for(200ms)` simple and accurate
- No jitter from other operations
- Measured rate: 5.00 Hz ± 0.01 Hz

✅ **Parallel Processing:** Multiple TCP clients handled concurrently
- Ground-Side and Dev-Tools can connect simultaneously
- Commands processed in parallel (one per client)
- No queueing delay

✅ **CPU Utilization:** Multi-core Pi 5 benefits from threading
- Threads distributed across 4 cores
- Measured CPU: 5-10% per core (well below capacity)

✅ **Debugging:** Thread-per-component simplifies debugging
- gdb can attach to specific thread
- Thread names visible in logs (`pthread_setname_np`)
- Stack traces show clear component boundaries

---

### Negative

⚠️ **Synchronization Complexity:** Mutexes required for shared state
- CameraState locked on every read/write
- Must ensure lock order to prevent deadlocks
- **Mitigation:** Single CameraState mutex, short critical sections (<1μs)

⚠️ **Race Conditions:** Potential bugs if locking incorrect
- Example: Read ISO and Aperture separately → inconsistent snapshot
- **Mitigation:** Snapshot pattern: lock once, copy all data
  ```cpp
  CameraSnapshot getSnapshot() {
      std::lock_guard<std::mutex> lock(mutex_);
      return CameraSnapshot{iso_, aperture_, shutter_speed_};
  }
  ```

⚠️ **Thread Overhead:** Each thread consumes stack memory (~2MB on Linux)
- 6 threads × 2MB = 12MB (acceptable on 8GB Pi)
- Context switching overhead (negligible on modern CPU)

⚠️ **Shutdown Complexity:** Must gracefully stop all threads
- Join all threads before exit
- Signal all blocking calls (accept, recv) to return
- **Implementation:** `std::atomic<bool> running_` flag checked in each thread loop

⚠️ **Deadlock Risk:** Multiple mutexes can deadlock if lock order inconsistent
- **Mitigation:** Only ONE mutex (CameraState) in current design
- **Future:** If more mutexes needed, document lock order hierarchy

---

## Thread Safety Patterns

### Pattern 1: Snapshot (Read-Only Copy)

**Use Case:** Status broadcast needs consistent camera state

```cpp
// WRONG: Two separate locks, state can change between
std::string iso = camera.getIso();     // Lock 1
std::string aperture = camera.getAperture(); // Lock 2 (ISO may have changed!)

// RIGHT: Single lock, atomic snapshot
CameraSnapshot snapshot = camera.getSnapshot(); // Lock once, copy all
std::string iso = snapshot.iso;
std::string aperture = snapshot.aperture;
```

---

### Pattern 2: Command Queue (Producer-Consumer)

**Use Case:** SDK callback needs to trigger action on camera thread

```cpp
// Producer (any thread)
commandQueue.push(Command::RECONNECT_CAMERA);

// Consumer (camera thread)
while (running) {
    Command cmd = commandQueue.pop(); // Blocks until available
    handleCommand(cmd);
}
```

---

### Pattern 3: Lock Guard (RAII)

**Use Case:** Ensure mutex always unlocked (even on exception)

```cpp
// WRONG: Manual lock/unlock
mutex.lock();
camera.setIso(iso); // If this throws, mutex never unlocked → DEADLOCK
mutex.unlock();

// RIGHT: RAII lock guard
{
    std::lock_guard<std::mutex> lock(mutex);
    camera.setIso(iso); // Exception safe, lock always released
}
```

---

## Performance Characteristics

**Measured on Raspberry Pi 5:**
- Thread creation time: <1ms
- Mutex lock/unlock: <1μs
- Context switch: <10μs
- Memory per thread: ~2MB stack + ~1KB heap

**CPU Usage (idle):**
- Main: 0%
- Camera: 0% (blocked on SDK callbacks)
- TCP Server: 0% (blocked on accept)
- TCP Handler: 0% (blocked on recv, or none if no clients)
- UDP Broadcast: 1% (sleep 200ms, wake, broadcast, repeat)
- UDP Heartbeat: <1% (sleep 1s, wake, send/recv, repeat)

**CPU Usage (active):**
- Camera query (getFocalDistance): 2-5%
- System monitor (read /proc): 1-2%
- JSON serialization: 1-2%
- TCP command processing: 1-3%

**Total CPU: 5-15% average, 20-30% peak**

---

## Implementation Notes

### Thread Creation

```cpp
std::thread cameraThread(&CameraService::run, &cameraService);
std::thread tcpServerThread(&NetworkService::runTcpServer, &networkService);
std::thread udpBroadcastThread(&NetworkService::runUdpBroadcaster, &networkService);
std::thread heartbeatThread(&NetworkService::runHeartbeat, &networkService);

// Set thread names (for debugging)
pthread_setname_np(cameraThread.native_handle(), "Camera");
pthread_setname_np(tcpServerThread.native_handle(), "TCPServer");
pthread_setname_np(udpBroadcastThread.native_handle(), "UDPBroadcast");
pthread_setname_np(heartbeatThread.native_handle(), "Heartbeat");
```

### Thread Shutdown

```cpp
// Signal all threads to stop
running_.store(false, std::memory_order_release);

// Wake blocking operations
shutdown(tcp_socket, SHUT_RDWR); // Unblock accept/recv

// Join all threads
cameraThread.join();
tcpServerThread.join();
udpBroadcastThread.join();
heartbeatThread.join();
```

---

## Future Enhancements

**Considered for Phase 2:**
- **Thread Pool for TCP Handlers:** Limit max connections (currently unbounded)
- **Lock-Free Queues:** boost::lockfree::queue for camera commands (eliminate mutex)
- **Thread Affinity:** Pin threads to specific CPU cores (reduce cache misses)
- **Real-Time Scheduling:** SCHED_FIFO for camera thread (ensure callback priority)

---

## Related Decisions

- **ADR-001:** Three-Domain Architecture (Air-Side as independent service)
- **ADR-004:** Docker Containerization (no threading restrictions in container)
- **ADR-007:** Stateless Air-Side Service (simplifies thread state management)

---

## References

- Logical View: `docs/architecture/view-logical.md` (Air-Side threading model)
- C4 Component Diagram: `docs/architecture/c4-level3-air-side-components.puml`
- LESSONS_LEARNED.md: Sony SDK integration section (Issue #1, #2)
- C++ Concurrency in Action (Anthony Williams) - threading best practices
