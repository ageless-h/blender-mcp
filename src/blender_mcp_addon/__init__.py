# -*- coding: utf-8 -*-
"""Blender MCP Addon - MCP server integration for AI-assisted Blender automation."""

import logging

import bpy  # type: ignore

from . import operators
from .preferences import BlenderMCPPreferences
from .server.socket_server import start_socket_server, stop_socket_server, is_server_running

bl_info = {
    "name": "Blender MCP",
    "author": "Blender MCP Contributors",
    "version": (0, 1, 0),
    "blender": (3, 6, 0),
    "category": "Development",
    "description": "MCP server integration for AI-assisted Blender automation",
}

_logger = logging.getLogger(__name__)


def register() -> None:
    """Register addon components."""
    _logger.info("Registering Blender MCP addon")

    bpy.utils.register_class(BlenderMCPPreferences)
    operators.register()

    prefs = bpy.context.preferences.addons[__name__].preferences
    if prefs.auto_start:
        _logger.info("Auto-starting MCP socket server")
        result = start_socket_server(host=prefs.host, port=prefs.port)
        if result.get("ok"):
            _logger.info(f"Server started on {prefs.host}:{prefs.port}")
        else:
            _logger.warning(f"Failed to auto-start server: {result.get('error')}")

    _logger.info("Blender MCP addon registered")


def unregister() -> None:
    """Unregister addon components."""
    _logger.info("Unregistering Blender MCP addon")

    if is_server_running():
        _logger.info("Stopping MCP socket server")
        stop_socket_server()

    operators.unregister()
    bpy.utils.unregister_class(BlenderMCPPreferences)

    _logger.info("Blender MCP addon unregistered")
