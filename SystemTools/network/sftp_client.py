"""
SFTP File Transfer Client for Air-Side Communication
Issue #133 - Simple SFTP-based file transfer for camera images and logs
"""

import paramiko
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
import stat

from utils.logger import logger


class AirSideSFTPClient:
    """SFTP client for downloading files from Air-Side (Pi 5)"""

    def __init__(self, host: str = '10.0.1.53', port: int = 22,
                 username: str = 'dpm', password: Optional[str] = None,
                 key_filename: Optional[str] = None):
        """
        Initialize SFTP client connection to Air-Side

        Args:
            host: Air-Side hostname/IP (default: 10.0.1.53)
            port: SSH port (default: 22)
            username: SSH username (default: dpm)
            password: SSH password (if not using key auth)
            key_filename: Path to SSH private key file
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.key_filename = key_filename

        self.transport: Optional[paramiko.Transport] = None
        self.sftp: Optional[paramiko.SFTPClient] = None

        logger.info(f"AirSideSFTPClient initialized for {username}@{host}:{port}")

    def connect(self) -> bool:
        """
        Establish SFTP connection to Air-Side

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Create SSH transport
            self.transport = paramiko.Transport((self.host, self.port))

            # Authenticate
            if self.key_filename:
                # Use SSH key authentication
                private_key = paramiko.RSAKey.from_private_key_file(self.key_filename)
                self.transport.connect(username=self.username, pkey=private_key)
                logger.info(f"Connected to {self.host} using key authentication")
            elif self.password:
                # Use password authentication
                self.transport.connect(username=self.username, password=self.password)
                logger.info(f"Connected to {self.host} using password authentication")
            else:
                logger.error("No authentication method provided (password or key)")
                return False

            # Create SFTP client
            self.sftp = paramiko.SFTPClient.from_transport(self.transport)
            logger.info("SFTP connection established")
            return True

        except Exception as e:
            logger.error(f"Failed to connect via SFTP: {e}")
            return False

    def disconnect(self):
        """Close SFTP connection"""
        try:
            if self.sftp:
                self.sftp.close()
                logger.debug("SFTP client closed")
            if self.transport:
                self.transport.close()
                logger.debug("SSH transport closed")
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")

    def list_files(self, remote_directory: str,
                   file_extension: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List files in remote directory with metadata

        Args:
            remote_directory: Remote path to list (e.g., /home/dpm/camera_images)
            file_extension: Filter by extension (e.g., '.jpg', '.log'). None = all files

        Returns:
            List of file dictionaries with metadata:
            [
                {
                    'name': 'IMG_001.jpg',
                    'path': '/home/dpm/camera_images/IMG_001.jpg',
                    'size': 1024768,
                    'modified': '2025-11-17T12:30:00',
                    'is_directory': False
                },
                ...
            ]
        """
        if not self.sftp:
            logger.error("SFTP not connected. Call connect() first.")
            return []

        try:
            files = []

            # List directory contents
            for entry in self.sftp.listdir_attr(remote_directory):
                # Skip directories if we're looking for files
                is_dir = stat.S_ISDIR(entry.st_mode)

                # Filter by extension if specified
                if file_extension and not is_dir:
                    if not entry.filename.endswith(file_extension):
                        continue

                # Get modification time
                modified = datetime.fromtimestamp(entry.st_mtime).isoformat()

                # Build file info dictionary
                file_info = {
                    'name': entry.filename,
                    'path': os.path.join(remote_directory, entry.filename),
                    'size': entry.st_size,
                    'modified': modified,
                    'is_directory': is_dir
                }

                files.append(file_info)

            # Sort by modification time (newest first)
            files.sort(key=lambda x: x['modified'], reverse=True)

            logger.info(f"Listed {len(files)} files from {remote_directory}")
            return files

        except Exception as e:
            logger.error(f"Failed to list files in {remote_directory}: {e}")
            return []

    def download_file(self, remote_path: str, local_path: str,
                      progress_callback: Optional[Callable[[int, int], None]] = None) -> bool:
        """
        Download file from Air-Side to local system

        Args:
            remote_path: Remote file path (e.g., /home/dpm/camera_images/IMG_001.jpg)
            local_path: Local destination path (e.g., /local/downloads/IMG_001.jpg)
            progress_callback: Optional callback(bytes_transferred, total_bytes)

        Returns:
            True if download successful, False otherwise
        """
        if not self.sftp:
            logger.error("SFTP not connected. Call connect() first.")
            return False

        try:
            # Ensure local directory exists
            local_dir = os.path.dirname(local_path)
            if local_dir:
                Path(local_dir).mkdir(parents=True, exist_ok=True)

            # Download file with progress tracking
            if progress_callback:
                # Wrapper to call progress_callback
                def _progress(transferred, total):
                    progress_callback(transferred, total)

                self.sftp.get(remote_path, local_path, callback=_progress)
            else:
                self.sftp.get(remote_path, local_path)

            logger.info(f"Downloaded {remote_path} → {local_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to download {remote_path}: {e}")
            return False

    def get_file_info(self, remote_path: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific remote file

        Args:
            remote_path: Remote file path

        Returns:
            File info dictionary or None if file not found
        """
        if not self.sftp:
            logger.error("SFTP not connected. Call connect() first.")
            return None

        try:
            stat_info = self.sftp.stat(remote_path)

            file_info = {
                'name': os.path.basename(remote_path),
                'path': remote_path,
                'size': stat_info.st_size,
                'modified': datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                'is_directory': stat.S_ISDIR(stat_info.st_mode)
            }

            logger.debug(f"Got file info for {remote_path}: {file_info}")
            return file_info

        except Exception as e:
            logger.error(f"Failed to get file info for {remote_path}: {e}")
            return None

    def file_exists(self, remote_path: str) -> bool:
        """
        Check if remote file exists

        Args:
            remote_path: Remote file path

        Returns:
            True if file exists, False otherwise
        """
        try:
            self.sftp.stat(remote_path)
            return True
        except:
            return False

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()


# Example usage
if __name__ == "__main__":
    # Example: Download test file from Air-Side
    print("Testing SFTP connection to Air-Side...")

    # Initialize client (will prompt for password if not using key)
    client = AirSideSFTPClient(
        host='10.0.1.53',
        username='dpm',
        password='your_password_here'  # Replace with actual password
    )

    # Connect
    if client.connect():
        print("✓ Connected to Air-Side")

        # List camera images
        print("\nListing camera images...")
        images = client.list_files('/home/dpm/camera_images')
        for img in images:
            print(f"  {img['name']} ({img['size']} bytes, modified: {img['modified']})")

        # Download test file
        if images:
            print(f"\nDownloading {images[0]['name']}...")
            success = client.download_file(
                images[0]['path'],
                f"/tmp/{images[0]['name']}",
                progress_callback=lambda t, total: print(f"  Progress: {t}/{total} bytes ({100*t//total}%)")
            )
            if success:
                print(f"✓ Downloaded to /tmp/{images[0]['name']}")

        # Disconnect
        client.disconnect()
        print("\n✓ Disconnected")
    else:
        print("✗ Failed to connect")
