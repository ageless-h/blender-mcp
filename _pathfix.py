"""Shared utility to ensure repo root and src/ are on sys.path.

Import this module from examples/, tests/, or scripts/ sub-packages
to guarantee importability of the project source tree.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

__all__ = ["ROOT", "SRC"]
