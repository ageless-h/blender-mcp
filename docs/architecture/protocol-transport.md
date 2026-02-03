# Protocol and Transport Choices

## Protocol
- Use the official MCP protocol and official SDK for core server implementation.

## Transport
- MVP default: stdio transport.
- Future extensions: HTTP or WebSocket adapters via the transport interface.

## Dependency Policy
- Pin MCP SDK versions to avoid breaking changes.
- Prefer official SDKs and minimize third-party protocol layers.
