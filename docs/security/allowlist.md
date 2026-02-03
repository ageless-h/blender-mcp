# Capability Allowlist

## Format
Allowlist is a set of capability names. Only names on the allowlist are executable.

## Enforcement Flow
1. Receive request
2. Check allowlist
3. Reject with capability_not_allowed if missing

## Change Control
Allowlist updates require explicit configuration changes and audit log entry.
