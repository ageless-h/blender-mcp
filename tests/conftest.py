# -*- coding: utf-8 -*-
"""Pytest configuration and shared fixtures.

This module provides centralized path setup so that individual test files
do not need to manipulate sys.path. Simply importing from conftest or
running via pytest automatically ensures the src/ directory is on the path.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

# Project paths - available to all tests
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
TESTS = ROOT / "tests"

# Ensure src/ is on sys.path for all tests
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# Ensure tests/ is on sys.path for fake_bpy imports
if str(TESTS) not in sys.path:
    sys.path.insert(0, str(TESTS))


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Return the project root directory."""
    return ROOT


@pytest.fixture(scope="session")
def src_path() -> Path:
    """Return the src/ directory path."""
    return SRC


@pytest.fixture(scope="session")
def use_mock_adapter():
    """Set MCP_ADAPTER to 'mock' for tests that don't require real Blender."""
    original = os.environ.get("MCP_ADAPTER")
    os.environ["MCP_ADAPTER"] = "mock"
    yield
    if original is None:
        os.environ.pop("MCP_ADAPTER", None)
    else:
        os.environ["MCP_ADAPTER"] = original
