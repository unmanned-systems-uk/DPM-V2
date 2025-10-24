FROM ubuntu:22.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    g++ \
    libxml2-dev \
    nlohmann-json3-dev \
    libudev-dev \
    libusb-1.0-0-dev \
    usbutils \
    vim \
    less \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Create directories for mounted volumes
RUN mkdir -p /workspace/sbc /workspace/sdk

# Default command
CMD ["/bin/bash"]
