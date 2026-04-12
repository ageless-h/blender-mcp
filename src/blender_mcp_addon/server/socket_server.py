# -*- coding: utf-8 -*-
"""Socket server for MCP communication with the addon."""

from __future__ import annotations

import json
import logging
import queue
import socket
import threading
from typing import Any

from ..capabilities.base import execute_capability
from .timeouts import get_timeout

logger = logging.getLogger(__name__)

_server_lock = threading.Lock()
_server_socket: socket.socket | None = None
_server_thread: threading.Thread | None = None
_shutdown_flag = threading.Event()

# Main-thread dispatch queue: items are (request, response_holder, done_event, timeout)
_dispatch_queue: queue.Queue[tuple[dict, list, threading.Event, float]] = queue.Queue()
_timer_registered = False

_TIMER_INTERVAL = 0.05  # seconds between main-thread polls
_WATCHDOG_INTERVAL = 2.0  # seconds between watchdog checks
_last_poll_time: float = 0.0


def is_server_running() -> bool:
    """Check if the socket server is currently running."""
    with _server_lock:
        return _server_socket is not None


def get_server_address() -> tuple[str, int]:
    """Get the server address from addon preferences."""
    try:
        import bpy  # type: ignore

        prefs = bpy.context.preferences.addons["blender_mcp_addon"].preferences
        return prefs.host, prefs.port
    except (AttributeError, KeyError, ImportError):
        return "127.0.0.1", 9876


def start_socket_server(host: str | None = None, port: int | None = None) -> dict[str, Any]:
    """Start the socket server for receiving capability requests."""
    global _server_socket, _server_thread

    with _server_lock:
        if _server_socket is not None:
            return {"ok": False, "error": "server_already_running"}

        if host is None or port is None:
            default_host, default_port = get_server_address()
            host = host or default_host
            port = port or default_port

        _shutdown_flag.clear()

        try:
            _server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            _server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            _server_socket.bind((host, port))
            _server_socket.listen(5)
            _server_socket.settimeout(1.0)

            _server_thread = threading.Thread(
                target=_server_loop,
                daemon=True,
            )
            _server_thread.start()
            _ensure_timer_registered()
            _ensure_watchdog_registered()

            logger.info("Socket server started on %s:%s", host, port)
            return {"ok": True, "host": host, "port": port}
        except (OSError, RuntimeError) as exc:
            logger.error("Failed to start socket server: %s", exc)
            _server_socket = None
            return {"ok": False, "error": str(exc)}


def stop_socket_server() -> dict[str, Any]:
    """Stop the socket server."""
    global _server_socket, _server_thread

    with _server_lock:
        if _server_socket is None:
            return {"ok": False, "error": "server_not_running"}

        _shutdown_flag.set()

        try:
            _server_socket.close()
        except (OSError, RuntimeError) as exc:
            logger.debug("Error closing server socket: %s", exc)

        if _server_thread is not None:
            _server_thread.join(timeout=5.0)
            _server_thread = None

        _server_socket = None
        _unregister_timer()
        logger.info("Socket server stopped")
        return {"ok": True}


def _server_loop() -> None:
    """Main server loop accepting connections."""
    global _server_socket

    while not _shutdown_flag.is_set():
        with _server_lock:
            sock = _server_socket
        if sock is None:
            break

        try:
            client_socket, addr = sock.accept()
            client_thread = threading.Thread(
                target=_handle_client,
                args=(client_socket,),
                daemon=True,
            )
            client_thread.start()
        except socket.timeout:
            continue
        except OSError:
            break


def _handle_client(client_socket: socket.socket) -> None:
    """Handle a single client connection."""
    try:
        client_socket.settimeout(30.0)
        data = b""

        while True:
            chunk = client_socket.recv(4096)
            if not chunk:
                break
            data += chunk
            if b"\n" in data:
                break

        if not data:
            return

        request_str = data.decode("utf-8").strip()
        try:
            request = json.loads(request_str)
        except json.JSONDecodeError:
            response = {
                "ok": False,
                "result": None,
                "error": {"code": "parse_error", "message": "Invalid JSON"},
            }
            client_socket.sendall((json.dumps(response) + "\n").encode("utf-8"))
            return

        response = _dispatch_to_main_thread(request)
        client_socket.sendall((json.dumps(response, ensure_ascii=False) + "\n").encode("utf-8"))

    except (OSError, RuntimeError, ConnectionError) as exc:
        logger.error("Error handling client: %s", exc)
    finally:
        try:
            client_socket.close()
        except (OSError, RuntimeError) as exc:
            logger.debug("Error closing client socket: %s", exc)


