# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable

from blender_mcp.catalog.catalog import CapabilityCatalog, capability_to_dict
from blender_mcp.core.lifecycle import ServiceLifecycle
from blender_mcp.core.types import Request, Response
from blender_mcp.security.allowlist import Allowlist
from blender_mcp.security.audit import AuditEvent, AuditLogger
from blender_mcp.security.permissions import PermissionPolicy
from blender_mcp.security.rate_limit import RateLimiter
from blender_mcp.security.guardrails import Guardrails
from blender_mcp.transport.base import TransportAdapter


@dataclass
class MCPServer:
    catalog: CapabilityCatalog
    lifecycle: ServiceLifecycle
    allowlist: Allowlist
    permissions: PermissionPolicy
    rate_limiter: RateLimiter
    audit_logger: AuditLogger
    guardrails: Guardrails | None = None

    def handle_request(self, request: Request) -> Response:
        if self.guardrails is not None and not self.guardrails.allow(
            request.capability, request.payload
        ):
            self.audit_logger.record(
                AuditEvent(
                    capability=request.capability,
                    ok=False,
                    error="guardrails_blocked",
                )
            )
            return Response(ok=False, error="guardrails_blocked")
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
        if request.capability == "capabilities.list":
            blender_version = request.payload.get("blender_version")
            version = (
                blender_version if isinstance(blender_version, str) else None
            )
            return Response(
                ok=True,
                result={
                    "capabilities": [
                        capability_to_dict(cap, version)
                        for cap in self.catalog.list()
                    ]
                },
            )
        return Response(ok=True, result={"status": "accepted"})

    def health(self) -> Dict[str, str | int | None]:
        return {
            "state": self.lifecycle.state.value,
            "error_code": self.lifecycle.error_code,
        }

    def set_allowed_capabilities(self, capabilities: Iterable[str]) -> None:
        self.allowlist.replace(capabilities)
        if self.allowlist.audit_logger is None:
            current = set(self.allowlist.allowed)
            self.audit_logger.record(
                AuditEvent(
                    capability="allowlist.update",
                    ok=True,
                    data={
                        "count": len(current),
                        "added": sorted(current),
                        "removed": [],
                    },
                )
            )

    def handle_transport(self, transport: TransportAdapter) -> None:
        import json

        for raw in transport.receive():
            if not raw:
                continue
            try:
                payload = json.loads(raw.decode("utf-8"))
            except json.JSONDecodeError:
                self.audit_logger.record(
                    AuditEvent(
                        capability="jsonrpc.parse",
                        ok=False,
                        error="parse_error",
                    )
                )
                transport.send(
                    json.dumps(
                        {
                            "jsonrpc": "2.0",
                            "id": None,
                            "error": {
                                "code": -32700,
                                "message": "Parse error",
                            },
                        }
                    ).encode("utf-8")
                )
                continue
            if payload.get("jsonrpc") != "2.0" or "method" not in payload:
                transport.send(
                    json.dumps(
                        {
                            "jsonrpc": "2.0",
                            "id": payload.get("id"),
                            "error": {
                                "code": -32600,
                                "message": "Invalid Request",
                            },
                        }
                    ).encode("utf-8")
                )
                continue
            if "params" in payload and not isinstance(payload["params"], dict):
                transport.send(
                    json.dumps(
                        {
                            "jsonrpc": "2.0",
                            "id": payload.get("id"),
                            "error": {
                                "code": -32602,
                                "message": "Invalid params",
                            },
                        }
                    ).encode("utf-8")
                )
                continue
            params = payload.get("params") or {}
            request = Request(
                capability=payload.get("method", ""),
                payload=params.get("payload", {}),
                scopes=params.get("scopes", []),
            )
            response = self.handle_request(request)
            if response.ok:
                reply = {
                    "jsonrpc": "2.0",
                    "id": payload.get("id"),
                    "result": response.result,
                }
            else:
                reply = {
                    "jsonrpc": "2.0",
                    "id": payload.get("id"),
                    "error": {
                        "code": -32000,
                        "message": response.error or "Server error",
                    },
                }
            transport.send(json.dumps(reply).encode("utf-8"))
