# Blender Plugin Boundary

## Contract Surface
The Blender adapter exposes a versioned contract with explicit entrypoints. The core validates contract version compatibility at startup.

## Ownership Rules
- The core owns protocol handling, security, and capability dispatch.
- The plugin owns Blender-specific execution and access to bpy.

## Compatibility
Contract versions must be forward compatible within a major version. Breaking changes require a major version bump.
