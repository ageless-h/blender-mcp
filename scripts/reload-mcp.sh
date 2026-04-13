#!/bin/bash
# Reload the Blender MCP server process for OpenCode.
# Kills the running process; OpenCode auto-restarts it on next tool call.
set -e

PIDS=$(pgrep -f "blender_mcp.mcp_protocol|ageless-blender-mcp" 2>/dev/null || true)
if [ -z "$PIDS" ]; then
    echo "No Blender MCP process found."
    exit 0
fi

echo "Killing Blender MCP process(es): $PIDS"
for pid in $PIDS; do
    kill "$pid" 2>/dev/null || true
done
sleep 1

REMAINING=$(pgrep -f "blender_mcp.mcp_protocol|ageless-blender-mcp" 2>/dev/null || true)
if [ -n "$REMAINING" ]; then
    echo "Force killing: $REMAINING"
    for pid in $REMAINING; do
        kill -9 "$pid" 2>/dev/null || true
    done
fi

echo "Blender MCP process killed. OpenCode will restart it on next tool call."
