#!/usr/bin/env python3
"""
Shutter Speed Discovery Script
Systematically tests all shutter speeds to build a complete value map.

This script:
1. Sends camera.set_property with a known shutter speed string
2. Reads back the actual value with camera.get_properties
3. Logs the mapping between sent string and received hex value
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

# All known shutter speeds from Sony Alpha 1 (from fastest to slowest)
SHUTTER_SPEEDS = [
    # Very fast (1/8000 to 1/1000)
    "1/8000", "1/6400", "1/5000", "1/4000", "1/3200", "1/2500",
    "1/2000", "1/1600", "1/1250", "1/1000",
    # Fast (1/800 to 1/100)
    "1/800", "1/640", "1/500", "1/400", "1/320", "1/250",
    "1/200", "1/160", "1/125", "1/100",
    # Medium (1/80 to 1/10)
    "1/80", "1/60", "1/50", "1/40", "1/30", "1/25",
    "1/20", "1/15", "1/13", "1/10",
    # Slow (1/8 to 1/3)
    "1/8", "1/6", "1/5", "1/4", "1/3"
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
    print("Shutter Speed Discovery Script")
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
        response = send_command(sock, "handshake", {"client_id": "shutter_discovery"})
        if response["payload"]["status"] != "success":
            print("✗ Handshake failed!")
            return

        print("✓ Handshake successful")
        print()
        print("Starting shutter speed discovery...")
        print("-" * 70)

        # Storage for discovered mappings
        mappings = {}
        failed = []

        for i, speed in enumerate(SHUTTER_SPEEDS, 1):
            print(f"\n[{i}/{len(SHUTTER_SPEEDS)}] Testing: {speed}")

            # Set the shutter speed
            set_response = send_command(sock, "camera.set_property", {
                "property": "shutter_speed",
                "value": speed
            })

            if set_response["payload"]["status"] != "success":
                error_msg = set_response["payload"].get("error", {}).get("message", "Unknown error")
                print(f"  ✗ Failed to set: {error_msg}")
                failed.append(speed)
                continue

            print(f"  ✓ Set successfully")

            # Wait a moment for camera to process
            time.sleep(0.2)

            # Read back the value
            get_response = send_command(sock, "camera.get_properties", {
                "properties": ["shutter_speed"]
            })

            if get_response["payload"]["status"] != "success":
                print(f"  ✗ Failed to read back")
                failed.append(speed)
                continue

            result = get_response["payload"]["result"]["shutter_speed"]

            # Parse the hex value if it's in unknown() format
            if result.startswith("unknown(0x"):
                hex_value = result.split("(")[1].split(")")[0]
                print(f"  → Read back: {result}")
                mappings[speed] = hex_value
            elif result == speed:
                print(f"  → Read back: {result} (already mapped!)")
            else:
                print(f"  → Read back: {result} (different value)")

        # Print summary
        print()
        print("=" * 70)
        print("DISCOVERY COMPLETE")
        print("=" * 70)
        print()

        if mappings:
            print("Discovered Mappings (C++ format):")
            print("-" * 70)
            print("static const std::unordered_map<uint32_t, std::string> SHUTTER_REVERSE = {")
            print('    {0x00000000, "auto"},')

            for speed, hex_val in sorted(mappings.items(), key=lambda x: int(x[1], 16), reverse=True):
                dec_val = int(hex_val, 16)
                print(f'    {{{hex_val}, "{speed}"}},  // {dec_val}')

            print("};")
            print()

        if failed:
            print(f"\nFailed to map {len(failed)} speeds:")
            for speed in failed:
                print(f"  - {speed}")
            print()

        print(f"Successfully mapped: {len(mappings)}/{len(SHUTTER_SPEEDS)}")
        print()

        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"shutter_map_{timestamp}.txt"

        with open(filename, 'w') as f:
            f.write("Shutter Speed Mapping Discovery\n")
            f.write(f"Timestamp: {datetime.now()}\n")
            f.write("=" * 70 + "\n\n")

            f.write("Discovered Mappings:\n")
            f.write("-" * 70 + "\n")
            for speed, hex_val in sorted(mappings.items(), key=lambda x: int(x[1], 16), reverse=True):
                dec_val = int(hex_val, 16)
                f.write(f"{hex_val} -> {speed} (dec: {dec_val})\n")

            f.write("\n" + "=" * 70 + "\n")
            f.write("C++ Code:\n")
            f.write("-" * 70 + "\n")
            f.write("static const std::unordered_map<uint32_t, std::string> SHUTTER_REVERSE = {\n")
            f.write('    {0x00000000, "auto"},\n')

            for speed, hex_val in sorted(mappings.items(), key=lambda x: int(x[1], 16), reverse=True):
                dec_val = int(hex_val, 16)
                f.write(f'    {{{hex_val}, "{speed}"}},  // {dec_val}\n')

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
