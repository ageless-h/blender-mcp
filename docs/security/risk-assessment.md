# Security Risk Assessment

## Boundary Risks
- Addon/core boundary misuse could allow unsafe operations.
  - Mitigation: strict contract validation and version checks.

## Transport Risks
- stdio exposure can leak sensitive logs if mixed with stdout.
  - Mitigation: log to stderr only and avoid printing secrets.
- Future network transports expand attack surface.
  - Mitigation: authentication, rate limits, and allowlists.

## Dependency Risks
- SDK or Blender version drift can break contracts.
  - Mitigation: pin versions and maintain a compatibility matrix.
