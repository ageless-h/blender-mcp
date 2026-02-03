# -*- coding: utf-8 -*-
from __future__ import annotations


def addon_entrypoint() -> dict[str, str]:
    return {"status": "ok", "message": "addon ready"}
