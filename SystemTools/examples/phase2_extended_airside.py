#!/usr/bin/env python3
"""
Phase 2: Extended Air-Side Operations - Examples
=================================================

Demonstrates advanced Air-Side operations:
- Response callbacks
- Status subscriptions
- Log streaming
- File transfers
- Camera file management
- Docker container management
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from api import DPMController


def example_callbacks():
    """Example: Send command with callbacks"""
    print("=" * 60)
    print("Example 1: Command with Callbacks")
    print("=" * 60)

    dpm = DPMController()

    def on_response(data):
        print(f"   ✓ Response received: {data}")

    def on_error(error):
        print(f"   ✗ Error occurred: {error}")

    print("\n1. Sending command with callbacks...")
    result = dpm.air_side.send_command_with_callback(
        'camera.get_properties',
        {},
        on_response=on_response,
        on_error=on_error
    )

    if result.success:
        print(f"   ✓ Command sent with callback_id: {result.data.get('callback_id')}")


def example_status_subscription():
    """Example: Subscribe to status updates"""
    print("\n" + "=" * 60)
    print("Example 2: Status Subscriptions")
    print("=" * 60)

    dpm = DPMController()

    def on_status_update(status):
        print(f"   Status update: CPU={status.get('cpu_percent')}%")

    print("\n1. Subscribing to status updates...")
    result = dpm.air_side.subscribe_to_status(
        callback=on_status_update,
        interval_ms=200
    )

    if result.success:
        print(f"   ✓ Subscribed (subscribers: {result.data['subscriber_count']})")

    print("\n2. Unsubscribing...")
    result = dpm.air_side.unsubscribe_from_status(on_status_update)
    if result.success:
        print("   ✓ Unsubscribed")


def example_log_streaming():
    """Example: Stream Docker logs"""
    print("\n" + "=" * 60)
    print("Example 3: Log Streaming")
    print("=" * 60)

    dpm = DPMController()

    print("\n1. Getting log stream command...")
    result = dpm.air_side.stream_logs(lines=50, follow=False)

    if result.success:
        print(f"   ✓ Stream command: {result.data['stream_command']}")
        print(f"   Lines: {result.data['lines']}, Follow: {result.data['follow']}")


def example_file_transfer():
    """Example: File transfer operations"""
    print("\n" + "=" * 60)
    print("Example 4: File Transfer")
    print("=" * 60)

    dpm = DPMController()

    print("\n1. Transferring file from Air-Side...")
    result = dpm.air_side.transfer_file(
        remote_path='/tmp/test.txt',
        local_path='/tmp/downloaded_test.txt',
        direction='download'
    )

    if result.success:
        print(f"   ✓ Transfer setup: {result.data['direction']}")
        print(f"   SCP command: {result.data['scp_command']}")


def example_camera_files():
    """Example: Camera file management"""
    print("\n" + "=" * 60)
    print("Example 5: Camera File Management")
    print("=" * 60)

    dpm = DPMController()

    print("\n1. Getting camera images...")
    result = dpm.air_side.get_camera_files(file_type='image', limit=5)

    if result.success:
        print(f"   ✓ Found {result.data['count']} images")
        for file in result.data['files'][:3]:
            print(f"     - {file}")
    else:
        print(f"   ℹ {result.error}")

    print("\n2. Downloading camera file...")
    result = dpm.air_side.download_camera_file(
        remote_file='/home/dpm/camera_files/IMG_001.jpg',
        local_directory='/tmp'
    )

    if result.success:
        print(f"   ✓ Download setup for: {result.data['remote_path']}")


def example_docker_management():
    """Example: Docker container management"""
    print("\n" + "=" * 60)
    print("Example 6: Docker Container Management")
    print("=" * 60)

    dpm = DPMController()

    print("\n1. Getting container status...")
    result = dpm.air_side.manage_docker_container(action='status')

    if result.success:
        print(f"   ✓ Status: {result.data['output']}")
    else:
        print(f"   ℹ {result.error}")

    print("\n2. Getting container logs...")
    result = dpm.air_side.manage_docker_container(action='logs')

    if result.success:
        print(f"   ✓ Retrieved logs (50 lines)")


def main():
    """Run all Phase 2 examples"""
    print("\n" + "=" * 60)
    print("Phase 2: Extended Air-Side Operations")
    print("=" * 60)
    print("\nDemonstrates advanced Air-Side control capabilities\n")

    try:
        example_callbacks()
        example_status_subscription()
        example_log_streaming()
        example_file_transfer()
        example_camera_files()
        example_docker_management()

        print("\n" + "=" * 60)
        print("Phase 2 Examples Complete")
        print("=" * 60)
        print("\nPhase 2 adds:")
        print("- ✓ Command callbacks for async responses")
        print("- ✓ Real-time status subscriptions")
        print("- ✓ Log streaming capabilities")
        print("- ✓ File transfer (download/upload)")
        print("- ✓ Camera file management")
        print("- ✓ Docker container control")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
