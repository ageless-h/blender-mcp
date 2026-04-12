"""Blender process harness for real Blender integration tests.

This module provides a test harness that manages the lifecycle of a Blender
process, enabling automated testing against real Blender installations via
socket communication.
"""

from __future__ import annotations

import json
import logging
import os
import socket
import subprocess
import time
from contextlib import suppress
from pathlib import Path
from typing import Any

# Default timeout for Blender startup (seconds)
DEFAULT_START_TIMEOUT = 30.0

# Default timeout for socket communication (seconds)
DEFAULT_REQUEST_TIMEOUT = 30.0

logger = logging.getLogger(__name__)


def find_free_port() -> int:
    """Find a free port on localhost.

    Returns:
        A free port number that can be used for socket communication.

    Examples:
        >>> port = find_free_port()
        >>> sock = socket.socket()
        >>> sock.bind(('', port))
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port


class BlenderProcessHarness:
    """Harness for managing a Blender process for testing.

    This class handles the complete lifecycle of a Blender process:
    - Starting Blender with the socket server script
    - Waiting for the socket server to be ready
    - Sending capability requests via socket
    - Cleaning up the process on completion

    Example:
        >>> with BlenderProcessHarness("/path/to/blender") as harness:
        ...     response = harness.send_request({
        ...         "capability": "blender.get_scene",
        ...         "payload": {}
        ...     })
        ...     print(response["ok"])
    """

    def __init__(
        self,
        blender_path: str | Path,
        port: int | None = None,
        start_timeout: float = DEFAULT_START_TIMEOUT,
        request_timeout: float = DEFAULT_REQUEST_TIMEOUT,
    ) -> None:
        """Initialize the Blender process harness.

        Args:
            blender_path: Path to the Blender executable.
            port: Port number for socket communication. If None, a free port
                will be allocated automatically.
            start_timeout: Maximum time to wait for Blender to start (seconds).
            request_timeout: Maximum time to wait for a response (seconds).
        """
        self._blender_path = Path(blender_path)
        self._port = port if port is not None else find_free_port()
        self._start_timeout = start_timeout
        self._request_timeout = request_timeout

        self._process: subprocess.Popen[bytes] | None = None
        self._stdout: list[str] = []
        self._stderr: list[str] = []
        self._started = False

        # Path to the addon package that starts the socket server
        self._server_script = (
            Path(__file__).parent.parent.parent.parent / "src" / "blender_mcp_addon" / "server" / "socket_server.py"
        )

    def start(self) -> bool:
        """Start the Blender process with the socket server.

        Returns:
            True if Blender started successfully and the socket server is ready,
            False otherwise.
        """
        if self._started:
            logger.warning("Blender process already started")
            return True

        if not self._blender_path.exists():
            logger.error("Blender executable not found: %s", self._blender_path)
            return False

        # Prepare environment with port
        env = os.environ.copy()
        env["MCP_SOCKET_PORT"] = str(self._port)

        # Build command
        cmd = [
            str(self._blender_path),
            "--background",
            "--python",
            str(self._server_script),
        ]

        logger.debug("Starting Blender: %s", " ".join(cmd))

        try:
            # Start process
            self._process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",  # Handle encoding errors gracefully
                bufsize=1,  # Line buffered
            )

            # Wait for socket server to be ready
            if not self._wait_for_ready():
                self.stop()
                return False

            self._started = True
            return True

        except (OSError, subprocess.SubprocessError) as e:
            logger.error("Failed to start Blender: %s", e)
            return False

    def _wait_for_ready(self) -> bool:
        """Wait for the Blender socket server to be ready.

        Returns:
            True if the server is ready, False if timeout occurred.
        """
        start_time = time.time()
        deadline = start_time + self._start_timeout

        while time.time() < deadline:
            # Try to connect to the socket
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1.0)
                    s.connect(("127.0.0.1", self._port))
                    logger.debug("Socket server ready on port %d", self._port)
                    return True
            except (ConnectionRefusedError, socket.timeout, OSError):
                # Check if process is still running
                if self._process and self._process.poll() is not None:
                    # Process exited unexpectedly
                    stdout, stderr = self._process.communicate()
                    logger.error("Blender process exited unexpectedly")
                    logger.error("stdout: %s", stdout)
                    logger.error("stderr: %s", stderr)
                    return False
                time.sleep(0.1)

        logger.error("Timeout waiting for Blender to start (%.1fs)", self._start_timeout)
        return False

    def send_request(self, request: dict[str, Any]) -> dict[str, Any]:
        """Send a capability request to Blender via socket.

        Args:
            request: The capability request dictionary.

        Returns:
            The response dictionary from Blender.

        Raises:
            RuntimeError: If the harness is not started or connection fails.
            TimeoutError: If no response is received within the timeout.
        """
        if not self._started or self._process is None:
            raise RuntimeError("Blender process not started. Call start() first.")

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(self._request_timeout)
                s.connect(("127.0.0.1", self._port))

                # Send request
                request_json = json.dumps(request) + "\n"
                s.sendall(request_json.encode("utf-8"))

                # Receive response
                data = b""
                while True:
                    chunk = s.recv(4096)
                    if not chunk:
                        break
                    data += chunk
                    if b"\n" in data:
                        break

                if not data:
                    raise RuntimeError("No response from Blender")

                response = json.loads(data.decode("utf-8").strip())
                return response

        except socket.timeout:
            raise TimeoutError(f"Request timeout after {self._request_timeout}s. Blender may be unresponsive.")
        except (ConnectionError, OSError) as e:
            raise RuntimeError(f"Socket communication failed: {e}") from e
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON response from Blender: {e}") from e

    def stop(self) -> None:
        """Stop the Blender process and cleanup resources."""
        if self._process is not None:
            # Capture output before terminating
            try:
                if self._process.stdout:
                    remaining_stdout = self._process.stdout.read()
                    self._stdout.extend(remaining_stdout.splitlines())
                if self._process.stderr:
                    remaining_stderr = self._process.stderr.read()
                    self._stderr.extend(remaining_stderr.splitlines())
            except (OSError, UnicodeDecodeError):
                # Ignore errors when reading output
                pass

            # Terminate the process
            with suppress(OSError):
                self._process.terminate()

            try:
                self._process.wait(timeout=5.0)
            except subprocess.TimeoutExpired:
                self._process.kill()
                self._process.wait()

            self._process = None

        self._started = False

    def get_stdout(self) -> list[str]:
        """Get captured stdout from the Blender process.

        Returns:
            List of stdout lines.
        """
        return self._stdout.copy()

    def get_stderr(self) -> list[str]:
        """Get captured stderr from the Blender process.

        Returns:
            List of stderr lines.
        """
        return self._stderr.copy()

    def __enter__(self) -> BlenderProcessHarness:
        """Enter the context manager and start Blender.

        Returns:
            The harness instance.
        """
        if not self.start():
            raise RuntimeError("Failed to start Blender process")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
        """Exit the context manager and ensure Blender is stopped.

        Args:
            exc_type: Exception type if an exception occurred.
            exc_val: Exception value if an exception occurred.
            exc_tb: Exception traceback if an exception occurred.
        """
        self.stop()
