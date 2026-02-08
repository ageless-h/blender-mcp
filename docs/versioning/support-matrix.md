# Blender Version Support Matrix

## Policy

### Support Scope
- **LTS Versions**: Support the 2 most recent LTS releases (4.2, 4.5)
- **Latest Stable**: Always support the current 5.x series
- **Minimum Version**: Blender 4.2 LTS

### Support Timeline
| Version | Status | Support Until | Notes |
|---------|--------|---------------|-------|
| 4.2 | ✅ LTS | 2026-07 | Current baseline |
| 4.5 | ✅ LTS | 2027-07 | Latest LTS |
| 5.0+ | ✅ Latest | Until next release | Current stable |
| 3.6 | ❌ EOL | 2025-11 | Unsupported |
| 4.0 | ❌ EOL | 2024 | Superseded by 4.2 LTS |

## Capability Version Requirements

All capabilities require **Blender 4.2 or later**:

| Capability | Min Version | Reason |
|------------|-------------|--------|
| `blender.get_objects` | 4.2 | bpy.data access patterns |
| `blender.get_object_data` | 4.2 | bpy.data access patterns |
| `blender.get_scene` | 4.2 | Depsgraph API |
| `blender.create_object` | 4.2 | Stable bmesh API from 4.2+ |
| `blender.modify_object` | 4.2 | Context override API |
| `blender.execute_operator` | 4.2 | bpy.ops context override |
| `blender.execute_script` | 4.2 | Threading support |
| `blender.import_export` | 4.2 | Standard I/O API |
| All other `blender.*` | 4.2 | Standard API |

## Testing Status

See `compatibility-results.json` for detailed test results.

- **4.2 LTS**: ✅ All tests passing
- **4.5 LTS**: ⏳ Testing pending
- **5.0+**: ⏳ Basic compatibility testing pending

## Update Rules

### When Blender Releases New Versions
1. Add new version to `support-matrix.json`
2. Run compatibility tests
3. Update `compatibility-results.json`
4. Mark old LTS as EOL when support ends

### Deprecation Notice
When dropping support for a version:
1. Announce 3 months in advance
2. Update documentation
3. Provide migration guide if needed
4. Keep rollback path for last LTS

## CI Testing

The CI matrix tests against:
- Blender 4.2 LTS (full coverage)
- Blender 4.5 LTS (full coverage, pending)
- Blender 5.0+ (basic coverage, pending)

See `docs/testing/ci-matrix.md` for CI configuration details.
