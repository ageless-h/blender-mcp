#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run integration tests against a real Blender instance in CI.

Delegates to test_all_26_tools.py (36 E2E tests) via unittest subprocess.
The test module manages Blender process lifecycle via BlenderProcessHarness.

Usage:
    python scripts/ci_run_blender_tests.py <blender_executable>

Environment variables:
    MCP_SOCKET_PORT  - Port override (default: auto-assign in test)
    TEST_TIMEOUT     - Per-test timeout in seconds (default: 30)
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


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


def run_tests(blender_exe: str, blender_version: tuple[int, ...]) -> int:
    env = os.environ.copy()
    env["BLENDER_EXECUTABLE"] = blender_exe

    cmd = [
        "uv",
        "run",
        "python",
        "-m",
        "unittest",
        "tests.integration.real_blender.test_all_26_tools",
        "-v",
    ]

    print(f"Running: {' '.join(cmd)}")
    print(f"BLENDER_EXECUTABLE={blender_exe}")
    print()

    start = time.time()
    result = subprocess.run(
        cmd,
        env=env,
        cwd=str(PROJECT_ROOT),
        check=False,
    )
    elapsed = time.time() - start

    print(f"\nTests finished in {elapsed:.1f}s — exit code {result.returncode}")
    return result.returncode


def _write_results(
    path: Path,
    version: tuple[int, ...],
    returncode: int,
    exe_path: str,
) -> None:
    existing: dict = {}
    if path.exists():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            existing = {"test_results": []}

    version_str = ".".join(str(v) for v in version)
    results_map = {r["version"]: r for r in existing.get("test_results", [])}

    results_map[version_str] = {
        "version": version_str,
        "status": "pass" if returncode == 0 else "fail",
        "checked_at": datetime.now().isoformat()[:10],
        "ci": True,
        "tests": {"integration": "pass" if returncode == 0 else "fail"},
        "path": exe_path,
    }

    existing["test_results"] = list(results_map.values())
    existing["last_updated"] = datetime.now().isoformat()[:10]

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(existing, indent=2) + "\n", encoding="utf-8")
    print(f"Results written to {path}")


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

    returncode = run_tests(blender_exe, blender_version)

    results_path = PROJECT_ROOT / "docs" / "versioning" / "compatibility-results.json"
    _write_results(results_path, blender_version, returncode, blender_exe)

    return returncode


if __name__ == "__main__":
    sys.exit(main())
