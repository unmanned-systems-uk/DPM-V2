cmake_minimum_required(VERSION 3.16)
project(payload_manager VERSION 1.0.0 LANGUAGES CXX)

# C++17 standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS NO)

# Compiler warnings
add_compile_options(-Wall -Wextra -Wpedantic -fsigned-char)

# Add optimization for Release builds
if(CMAKE_BUILD_TYPE STREQUAL "Release")
    add_compile_options(-O3)
elseif(CMAKE_BUILD_TYPE STREQUAL "Debug")
    add_compile_options(-g -O0)
endif()

# RPATH configuration for runtime library loading
set(CMAKE_BUILD_RPATH "$ORIGIN")
set(CMAKE_INSTALL_RPATH "$ORIGIN")
set(CMAKE_BUILD_RPATH_USE_ORIGIN ON)

# Sony SDK paths (prepared for Phase 2, not used in Phase 1)
# Auto-detect if running in Docker container or on host
if(EXISTS "/workspace/sdk")
    set(SONY_SDK_ROOT "/workspace/sdk")
    message(STATUS "Detected Docker environment - using /workspace/sdk")
elseif(EXISTS "/app/sdk")
    set(SONY_SDK_ROOT "/app/sdk")
    message(STATUS "Detected Docker environment - using /app/sdk")
else()
    set(SONY_SDK_ROOT "/home/dpm/SonySDK/CrSDK_v2.00.00_20250805a_Linux64ARMv8")
    message(STATUS "Using host Sony SDK path")
endif()

set(SONY_SDK_INCLUDE "${SONY_SDK_ROOT}/app")
set(SONY_SDK_LIB_DIR "${SONY_SDK_ROOT}/external/crsdk")
set(SONY_SDK_ADAPTER_DIR "${SONY_SDK_LIB_DIR}/CrAdapter")

# Include directories
include_directories(${CMAKE_SOURCE_DIR}/src)

# Source files
set(SOURCES
    src/main.cpp
    src/utils/logger.cpp
    src/utils/system_info.cpp
    src/protocol/tcp_server.cpp
    src/protocol/udp_broadcaster.cpp
    src/protocol/heartbeat.cpp
    src/camera/camera_sony.cpp
)

# Create executable
add_executable(payload_manager ${SOURCES})

# Add Sony SDK include directories for payload_manager
target_include_directories(payload_manager
    PRIVATE
        ${SONY_SDK_INCLUDE}
)

# Link libraries (Phase 2 - with Sony SDK)
# NOTE: Only link libCr_Core.so - adapters are loaded dynamically by SDK from ./CrAdapter/
target_link_libraries(payload_manager
    PRIVATE
        -Wl,--no-as-needed
        pthread
        ${SONY_SDK_LIB_DIR}/libCr_Core.so
        xml2
        -Wl,--as-needed
)

# Try to find nlohmann/json via system package
find_package(nlohmann_json 3.0 QUIET)
if(nlohmann_json_FOUND)
    message(STATUS "Found nlohmann/json via package")
    target_link_libraries(payload_manager PRIVATE nlohmann_json::nlohmann_json)
else()
    # Use header-only from system include path
    message(STATUS "Using nlohmann/json header-only from system")
    # Headers should be in /usr/include/nlohmann/
endif()

# Set RPATH for payload_manager to find Sony SDK libraries
set_target_properties(payload_manager PROPERTIES
    BUILD_RPATH "${SONY_SDK_LIB_DIR}:${SONY_SDK_ADAPTER_DIR}"
    INSTALL_RPATH "${SONY_SDK_LIB_DIR}:${SONY_SDK_ADAPTER_DIR}"
)

# GCC version check for filesystem library
if(UNIX AND NOT APPLE)
    if("${CMAKE_CXX_COMPILER_ID}" STREQUAL "GNU")
        if(CMAKE_CXX_COMPILER_VERSION VERSION_LESS 9)
            # Must explicitly link separate std::filesystem if older than GCC9
            message(STATUS "GCC version less than 9. Explicitly linking std::filesystem library.")
            target_link_libraries(payload_manager PRIVATE stdc++fs)
        endif()
    endif()
endif()

# Installation
install(TARGETS payload_manager DESTINATION /usr/local/bin)

# ============================================================
# Camera Test Program (for testing Sony SDK connectivity)
# ============================================================

# Create test_camera executable
add_executable(test_camera src/test_camera.cpp)

# Add Sony SDK include directories for test_camera
target_include_directories(test_camera
    PRIVATE
        ${SONY_SDK_INCLUDE}
)

# Link Sony SDK libraries for test_camera
# NOTE: Only link libCr_Core.so - adapters are loaded dynamically by SDK
target_link_libraries(test_camera
    PRIVATE
        -Wl,--no-as-needed
        pthread
        ${SONY_SDK_LIB_DIR}/libCr_Core.so
        xml2
        -Wl,--as-needed
)

# GCC version check for filesystem library (test_camera)
if(UNIX AND NOT APPLE)
    if("${CMAKE_CXX_COMPILER_ID}" STREQUAL "GNU")
        if(CMAKE_CXX_COMPILER_VERSION VERSION_LESS 9)
            target_link_libraries(test_camera PRIVATE stdc++fs)
        endif()
    endif()
