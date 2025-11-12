#include "file_sink.h"
#include <filesystem>
#include <iostream>

namespace fs = std::filesystem;

FileSink::FileSink(const std::string& file_path, size_t max_size_mb, int max_rotated)
    : file_path_(file_path), max_size_bytes_(max_size_mb * 1024 * 1024), max_rotated_(max_rotated) {
    openFile();
}

FileSink::~FileSink() {
    closeFile();
}

void FileSink::write(const json& log_entry) {
    std::lock_guard<std::mutex> lock(mutex_);

    if (!file_.is_open()) {
        openFile();
    }

    // Write as JSON Lines format (one JSON object per line)
    file_ << log_entry.dump() << '\n';

    // Check if rotation is needed
    if (getFileSize() >= max_size_bytes_) {
        rotateFile();
    }
}

void FileSink::flush() {
    std::lock_guard<std::mutex> lock(mutex_);
    if (file_.is_open()) {
        file_.flush();
    }
}

std::string FileSink::name() const {
    return "file:" + file_path_;
}

void FileSink::openFile() {
    // Create parent directory if it doesn't exist
    fs::path file_path(file_path_);
    if (file_path.has_parent_path()) {
        fs::create_directories(file_path.parent_path());
    }

    file_.open(file_path_, std::ios::out | std::ios::app);
    if (!file_.is_open()) {
        std::cerr << "FileSink: Failed to open log file: " << file_path_ << std::endl;
    }
}

void FileSink::closeFile() {
    if (file_.is_open()) {
        file_.flush();
        file_.close();
    }
}

void FileSink::rotateFile() {
    closeFile();

    // Rotate existing files: file.2 -> file.3, file.1 -> file.2, file -> file.1
    for (int i = max_rotated_ - 1; i >= 1; i--) {
        std::string old_path = file_path_ + "." + std::to_string(i);
        std::string new_path = file_path_ + "." + std::to_string(i + 1);

        if (fs::exists(old_path)) {
            if (i == max_rotated_ - 1) {
                // Delete oldest file
                fs::remove(old_path);
            } else {
                // Rename file
                fs::rename(old_path, new_path);
            }
        }
    }

    // Rename current file to .1
    if (fs::exists(file_path_)) {
        std::string backup_path = file_path_ + ".1";
        fs::rename(file_path_, backup_path);
    }

    // Open new file
    openFile();
}

size_t FileSink::getFileSize() {
    if (!file_.is_open()) {
        return 0;
    }

    // Get current position
    auto pos = file_.tellp();
    if (pos < 0) {
        // If tellp() fails, check file size on disk
        if (fs::exists(file_path_)) {
            return fs::file_size(file_path_);
        }
        return 0;
    }

    return static_cast<size_t>(pos);
}
