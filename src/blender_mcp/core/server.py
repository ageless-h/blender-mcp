# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable

from blender_mcp.core.lifecycle import ServiceLifecycle
from blender_mcp.core.types import Request, Response
from blender_mcp.security.allowlist import Allowlist
from blender_mcp.security.audit import AuditEvent, AuditLogger
from blender_mcp.security.permissions import PermissionPolicy
from blender_mcp.security.rate_limit import RateLimiter
from blender_mcp.transport.base import TransportAdapter


@dataclass
class MCPServer:
    lifecycle: ServiceLifecycle
    allowlist: Allowlist
    permissions: PermissionPolicy
    rate_limiter: RateLimiter
    audit_logger: AuditLogger

    def handle_request(self, request: Request) -> Response:
        if not self.allowlist.is_allowed(request.capability):
            self.audit_logger.record(
                AuditEvent(
                    capability=request.capability,
                    ok=False,
                    error="capability_not_allowed",
                )
            )
            return Response(ok=False, error="capability_not_allowed")

        if not self.permissions.is_authorized(request.capability, request.scopes):
            self.audit_logger.record(
                AuditEvent(
                    capability=request.capability,
                    ok=False,
                    error="missing_scope",
                )
            )
            return Response(ok=False, error="missing_scope")

        if not self.rate_limiter.allow(request.capability):
            self.audit_logger.record(
                AuditEvent(
                    capability=request.capability,
                    ok=False,
                    error="rate_limited",
                )
            )
            return Response(ok=False, error="rate_limited")

        self.audit_logger.record(AuditEvent(capability=request.capability, ok=True))
        return Response(ok=True, result={"status": "accepted"})

    def health(self) -> Dict[str, str | int | None]:
        return {
            "state": self.lifecycle.state.value,
            "error_code": self.lifecycle.error_code,
        }

    def set_allowed_capabilities(self, capabilities: Iterable[str]) -> None:
        self.allowlist.replace(capabilities)
        if self.allowlist.audit_logger is None:
            self.audit_logger.record(
                AuditEvent(
                    capability="allowlist.update",
                    ok=True,
                )
            )

    def handle_transport(self, transport: TransportAdapter) -> None:
        import json

        for raw in transport.receive():
            if not raw:
                continue
            payload = json.loads(raw.decode("utf-8"))
            request = Request(
                capability=payload.get("capability", ""),
                payload=payload.get("payload", {}),
                scopes=payload.get("scopes", []),
            )
            response = self.handle_request(request)
            transport.send(json.dumps(response.__dict__).encode("utf-8"))
