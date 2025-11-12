#include "health/health_monitor.h"
#include "config/config_manager.h"
#include "utils/logger.h"
#include <fstream>
#include <filesystem>
#include <sstream>
#include <iomanip>
#include <arpa/inet.h>
#include <unistd.h>
#include <sys/socket.h>

namespace fs = std::filesystem;

// SystemMetrics JSON conversion
json SystemMetrics::toJson() const {
    return {
        {"cpu_percent", cpu_percent},
        {"memory_used_mb", memory_used_mb},
        {"memory_total_mb", memory_total_mb},
        {"disk_used_mb", disk_used_mb},
        {"disk_total_mb", disk_total_mb},
        {"network_rx_mbps", network_rx_mbps},
        {"network_tx_mbps", network_tx_mbps}
    };
}

// CameraMetrics JSON conversion
json CameraMetrics::toJson() const {
    return {
        {"connected", connected},
        {"sdk_latency_ms", sdk_latency_ms},
        {"usb_traffic_mbps", usb_traffic_mbps},
        {"error_count", error_count}
    };
}

// NetworkMetrics JSON conversion
json NetworkMetrics::toJson() const {
    return {
        {"tcp_connected", tcp_connected},
        {"tcp_latency_ms", tcp_latency_ms},
        {"udp_loss_percent", udp_loss_percent},
        {"command_queue_depth", command_queue_depth}
    };
}

// SyncMetrics JSON conversion
json SyncMetrics::toJson() const {
    return {
        {"exposure_rate_hz", exposure_rate_hz},
        {"health_rate_hz", health_rate_hz},
        {"property_reads_sec", property_reads_sec}
    };
}

// HealthSnapshot JSON conversion
json HealthSnapshot::toJson() const {
    // Convert timestamp to ISO 8601 format
    auto time_t_val = std::chrono::system_clock::to_time_t(timestamp);
    auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(
        timestamp.time_since_epoch()) % 1000;

    std::stringstream timestamp_ss;
    timestamp_ss << std::put_time(std::gmtime(&time_t_val), "%Y-%m-%dT%H:%M:%S")
                 << '.' << std::setfill('0') << std::setw(3) << ms.count() << 'Z';

    return {
        {"timestamp", timestamp_ss.str()},
        {"system", system.toJson()},
        {"camera", camera.toJson()},
        {"network", network.toJson()},
        {"sync", sync.toJson()}
    };
}

HealthSnapshot HealthSnapshot::fromJson(const json& j) {
    HealthSnapshot snapshot;

    // Parse timestamp (simplified - would need proper ISO 8601 parsing)
    // For now, use current time if timestamp parsing fails
    snapshot.timestamp = std::chrono::system_clock::now();

    if (j.contains("system")) {
        auto sys = j["system"];
        snapshot.system.cpu_percent = sys.value("cpu_percent", 0.0f);
        snapshot.system.memory_used_mb = sys.value("memory_used_mb", 0ULL);
        snapshot.system.memory_total_mb = sys.value("memory_total_mb", 0ULL);
        snapshot.system.disk_used_mb = sys.value("disk_used_mb", 0ULL);
        snapshot.system.disk_total_mb = sys.value("disk_total_mb", 0ULL);
        snapshot.system.network_rx_mbps = sys.value("network_rx_mbps", 0.0f);
        snapshot.system.network_tx_mbps = sys.value("network_tx_mbps", 0.0f);
    }

    if (j.contains("camera")) {
        auto cam = j["camera"];
        snapshot.camera.connected = cam.value("connected", false);
        snapshot.camera.sdk_latency_ms = cam.value("sdk_latency_ms", 0.0f);
        snapshot.camera.usb_traffic_mbps = cam.value("usb_traffic_mbps", 0ULL);
        snapshot.camera.error_count = cam.value("error_count", 0U);
    }

    if (j.contains("network")) {
        auto net = j["network"];
        snapshot.network.tcp_connected = net.value("tcp_connected", false);
        snapshot.network.tcp_latency_ms = net.value("tcp_latency_ms", 0.0f);
        snapshot.network.udp_loss_percent = net.value("udp_loss_percent", 0.0f);
        snapshot.network.command_queue_depth = net.value("command_queue_depth", 0U);
    }

    if (j.contains("sync")) {
        auto sync = j["sync"];
        snapshot.sync.exposure_rate_hz = sync.value("exposure_rate_hz", 0.0f);
        snapshot.sync.health_rate_hz = sync.value("health_rate_hz", 0.0f);
        snapshot.sync.property_reads_sec = sync.value("property_reads_sec", 0U);
    }

    return snapshot;
}

// HealthMonitor implementation
HealthMonitor& HealthMonitor::getInstance() {
    static HealthMonitor instance;
    return instance;
}

void HealthMonitor::init() {
    std::lock_guard<std::mutex> lock(mutex_);
    Logger::info("HealthMonitor: Initialized");
}

