## ADDED Requirements

### Requirement: Server dispatches to adapter after security checks
MCPServer.handle_request() SHALL dispatch capability execution to the BlenderAdapter after all security checks (allowlist, permissions, rate limiting) pass.

#### Scenario: Authorized request dispatched to adapter
- **WHEN** a request passes allowlist, permission, and rate limit checks
- **THEN** server calls adapter.execute(capability, payload) instead of returning stub response

#### Scenario: Security rejection before dispatch
- **WHEN** a request fails any security check
- **THEN** adapter is NOT called and appropriate error response is returned

### Requirement: Adapter result mapped to Response
The server SHALL map AdapterResult to Response, preserving ok status, result data, and error information.

#### Scenario: Successful adapter result becomes success response
- **WHEN** adapter returns AdapterResult with ok=True
- **THEN** server returns Response with ok=True and result from adapter

#### Scenario: Failed adapter result becomes error response
- **WHEN** adapter returns AdapterResult with ok=False
- **THEN** server returns Response with ok=False and error from adapter

### Requirement: Graceful handling when no adapter configured
The server SHALL return a stub response when no adapter is configured, maintaining backward compatibility.

#### Scenario: No adapter configured
- **WHEN** MCPServer has no BlenderAdapter injected
- **THEN** handle_request returns Response with ok=True and result={"status": "accepted"}

### Requirement: Adapter errors are audited
The server SHALL record adapter execution failures in the audit log.

#### Scenario: Adapter failure audited
- **WHEN** adapter returns ok=False
- **THEN** audit logger records event with capability name and error code

#### Scenario: Adapter timeout audited
- **WHEN** adapter execution times out
- **THEN** audit logger records event with capability name and error="adapter_timeout"

### Requirement: End-to-end scene.read execution
The system SHALL execute scene.read capability end-to-end, returning actual Blender scene data.

#### Scenario: scene.read returns real data
- **WHEN** client sends scene.read request with valid scopes
- **THEN** response contains scene_name, object_count, selected_objects, active_object from Blender

### Requirement: End-to-end scene.write execution
The system SHALL execute scene.write capability end-to-end, performing actual Blender operations.

#### Scenario: scene.write creates object
- **WHEN** client sends scene.write request with name parameter and valid scopes
- **THEN** response confirms object creation in Blender scene
