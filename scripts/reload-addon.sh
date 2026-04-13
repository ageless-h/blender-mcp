#!/bin/bash
# Copy updated addon files to Blender addon directory.
# With symlink setup this is automatic; this script exists
# for the case where symlink is replaced by a copy.
set -e

BLENDER_ADDON_DIR="$HOME/Library/Application Support/Blender/5.1/scripts/addons/blender_mcp_addon"
SOURCE_DIR="/Users/huzhiheng/code/blender-mcp/blender-mcp-test-real/src/blender_mcp_addon"

if [ -L "$BLENDER_ADDON_DIR" ]; then
    echo "Addon is a symlink — changes are already live."
    echo "In Blender: press F8 or Edit > Preferences > Add-ons > Blender MCP > Reload"
    exit 0
fi

rsync -av --delete "$SOURCE_DIR/" "$BLENDER_ADDON_DIR/"
echo "Addon files synced. In Blender: press F8 to reload scripts."
