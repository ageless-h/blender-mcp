# AGENTS

## Execution Guidance

- Keep changes minimal and aligned to OpenSpec artifacts.
- Record decisions in OpenSpec change docs before implementation.
- Prefer updating tests and examples alongside behavior changes.

## Common Commands

- Install: `uv sync`
- Run example: `python -m examples.stdio_loop`
- Run tests: `uv run python -m unittest discover -s tests -p "test_*.py"`