void HealthMonitor::shutdown() {
    std::lock_guard<std::mutex> lock(mutex_);

    stopBroadcasting();
    disableArchive();

    Logger::info("HealthMonitor: Shutdown complete");
}

void HealthMonitor::updateSystemMetrics(const SystemMetrics& metrics) {
    std::lock_guard<std::mutex> lock(mutex_);
    current_system_ = metrics;
    recordSnapshot();
}

void HealthMonitor::updateCameraMetrics(const CameraMetrics& metrics) {
    std::lock_guard<std::mutex> lock(mutex_);
    current_camera_ = metrics;
}

void HealthMonitor::updateNetworkMetrics(const NetworkMetrics& metrics) {
    std::lock_guard<std::mutex> lock(mutex_);
    current_network_ = metrics;
}

void HealthMonitor::updateSyncMetrics(const SyncMetrics& metrics) {
    std::lock_guard<std::mutex> lock(mutex_);
    current_sync_ = metrics;
}

HealthSnapshot HealthMonitor::getCurrentSnapshot() const {
    std::lock_guard<std::mutex> lock(mutex_);

    HealthSnapshot snapshot;
    snapshot.timestamp = std::chrono::system_clock::now();
    snapshot.system = current_system_;
    snapshot.camera = current_camera_;
    snapshot.network = current_network_;
    snapshot.sync = current_sync_;

    return snapshot;
}

std::vector<HealthSnapshot> HealthMonitor::getRecentHistory(int minutes) const {
    std::lock_guard<std::mutex> lock(mutex_);

    auto cutoff_time = std::chrono::system_clock::now() - std::chrono::minutes(minutes);
    std::vector<HealthSnapshot> result;

    for (const auto& snapshot : ram_buffer_) {
        if (snapshot.timestamp >= cutoff_time) {
            result.push_back(snapshot);
        }
    }

    return result;
}

void HealthMonitor::startBroadcasting(const std::string& ground_ip, int port) {
    std::lock_guard<std::mutex> lock(mutex_);

    if (broadcasting_enabled_) {
        stopBroadcasting();
    }

    ground_ip_ = ground_ip;
    broadcast_port_ = port;

    // Create UDP socket
    broadcast_socket_ = socket(AF_INET, SOCK_DGRAM, 0);
    if (broadcast_socket_ < 0) {
        Logger::error("HealthMonitor: Failed to create UDP socket for broadcasting");
        return;
    }

    broadcasting_enabled_ = true;
    Logger::info("HealthMonitor: Started broadcasting to " + ground_ip + ":" + std::to_string(port));
}

void HealthMonitor::stopBroadcasting() {
    if (broadcast_socket_ >= 0) {
        close(broadcast_socket_);
        broadcast_socket_ = -1;
    }
    broadcasting_enabled_ = false;
}

void HealthMonitor::enableArchive(const std::string& archive_dir, int retention_days) {
    std::lock_guard<std::mutex> lock(mutex_);

    archive_dir_ = archive_dir;
    archive_retention_days_ = retention_days;

    // Create archive directory if it doesn't exist
    fs::create_directories(archive_dir);

    archive_enabled_ = true;
    Logger::info("HealthMonitor: Enabled archiving to " + archive_dir);
}

void HealthMonitor::disableArchive() {
    std::lock_guard<std::mutex> lock(mutex_);
    archive_enabled_ = false;
}

void HealthMonitor::recordSnapshot() {
    // Build snapshot
    HealthSnapshot snapshot;
    snapshot.timestamp = std::chrono::system_clock::now();
    snapshot.system = current_system_;
    snapshot.camera = current_camera_;
    snapshot.network = current_network_;
    snapshot.sync = current_sync_;

    // Add to RAM ring buffer
    ram_buffer_.push_back(snapshot);
    if (ram_buffer_.size() > ram_buffer_max_size_) {
        ram_buffer_.pop_front();
    }

    // Check thresholds
    checkThresholds(snapshot);

    // Broadcast if enabled
    if (broadcasting_enabled_) {
        broadcastSnapshot(snapshot);
    }

    // Archive if enabled
    if (archive_enabled_) {
        archiveSnapshot(snapshot);
    }
}

