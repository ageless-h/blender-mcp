# Core Service Lifecycle

## States
- init: dependency checks and adapter validation
- ready: service accepts requests
- stopping: shutdown in progress
- stopped: shutdown complete
- error: critical failure with deterministic error code

## Health Reporting
The core MUST expose a health surface that includes current state and error code. Readiness is true only in the ready state.
