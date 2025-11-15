#ifndef NETWORK_SINK_H
#define NETWORK_SINK_H

#include "../log_sink.h"
#include <string>
#include <mutex>
#include <chrono>
#include <set>
#include <sys/socket.h>
#include <netinet/in.h>

class NetworkSink : public LogSink {
public:
    NetworkSink(const std::string& ground_ip, int ground_port,
                const std::string& systemtools_ip, int systemtools_port,
                bool systemtools_enabled);
    ~NetworkSink() override;

    void write(const json& log_entry) override;
    void flush() override;
    std::string name() const override;

    // Ground-Side on-demand streaming control
    void enableGroundStreaming(int duration_sec = 300);
    void disableGroundStreaming();
    bool isGroundStreamingEnabled() const;

    // Dynamic client IP management (like UDP broadcaster)
    void addClient(const std::string& client_ip);
    void removeClient(const std::string& client_ip);
    size_t getClientCount() const;

    // Dynamic SystemTools IP update (resolves Issue #99 for Air-Side)
    void setSystemToolsIP(const std::string& ip);

private:
    void sendUDP(const std::string& ip, int port, const std::string& data);
    void checkGroundStreamingTimeout();

    std::string ground_ip_;
    int ground_port_;
    std::string systemtools_ip_;
    int systemtools_port_;
    bool systemtools_enabled_;

    bool ground_streaming_enabled_;
    std::chrono::system_clock::time_point ground_streaming_end_time_;

    // Dynamic client IP tracking (for Ground-Side log streaming)
    std::set<std::string> client_ips_;

    int socket_fd_;
    mutable std::mutex mutex_;
};

#endif // NETWORK_SINK_H