endif()

# Set RPATH for test_camera to find Sony SDK libraries
set_target_properties(test_camera PROPERTIES
    BUILD_RPATH "${SONY_SDK_LIB_DIR}:${SONY_SDK_ADAPTER_DIR}"
    INSTALL_RPATH "${SONY_SDK_LIB_DIR}:${SONY_SDK_ADAPTER_DIR}"
)

message(STATUS "Camera test program enabled with Sony SDK support")
message(STATUS "Sony SDK Include: ${SONY_SDK_INCLUDE}")
message(STATUS "Sony SDK Library: ${SONY_SDK_LIB_DIR}")

# ============================================================
# Shutter Test Program (for testing camera control)
# ============================================================

# Create test_shutter executable
add_executable(test_shutter src/test_shutter.cpp)

# Add Sony SDK include directories
target_include_directories(test_shutter
    PRIVATE
        ${SONY_SDK_INCLUDE}
)

# Link Sony SDK libraries
target_link_libraries(test_shutter
    PRIVATE
        -Wl,--no-as-needed
        pthread
        ${SONY_SDK_LIB_DIR}/libCr_Core.so
        xml2
        -Wl,--as-needed
)

# Set RPATH for test_shutter
set_target_properties(test_shutter PROPERTIES
    BUILD_RPATH "${SONY_SDK_LIB_DIR}:${SONY_SDK_ADAPTER_DIR}"
    INSTALL_RPATH "${SONY_SDK_LIB_DIR}:${SONY_SDK_ADAPTER_DIR}"
)

message(STATUS "Shutter test program enabled")

# ============================================================
# Property Mapping Test Program (automated mapping discovery)
# ============================================================

# Create test_property_mapping executable
add_executable(test_property_mapping
    src/test_property_mapping.cpp
    src/camera/camera_sony.cpp
    src/utils/logger.cpp
)

# Add include directories
target_include_directories(test_property_mapping
    PRIVATE
        ${CMAKE_SOURCE_DIR}/src
        ${SONY_SDK_INCLUDE}
)

# Link Sony SDK libraries and dependencies
target_link_libraries(test_property_mapping
    PRIVATE
        -Wl,--no-as-needed
        pthread
        ${SONY_SDK_LIB_DIR}/libCr_Core.so
        xml2
        -Wl,--as-needed
)

# Set RPATH for test_property_mapping
set_target_properties(test_property_mapping PROPERTIES
    BUILD_RPATH "${SONY_SDK_LIB_DIR}:${SONY_SDK_ADAPTER_DIR}"
    INSTALL_RPATH "${SONY_SDK_LIB_DIR}:${SONY_SDK_ADAPTER_DIR}"
)

message(STATUS "Property mapping test program enabled")

# ============================================================
# Shutter Speed Discovery Tool
# ============================================================

add_executable(discover_shutter_speeds src/discover_shutter_speeds.cpp)

target_include_directories(discover_shutter_speeds
    PRIVATE
        ${SONY_SDK_INCLUDE}
)

target_link_libraries(discover_shutter_speeds
    PRIVATE
        -Wl,--no-as-needed
        pthread
        ${SONY_SDK_LIB_DIR}/libCr_Core.so
        xml2
        -Wl,--as-needed
)

set_target_properties(discover_shutter_speeds PROPERTIES
    BUILD_RPATH "${SONY_SDK_LIB_DIR}:${SONY_SDK_ADAPTER_DIR}"
    INSTALL_RPATH "${SONY_SDK_LIB_DIR}:${SONY_SDK_ADAPTER_DIR}"
)

message(STATUS "Shutter speed discovery tool enabled")

# ============================================================

# Print build configuration
message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "C++ compiler: ${CMAKE_CXX_COMPILER_ID} ${CMAKE_CXX_COMPILER_VERSION}")
message(STATUS "C++ standard: ${CMAKE_CXX_STANDARD}")
message(STATUS "Install prefix: ${CMAKE_INSTALL_PREFIX}")

# ============================================================
# Integration Test Program (for testing components without network)
# ============================================================

# Create test_integration executable
add_executable(test_integration 
    src/test_integration.cpp
    src/utils/logger.cpp
    src/utils/system_info.cpp
    src/camera/camera_sony.cpp
)

# Add include directories
target_include_directories(test_integration
    PRIVATE
        ${CMAKE_SOURCE_DIR}/src
        ${SONY_SDK_INCLUDE}
)

# Link libraries
target_link_libraries(test_integration
    PRIVATE
        -Wl,--no-as-needed
        pthread
        ${SONY_SDK_LIB_DIR}/libCr_Core.so
        xml2
        -Wl,--as-needed
)

# nlohmann/json
if(nlohmann_json_FOUND)
    target_link_libraries(test_integration PRIVATE nlohmann_json::nlohmann_json)
endif()

# Set RPATH
set_target_properties(test_integration PROPERTIES
    BUILD_RPATH "${SONY_SDK_LIB_DIR}:${SONY_SDK_ADAPTER_DIR}"
    INSTALL_RPATH "${SONY_SDK_LIB_DIR}:${SONY_SDK_ADAPTER_DIR}"
)

message(STATUS "Integration test program enabled")

