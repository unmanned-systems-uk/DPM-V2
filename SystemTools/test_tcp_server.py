#!/usr/bin/env python3
"""
Simple TCP server test for port 5008
Tests if GroundSideListener can accept connections
"""
import socket
import sys

def test_tcp_server():
    """Test TCP server on port 5008"""
    host = "0.0.0.0"
    port = 5008

    print(f"Creating TCP server on {host}:{port}...")

    try:
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((host, port))
        server_sock.listen(5)

        print(f"✅ TCP server listening on {host}:{port}")
        print(f"Waiting for client connections...")
        print(f"Press Ctrl+C to stop")

        server_sock.settimeout(1.0)

        while True:
            try:
                client_sock, client_addr = server_sock.accept()
                print(f"\n🎉 CLIENT CONNECTED from {client_addr}")

                # Receive and echo data
                data = client_sock.recv(1024)
                if data:
                    print(f"Received {len(data)} bytes: {data[:100]}")

                client_sock.close()
                print(f"Client {client_addr} disconnected")

            except socket.timeout:
                continue

    except PermissionError:
        print(f"❌ ERROR: Permission denied on port {port}")
        print(f"   Try: sudo python3 {sys.argv[0]}")
        return 1
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ ERROR: Port {port} is already in use!")
            print(f"   Another process is using this port.")
            print(f"   Check with: ss -tlnp | grep {port}")
        else:
            print(f"❌ ERROR: {e}")
        return 1
    except KeyboardInterrupt:
        print(f"\n\nStopping server...")
    finally:
        try:
            server_sock.close()
            print("Server stopped")
        except:
            pass

    return 0

if __name__ == "__main__":
    sys.exit(test_tcp_server())
