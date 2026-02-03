# Blender API Surfaces (Stable, Versioned)

## Summary
Blender exposes a primary Python API surface that is versioned with Blender releases. Long-term integration should prefer stable, documented modules and avoid internal or private APIs that tend to change between versions.

## Recommended Integration Surfaces
- Python API (bpy) for core data access, operators, and scene manipulation.
- Command-line entry points for headless execution and batch workflows.
- Add-on system for plugin deployment and extension points.

## Versioning Considerations
- Track LTS releases and latest stable release in the support matrix.
- Document known API changes and limitations per version.
- Avoid private or undocumented API usage in the core contract.
