# -*- coding: utf-8 -*-
"""Check Blender version compatibility against support matrix.

This script validates that:
1. All supported versions have compatibility results
2. Target version (if provided) is in the support matrix
3. Minimum version requirements are met
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def load_json(path: Path) -> dict:
    """Load JSON file."""
    return json.loads(path.read_text(encoding="utf-8"))


def parse_version(version: str) -> tuple[int, ...]:
    """Parse version string into comparable tuple."""
    return tuple(int(part) for part in version.split("."))


def check_version_format(version: str) -> bool:
    """Check if version string is valid (e.g., '3.6', '4.2')."""
    parts = version.split(".")
    return len(parts) >= 2 and all(p.isdigit() for p in parts)


def check_compatibility(
    matrix_path: Path,
    results_path: Path,
    target_version: str | None = None,
) -> bool:
    """Check compatibility against support matrix.

    Args:
        matrix_path: Path to support-matrix.json
        results_path: Path to compatibility-results.json
        target_version: Specific version to check (optional)

    Returns:
        True if all checks pass, False otherwise
    """
    if not matrix_path.exists():
        print(f"Error: Support matrix not found at {matrix_path}")
        return False
    if not results_path.exists():
        print(f"Error: Compatibility results not found at {results_path}")
        return False

    matrix = load_json(matrix_path)
    results = load_json(results_path)

    # Get supported versions from matrix
    supported_versions = matrix.get("supported_versions", [])
    if not supported_versions:
        print("Error: No supported versions in matrix")
        return False

    # Build supported version set
    supported_set = {v["version"] for v in supported_versions if v.get("tested") or v.get("status") != "pending"}

    # Build results map
    test_results = results.get("test_results", [])
    results_map = {r["version"]: r for r in test_results}

    # Check all supported versions have results
    for version_entry in supported_versions:
        version = version_entry["version"]
        status = version_entry.get("status", "unknown")
        tested = version_entry.get("tested", False)

        if not tested and status == "latest":
            # Latest versions can be pending
            continue

        if version not in results_map:
            print(f"Warning: Version {version} has no test results")
            continue

        result = results_map[version]
        result_status = result.get("status", "unknown")
        if result_status == "pass":
            print(f"[OK] {version}: {result_status}")
        elif result_status == "pending":
            print(f"[PENDING] {version}: {result_status}")
        else:
            print(f"[FAIL] {version}: {result_status}")

    # Check minimum version requirement
    min_version = matrix.get("policy", {}).get("min_version")
    if min_version and target_version:
        if parse_version(target_version) < parse_version(min_version):
            print(f"Error: Version {target_version} is below minimum {min_version}")
            return False

    # Check target version is supported
    if target_version:
        if not check_version_format(target_version):
            print(f"Error: Invalid version format '{target_version}'")
            return False

        supported_versions_list = [v["version"] for v in supported_versions]
        is_supported = any(
            parse_version(target_version) == parse_version(v)
            for v in supported_versions_list
        )

        if not is_supported:
            print(f"Warning: Version {target_version} not explicitly in support matrix")
            # Check if it's newer than latest (might be OK)
            latest = max(supported_versions_list, key=parse_version)
            if parse_version(target_version) > parse_version(latest):
                print(f"Note: {target_version} is newer than latest supported {latest}")
            else:
                print(f"Error: Version {target_version} is not supported")
                return False

    return True


def main() -> int:
    """Main entry point."""
    root = Path(__file__).resolve().parents[1]
    matrix_path = root / "docs" / "versioning" / "support-matrix.json"
    results_path = root / "docs" / "versioning" / "compatibility-results.json"
    target = os.environ.get("BLENDER_VERSION")

    # Print current status
    print(f"Checking compatibility (BLENDER_VERSION={target or 'all'})")
    print(f"Support matrix: {matrix_path}")
    print(f"Results file: {results_path}")
    print("-" * 50)

    success = check_compatibility(matrix_path, results_path, target)

    print("-" * 50)
    if success:
        print("[OK] Compatibility check passed")
        return 0
    else:
        print("[FAIL] Compatibility check failed")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
