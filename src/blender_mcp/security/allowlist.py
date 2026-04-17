# -*- coding: utf-8 -*-
from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Set

from blender_mcp.security.audit import AuditEvent, AuditLogger

# Default allowlist for 29-tool architecture (excludes blender.execute_script for safety)
DEFAULT_ALLOWED_TOOLS: Set[str] = {
    "blender.get_objects",
    "blender.get_object_data",
    "blender.get_node_tree",
    "blender.get_animation_data",
    "blender.get_materials",
    "blender.get_scene",
    "blender.get_collections",
    "blender.get_armature_data",
    "blender.get_images",
    "blender.capture_viewport",
    "blender.get_selection",
    "blender.edit_nodes",
    "blender.edit_animation",
    "blender.edit_sequencer",
    "blender.create_object",
    "blender.modify_object",
    "blender.manage_material",
    "blender.manage_modifier",
    "blender.manage_collection",
    "blender.manage_uv",
    "blender.manage_constraints",
    "blender.manage_physics",
    "blender.setup_scene",
    "blender.edit_mesh",
    "blender.execute_operator",
    "blender.import_export",
    "blender.render_scene",
    "blender.batch_execute",
}

# Dangerous tools that require explicit enablement
DANGEROUS_TOOLS: Set[str] = {
    "blender.execute_script",
}


@dataclass
class Allowlist:
    allowed: Set[str] = field(default_factory=lambda: set(DEFAULT_ALLOWED_TOOLS))
    audit_logger: AuditLogger | None = None
    script_execute_enabled: bool = False
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False, compare=False)

    def is_allowed(self, capability: str) -> bool:
        with self._lock:
            if capability in DANGEROUS_TOOLS:
                return self.script_execute_enabled and capability in self.allowed
            return capability in self.allowed

    def enable_script_execute(self) -> None:
        """Explicitly enable script execution (dangerous operation)."""
        with self._lock:
            self.script_execute_enabled = True
            self.allowed.add("blender.execute_script")
        if self.audit_logger is not None:
            self.audit_logger.record(
                AuditEvent(
                    capability="allowlist.enable_dangerous",
                    ok=True,
                    data={"tool": "blender.execute_script", "warning": "Arbitrary code execution enabled"},
                )
            )

    def disable_script_execute(self) -> None:
        """Disable script execution."""
        with self._lock:
            self.script_execute_enabled = False
            self.allowed.discard("blender.execute_script")
        if self.audit_logger is not None:
            self.audit_logger.record(
                AuditEvent(
                    capability="allowlist.disable_dangerous",
                    ok=True,
                    data={"tool": "blender.execute_script"},
                )
            )
