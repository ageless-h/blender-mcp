# Transport Adapters

## MVP Transport
The MVP selects stdio as the primary transport for simplicity and compatibility.

## Adapter Interface
Transports MUST support start, stop, send, and receive operations. The MCP core does not depend on transport details beyond this interface.

## Future Extensions
Additional transports can be added without modifying core request handling.
