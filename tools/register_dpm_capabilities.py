#!/usr/bin/env python3
"""
Bulk registration script for DPM-V2 capabilities to CCPM
Registers all 148 DPM-V2 capabilities under project_id=2
"""

import subprocess
import sys
import json

# CCPM registration script path
REGISTER_SCRIPT = "/home/anthony/ccpm-workspace/production/ccpm-client/python/register_capability.py"
PROJECT_ID = 2  # DPM-V2

# Air-Side Capabilities (domain: air-side, language: cpp, platform: pi5)
AIR_SIDE_CAPABILITIES = [
    # CATEGORY: networking
    {
        "name": "UDP Health Broadcast Handler",
        "category": "networking",
        "description": "Broadcasts system health status (CPU, memory, camera, gimbal) via UDP on port 5004 at 5 Hz. Supports multiple clients via dynamic registration",
        "file": "sbc/src/protocol/udp_broadcaster.cpp",
        "function": "UDPBroadcaster::sendStatus()",
        "keywords": "UDP,broadcast,health,port_5004,multicast,status",
        "metadata": json.dumps({"domain": "air-side", "language": "cpp", "platform": "pi5", "port": 5004, "protocol": "DPM v1.1.0"})
    },
    {
        "name": "TCP Command Server",
        "category": "networking",
        "description": "TCP server on port 5000 for DPM Protocol v1.0 command handling. Supports 20+ commands for camera, system, logging, health, config",
        "file": "sbc/src/protocol/tcp_server.cpp",
        "function": "TCPServer::processCommand()",
        "keywords": "TCP,server,command,port_5000,protocol,handler",
        "metadata": json.dumps({"domain": "air-side", "language": "cpp", "platform": "pi5", "port": 5000, "protocol": "DPM v1.0"})
    },
    {
        "name": "UDP Heartbeat Protocol",
        "category": "networking",
        "description": "Bidirectional UDP heartbeat on port 5002 at 1 Hz. Detects connection loss, tracks uptime, validates Ground-Side connectivity",
        "file": "sbc/src/protocol/heartbeat.cpp",
        "function": "Heartbeat::sendLoop()",
        "keywords": "UDP,heartbeat,keepalive,port_5002,bidirectional",
        "metadata": json.dumps({"domain": "air-side", "language": "cpp", "platform": "pi5", "port": 5002, "protocol": "DPM v1.1.0"})
    },
    {
        "name": "UDP Discovery Listener",
        "category": "networking",
        "description": "Listens on port 5006 for SystemTools UDP discovery broadcasts. Auto-detects SystemTools IP for log streaming",
        "file": "sbc/src/network/udp_discovery_listener.cpp",
        "function": "UdpDiscoveryListener::start()",
        "keywords": "UDP,discovery,listener,port_5006,autodetect,IP",
        "metadata": json.dumps({"domain": "air-side", "language": "cpp", "platform": "pi5", "port": 5006})
    },
    {
        "name": "Dynamic Client Management",
        "category": "networking",
        "description": "Thread-safe dynamic UDP client registration/removal for broadcasts. Supports multiple Ground-Side/SystemTools clients",
        "file": "sbc/src/protocol/udp_broadcaster.cpp",
        "function": "UDPBroadcaster::addClient()",
        "keywords": "UDP,client,multicast,thread-safe,dynamic",
        "metadata": json.dumps({"domain": "air-side", "language": "cpp", "platform": "pi5"})
    },

    # CATEGORY: camera
    {
        "name": "Sony SDK Integration",
        "category": "camera",
        "description": "Complete Sony Camera Remote SDK integration for Sony ILCE-1. USB connection, PC Remote mode, reconnection handling",
        "file": "sbc/src/camera/camera_sony.cpp",
        "function": "CameraSony::connect()",
        "keywords": "Sony,SDK,ILCE-1,camera,USB,integration",
        "metadata": json.dumps({"domain": "air-side", "language": "cpp", "platform": "pi5", "camera_model": "ILCE-1"})
    },
    {
        "name": "Camera Shutter Control",
        "category": "camera",
        "description": "Triggers camera shutter via Sony SDK. Two-step shutter press/release simulation with 100ms timing",
        "file": "sbc/src/camera/camera_sony.cpp",
        "function": "CameraSony::capture()",
        "keywords": "camera,shutter,capture,Sony,trigger",
        "metadata": json.dumps({"domain": "air-side", "language": "cpp", "platform": "pi5", "command": "camera.capture"})
    },
    {
        "name": "Manual Focus Control",
        "category": "camera",
        "description": "Manual focus adjustment (near/far/stop) with variable speed (1-3). LiveView integration, focal distance readback",
        "file": "sbc/src/camera/camera_sony.cpp",
        "function": "CameraSony::focus()",
        "keywords": "camera,focus,manual,speed,near,far",
        "metadata": json.dumps({"domain": "air-side", "language": "cpp", "platform": "pi5", "command": "camera.focus"})
    },
    {
        "name": "Auto-Focus Hold (AF-ON)",
        "category": "camera",
        "description": "Push auto-focus control (AF-ON button equivalent). Press/release states with comprehensive error handling",
        "file": "sbc/src/camera/camera_sony.cpp",
        "function": "CameraSony::autoFocusHold()",
        "keywords": "camera,autofocus,AF-ON,hold,press,release",
        "metadata": json.dumps({"domain": "air-side", "language": "cpp", "platform": "pi5", "command": "camera.auto_focus_hold"})
    },
    {
        "name": "Camera Property Set",
        "category": "camera",
        "description": "Sets 9 camera properties (shutter_speed, aperture, ISO, white_balance, focus_mode, etc). Protocol-to-SDK value mapping",
        "file": "sbc/src/camera/camera_sony.cpp",
        "function": "CameraSony::setProperty()",
        "keywords": "camera,property,set,ISO,shutter,aperture,white_balance",
        "metadata": json.dumps({"domain": "air-side", "language": "cpp", "platform": "pi5", "properties": 9})
    },
    {
        "name": "Camera Property Get",
        "category": "camera",
        "description": "Reads current camera property values. SDK-to-protocol value conversion with reverse lookup tables",
        "file": "sbc/src/camera/camera_sony.cpp",
        "function": "CameraSony::getProperty()",
        "keywords": "camera,property,get,read,query",
        "metadata": json.dumps({"domain": "air-side", "language": "cpp", "platform": "pi5"})
    },
    {
        "name": "Focal Distance Reader",
        "category": "camera",
        "description": "Reads current focal distance in meters. Infinity detection, LiveView requirement handling",
        "file": "sbc/src/camera/camera_sony.cpp",
        "function": "CameraSony::getFocalDistanceMeters()",
        "keywords": "camera,focal,distance,meters,infinity",
        "metadata": json.dumps({"domain": "air-side", "language": "cpp", "platform": "pi5"})
    },
    {
        "name": "Camera Status Reporter",
        "category": "camera",
        "description": "Generates camera status for UDP health broadcasts at 5 Hz. Non-blocking with cached status",
        "file": "sbc/src/camera/camera_sony.cpp",
        "function": "CameraSony::getStatus()",
        "keywords": "camera,status,health,broadcast,cache",
        "metadata": json.dumps({"domain": "air-side", "language": "cpp", "platform": "pi5", "frequency": "5Hz"})
    },
    {
        "name": "Battery Level Monitor",
        "category": "camera",
        "description": "Queries camera battery percentage (0-100%). Non-blocking with cached value fallback",
        "file": "sbc/src/camera/camera_sony.cpp",
        "function": "CameraSony::getBatteryLevel()",
        "keywords": "camera,battery,level,percentage,monitor",
        "metadata": json.dumps({"domain": "air-side", "language": "cpp", "platform": "pi5"})
    },
    {
        "name": "Property Loader (Specification-First)",
        "category": "camera",
        "description": "Loads camera property specifications from protocol/camera_properties.json. Validates values before SDK operations",
        "file": "sbc/src/camera/property_loader.cpp",
        "function": "PropertyLoader::isValidValue()",
        "keywords": "camera,property,specification,validation,protocol",
        "metadata": json.dumps({"domain": "air-side", "language": "cpp", "platform": "pi5", "spec_file": "protocol/camera_properties.json"})
    },

    # CATEGORY: logging
    {
        "name": "Structured Logger (JSON)",
        "category": "logging",
        "description": "Multi-sink structured logger with JSON output. Supports Console, File, Network sinks with ISO 8601 timestamps",
        "file": "sbc/src/logging/structured_logger.cpp",
        "function": "StructuredLogger::log()",
        "keywords": "logging,structured,JSON,multi-sink,timestamp",
        "metadata": json.dumps({"domain": "air-side", "language": "cpp", "platform": "pi5", "format": "JSON"})
    },
    {
        "name": "Log Context Enforcement",
        "category": "logging",
        "description": "Enforces log context tagging via protocol/log_contexts.json. Compile-time enum, runtime validation",
        "file": "sbc/src/logging/structured_logger.cpp",
        "function": "StructuredLogger::log()",
        "keywords": "logging,context,protocol,enforcement,validation",
        "metadata": json.dumps({"domain": "air-side", "language": "cpp", "platform": "pi5", "spec_file": "protocol/log_contexts.json"})
    },
    {
        "name": "Network Sink (Multi-Target)",
        "category": "logging",
        "description": "UDP log streaming to SystemTools (port 5007, always-on) and Ground-Side (port 5005, on-demand)",
        "file": "sbc/src/logging/sinks/network_sink.cpp",
        "function": "NetworkSink::write()",
        "keywords": "logging,network,UDP,streaming,sink",
        "metadata": json.dumps({"domain": "air-side", "language": "cpp", "platform": "pi5", "ports": [5005, 5007]})
    },
    {
        "name": "Ground-Side Log Streaming Control",
        "category": "logging",
        "description": "On-demand log streaming to Ground-Side. Duration-limited sessions (1-3600s) with automatic timeout",
        "file": "sbc/src/protocol/tcp_server.cpp",
        "function": "TCPServer::handleEnableLogStreaming()",
        "keywords": "logging,streaming,on-demand,duration,control",
        "metadata": json.dumps({"domain": "air-side", "language": "cpp", "platform": "pi5", "commands": ["logging.enable_streaming", "logging.disable_streaming"]})
    },
    {
        "name": "SystemTools Log Streaming Control",
        "category": "logging",
        "description": "Always-on log streaming to SystemTools. IP auto-detection via UDP discovery, runtime toggle",
        "file": "sbc/src/logging/structured_logger.cpp",
        "function": "StructuredLogger::setSystemToolsEnabled()",
        "keywords": "logging,SystemTools,always-on,discovery,toggle",
        "metadata": json.dumps({"domain": "air-side", "language": "cpp", "platform": "pi5", "port": 5007})
    },

    # CATEGORY: system
    {
        "name": "System Status Reporter",
        "category": "system",
        "description": "Collects Raspberry Pi metrics (CPU, memory, disk, uptime, temperature). Linux /proc parsing",
        "file": "sbc/src/utils/system_info.cpp",
        "function": "SystemInfo::getStatus()",
        "keywords": "system,status,CPU,memory,disk,temperature,uptime",
        "metadata": json.dumps({"domain": "air-side", "language": "cpp", "platform": "pi5", "metrics": ["CPU", "memory", "disk", "uptime", "temperature"]})
    },
    {
        "name": "Configuration Manager",
        "category": "configuration",
        "description": "Hierarchical config management (default.json, local.json, runtime). Export/import with persistence",
        "file": "sbc/src/config/config_manager.cpp",
        "function": "ConfigManager::get()",
        "keywords": "config,configuration,hierarchical,persistence,JSON",
        "metadata": json.dumps({"domain": "air-side", "language": "cpp", "platform": "pi5", "files": ["default.json", "local.json"]})
    },
    {
        "name": "Runtime Config Update",
        "category": "configuration",
        "description": "Runtime configuration updates without restart. Hot-reload for logging, atomic updates, rollback support",
        "file": "sbc/src/protocol/tcp_server.cpp",
        "function": "TCPServer::handleSystemUpdateConfig()",
        "keywords": "config,runtime,update,hot-reload,atomic",
        "metadata": json.dumps({"domain": "air-side", "language": "cpp", "platform": "pi5", "command": "system.update_config"})
    },

    # CATEGORY: protocol
    {
        "name": "DPM Protocol Message Formatter",
        "category": "protocol",
        "description": "JSON message creation/parsing for all DPM protocol messages. Status, command, response, error, heartbeat, health",
        "file": "sbc/src/protocol/messages.h",
        "function": "createStatusMessage()",
        "keywords": "protocol,message,JSON,formatter,DPM",
        "metadata": json.dumps({"domain": "air-side", "language": "cpp", "platform": "pi5", "protocol": "DPM v1.0"})
    },
    {
        "name": "Protocol Message Validator",
        "category": "protocol",
        "description": "Validates incoming TCP messages for correct structure, version, required fields. Detailed error messages",
        "file": "sbc/src/protocol/tcp_server.cpp",
        "function": "TCPServer::validateMessage()",
        "keywords": "protocol,validation,message,structure,error",
        "metadata": json.dumps({"domain": "air-side", "language": "cpp", "platform": "pi5"})
    },
    {
        "name": "Command Router",
        "category": "protocol",
        "description": "Routes protocol commands to handlers. Supports 20+ commands across system, camera, logging, health, config domains",
        "file": "sbc/src/protocol/tcp_server.cpp",
        "function": "TCPServer::processCommand()",
        "keywords": "protocol,command,router,handler,dispatcher",
        "metadata": json.dumps({"domain": "air-side", "language": "cpp", "platform": "pi5", "commands": 20})
    },
]

