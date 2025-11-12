#ifndef HEALTH_MONITOR_H
#define HEALTH_MONITOR_H

#include <string>
#include <vector>
#include <deque>
#include <mutex>
#include <chrono>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

struct SystemMetrics {
    float cpu_percent = 0.0f;
    uint64_t memory_used_mb = 0;
    uint64_t memory_total_mb = 0;
    uint64_t disk_used_mb = 0;
    uint64_t disk_total_mb = 0;
    float network_rx_mbps = 0.0f;
    float network_tx_mbps = 0.0f;

    json toJson() const;
};

struct CameraMetrics {
    bool connected = false;
    float sdk_latency_ms = 0.0f;
    uint64_t usb_traffic_mbps = 0;
    uint32_t error_count = 0;

    json toJson() const;
};

struct NetworkMetrics {
    bool tcp_connected = false;
    float tcp_latency_ms = 0.0f;
    float udp_loss_percent = 0.0f;
    uint32_t command_queue_depth = 0;

    json toJson() const;
};

struct SyncMetrics {
    float exposure_rate_hz = 0.0f;
    float health_rate_hz = 0.0f;
    uint32_t property_reads_sec = 0;

    json toJson() const;
};

struct HealthSnapshot {
    std::chrono::system_clock::time_point timestamp;
    SystemMetrics system;
    CameraMetrics camera;
    NetworkMetrics network;
    SyncMetrics sync;

    json toJson() const;
    static HealthSnapshot fromJson(const json& j);
};

class HealthMonitor {
public:
    static HealthMonitor& getInstance();

    // Initialize and start health monitoring
    void init();

    // Shutdown health monitoring
    void shutdown();

    // Update metrics (called by various components)
    void updateSystemMetrics(const SystemMetrics& metrics);
    void updateCameraMetrics(const CameraMetrics& metrics);
    void updateNetworkMetrics(const NetworkMetrics& metrics);
    void updateSyncMetrics(const SyncMetrics& metrics);

    // Get current health snapshot
    HealthSnapshot getCurrentSnapshot() const;

    // Get recent history (from RAM ring buffer)
    std::vector<HealthSnapshot> getRecentHistory(int minutes = 30) const;

    // Start/stop UDP broadcasting
    void startBroadcasting(const std::string& ground_ip, int port);
    void stopBroadcasting();

    // Archive management
    void enableArchive(const std::string& archive_dir, int retention_days = 7);
    void disableArchive();

private:
    HealthMonitor() = default;
    ~HealthMonitor() = default;

    // Delete copy/move constructors and operators
    HealthMonitor(const HealthMonitor&) = delete;
    HealthMonitor& operator=(const HealthMonitor&) = delete;
    HealthMonitor(HealthMonitor&&) = delete;
    HealthMonitor& operator=(HealthMonitor&&) = delete;

    // Internal methods
    void recordSnapshot();
    void checkThresholds(const HealthSnapshot& snapshot);
    void broadcastSnapshot(const HealthSnapshot& snapshot);
    void archiveSnapshot(const HealthSnapshot& snapshot);
    void cleanupOldArchives();

    // 3-tier storage
    // Tier 1: RAM ring buffer (30 min @ 5 sec = 360 snapshots)
    std::deque<HealthSnapshot> ram_buffer_;
    const size_t ram_buffer_max_size_ = 360;

    // Current metrics (latest values)
    SystemMetrics current_system_;
    CameraMetrics current_camera_;
    NetworkMetrics current_network_;
    SyncMetrics current_sync_;

    // Broadcasting
    bool broadcasting_enabled_ = false;
    std::string ground_ip_;
    int broadcast_port_ = 0;
    int broadcast_socket_ = -1;

    // Archiving
    bool archive_enabled_ = false;
    std::string archive_dir_;
    int archive_retention_days_ = 7;

    mutable std::mutex mutex_;
};

#endif // HEALTH_MONITOR_H
