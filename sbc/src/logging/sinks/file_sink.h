#ifndef FILE_SINK_H
#define FILE_SINK_H

#include "../log_sink.h"
#include <fstream>
#include <string>
#include <mutex>

class FileSink : public LogSink {
public:
    FileSink(const std::string& file_path, size_t max_size_mb = 50, int max_rotated = 3);
    ~FileSink() override;

    void write(const json& log_entry) override;
    void flush() override;
    std::string name() const override;

private:
    void openFile();
    void closeFile();
    void rotateFile();
    size_t getFileSize();

    std::string file_path_;
    size_t max_size_bytes_;
    int max_rotated_;
    std::ofstream file_;
    std::mutex mutex_;
};

#endif // FILE_SINK_H
