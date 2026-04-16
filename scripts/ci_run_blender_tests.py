#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run integration tests against a real Blender instance in CI.

Launches Blender in background mode, starts the MCP socket server,
runs the E2E test suite via socket communication, and reports results.

Usage:
    python scripts/ci_run_blender_tests.py <blender_executable>

Environment variables:
    MCP_SOCKET_PORT  - Port for socket communication (default: auto-assign)
    MCP_SOCKET_HOST  - Host for socket communication (default: 127.0.0.1)
    TEST_TIMEOUT     - Per-test timeout in seconds (default: 30)
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LAUNCH_SCRIPT = PROJECT_ROOT / "src" / "blender_mcp_addon" / "server" / "_launch.py"

DEFAULT_START_TIMEOUT = 60
DEFAULT_REQUEST_TIMEOUT = 30
POLL_INTERVAL = 0.5


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        s.listen(1)
        return s.getsockname()[1]


CAPABILITY_TESTS: list[tuple[str, str, dict]] = [
    ("blender.get_scene", "Get scene info", {"include": ["stats", "version"]}),
    ("blender.get_objects", "List objects", {}),
    ("blender.get_object_data", "Get default Cube data", {"name": "Cube", "include": ["summary", "mesh_stats"]}),
    ("blender.get_selection", "Get selection", {}),
    ("blender.get_materials", "List materials", {}),
    (
        "blender.create_object",
        "Create test sphere",
        {"name": "CI_TestSphere", "object_type": "MESH", "primitive": "sphere"},
    ),
    ("blender.modify_object", "Move test sphere", {"name": "CI_TestSphere", "location": [2.0, 0.0, 1.0]}),
    (
        "blender.manage_material",
        "Create test material",
        {"action": "create", "name": "CI_TestMat", "base_color": [0.8, 0.2, 0.1, 1.0]},
    ),
    (
        "blender.manage_material",
        "Assign material",
        {"action": "assign", "name": "CI_TestMat", "object_name": "CI_TestSphere"},
    ),
    (
        "blender.manage_modifier",
        "Add subdivision",
        {"action": "add", "object_name": "CI_TestSphere", "modifier_type": "SUBSURF"},
    ),
    ("blender.get_object_data", "Verify modifiers", {"name": "CI_TestSphere", "include": ["modifiers"]}),
    ("blender.manage_collection", "Create collection", {"action": "create", "collection_name": "CI_TestCollection"}),
    (
        "blender.setup_scene",
        "Setup render settings",
        {"engine": "BLENDER_EEVEE", "resolution_x": 640, "resolution_y": 480},
    ),
    ("blender.get_scene", "Verify scene after modifications", {"include": ["stats"]}),
]

CLEANUP_TESTS: list[tuple[str, str, dict]] = [
    ("blender.modify_object", "Delete test sphere", {"name": "CI_TestSphere", "action": "delete"}),
    ("blender.manage_material", "Delete test material", {"action": "delete", "name": "CI_TestMat"}),
    (
        "blender.manage_collection",
        "Delete test collection",
        {"action": "delete", "collection_name": "CI_TestCollection"},
    ),
]

BLENDER_5x_CAPABILITIES: list[tuple[str, str, dict]] = [
    ("blender.get_animation_data", "Check animation (may be empty)", {"target": "Cube", "include": ["keyframes"]}),
]


def send_request(sock: socket.socket, request: dict, timeout: float = DEFAULT_REQUEST_TIMEOUT) -> dict:
    request_json = json.dumps(request) + "\n"
    sock.sendall(request_json.encode("utf-8"))
    data = b""
    while True:
        sock.settimeout(timeout)
        chunk = sock.recv(4096)
        if not chunk:
            break
        data += chunk
        if b"\n" in data:
            break
    if not data:
        raise RuntimeError("No response from Blender")
    return json.loads(data.decode("utf-8").strip())


def run_tests(port: int, blender_version: tuple[int, ...]) -> tuple[int, int, int, list[str]]:
    passed = 0
    failed = 0
    errors: list[str] = []

    all_tests = list(CAPABILITY_TESTS)
    if blender_version >= (5, 0):
        all_tests.extend(BLENDER_5x_CAPABILITIES)
    all_tests.extend(CLEANUP_TESTS)

    for capability, description, payload in all_tests:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect(("127.0.0.1", port))
                sock.settimeout(DEFAULT_REQUEST_TIMEOUT)
                response = send_request(sock, {"capability": capability, "payload": payload})

            if response.get("ok", False):
                passed += 1
                print(f"  ✓ {description} ({capability})")
            else:
                failed += 1
                error_msg = response.get("error", {}).get("message", "unknown error")
                errors.append(f"  ✗ {description} ({capability}): {error_msg}")
                print(f"  ✗ {description} ({capability}): {error_msg}")
        except Exception as e:
            failed += 1
            errors.append(f"  ✗ {description} ({capability}): {e}")
            print(f"  ✗ {description} ({capability}): {e}")

    if errors:
        print(f"\nFailed tests ({len(errors)}):")
        for err in errors:
            print(err)

    return passed, failed, len(all_tests), errors


