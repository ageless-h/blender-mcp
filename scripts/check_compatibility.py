# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import os
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def check_compatibility(
    matrix_path: Path,
    results_path: Path,
    target_version: str | None = None,
) -> bool:
    if not matrix_path.exists() or not results_path.exists():
        return False

    matrix = load_json(matrix_path)
    results = load_json(results_path)
    supported = set(matrix.get("lts_versions", []))
    latest = matrix.get("latest_version")
    if latest:
        supported.add(latest)

    recorded = set(results.keys())
    if not supported.issubset(recorded):
        return False

    if target_version and target_version not in supported:
        return False
    return True


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    matrix_path = root / "docs" / "versioning" / "support-matrix.json"
    results_path = root / "docs" / "versioning" / "compatibility-results.json"
    target = os.environ.get("BLENDER_VERSION")
    return 0 if check_compatibility(matrix_path, results_path, target) else 1


if __name__ == "__main__":
    raise SystemExit(main())
