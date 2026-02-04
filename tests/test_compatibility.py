# -*- coding: utf-8 -*-
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
                json.dumps({"lts_versions": ["3.6"], "latest_version": "4.0"}),
                encoding="utf-8",
            )
            results_path.write_text(json.dumps({"3.6": {}}), encoding="utf-8")

            self.assertFalse(check_compatibility(matrix_path, results_path))

    def test_check_compatibility_accepts_supported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            matrix_path = base / "support-matrix.json"
            results_path = base / "compatibility-results.json"

            matrix_path.write_text(
                json.dumps({"lts_versions": ["3.6"], "latest_version": "4.0"}),
                encoding="utf-8",
            )
            results_path.write_text(
                json.dumps(
                    {
                        "3.6": {"status": "unknown", "checked_at": "n/a"},
                        "4.0": {"status": "unknown", "checked_at": "n/a"},
                    }
                ),
                encoding="utf-8",
            )

            self.assertTrue(check_compatibility(matrix_path, results_path))


if __name__ == "__main__":
    unittest.main()
