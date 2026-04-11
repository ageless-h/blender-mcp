# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import logging
import socket
import time
from typing import Any, Dict

from blender_mcp.adapters.types import AdapterResult

logger = logging.getLogger(__name__)

_FRIENDLY_ERRORS: Dict[str, str] = {
    "adapter_timeout": (
        "Command timed out. Try simplifying the request or breaking it into smaller steps."
    ),
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
        "Blender returned an invalid response that could not be parsed. "
        "Try restarting the addon server."
    ),
}

_RETRYABLE_ERRORS = {"adapter_unavailable", "adapter_timeout"}


def _friendly_error(code: str) -> str:
    """Return a user-friendly error message for the given error code."""
    return _FRIENDLY_ERRORS.get(code, code)


class SocketAdapter:
    """Adapter that communicates with Blender addon over TCP socket.

    Supports automatic retry with exponential backoff for transient errors.
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 9876,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_base_delay: float = 1.0,
    ) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_base_delay = retry_base_delay

    def execute(self, capability: str, payload: Dict[str, Any]) -> AdapterResult:
        """Execute a capability with automatic retry on transient errors."""
        last_result: AdapterResult | None = None

        for attempt in range(self.max_retries):
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

    def _execute_once(self, capability: str, payload: Dict[str, Any]) -> AdapterResult:
        """Execute a single attempt via socket connection to Blender addon."""
        started = time.perf_counter()
        logger.debug(
            "Connecting to %s:%d for capability=%s", self.host, self.port, capability
        )
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(self.timeout)
                sock.connect((self.host, self.port))
                logger.debug("Connected to %s:%d", self.host, self.port)

                request = json.dumps(
                    {"capability": capability, "payload": payload}, ensure_ascii=False
                )
                sock.sendall((request + "\n").encode("utf-8"))

                response_data = b""
                while True:
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    response_data += chunk
                    if b"\n" in response_data:
                        break

                elapsed_ms = (time.perf_counter() - started) * 1000.0
                logger.debug("Response received in %.1fms", elapsed_ms)

                if not response_data:
                    return AdapterResult(
                        ok=False,
                        error="adapter_empty_response",
                        timing_ms=elapsed_ms,
                    )

                response = json.loads(response_data.decode("utf-8").strip())
                err_obj = response.get("error")
                return AdapterResult(
                    ok=response.get("ok", False),
                    result=response.get("result"),
                    error=err_obj.get("code") if err_obj else None,
                    error_message=err_obj.get("message") if err_obj else None,
                    timing_ms=elapsed_ms,
                )

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
        except json.JSONDecodeError:
            elapsed_ms = (time.perf_counter() - started) * 1000.0
            logger.debug("Invalid JSON response after %.1fms", elapsed_ms)
            return AdapterResult(
                ok=False,
                error="adapter_invalid_response",
                timing_ms=elapsed_ms,
            )
