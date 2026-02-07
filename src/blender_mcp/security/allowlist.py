# -*- coding: utf-8 -*-
from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Iterable, Set

from blender_mcp.security.audit import AuditEvent, AuditLogger


# Default allowlist for new unified tools (excludes script.execute for safety)
DEFAULT_ALLOWED_TOOLS: Set[str] = {
    "data.create",
    "data.read",
    "data.write",
    "data.delete",
    "data.list",
    "data.link",
    "operator.execute",
    "info.query",
    # Legacy tools (deprecated)
    "scene.read",
    "scene.write",
}

# Dangerous tools that require explicit enablement
DANGEROUS_TOOLS: Set[str] = {
    "script.execute",
}


@dataclass
class Allowlist:
    allowed: Set[str] = field(default_factory=lambda: set(DEFAULT_ALLOWED_TOOLS))
    audit_logger: AuditLogger | None = None
    script_execute_enabled: bool = False
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False, compare=False)

    def is_allowed(self, capability: str) -> bool:
        with self._lock:
            # Special handling for dangerous tools
            if capability in DANGEROUS_TOOLS:
                if capability == "script.execute":
                    return self.script_execute_enabled and capability in self.allowed
                return False
            return capability in self.allowed

    def enable_script_execute(self) -> None:
        """Explicitly enable script.execute (dangerous operation)."""
        with self._lock:
            self.script_execute_enabled = True
            self.allowed.add("script.execute")
        if self.audit_logger is not None:
            self.audit_logger.record(
                AuditEvent(
                    capability="allowlist.enable_dangerous",
                    ok=True,
                    data={"tool": "script.execute", "warning": "Arbitrary code execution enabled"},
                )
            )

    def disable_script_execute(self) -> None:
        """Disable script.execute."""
        with self._lock:
            self.script_execute_enabled = False
            self.allowed.discard("script.execute")
        if self.audit_logger is not None:
            self.audit_logger.record(
                AuditEvent(
                    capability="allowlist.disable_dangerous",
                    ok=True,
                    data={"tool": "script.execute"},
                )
            )

    def replace(self, capabilities: Iterable[str]) -> None:
        with self._lock:
            previous = self.allowed
            new_capabilities = set(capabilities)
            
            # Automatically filter out dangerous tools unless explicitly enabled
            if not self.script_execute_enabled:
                new_capabilities -= DANGEROUS_TOOLS
            
            self.allowed = new_capabilities
            added = sorted(self.allowed - previous)
            removed = sorted(previous - self.allowed)
        if self.audit_logger is not None:
            self.audit_logger.record(
                AuditEvent(
                    capability="allowlist.update",
                    ok=True,
                    data={
                        "count": len(self.allowed),
                        "added": added,
                        "removed": removed,
                    },
                )
            )

    def add_tool(self, capability: str) -> bool:
        """Add a tool to the allowlist.
        
        Returns False if the tool is dangerous and not enabled.
        """
        with self._lock:
            if capability in DANGEROUS_TOOLS:
                if capability == "script.execute" and not self.script_execute_enabled:
                    return False
            self.allowed.add(capability)
            return True

    def remove_tool(self, capability: str) -> None:
        """Remove a tool from the allowlist."""
        with self._lock:
            self.allowed.discard(capability)
