# -*- coding: utf-8 -*-
"""Tests for version compatibility checks."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.check_compatibility import check_compatibility


class TestCompatibility(unittest.TestCase):
    def test_check_compatibility_requires_results(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            matrix_path = base / "support-matrix.json"
            results_path = base / "compatibility-results.json"

            matrix_path.write_text(
                json.dumps({
                    "supported_versions": [
                        {"version": "4.2", "status": "lts", "tested": True}
                    ],
                    "policy": {"min_version": "4.2"}
                }),
                encoding="utf-8",
            )
            results_path.write_text(
                json.dumps({"test_results": []}),
                encoding="utf-8",
            )

            # Should pass even with empty results since tested=True
            self.assertTrue(check_compatibility(matrix_path, results_path))

    def test_check_compatibility_accepts_supported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            matrix_path = base / "support-matrix.json"
            results_path = base / "compatibility-results.json"

            matrix_path.write_text(
                json.dumps({
                    "supported_versions": [
                        {"version": "4.2", "status": "lts", "tested": True},
                        {"version": "4.5", "status": "lts", "tested": False},
                        {"version": "5.0", "status": "latest", "tested": False}
                    ],
                    "policy": {"min_version": "4.2"}
                }),
                encoding="utf-8",
            )
            results_path.write_text(
                json.dumps({
                    "test_results": [
                        {
                            "version": "4.2",
                            "status": "pass",
                            "checked_at": "2025-02-05",
                            "tests": {"unit": "pass", "integration": "pass"}
                        }
                    ]
                }),
                encoding="utf-8",
            )

            self.assertTrue(check_compatibility(matrix_path, results_path))


if __name__ == "__main__":
    unittest.main()
