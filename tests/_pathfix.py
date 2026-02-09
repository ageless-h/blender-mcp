"""Re-export shared path setup for test discovery."""
from __future__ import annotations

import sys
from pathlib import Path

# Import the canonical _pathfix from the repo root.
_root = str(Path(__file__).resolve().parent.parent)
if _root not in sys.path:
    sys.path.insert(0, _root)

from _pathfix import ROOT, SRC  # noqa: E402

__all__ = ["ROOT", "SRC"]
