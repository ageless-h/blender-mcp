"""Ensure src/ is on sys.path before other tests import blender_mcp."""
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def test_src_path_added():
    assert str(SRC) in sys.path
