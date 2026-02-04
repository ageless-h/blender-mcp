# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _print(obj: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(obj, sort_keys=True) + "\n")
    sys.stdout.flush()


def main() -> int:
    sys.path.insert(0, str(_repo_root()))

    from addon.entrypoint import addon_entrypoint, execute_capability

    _print({"event": "addon_entrypoint", "result": addon_entrypoint()})

    read_resp = execute_capability({"capability": "scene.read", "payload": {}})
    _print({"event": "scene.read", "response": read_resp})

    write_resp = execute_capability(
        {"capability": "scene.write", "payload": {"name": "MCP_POC_CUBE", "cleanup": True}}
    )
    _print({"event": "scene.write", "response": write_resp})

    error_resp = execute_capability({"capability": "scene.write", "payload": {"cleanup": "no"}})
    _print({"event": "error_case", "response": error_resp})

    if not read_resp.get("ok") or not write_resp.get("ok"):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
