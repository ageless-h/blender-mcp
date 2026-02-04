# Capability Catalog

## Grouping
- Scene management
- Object manipulation
- Geometry and modifiers
- Materials and shading
- Rendering and output
- Animation and simulation
- File import/export

## Catalog Fields
- name
- description
- scopes
- min_version / max_version
- limitations

## Minimum Capability Set
- scene.read (scopes: scene:read)
- object.read (scopes: object:read)
- object.transform.write (scopes: object:write)
- object.selection.write (scopes: object:write)
- render.settings.read (scopes: render:read)
- render.still (scopes: render:execute)
- render.animation (scopes: render:execute)
