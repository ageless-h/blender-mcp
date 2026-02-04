# Protocol and Transport Choices

## Protocol
- The current implementation uses a minimal JSON-line loop over stdio for the runnable example.
- Messages are JSON-RPC 2.0 objects serialized as one JSON document per line.
- Messages MUST be UTF-8 encoded and MUST NOT contain embedded newlines.
- stdout MUST NOT include non-protocol output; stderr MAY be used for logs.
- Official MCP SDK integration is planned for a future change.

## Transport
- MVP default: stdio transport.
- Future extensions: HTTP or WebSocket adapters via the transport interface.

## Dependency Policy
- Pin MCP SDK versions to avoid breaking changes.
- Prefer official SDKs and minimize third-party protocol layers.
