# -*- coding: utf-8 -*-
from __future__ import annotations

import sys
from pathlib import Path

try:
    from blender_mcp.adapters.plugin_contract import PluginContract, validate_contract
except ModuleNotFoundError:
    repo_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo_root))
    sys.path.insert(0, str(repo_root / "src"))
    from blender_mcp.adapters.plugin_contract import PluginContract, validate_contract


def main() -> int:
    contract_path = Path(__file__).resolve().parents[1] / "addon" / "contract.md"
    text = contract_path.read_text(encoding="utf-8")
    version = "0.0.0"
    entrypoints = []
    for line in text.splitlines():
        if line.strip().startswith("- Version:"):
            version = line.split(":", 1)[1].strip()
        if line.strip().startswith("- `") and "`:" in line:
            entry = line.split("`", 2)[1]
            entrypoints.append(entry)
    contract = PluginContract(version=version, entrypoints=tuple(entrypoints))
    if not validate_contract(contract, ["addon_entrypoint", "execute_capability"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
