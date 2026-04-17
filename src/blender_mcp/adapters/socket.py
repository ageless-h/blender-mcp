# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import logging
import socket
import threading
import time
from typing import Any, Callable, Dict, Optional

from blender_mcp.adapters.types import AdapterResult

logger = logging.getLogger(__name__)

_FRIENDLY_ERRORS: Dict[str, str] = {
    "adapter_timeout": ("Command timed out. Try simplifying the request or breaking it into smaller steps."),
    "adapter_unavailable": (
        "Cannot connect to Blender. "
        "Please ensure the Blender MCP addon is enabled and the server is started "
        "(N-panel > Blender MCP > Start Server). Also check the host/port settings."
    ),
    "adapter_empty_response": (
        "Blender returned an empty response. "
        "The addon server may have crashed or is in an inconsistent state. "
        "Try restarting the server in Blender."
    ),
    "adapter_invalid_response": (
        "Blender returned an invalid response that could not be parsed. Try restarting the addon server."
    ),
}

_RETRYABLE_ERRORS = {"adapter_unavailable", "adapter_timeout"}


def _friendly_error(code: str) -> str:
    """Return a user-friendly error message for the given error code."""
    return _FRIENDLY_ERRORS.get(code, code)


class SocketAdapter:
    """Adapter that communicates with Blender addon over TCP socket.

    Supports persistent connection with automatic reconnection on failure.
    Thread-safe: uses a lock to prevent concurrent access to the socket.
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 9876,
        timeout: float = 300.0,
        max_retries: int = 3,
        retry_base_delay: float = 1.0,
        use_persistent_connection: bool = True,
    ) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_base_delay = retry_base_delay
        self.use_persistent_connection = use_persistent_connection

        # Persistent connection state
        self._socket: Optional[socket.socket] = None
        self._lock = threading.Lock()
        self._connected = False

    def _connect(self) -> socket.socket:
        """Create a new socket connection."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        sock.connect((self.host, self.port))
        logger.debug("Connected to %s:%d", self.host, self.port)
        return sock

    def _recv_response(self, sock: socket.socket, started: float) -> AdapterResult:
        response_chunks = []
        leftover_data = b""
        while True:
            chunk = sock.recv(65536)
            if not chunk:
                break
            if b"\n" in chunk:
                idx = chunk.index(b"\n")
                response_chunks.append(chunk[:idx])
                leftover_data = chunk[idx + 1 :]
                break
            response_chunks.append(chunk)

        response_data = b"".join(response_chunks)
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        logger.debug("Response received in %.1fms", elapsed_ms)

        if not response_data and not leftover_data:
            return AdapterResult(
                ok=False,
                error="adapter_empty_response",
                timing_ms=elapsed_ms,
            )

        try:
            response = json.loads(response_data.decode("utf-8").strip())
        except json.JSONDecodeError:
            return AdapterResult(
                ok=False,
                error="adapter_invalid_response",
                timing_ms=elapsed_ms,
            )

        err_obj = response.get("error")
        return AdapterResult(
            ok=response.get("ok", False),
            result=response.get("result"),
            error=err_obj.get("code") if err_obj else None,
            error_message=err_obj.get("message") if err_obj else None,
            error_suggestion=err_obj.get("suggestion") if err_obj else None,
            timing_ms=elapsed_ms,
        )

    def _ensure_connected(self) -> socket.socket:
        """Ensure we have a valid connection, reconnecting if necessary."""
        if self._socket is not None:
            try:
                self._socket.setblocking(False)
                try:
                    # MSG_DONTWAIT is not available on Windows
                    # setblocking(False) already provides non-blocking behavior
                    flags = socket.MSG_PEEK
                    if hasattr(socket, "MSG_DONTWAIT"):
                        flags |= socket.MSG_DONTWAIT
                    data = self._socket.recv(1, flags)
                    if not data:
                        logger.debug("Socket connection closed, reconnecting")
                        self._close_socket()
                except BlockingIOError:
                    pass
                except (OSError, ConnectionError):
                    logger.debug("Socket error detected, reconnecting")
                    self._close_socket()
                finally:
                    if self._socket is not None:
                        self._socket.setblocking(True)
                        self._socket.settimeout(self.timeout)
            except (OSError, ConnectionError):
                self._close_socket()

        if self._socket is None:
            self._socket = self._connect()
            self._connected = True

        return self._socket

    def _close_socket(self) -> None:
        """Close the current socket if it exists."""
        if self._socket is not None:
            try:
                self._socket.close()
            except (OSError, RuntimeError):
                pass
            self._socket = None
            self._connected = False

    def close(self) -> None:
        """Close the persistent connection. Can be called externally for cleanup."""
        with self._lock:
            self._close_socket()

    def execute(
        self,
        capability: str,
        payload: Dict[str, Any],
        progress_callback: Callable[[float, float | None, str | None], None] | None = None,
    ) -> AdapterResult:
        """Execute a capability with automatic retry on transient errors.

        Args:
            capability: The capability to execute
            payload: The payload for the capability
            progress_callback: Optional callback for progress updates.
                Note: For socket adapter, progress updates require the Blender
                addon to send progress messages back. This callback is stored
                for potential future use with bidirectional communication.
        """
        self._progress_callback = progress_callback
        last_result: AdapterResult | None = None

        for attempt in range(self.max_retries):
            if self.use_persistent_connection:
                result = self._execute_persistent(capability, payload)
            else:
                result = self._execute_once(capability, payload)

            if result.ok:
                if attempt > 0:
                    logger.info("Succeeded on retry attempt %d", attempt)
                return result

            last_result = result
            error_code = result.error or ""

            if error_code not in _RETRYABLE_ERRORS:
                logger.debug("Non-retryable error: %s", error_code)
                break

            # On retryable error, close connection and retry
            if self.use_persistent_connection:
                self._close_socket()

            if attempt < self.max_retries - 1:
                delay = self.retry_base_delay * (2**attempt)
                logger.debug(
                    "Retry %d/%d after %.1fs (error: %s)",
                    attempt + 1,
                    self.max_retries,
                    delay,
                    error_code,
                )
                time.sleep(delay)

        assert last_result is not None
        last_result.error = _friendly_error(last_result.error or "")
        return last_result

    def _execute_persistent(self, capability: str, payload: Dict[str, Any]) -> AdapterResult:
        """Execute using persistent connection with reconnection on failure."""
        started = time.perf_counter()
        logger.debug("Executing capability=%s (persistent connection)", capability)

        with self._lock:
            try:
                sock = self._ensure_connected()

                request = json.dumps({"capability": capability, "payload": payload}, ensure_ascii=False)
                sock.sendall((request + "\n").encode("utf-8"))

                return self._recv_response(sock, started)

            except socket.timeout:
                elapsed_ms = (time.perf_counter() - started) * 1000.0
                logger.debug("Socket timeout after %.1fms", elapsed_ms)
                self._close_socket()
                return AdapterResult(
                    ok=False,
                    error="adapter_timeout",
                    timing_ms=elapsed_ms,
                )
            except (socket.error, ConnectionRefusedError, OSError) as exc:
                elapsed_ms = (time.perf_counter() - started) * 1000.0
                logger.debug("Connection error after %.1fms: %s", elapsed_ms, exc)
                self._close_socket()
                return AdapterResult(
                    ok=False,
                    error="adapter_unavailable",
                    timing_ms=elapsed_ms,
                )

    def _execute_once(self, capability: str, payload: Dict[str, Any]) -> AdapterResult:
        """Execute a single attempt via socket connection to Blender addon (non-persistent)."""
        started = time.perf_counter()
        logger.debug("Connecting to %s:%d for capability=%s", self.host, self.port, capability)
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(self.timeout)
                sock.connect((self.host, self.port))
                logger.debug("Connected to %s:%d", self.host, self.port)

                request = json.dumps({"capability": capability, "payload": payload}, ensure_ascii=False)
                sock.sendall((request + "\n").encode("utf-8"))

                return self._recv_response(sock, started)

        except socket.timeout:
            elapsed_ms = (time.perf_counter() - started) * 1000.0
            logger.debug("Socket timeout after %.1fms", elapsed_ms)
            return AdapterResult(
                ok=False,
                error="adapter_timeout",
                timing_ms=elapsed_ms,
            )
        except (socket.error, ConnectionRefusedError, OSError) as exc:
            elapsed_ms = (time.perf_counter() - started) * 1000.0
            logger.debug("Connection error after %.1fms: %s", elapsed_ms, exc)
            return AdapterResult(
                ok=False,
                error="adapter_unavailable",
                timing_ms=elapsed_ms,
            )

    def __del__(self) -> None:
        """Cleanup on destruction."""
        self._close_socket()
