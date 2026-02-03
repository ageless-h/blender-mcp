# Protocol and Transport Choices

## Protocol
- The current implementation uses a minimal JSON-line loop over stdio for the runnable example.
- Messages are JSON-RPC 2.0 objects serialized as one JSON document per line.
- Official MCP SDK integration is planned for a future change.

## Transport
- MVP default: stdio transport.
- Future extensions: HTTP or WebSocket adapters via the transport interface.

## Dependency Policy
- Pin MCP SDK versions to avoid breaking changes.
- Prefer official SDKs and minimize third-party protocol layers.
