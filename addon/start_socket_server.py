# -*- coding: utf-8 -*-
"""Blender script to start the MCP socket server for testing.

Run this in Blender:
    1. Open Blender
    2. Scripting workspace
    3. Open this file
    4. Click "Run Script"

Or from command line:
    blender.exe --background --python addon/start_socket_server.py
"""

import json
import socket
import sys
import threading
import time
from typing import Any


# =============================================================================
# Entrypoint functions (from entrypoint.py)
# =============================================================================

def addon_entrypoint() -> dict[str, str]:
    return {"status": "ok", "message": "addon ready"}


def execute_capability(request: dict[str, Any]) -> dict[str, Any]:
    import bpy
    started = time.perf_counter()
    try:
        if not isinstance(request, dict):
            return _error(
                code="invalid_request",
                message="request must be a dict",
                data={"type": type(request).__name__},
                started=started,
            )

        capability = request.get("capability")
        if not isinstance(capability, str) or not capability.strip():
            return _error(
                code="invalid_request",
                message="missing or invalid 'capability'",
                data={"capability": capability},
                started=started,
            )

        payload = request.get("payload", {})
        if payload is None:
            payload = {}
        if not isinstance(payload, dict):
            return _error(
                code="invalid_request",
                message="'payload' must be a dict",
                data={"type": type(payload).__name__},
                started=started,
            )

        if capability == "scene.read":
            return _scene_read(payload, started=started)
        if capability == "scene.write":
            return _scene_write(payload, started=started)

        return _error(
            code="unsupported_capability",
            message="capability is not supported by this addon",
            data={"capability": capability},
            started=started,
        )
    except Exception as exc:
        return _error(
            code="addon_exception",
            message="unhandled addon exception",
            data={"type": type(exc).__name__},
            started=started,
        )


def _scene_read(payload: dict[str, Any], *, started: float) -> dict[str, Any]:
    import bpy
    try:
        scene = bpy.context.scene
        selected = getattr(bpy.context, "selected_objects", []) or []
        active_obj = getattr(bpy.context, "active_object", None)
        snapshot = {
            "scene_name": getattr(scene, "name", None),
            "object_count": len(getattr(scene, "objects", []) or []),
            "selected_objects": sorted(
                [getattr(obj, "name", "") for obj in selected if getattr(obj, "name", "")]
            ),
            "active_object": getattr(active_obj, "name", None),
        }
        return _ok(result=snapshot, started=started)
    except Exception as exc:
        return _error(
            code="operation_failed",
            message="scene.read failed",
            data={"type": type(exc).__name__},
            started=started,
        )


def _scene_write(payload: dict[str, Any], *, started: float) -> dict[str, Any]:
    import bpy
    name = payload.get("name")
    if name is None:
        name = "MCP_POC_CUBE"
    if not isinstance(name, str) or not name.strip():
        return _error(
            code="invalid_params",
            message="'name' must be a non-empty string",
            data={"name": name},
            started=started,
        )

    cleanup = payload.get("cleanup")
    if cleanup is None:
        cleanup = True
    if not isinstance(cleanup, bool):
        return _error(
            code="invalid_params",
            message="'cleanup' must be a bool",
            data={"cleanup": cleanup},
            started=started,
        )

    try:
        mesh_name = f"{name}_mesh"

        if name in bpy.data.objects:
            existing = bpy.data.objects[name]
            bpy.data.objects.remove(existing, do_unlink=True)
        if mesh_name in bpy.data.meshes:
            existing_mesh = bpy.data.meshes[mesh_name]
            bpy.data.meshes.remove(existing_mesh)

        mesh = bpy.data.meshes.new(name=mesh_name)
        try:
            import bmesh
            bm = bmesh.new()
            bmesh.ops.create_cube(bm, size=2.0)
            bm.to_mesh(mesh)
            bm.free()
        except Exception:
            pass

        obj = bpy.data.objects.new(name=name, object_data=mesh)
        bpy.context.scene.collection.objects.link(obj)
        obj.location = (0.0, 0.0, 0.0)

        created = True
        if cleanup:
            bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.meshes.remove(mesh)
        result = {
            "action": "create_cube_placeholder",
            "name": name,
            "created": created,
            "cleanup": cleanup,
        }
        return _ok(result=result, started=started)
    except Exception as exc:
        return _error(
            code="operation_failed",
            message="scene.write failed",
            data={"type": type(exc).__name__},
            started=started,
        )


