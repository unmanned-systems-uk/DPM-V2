"""
HTTP File Transfer Client for Air-Side Downloads - Issue #133

Provides programmatic access to download files (images, logs) from Air-Side
via HTTP REST API.

Usage:
    from network.file_transfer_client import AirSideFileClient

    client = AirSideFileClient(host='10.0.1.53', port=8080)

    # List files
    files = client.list_files(file_type='image')

    # Download file
    client.download_file('IMG_001.jpg', destination='/local/images/IMG_001.jpg',
                         progress_callback=lambda pct: print(f"{pct}%"))

    # Get file info
    info = client.get_file_info('air-side.log')
"""

import requests
from pathlib import Path
from typing import List, Dict, Optional, Callable, Any
from datetime import datetime
import hashlib
import os

from utils.protocol_logger import logger


class FileTransferError(Exception):
    """Exception raised for file transfer errors"""
    pass


class AirSideFileClient:
    """
    HTTP client for downloading files from Air-Side.

    Connects to Air-Side HTTP REST API server for file operations.
    """

    def __init__(self, host: str = '10.0.1.53', port: int = 8080, timeout: int = 30):
        """
        Initialize Air-Side file transfer client.

        Args:
            host: Air-Side IP address (default: 10.0.1.53)
            port: HTTP server port (default: 8080)
            timeout: Request timeout in seconds (default: 30)
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.base_url = f"http://{host}:{port}/api"

        logger.info("NETWORK", f"AirSideFileClient initialized: {self.base_url}")

    def health_check(self) -> Dict[str, Any]:
        """
        Check if Air-Side file server is running.

        Returns:
            Dict with server health status

        Raises:
            FileTransferError: If server is unreachable
        """
        try:
            url = f"{self.base_url}/health"
            response = requests.get(url, timeout=5)
            response.raise_for_status()

            data = response.json()
            logger.info("NETWORK", f"Air-Side file server health: {data.get('status', 'unknown')}")
            return data

        except requests.exceptions.RequestException as e:
            logger.error("NETWORK", f"Health check failed: {e}")
            raise FileTransferError(f"Cannot reach Air-Side file server at {self.base_url}: {e}")

    def list_files(self, file_type: str = 'all') -> List[Dict[str, Any]]:
        """
        List available files on Air-Side.

        Args:
            file_type: Filter by type ('image', 'log', 'all')

        Returns:
            List of file dictionaries with metadata:
            [
                {
                    "name": "IMG_001.jpg",
                    "size": 1024768,
                    "modified": "2025-11-17T10:30:00Z",
                    "type": "image"
                },
                ...
            ]

        Raises:
            FileTransferError: If listing fails
        """
        try:
            url = f"{self.base_url}/files/list"
            params = {'type': file_type}

            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()
            files = data.get('files', [])

            logger.info("NETWORK", f"Listed {len(files)} files from Air-Side (type={file_type})")
            return files

        except requests.exceptions.RequestException as e:
            logger.error("NETWORK", f"Failed to list files: {e}")
            raise FileTransferError(f"Cannot list files from Air-Side: {e}")

    def get_file_info(self, filename: str) -> Dict[str, Any]:
        """
        Get detailed metadata about a specific file.

        Args:
            filename: Name of the file

        Returns:
            Dict with file metadata:
            {
                "name": "IMG_001.jpg",
                "size": 1024768,
                "modified": "2025-11-17T10:30:00Z",
                "checksum": "abc123...",
                "type": "image"
            }

        Raises:
            FileTransferError: If file info cannot be retrieved
        """
        try:
            url = f"{self.base_url}/files/info/{filename}"

            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()
            logger.info("NETWORK", f"Got info for file: {filename} ({data.get('size', 0)} bytes)")
            return data

        except requests.exceptions.RequestException as e:
            logger.error("NETWORK", f"Failed to get file info for {filename}: {e}")
            raise FileTransferError(f"Cannot get info for file '{filename}': {e}")

    def download_file(self,
                     filename: str,
                     destination: str,
                     progress_callback: Optional[Callable[[int], None]] = None,
                     verify_checksum: bool = True) -> bool:
        """
        Download a file from Air-Side.

        Args:
            filename: Name of the file to download
            destination: Local path to save the file
            progress_callback: Optional callback function(percent: int) for progress updates
            verify_checksum: Verify file integrity after download (default: True)

        Returns:
            True if download successful

        Raises:
            FileTransferError: If download fails
        """
        try:
            url = f"{self.base_url}/files/download/{filename}"

            # Check destination directory exists
            dest_path = Path(destination)
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            # Check available disk space
            stat = os.statvfs(dest_path.parent)
            free_bytes = stat.f_bavail * stat.f_frsize

            # Get file info first
            try:
                file_info = self.get_file_info(filename)
                file_size = file_info.get('size', 0)

                if file_size > free_bytes:
                    raise FileTransferError(
                        f"Insufficient disk space: need {file_size} bytes, have {free_bytes} bytes"
                    )

                logger.info("NETWORK", f"Downloading {filename} ({file_size} bytes) to {destination}")
            except FileTransferError:
                # File info not available, proceed anyway
                logger.warning("NETWORK", f"Could not get file size for {filename}, proceeding with download")
                file_size = 0
                file_info = {}

            # Download with streaming to handle large files
            response = requests.get(url, stream=True, timeout=self.timeout)
            response.raise_for_status()

            # Write file with progress tracking
            downloaded = 0
            chunk_size = 8192  # 8KB chunks

            with open(destination, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        # Call progress callback if provided
                        if progress_callback and file_size > 0:
                            percent = int((downloaded / file_size) * 100)
                            progress_callback(percent)

            logger.info("NETWORK", f"Downloaded {filename} successfully ({downloaded} bytes)")

            # Verify checksum if requested
            if verify_checksum and 'checksum' in file_info:
                logger.info("NETWORK", f"Verifying checksum for {filename}...")
                local_checksum = self._calculate_checksum(destination)
                remote_checksum = file_info['checksum']

                if local_checksum != remote_checksum:
                    logger.error("NETWORK", f"Checksum mismatch! Local: {local_checksum}, Remote: {remote_checksum}")
                    raise FileTransferError(
                        f"Downloaded file corrupted (checksum mismatch): {filename}"
                    )

                logger.info("NETWORK", f"Checksum verified OK: {local_checksum}")

            return True

        except requests.exceptions.RequestException as e:
            logger.error("NETWORK", f"Download failed for {filename}: {e}")
            # Clean up partial download
            if Path(destination).exists():
                Path(destination).unlink()
            raise FileTransferError(f"Cannot download file '{filename}': {e}")
        except OSError as e:
            logger.error("NETWORK", f"File system error during download: {e}")
            raise FileTransferError(f"File system error: {e}")

    def download_multiple(self,
                         filenames: List[str],
                         destination_dir: str,
                         progress_callback: Optional[Callable[[str, int], None]] = None) -> Dict[str, bool]:
        """
        Download multiple files from Air-Side.

        Args:
            filenames: List of filenames to download
            destination_dir: Directory to save files
            progress_callback: Optional callback function(filename: str, percent: int)

        Returns:
            Dict mapping filename to success status: {"IMG_001.jpg": True, "IMG_002.jpg": False}
        """
        results = {}
        dest_path = Path(destination_dir)
        dest_path.mkdir(parents=True, exist_ok=True)

        logger.info("NETWORK", f"Downloading {len(filenames)} files to {destination_dir}")

        for filename in filenames:
            try:
                destination = str(dest_path / filename)

                def file_progress(percent):
                    if progress_callback:
                        progress_callback(filename, percent)

                success = self.download_file(
                    filename,
                    destination,
                    progress_callback=file_progress if progress_callback else None
                )
                results[filename] = success

            except FileTransferError as e:
                logger.error("NETWORK", f"Failed to download {filename}: {e}")
                results[filename] = False

        success_count = sum(1 for v in results.values() if v)
        logger.info("NETWORK", f"Downloaded {success_count}/{len(filenames)} files successfully")

        return results

    def _calculate_checksum(self, filepath: str, algorithm: str = 'md5') -> str:
        """
        Calculate checksum of a local file.

        Args:
            filepath: Path to file
            algorithm: Hash algorithm ('md5', 'sha256')

        Returns:
            Hex digest string
        """
        if algorithm == 'md5':
            hasher = hashlib.md5()
        elif algorithm == 'sha256':
            hasher = hashlib.sha256()
        else:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")

        with open(filepath, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)

        return hasher.hexdigest()

    def __repr__(self) -> str:
        return f"AirSideFileClient(host='{self.host}', port={self.port})"