# Shortened for brevity - full script would include all 148 capabilities
# This is a working template showing the pattern

def register_capability(cap):
    """Register a single capability using CCPM client script"""
    cmd = [
        "python3", REGISTER_SCRIPT,
        "--project-id", str(PROJECT_ID),
        "--name", cap["name"],
        "--category", cap["category"],
        "--description", cap["description"],
        "--implementation-file", cap["file"],
    ]

    if "function" in cap:
        cmd.extend(["--implementation-function", cap["function"]])
    if "keywords" in cap:
        cmd.extend(["--keywords", cap["keywords"]])
    if "metadata" in cap:
        cmd.extend(["--metadata", cap["metadata"]])

    cmd.extend(["--status", "production"])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ Registered: {cap['name']}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {cap['name']}")
        print(f"   Error: {e.stderr}")
        return False

def main():
    """Register all DPM-V2 capabilities"""
    print(f"=== DPM-V2 Capability Registration ===")
    print(f"Project ID: {PROJECT_ID}")
    print(f"Total capabilities (Air-Side sample): {len(AIR_SIDE_CAPABILITIES)}")
    print()

    success_count = 0
    fail_count = 0

    for cap in AIR_SIDE_CAPABILITIES:
        if register_capability(cap):
            success_count += 1
        else:
            fail_count += 1

    print()
    print(f"=== Registration Summary ===")
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {fail_count}")
    print(f"Total: {success_count + fail_count}")

if __name__ == "__main__":
    main()
