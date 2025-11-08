"""
Quick raw TCP test for H16 diagnostics via Air-Side
"""
import socket
import json
import time

def test_command(command_name):
    print(f"\n{'='*60}")
    print(f"Testing: {command_name}")
    print(f"{'='*60}")

    request = {
        "protocol_version": "1.0",
        "message_type": "command",
        "sequence_id": 1,
        "timestamp": int(time.time()),
        "payload": {
            "command": command_name,
            "parameters": {}
        }
    }

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)

        print(f"Connecting to Air-Side (10.0.1.53:5000)...")
        sock.connect(("10.0.1.53", 5000))
        print("Connected!")

        request_json = json.dumps(request) + "\n"
        print(f"\nSending: {request_json}")
        sock.sendall(request_json.encode('utf-8'))
        print("Request sent!")

        print("\nWaiting for response...")
        response_data = b""
        sock.settimeout(5)

        while True:
            try:
                chunk = sock.recv(4096)
                if not chunk:
                    print("Connection closed by server")
                    break
                response_data += chunk
                print(f"Received {len(chunk)} bytes...")

                # Try to parse as JSON
                try:
                    response = json.loads(response_data.decode('utf-8'))
                    print(f"\n✅ Complete JSON received!")
                    print(json.dumps(response, indent=2))
                    break
                except json.JSONDecodeError:
                    print("Incomplete JSON, waiting for more data...")
                    continue

            except socket.timeout:
                print(f"\n❌ Timeout after 5 seconds")
                print(f"Partial data received: {len(response_data)} bytes")
                if response_data:
                    print(f"Raw data: {response_data}")
                break

        sock.close()

    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    print("H16 Diagnostic Command Raw Test (via Air-Side)")
    print("="*60)

    # Test all three commands
    test_command("diagnostics.ping")
    test_command("diagnostics.get_system_info")
    test_command("diagnostics.get_app_status")

    print(f"\n{'='*60}")
    print("Test complete!")
