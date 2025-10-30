# Dockerfile for RemoteCli v2 Diagnostic Tool
# Enhanced Sony SDK RemoteCli with comprehensive logging for debugging camera issues
FROM ubuntu:22.04

# Prevent interactive prompts during build
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/London

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    g++ \
    libxml2-dev \
    libusb-1.0-0-dev \
    udev \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy Sony SDK (will be mounted or copied during build)
# SDK structure should be at /sdk
COPY sony_sdk/ /sdk/

# Copy RemoteCli v2 source with enhanced logging
COPY remotecli_v2/ /app/remotecli_v2/

# Build RemoteCli v2
WORKDIR /app/remotecli_v2/build
RUN cmake .. && make -j4

# Create logs directory
RUN mkdir -p /app/logs

# Set up USB permissions for camera access
RUN echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="054c", MODE="0666"' > /etc/udev/rules.d/99-sony-camera.rules

# Runtime environment
WORKDIR /app/remotecli_v2/build
ENV LD_LIBRARY_PATH=/sdk/external/crsdk:$LD_LIBRARY_PATH

# Default command - run RemoteCli v2 with logging
CMD ["./RemoteCli_v2"]
