#!/usr/bin/env python3
"""
ISO Discovery Script
Systematically tests all ISO values to build a complete value map.

This script:
1. Sends camera.set_property with a known ISO value string
2. Reads back the actual value with camera.get_properties
3. Logs the mapping between sent string and received value
4. Builds a complete reverse lookup map
"""

import socket
import json
import time
from datetime import datetime

# Configuration
AIR_SIDE_IP = "127.0.0.1"  # localhost (running on same machine as container)
TCP_PORT = 5000
PROTOCOL_VERSION = "1.0"

# All known ISO values from Sony Alpha 1
# Standard range: 100-102400
# Extended low: 50
# Extended high: 204800, 409600, 819200, 1638400 (H1-H4)
ISO_VALUES = [
    # Extended low
    "50",
    # Base ISO (100-102400) - full stops
    "100", "125", "160", "200", "250", "320", "400", "500", "640",
    "800", "1000", "1250", "1600", "2000", "2500", "3200", "4000", "5000",
    "6400", "8000", "10000", "12800", "16000", "20000", "25600",
    "32000", "40000", "51200", "64000", "80000", "102400",
    # Extended high
    "204800", "409600", "819200", "1638400"
]

sequence_id = 0

def send_command(sock, command, parameters):
    """Send a command to the air-side TCP server."""
    global sequence_id
    sequence_id += 1

    message = {
        "protocol_version": PROTOCOL_VERSION,
        "message_type": "command",
        "sequence_id": sequence_id,
        "timestamp": int(time.time()),
        "payload": {
            "command": command,
            "parameters": parameters
        }
    }

    message_json = json.dumps(message)
    sock.sendall(message_json.encode('utf-8') + b'\n')

    # Receive response
    response_data = sock.recv(4096)
    response = json.loads(response_data.decode('utf-8'))

    return response

def main():
    print("=" * 70)
    print("ISO Discovery Script")
    print("=" * 70)
    print(f"Connecting to {AIR_SIDE_IP}:{TCP_PORT}...")

    # Connect to air-side
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)

    try:
        sock.connect((AIR_SIDE_IP, TCP_PORT))
        print("✓ Connected!")
        print()

        # Perform handshake
        response = send_command(sock, "handshake", {"client_id": "iso_discovery"})
        if response["payload"]["status"] != "success":
            print("✗ Handshake failed!")
            return

        print("✓ Handshake successful")
        print()
        print("Starting ISO discovery...")
        print("-" * 70)

        # Storage for discovered mappings
        mappings = {}
        failed = []

        for i, iso_value in enumerate(ISO_VALUES, 1):
            print(f"\n[{i}/{len(ISO_VALUES)}] Testing: ISO {iso_value}")

            # Set the ISO
            set_response = send_command(sock, "camera.set_property", {
                "property": "iso",
                "value": iso_value
            })

            if set_response["payload"]["status"] != "success":
                error_msg = set_response["payload"].get("error", {}).get("message", "Unknown error")
                print(f"  ✗ Failed to set: {error_msg}")
                failed.append(iso_value)
                continue

            print(f"  ✓ Set successfully")

            # Wait a moment for camera to process
            time.sleep(0.2)

            # Read back the value
            get_response = send_command(sock, "camera.get_properties", {
                "properties": ["iso"]
            })

            if get_response["payload"]["status"] != "success":
                print(f"  ✗ Failed to read back")
                failed.append(iso_value)
                continue

            result = get_response["payload"]["result"]["iso"]

            # Log the mapping
            print(f"  → Read back: {result}")

            if result == iso_value:
                print(f"    (Already mapped correctly!)")
            elif result.startswith("unknown("):
                hex_value = result.split("(")[1].split(")")[0]
                mappings[iso_value] = hex_value
            else:
                print(f"    (Different value - unexpected)")

        # Print summary
        print()
        print("=" * 70)
        print("DISCOVERY COMPLETE")
        print("=" * 70)
        print()

        if mappings:
            print("Discovered Mappings (C++ format):")
            print("-" * 70)
            print("// Forward mapping (set property)")
            print("static const std::unordered_map<std::string, uint32_t> ISO_MAP = {")
            print('    {"auto", 0xFFFFFFFF},')

            for iso_str in sorted(mappings.keys(), key=lambda x: int(x)):
                hex_val = mappings[iso_str]
                dec_val = int(hex_val, 16)
                print(f'    {{"{iso_str}", {hex_val}}},  // {dec_val}')

            print("};")
            print()
            print()
            print("// Reverse mapping (get property)")
            print("static const std::unordered_map<uint32_t, std::string> ISO_REVERSE = {")
            print('    {0xFFFFFFFF, "auto"},')

            for iso_str in sorted(mappings.keys(), key=lambda x: int(x)):
                hex_val = mappings[iso_str]
                dec_val = int(hex_val, 16)
                print(f'    {{{hex_val}, "{iso_str}"}},  // {dec_val}')

            print("};")
            print()

        if failed:
            print(f"\nFailed to map {len(failed)} values:")
            for iso_val in failed:
                print(f"  - {iso_val}")
            print()

        print(f"Successfully mapped: {len(mappings)}/{len(ISO_VALUES)}")
        print()

        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"iso_map_{timestamp}.txt"

        with open(filename, 'w') as f:
            f.write("ISO Mapping Discovery\n")
            f.write(f"Timestamp: {datetime.now()}\n")
            f.write("=" * 70 + "\n\n")

            f.write("Discovered Mappings:\n")
            f.write("-" * 70 + "\n")
            for iso_str in sorted(mappings.keys(), key=lambda x: int(x)):
                hex_val = mappings[iso_str]
                dec_val = int(hex_val, 16)
                f.write(f"{hex_val} -> ISO {iso_str} (dec: {dec_val})\n")

            f.write("\n" + "=" * 70 + "\n")
            f.write("C++ Code (Forward Mapping):\n")
            f.write("-" * 70 + "\n")
            f.write("static const std::unordered_map<std::string, uint32_t> ISO_MAP = {\n")
            f.write('    {"auto", 0xFFFFFFFF},\n')

            for iso_str in sorted(mappings.keys(), key=lambda x: int(x)):
                hex_val = mappings[iso_str]
                dec_val = int(hex_val, 16)
                f.write(f'    {{"{iso_str}", {hex_val}}},  // {dec_val}\n')

            f.write("};\n\n")

            f.write("=" * 70 + "\n")
            f.write("C++ Code (Reverse Mapping):\n")
            f.write("-" * 70 + "\n")
            f.write("static const std::unordered_map<uint32_t, std::string> ISO_REVERSE = {\n")
            f.write('    {0xFFFFFFFF, "auto"},\n')

            for iso_str in sorted(mappings.keys(), key=lambda x: int(x)):
                hex_val = mappings[iso_str]
                dec_val = int(hex_val, 16)
                f.write(f'    {{{hex_val}, "{iso_str}"}},  // {dec_val}\n')

            f.write("};\n")

        print(f"✓ Results saved to: {filename}")

    except socket.timeout:
        print("✗ Connection timeout!")
    except ConnectionRefusedError:
        print("✗ Connection refused! Is the air-side service running?")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        sock.close()
        print("\nConnection closed.")

if __name__ == "__main__":
    main()
