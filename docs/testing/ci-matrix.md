# CI Matrix

## Goals
Run integration tests across all supported Blender versions.

## Matrix Dimensions
- Blender version (LTS + latest)
- OS (linux, windows, macos)

## Execution Notes
Integration jobs should be separated from fast unit checks and require caching of Blender binaries.