def get_blender_version(exe_path: str) -> tuple[int, ...]:
    result = subprocess.run(
        [exe_path, "--version"],
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    for line in result.stdout.strip().split("\n"):
        if line.startswith("Blender "):
            parts = line.split()[1].split(".")
            return tuple(int(p) for p in parts[:3])
    return (0, 0, 0)


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python ci_run_blender_tests.py <blender_executable>")
        return 1

    blender_exe = sys.argv[1]
    if not Path(blender_exe).exists():
        print(f"ERROR: Blender executable not found: {blender_exe}")
        return 1

    blender_version = get_blender_version(blender_exe)
    print(f"Blender version: {'.'.join(str(v) for v in blender_version)}")

    port = int(os.environ.get("MCP_SOCKET_PORT", "0")) or find_free_port()
    host = os.environ.get("MCP_SOCKET_HOST", "127.0.0.1")

    env = os.environ.copy()
    env["MCP_SOCKET_PORT"] = str(port)
    env["MCP_SOCKET_HOST"] = host

    print(f"Starting Blender on {host}:{port}...")
    process = subprocess.Popen(
        [
            blender_exe,
            "--background",
            "-noaudio",
            "--python-exit-code",
            "1",
            "--python",
            str(LAUNCH_SCRIPT),
        ],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    started = False
    deadline = time.time() + DEFAULT_START_TIMEOUT
    while time.time() < deadline:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1.0)
                s.connect((host, port))
                started = True
                print(f"Blender socket server ready on port {port}")
                break
        except (ConnectionRefusedError, socket.timeout, OSError):
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                print(f"Blender process exited unexpectedly (code {process.returncode})")
                if stderr:
                    print(f"stderr:\n{stderr[-2000:]}")
                return 1
            time.sleep(POLL_INTERVAL)

    if not started:
        print(f"ERROR: Blender did not start within {DEFAULT_START_TIMEOUT}s")
        process.terminate()
        process.wait(timeout=5)
        return 1

    try:
        print(
            f"\nRunning {len(CAPABILITY_TESTS) + len(CLEANUP_TESTS)} core tests"
            + (f" + {len(BLENDER_5x_CAPABILITIES)} Blender 5.x tests" if blender_version >= (5, 0) else "")
            + "..."
        )
        passed, failed, total, errors = run_tests(port, blender_version)
    finally:
        print("\nShutting down Blender...")
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5.0)
                s.connect((host, port))
                s.sendall(json.dumps({"capability": "blender.shutdown", "payload": {}}).encode() + b"\n")
        except Exception:
            pass
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()

    print(f"\n{'=' * 60}")
    print(f"Results: {passed}/{total} passed, {failed} failed")
    print(f"{'=' * 60}")

    results_path = PROJECT_ROOT / "docs" / "versioning" / "compatibility-results.json"
    _write_results(results_path, blender_version, passed, failed, total, blender_exe, errors)

    return 1 if failed > 0 else 0


def _write_results(
    path: Path,
    version: tuple[int, ...],
    passed: int,
    failed: int,
    total: int,
    exe_path: str,
    errors: list[str],
) -> None:
    existing: dict = {}
    if path.exists():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            existing = {"test_results": []}

    version_str = ".".join(str(v) for v in version)
    results_map = {r["version"]: r for r in existing.get("test_results", [])}

    from datetime import datetime

    results_map[version_str] = {
        "version": version_str,
        "status": "pass" if failed == 0 else "fail",
        "checked_at": datetime.now().isoformat()[:10],
        "ci": True,
        "tests": {"integration": "pass" if failed == 0 else "fail"},
        "test_count": total,
        "passed": passed,
        "failed": failed,
        "path": exe_path,
        "errors": errors[:5],
    }

    existing["test_results"] = list(results_map.values())
    existing["last_updated"] = datetime.now().isoformat()[:10]

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(existing, indent=2) + "\n", encoding="utf-8")
    print(f"Results written to {path}")


if __name__ == "__main__":
    sys.exit(main())
