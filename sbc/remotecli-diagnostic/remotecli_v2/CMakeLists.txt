cmake_minimum_required(VERSION 3.10)
project(RemoteCli_v2 LANGUAGES CXX)

# C++17 standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED YES)
set(CMAKE_CXX_EXTENSIONS NO)

# Build type
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

# Compiler flags
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall")
set(CMAKE_CXX_FLAGS_DEBUG "-g -O0")
set(CMAKE_CXX_FLAGS_RELEASE "-O3")

# Specify char is signed-char
if(UNIX AND NOT APPLE)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fsigned-char -fstack-protector-all")
endif()

# Source files
set(SOURCES
    src/RemoteCli_v2.cpp
    src/CameraDevice.cpp
    src/ConnectionInfo.cpp
    src/CrDebugString.cpp
    src/MessageDefine.cpp
    src/PropertyValueTable.cpp
    src/Text.cpp
)

# Executable
add_executable(RemoteCli_v2 ${SOURCES})

# Include directories
target_include_directories(RemoteCli_v2 PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/src
    ${CMAKE_CURRENT_SOURCE_DIR}/src/CRSDK
)

# Sony SDK library paths
set(SDK_DIR "/sdk")
set(SDK_LIB_DIR "${SDK_DIR}/external/crsdk")

# Find Sony SDK library
find_library(CAMERA_REMOTE_LIB
    NAMES Cr_Core
    HINTS ${SDK_LIB_DIR}
    REQUIRED
)

# Link libraries
target_link_libraries(RemoteCli_v2 PRIVATE
    ${CAMERA_REMOTE_LIB}
    xml2
    pthread
    stdc++fs
)

# RPATH for runtime library loading
set_target_properties(RemoteCli_v2 PROPERTIES
    BUILD_RPATH "${SDK_LIB_DIR}"
    INSTALL_RPATH "${SDK_LIB_DIR}"
)

# Install target
install(TARGETS RemoteCli_v2
    RUNTIME DESTINATION /app/bin
)

# Print configuration summary
message(STATUS "")
message(STATUS "===== RemoteCli v2 Build Configuration =====")
message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "C++ Standard: ${CMAKE_CXX_STANDARD}")
message(STATUS "SDK directory: ${SDK_DIR}")
message(STATUS "SDK library: ${CAMERA_REMOTE_LIB}")
message(STATUS "==========================================")
message(STATUS "")
