# Real Blender Test Harness

## Purpose

提供启动真实 Blender 进程、建立 socket 通信、执行测试脚本的基础设施，支持端到端集成测试。

## ADDED Requirements

### Requirement: Blender process lifecycle management

The test harness SHALL manage the complete lifecycle of a Blender process, including startup, communication, and cleanup.

#### Scenario: Start Blender in background mode

- **WHEN** the harness is initialized with a valid Blender executable path
- **THEN** the harness SHALL start Blender with `--background` flag and inject the socket server script

#### Scenario: Wait for socket server ready

- **WHEN** Blender process starts successfully
- **THEN** the harness SHALL poll the socket connection until ready or timeout (default 30 seconds)

#### Scenario: Clean shutdown on test completion

- **WHEN** the test completes (success or failure)
- **THEN** the harness SHALL terminate the Blender process and release all resources

### Requirement: Socket communication for capability execution

The test harness SHALL provide methods to send capability requests to Blender and receive responses via socket.

#### Scenario: Send capability request

- **WHEN** `send_request(request)` is called with a valid capability request dict
- **THEN** the harness SHALL serialize the request as JSON, send to socket, and return the parsed response

#### Scenario: Handle communication timeout

- **WHEN** a request does not receive a response within the configured timeout
- **THEN** the harness SHALL raise a timeout exception with descriptive message

#### Scenario: Handle connection failure

- **WHEN** the socket connection fails or is lost
- **THEN** the harness SHALL raise a connection error with the underlying cause

### Requirement: Context manager support

The test harness SHALL support Python context manager protocol for automatic resource cleanup.

#### Scenario: Use harness as context manager

- **WHEN** the harness is used in a `with` statement
- **THEN** `__enter__` SHALL start Blender and return the harness, `__exit__` SHALL stop Blender

#### Scenario: Cleanup on exception

- **WHEN** an exception occurs within the `with` block
- **THEN** the harness SHALL still terminate the Blender process before propagating the exception

### Requirement: Dynamic port allocation

The test harness SHALL use dynamically allocated ports to support parallel test execution.

#### Scenario: Allocate free port

- **WHEN** the harness is initialized without explicit port
- **THEN** the harness SHALL find and use a free port on localhost

#### Scenario: Pass port to Blender via environment variable

- **WHEN** starting the Blender process
- **THEN** the harness SHALL set `MCP_SOCKET_PORT` environment variable to the allocated port

### Requirement: Process output capture

The test harness SHALL capture Blender process stdout/stderr for debugging.

#### Scenario: Access Blender output after test

- **WHEN** a test completes
- **THEN** the harness SHALL provide access to captured stdout and stderr content

