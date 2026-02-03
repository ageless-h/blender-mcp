# Rate Limiting and Resource Guards

## Goals
Protect Blender sessions from excessive requests and resource exhaustion.

## Baseline Policy
- Per-capability rate limits with configurable thresholds
- Global guardrails for memory and long-running operations

## Failure Mode
Requests beyond limits are rejected with rate_limited.
