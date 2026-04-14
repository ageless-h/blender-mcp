# Contributing to Blender MCP

Thank you for your interest in contributing! This guide will help you get started.

## Development Setup

```bash
# Clone the repository
git clone https://github.com/ageless-h/blender-mcp.git
cd blender-mcp

# Install dependencies
uv sync

# Run tests
uv run python -m unittest discover -s tests -p "test_*.py"
```

## Project Structure

```
src/
  blender_mcp/          # MCP server (Python package, published to PyPI)
    adapters/           # Socket/Mock adapters for Blender communication
    prompts/            # MCP prompt definitions (workflow + strategy)
    schemas/            # Tool definitions and JSON schemas
    mcp_protocol.py     # Main MCP JSON-RPC server
  blender_mcp_addon/    # Blender addon (installed in Blender)
    handlers/           # Capability handlers for each tool
    server/             # TCP socket server running inside Blender
    ui.py               # Sidebar panel UI
tests/                  # Unit and integration tests
docs/                   # Documentation
```

## Making Changes

1. **Fork** the repository and create a feature branch
2. **Make changes** following the existing code style
3. **Add tests** for new functionality
4. **Run tests** to ensure nothing is broken
5. **Submit a PR** with a clear description

## Code Style

- Follow existing patterns in the codebase
- Use type hints for all function signatures
- Keep imports at the top of files
- Use `logging` module for debug/info output (not `print`)

## Testing

```bash
# Run all tests
uv run python -m unittest discover -s tests -p "test_*.py"

# Run a specific test file
uv run python -m unittest tests.test_adapters

# Run the stdio example
python -m examples.stdio_loop
```

## Architecture Decisions

- See [docs/architecture/](docs/architecture/) for design documents
- See root `AGENTS.md` for project conventions and architecture overview

## Reporting Issues

- Use the [Bug Report](https://github.com/ageless-h/blender-mcp/issues/new?template=bug_report.md) template for bugs
- Use the [Feature Request](https://github.com/ageless-h/blender-mcp/issues/new?template=feature_request.md) template for new ideas
- Set `MCP_LOG_LEVEL=DEBUG` to capture detailed logs when reporting issues

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