def _dispatch_to_main_thread(request: dict) -> dict:
    """Queue a request for main-thread execution and block until done."""
    _kick_timer_if_dead()
    capability = request.get("capability", "")
    timeout = get_timeout(capability)
    response_holder: list[dict] = []
    done_event = threading.Event()
    _dispatch_queue.put((request, response_holder, done_event, timeout))
    done_event.wait(timeout=timeout)
    if response_holder:
        return response_holder[0]
    return {
        "ok": False,
        "result": None,
        "error": {
            "code": "timeout",
            "message": f"Main-thread dispatch timed out after {timeout:.0f}s for {capability}",
        },
    }


def _main_thread_poll() -> float | None:
    """Timer callback — runs on Blender's main thread, drains the queue."""
    global _last_poll_time
    import time as _time

    _last_poll_time = _time.monotonic()

    while not _dispatch_queue.empty():
        try:
            request, response_holder, done_event, _timeout = _dispatch_queue.get_nowait()
        except queue.Empty:
            break
        try:
            result = execute_capability(request)
            response_holder.append(result)
        except (AttributeError, RuntimeError, TypeError) as exc:
            logger.error("Main-thread execution error: %s", exc)
            response_holder.append(
                {
                    "ok": False,
                    "result": None,
                    "error": {"code": "main_thread_error", "message": str(exc)},
                }
            )
        finally:
            done_event.set()

    if _shutdown_flag.is_set():
        return None  # unregister timer
    return _TIMER_INTERVAL


def _ensure_timer_registered() -> None:
    """Register the main-thread poll timer if not already active."""
    global _timer_registered
    if _timer_registered:
        return
    try:
        import bpy  # type: ignore

        bpy.app.timers.register(_main_thread_poll, first_interval=_TIMER_INTERVAL, persistent=True)
        _timer_registered = True
        logger.debug("Main-thread dispatch timer registered")
    except (AttributeError, RuntimeError, ImportError) as exc:
        logger.error("Failed to register dispatch timer: %s", exc)


def _ensure_watchdog_registered() -> None:
    try:
        import bpy  # type: ignore

        if not bpy.app.timers.is_registered(_watchdog_poll):
            bpy.app.timers.register(_watchdog_poll, first_interval=_WATCHDOG_INTERVAL, persistent=True)
            logger.debug("Watchdog timer registered")
    except (AttributeError, RuntimeError, ImportError) as exc:
        logger.error("Failed to register watchdog timer: %s", exc)


def _unregister_timer() -> None:
    """Unregister the main-thread poll timer."""
    global _timer_registered
    if not _timer_registered:
        return
    try:
        import bpy  # type: ignore

        if bpy.app.timers.is_registered(_main_thread_poll):
            bpy.app.timers.unregister(_main_thread_poll)
        if bpy.app.timers.is_registered(_watchdog_poll):
            bpy.app.timers.unregister(_watchdog_poll)
        _timer_registered = False
        logger.debug("Main-thread dispatch timer unregistered")
    except (AttributeError, RuntimeError, ImportError) as exc:
        logger.debug("Error unregistering dispatch timer: %s", exc)


def _watchdog_poll() -> float | None:
    """Periodically verify _main_thread_poll is still registered.

    Blender can silently unregister timers on file-load or undo operations.
    This watchdog re-registers the poll timer if it detects it has died.
    """
    if _shutdown_flag.is_set():
        return None
    try:
        import bpy  # type: ignore

        if not bpy.app.timers.is_registered(_main_thread_poll):
            logger.warning("Watchdog: _main_thread_poll died — re-registering")
            bpy.app.timers.register(
                _main_thread_poll,
                first_interval=0.0,
                persistent=True,
            )
    except (AttributeError, RuntimeError, ImportError) as exc:
        logger.error("Watchdog: failed to re-register poll timer: %s", exc)
    return _WATCHDOG_INTERVAL


def _kick_timer_if_dead() -> None:
    """Called from connection threads to revive the poll timer if it died.

    Uses bpy.app.timers.register (not bpy.app.handlers) to schedule a
    one-shot restart from the main thread, which is thread-safe.
    """
    import time as _time

    if _shutdown_flag.is_set():
        return
    elapsed = _time.monotonic() - _last_poll_time if _last_poll_time else _WATCHDOG_INTERVAL + 1
    if elapsed > _WATCHDOG_INTERVAL and _last_poll_time > 0:
        logger.warning(
            "Timer appears dead (no tick for %.1fs), scheduling restart",
            elapsed,
        )
        try:
            import bpy  # type: ignore

            def _restart() -> None:
                if not bpy.app.timers.is_registered(_main_thread_poll):
                    bpy.app.timers.register(
                        _main_thread_poll,
                        first_interval=0.0,
                        persistent=True,
                    )

            bpy.app.timers.register(_restart, first_interval=0.0)
        except (AttributeError, RuntimeError, ImportError) as exc:
            logger.error("Failed to schedule timer restart: %s", exc)
