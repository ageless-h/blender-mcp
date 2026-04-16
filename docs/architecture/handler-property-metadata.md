# Handler Property Metadata System Design

## Problem Statement

Modifier handlers currently use hard-coded property path resolution in `MODIFIER_PROPERTY_PATHS`. This approach has limitations:

1. **Not scalable**: Adding new modifiers requires code changes
2. **Version fragility**: API changes between Blender versions require manual updates
3. **No introspection**: Cannot query supported properties at runtime
4. **Duplication**: Similar logic needed for other handlers (constraints, physics)

## Proposed Solution

### 1. Property Metadata Schema

```python
@dataclass
class PropertyMetadata:
    """Metadata for a single property on a Blender data type."""
    name: str                    # User-facing property name
    blender_path: str            # Actual path in Blender API (e.g., "settings.mass")
    type: str                    # Property type: "float", "int", "bool", "enum", "vector", "array"
    default: Any                 # Default value
    min_value: Any | None        # Minimum value (for numeric types)
    max_value: Any | None        # Maximum value
    enum_items: list[str] | None # Enum options (for enum types)
    version_added: tuple[int, int, int] | None  # Blender version when property was added
    version_deprecated: tuple[int, int, int] | None  # Version when deprecated
    description: str             # Human-readable description
```

### 2. Modifier Metadata Registry

```python
MODIFIER_METADATA: dict[str, ModifierMetadata] = {
    "CLOTH": ModifierMetadata(
        type="CLOTH",
        container_path="settings",  # Properties live in modifier.settings
        properties={
            "mass": PropertyMetadata(
                name="mass",
                blender_path="settings.mass",
                type="float",
                default=0.3,
                min_value=0.0,
                description="Vertex mass in kilograms",
            ),
            # ... more properties
        },
    ),
    "MIRROR": ModifierMetadata(
        type="MIRROR",
        container_path="",  # Properties on modifier directly
        properties={
            "use_x": PropertyMetadata(
                name="use_x",
                blender_path="use_axis[0]",  # Blender 5.0+ mapping
                type="bool",
                default=True,
                version_added=(4, 0, 0),
                version_deprecated=(5, 0, 0),  # Use use_axis instead
                description="Mirror on X axis",
            ),
            "use_axis": PropertyMetadata(
                name="use_axis",
                blender_path="use_axis",
                type="array",  # Boolean array of 3 items
                default=[True, False, False],
                version_added=(5, 0, 0),
                description="Enable axis mirror",
            ),
        },
    ),
}
```

### 3. Version-Aware Resolution

```python
def resolve_property_path(
    modifier_type: str,
    property_name: str,
    blender_version: tuple[int, int, int],
) -> str | None:
    """Resolve a user-facing property name to its Blender API path.
    
    Returns None if property doesn't exist in this Blender version.
    """
    meta = MODIFIER_METADATA.get(modifier_type)
    if not meta:
        return property_name  # Fallback to direct access
    
    prop_meta = meta.properties.get(property_name)
    if not prop_meta:
        return property_name  # Unknown property, try direct
    
    # Check version compatibility
    if prop_meta.version_added and blender_version < prop_meta.version_added:
        return None  # Property doesn't exist yet
    
    if prop_meta.version_deprecated and blender_version >= prop_meta.version_deprecated:
        # Property deprecated, use replacement if available
        replacement = prop_meta.replacement_property
        if replacement:
            return resolve_property_path(modifier_type, replacement, blender_version)
        return None
    
    return prop_meta.blender_path
```

### 4. Auto-Discovery (Future Enhancement)

```python
def discover_modifier_properties(modifier_type: str) -> dict[str, PropertyMetadata]:
    """Discover properties for a modifier by introspecting Blender RNA.
    
    This can be used to auto-generate metadata during development.
    """
    import bpy
    modifier_class = getattr(bpy.types, f"{modifier_type.title()}Modifier", None)
    if not modifier_class:
        return {}
    
    properties = {}
    for prop in modifier_class.bl_rna.properties:
        if prop.identifier in ("type", "name", "rna_type"):
            continue
        properties[prop.identifier] = PropertyMetadata(
            name=prop.identifier,
            blender_path=prop.identifier,
            type=_rna_type_to_schema_type(prop.type),
            default=prop.default,
            description=prop.description,
        )
    return properties
```

### 5. Benefits

1. **Single source of truth**: All property metadata in one place
2. **Version compatibility**: Automatic handling of API changes
3. **Runtime introspection**: Query supported properties for any modifier
4. **Documentation generation**: Auto-generate property docs from metadata
5. **Validation**: Catch invalid property names before sending to Blender
6. **Extensibility**: Easy to add new modifiers without code changes

### 6. Implementation Plan

**Phase 1**: Core Infrastructure (2-3 days)
- [ ] Define `PropertyMetadata` and `ModifierMetadata` dataclasses
- [ ] Implement `resolve_property_path()` with version awareness
- [ ] Update `ModifierHandler` to use metadata system

**Phase 2**: Metadata Population (1-2 days)
- [ ] Add metadata for all tested modifiers (54 types)
- [ ] Document version-specific property changes
- [ ] Add validation tests

**Phase 3**: Integration (1 day)
- [ ] Generate property docs from metadata
- [ ] Add tool to query supported properties
- [ ] Update README with property reference

### 7. File Structure

```
src/blender_mcp_addon/
  metadata/
    __init__.py
    types.py           # PropertyMetadata, ModifierMetadata dataclasses
    resolver.py        # resolve_property_path() function
    modifiers/
      __init__.py
      cloth.py         # ClothModifier metadata
      mirror.py        # MirrorModifier metadata
      # ... one file per modifier type
    generator.py       # Auto-discovery utilities
```

### 8. Open Questions

1. **Storage format**: Python dataclasses vs JSON/YAML files?
   - Recommendation: Python dataclasses for type safety, generate JSON for docs

2. **Backward compatibility**: Support Blender 4.x indefinitely?
   - Recommendation: Support current LTS + 1 major version (4.5 LTS, 5.1)

3. **Extensibility**: Allow user-defined property mappings?
   - Recommendation: Yes, via config file or plugin system

---

*Draft: 2026-04-16*
*Status: Design phase, not implemented*