void HealthMonitor::checkThresholds(const HealthSnapshot& snapshot) {
    // Check CPU
    int cpu_warn = CONFIG_INT("health.thresholds.cpu_warn");
    int cpu_crit = CONFIG_INT("health.thresholds.cpu_critical");

    if (snapshot.system.cpu_percent >= cpu_crit) {
        Logger::error("HealthMonitor: CPU usage critical: " +
                      std::to_string(snapshot.system.cpu_percent) + "%");
    } else if (snapshot.system.cpu_percent >= cpu_warn) {
        Logger::warning("HealthMonitor: CPU usage warning: " +
                        std::to_string(snapshot.system.cpu_percent) + "%");
    }

    // Check memory
    int mem_warn = CONFIG_INT("health.thresholds.memory_warn_mb");
    int mem_crit = CONFIG_INT("health.thresholds.memory_critical_mb");

    if (snapshot.system.memory_used_mb >= static_cast<uint64_t>(mem_crit)) {
        Logger::error("HealthMonitor: Memory usage critical: " +
                      std::to_string(snapshot.system.memory_used_mb) + " MB");
    } else if (snapshot.system.memory_used_mb >= static_cast<uint64_t>(mem_warn)) {
        Logger::warning("HealthMonitor: Memory usage warning: " +
                        std::to_string(snapshot.system.memory_used_mb) + " MB");
    }

    // Check camera latency
    int cam_latency_warn = CONFIG_INT("health.thresholds.camera_latency_warn_ms");
    int cam_latency_crit = CONFIG_INT("health.thresholds.camera_latency_critical_ms");

    if (snapshot.camera.sdk_latency_ms >= cam_latency_crit) {
        Logger::error("HealthMonitor: Camera latency critical: " +
                      std::to_string(snapshot.camera.sdk_latency_ms) + " ms");
    } else if (snapshot.camera.sdk_latency_ms >= cam_latency_warn) {
        Logger::warning("HealthMonitor: Camera latency warning: " +
                        std::to_string(snapshot.camera.sdk_latency_ms) + " ms");
    }

    // Check command queue depth
    int queue_warn = CONFIG_INT("health.thresholds.queue_depth_warn");
    int queue_crit = CONFIG_INT("health.thresholds.queue_depth_critical");

    if (snapshot.network.command_queue_depth >= static_cast<uint32_t>(queue_crit)) {
        Logger::error("HealthMonitor: Command queue depth critical: " +
                      std::to_string(snapshot.network.command_queue_depth));
    } else if (snapshot.network.command_queue_depth >= static_cast<uint32_t>(queue_warn)) {
        Logger::warning("HealthMonitor: Command queue depth warning: " +
                        std::to_string(snapshot.network.command_queue_depth));
    }
}

void HealthMonitor::broadcastSnapshot(const HealthSnapshot& snapshot) {
    if (broadcast_socket_ < 0) {
        return;
    }

    // Convert to JSON and send via UDP
    json data = snapshot.toJson();
    std::string json_str = data.dump();

    sockaddr_in dest_addr{};
    dest_addr.sin_family = AF_INET;
    dest_addr.sin_port = htons(broadcast_port_);

    if (inet_pton(AF_INET, ground_ip_.c_str(), &dest_addr.sin_addr) <= 0) {
        Logger::error("HealthMonitor: Invalid broadcast IP: " + ground_ip_);
        return;
    }

    ssize_t sent = sendto(broadcast_socket_, json_str.c_str(), json_str.length(), 0,
                          reinterpret_cast<sockaddr*>(&dest_addr), sizeof(dest_addr));

    if (sent < 0) {
        Logger::error("HealthMonitor: Failed to broadcast health snapshot");
    }
}

void HealthMonitor::archiveSnapshot(const HealthSnapshot& snapshot) {
    // Get current date for filename
    auto time_t_val = std::chrono::system_clock::to_time_t(snapshot.timestamp);
    std::tm tm = *std::gmtime(&time_t_val);

    std::stringstream filename_ss;
    filename_ss << archive_dir_ << "/health_"
                << std::put_time(&tm, "%Y%m%d") << ".jsonl";

    std::string filename = filename_ss.str();

    // Append snapshot to file (JSON Lines format)
    try {
        std::ofstream file(filename, std::ios::app);
        if (file.is_open()) {
            file << snapshot.toJson().dump() << '\n';
            file.close();
        }
    } catch (const std::exception& e) {
        Logger::error("HealthMonitor: Failed to archive snapshot: " + std::string(e.what()));
    }

    // Cleanup old archives
    cleanupOldArchives();
}

void HealthMonitor::cleanupOldArchives() {
    auto cutoff_time = std::chrono::system_clock::now() -
                       std::chrono::hours(24 * archive_retention_days_);

    try {
        for (const auto& entry : fs::directory_iterator(archive_dir_)) {
            if (entry.is_regular_file()) {
                auto file_time = fs::last_write_time(entry);
                auto sctp = std::chrono::time_point_cast<std::chrono::system_clock::duration>(
                    file_time - fs::file_time_type::clock::now() + std::chrono::system_clock::now());

                if (sctp < cutoff_time) {
                    fs::remove(entry);
                    Logger::info("HealthMonitor: Removed old archive: " + entry.path().string());
                }
            }
        }
    } catch (const std::exception& e) {
        Logger::error("HealthMonitor: Failed to cleanup old archives: " + std::string(e.what()));
    }
}
