# -*- coding: utf-8 -*-
from __future__ import annotations

import ast
import sys
from pathlib import Path

try:
    from blender_mcp.adapters.plugin_contract import PluginContract, validate_contract
except ModuleNotFoundError:
    repo_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo_root))
    sys.path.insert(0, str(repo_root / "src"))
    from blender_mcp.adapters.plugin_contract import PluginContract, validate_contract


def _has_function(source_path: Path, function_name: str) -> bool:
    """Check if a Python file contains a specific function definition."""
    try:
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                return True
        return False
    except Exception:
        return False


def main() -> int:
    """Validate the addon plugin boundary contract.

    The new addon implementation (src/blender_mcp_addon/) defines the following
    contract entrypoints:
    - `execute_capability`: Main entrypoint for capability execution
    """
    # The new contract is defined by the actual implementation
    # in src/blender_mcp_addon/capabilities/base.py
    version = "0.1.0"
    entrypoints = ("execute_capability",)

    contract = PluginContract(version=version, entrypoints=entrypoints)

    # Validate that required entrypoints are present
    required_entrypoints = ["execute_capability"]
    if not validate_contract(contract, required_entrypoints):
        print("ERROR: Contract validation failed", file=sys.stderr)
        return 1

    # Verify the actual implementation exists by checking the source file
    # (We can't import the module directly because it requires bpy)
    repo_root = Path(__file__).resolve().parents[1]
    impl_path = repo_root / "src" / "blender_mcp_addon" / "capabilities" / "base.py"

    if not impl_path.exists():
        print(f"ERROR: Implementation file not found: {impl_path}", file=sys.stderr)
        return 1

    # Check that execute_capability function exists
    if not _has_function(impl_path, "execute_capability"):
        print(f"ERROR: execute_capability function not found in {impl_path}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