def _ok(*, result: dict[str, Any], started: float) -> dict[str, Any]:
    return {
        "ok": True,
        "result": result,
        "error": None,
        "timing_ms": (time.perf_counter() - started) * 1000.0,
    }


def _error(
    *,
    code: str,
    message: str,
    started: float,
    data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "ok": False,
        "result": None,
        "error": {"code": code, "message": message, "data": data},
        "timing_ms": (time.perf_counter() - started) * 1000.0,
    }


# =============================================================================
# Socket Server
# =============================================================================

_server_socket: socket.socket | None = None
_server_thread: threading.Thread | None = None
_shutdown_flag = threading.Event()


def start_socket_server(host: str = "127.0.0.1", port: int = 9876) -> dict[str, Any]:
    """Start the socket server for receiving capability requests."""
    global _server_socket, _server_thread

    if _server_socket is not None:
        return {"ok": False, "error": "server_already_running"}

    _shutdown_flag.clear()

    try:
        _server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        _server_socket.bind((host, port))
        _server_socket.listen(1)
        _server_socket.settimeout(1.0)

        _server_thread = threading.Thread(
            target=_server_loop,
            daemon=True,
        )
        _server_thread.start()

        return {"ok": True, "host": host, "port": port}
    except Exception as exc:
        _server_socket = None
        return {"ok": False, "error": str(exc)}


def _server_loop() -> None:
    """Main server loop accepting connections."""
    global _server_socket

    print("[Socket Server] Server loop started, waiting for connections...")

    while not _shutdown_flag.is_set():
        if _server_socket is None:
            break

        try:
            client_socket, addr = _server_socket.accept()
            print(f"[Socket Server] Client connected from {addr}")
            _handle_client(client_socket)
        except socket.timeout:
            continue
        except OSError:
            break

    print("[Socket Server] Server loop stopped.")


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
            print("[Socket Server] No data received from client")
            return

        request_str = data.decode("utf-8").strip()
        print(f"[Socket Server] Received request: {request_str[:100]}...")

        try:
            request = json.loads(request_str)
        except json.JSONDecodeError:
            response = {
                "ok": False,
                "result": None,
                "error": {"code": "parse_error", "message": "Invalid JSON"},
            }
            client_socket.sendall((json.dumps(response) + "\n").encode("utf-8"))
            print(f"[Socket Server] Sent parse error response")
            return

        # Call execute_capability
        response = execute_capability(request)
        print(f"[Socket Server] Response: ok={response.get('ok')}, timing: {response.get('timing_ms', 0):.2f}ms")

        client_socket.sendall((json.dumps(response) + "\n").encode("utf-8"))
        print(f"[Socket Server] Sent response to client")

    except Exception as e:
        print(f"[Socket Server] Error handling client: {type(e).__name__}: {e}")
    finally:
        try:
            client_socket.close()
        except Exception:
            pass


# =============================================================================
# Main
# =============================================================================

def main():
    import bpy  # Import bpy to verify we're in Blender

    print("=" * 60)
    print("Blender MCP Socket Server")
    print("=" * 60)
    print(f"Blender version: {bpy.app.version_string}")
    print(f"Python: {sys.version}")

    # Start the socket server
    result = start_socket_server(host="127.0.0.1", port=9876)

    if result.get("ok"):
        print(f"\n✓ Socket server started on {result['host']}:{result['port']}")
        print("\nServer is ready to accept capability execution requests.")
        print("\nTo test, run in another terminal:")
        print('  set MCP_ADAPTER=socket')
        print('  python -m examples.stdio_loop')
        print("\nThen send a JSON-RPC request like:")
        print('  {"jsonrpc":"2.0","id":1,"method":"scene.read","params":{"payload":{},"scopes":[]}}')
        print("\n" + "=" * 60)

        # Keep server alive for testing
        print("\nServer running... (will auto-exit after 60 seconds for testing)")
        print("Press Ctrl+C to stop early.\n")

        try:
            # Run for 60 seconds then exit (for background testing)
            for i in range(60):
                if _shutdown_flag.is_set():
                    break
                time.sleep(1)
                if i % 10 == 0 and i > 0:
                    print(f"[Server] Still running... {60-i}s remaining")
        except KeyboardInterrupt:
            print("\n[Server] Interrupted by user")
    else:
        print(f"\n✗ Failed to start server: {result.get('error')}")
        return 1

    print("\n[Server] Shutting down...")
    return 0


if __name__ == "__main__":
    main()
