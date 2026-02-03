# Rate Limiting and Resource Guards

## Goals
Protect Blender sessions from excessive requests and resource exhaustion.

## Baseline Policy
- Per-capability rate limits with configurable thresholds
- Windowed rate limiting with reset behavior

## Failure Mode
Requests beyond limits are rejected with rate_limited.

## Notes
Global resource guardrails (memory/long tasks) are not implemented yet.
