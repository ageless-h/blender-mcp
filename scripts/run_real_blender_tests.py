#!/usr/bin/env python3
"""Script to run real Blender tests and aggregate results.

This script executes the real Blender integration tests against all
configured Blender versions and aggregates the results into the
compatibility-results.json file.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

import _pathfix  # noqa: F401 — ensure src/ and repo root are on sys.path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
COMPATIBILITY_RESULTS_PATH = PROJECT_ROOT / "docs" / "versioning" / "compatibility-results.json"


def run_pytest_for_version(blender_version: str, blender_path: str) -> dict[str, any]:
    """Run pytest for a specific Blender version.

    Args:
        blender_version: Version string (e.g., "4.2.17").
        blender_path: Path to the Blender executable.

    Returns:
        Dictionary with test results for this version.
    """
    import os

    env = os.environ.copy()
    env["BLENDER_EXECUTABLE"] = blender_path

    print(f"\n{'=' * 60}")
    print(f"Testing Blender {blender_version}")
    print(f"Path: {blender_path}")
    print('=' * 60)

    # Run pytest with JUnit XML output for structured result parsing
    xml_fd, xml_path = tempfile.mkstemp(suffix=".xml", prefix="pytest_results_")
    os.close(xml_fd)
    try:
        result = subprocess.run(
            [
                sys.executable, "-m", "pytest",
                "tests/integration/real_blender/test_real_capabilities.py",
                "-v",
                "--tb=short",
                "-o", "console_output_style=classic",
                f"--junitxml={xml_path}",
            ],
            cwd=PROJECT_ROOT,
            env=env,
            capture_output=True,
            text=True,
        )

        # Parse output
        output = result.stdout + result.stderr

        # Parse test counts from JUnit XML
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            for suite in root.iter("testsuite"):
                total_tests += int(suite.get("tests", 0))
                failed_tests += int(suite.get("failures", 0)) + int(suite.get("errors", 0))
            passed_tests = total_tests - failed_tests
        except (ET.ParseError, FileNotFoundError):
            pass
    finally:
        Path(xml_path).unlink(missing_ok=True)

    return {
        "version": blender_version,
        "status": "pass" if result.returncode == 0 else "fail",
        "timestamp": datetime.now().isoformat(),
        "test_count": total_tests,
        "passed": passed_tests,
        "failed": failed_tests,
        "path": str(blender_path),
        "output": output[-1000:] if len(output) > 1000 else output,  # Last 1000 chars
    }


def load_existing_results() -> dict[str, any]:
    """Load existing compatibility results.

    Returns:
        Existing results dictionary, or empty dict if file doesn't exist.
    """
    if COMPATIBILITY_RESULTS_PATH.exists():
        try:
            with open(COMPATIBILITY_RESULTS_PATH, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass

    return {
        "format_version": "1.0",
        "last_updated": None,
        "test_results": [],
    }


def save_results(results: dict[str, any]) -> None:
    """Save compatibility results to file.

    Args:
        results: Results dictionary to save.
    """
    COMPATIBILITY_RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(COMPATIBILITY_RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\n{'=' * 60}")
    print(f"Results saved to: {COMPATIBILITY_RESULTS_PATH}")
    print('=' * 60)


def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    from tests.integration.real_blender._config import load_blender_configs

    # Load Blender configurations
    configs = load_blender_configs()

    if not configs:
        print("ERROR: No Blender configurations found.")
        print("Please configure Blender paths in tests/blender-paths.json")
        print("or set the BLENDER_EXECUTABLE environment variable.")
        return 1

    print(f"Found {len(configs)} Blender configuration(s)")

    # Load existing results
    existing_results = load_existing_results()

    # Create a map of existing results by version
    existing_by_version = {
        v["version"]: v for v in existing_results.get("test_results", [])
    }

    # Run tests for each version
    new_results = []
    for config in configs:
        version = config["version"]
        path = config["path"]

        version_result = run_pytest_for_version(version, path)
        new_results.append(version_result)

        # Update existing map
        existing_by_version[version] = version_result

    # Update results
    results = {
        "format_version": existing_results.get("format_version", "1.0"),
        "last_updated": datetime.now().isoformat(),
        "test_results": list(existing_by_version.values()),
    }

    # Save results
    save_results(results)

    # Print summary
    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print('=' * 60)

    for result in new_results:
        status_symbol = "✓" if result["status"] == "pass" else "✗"
        print(f"{status_symbol} Blender {result['version']}: {result['status'].upper()}")
        print(f"  Tests: {result['passed']}/{result['test_count']} passed")

    # Return non-zero if any tests failed
    if any(r["status"] == "fail" for r in new_results):
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
