# AGENTS

## Execution Guidance

- Keep changes minimal and aligned to OpenSpec artifacts.
- Record decisions in OpenSpec change docs before implementation.
- Prefer updating tests and examples alongside behavior changes.

## Verification Steps

- Run unit and integration tests: `uv run python -m unittest discover -s tests -p "test_*.py"`
- Run the stdio example: `python -m examples.stdio_loop`

## Change Records

- Record decisions and rationale in OpenSpec change documents under `openspec/changes/<change>/`.

## Common Commands

- Install: `uv sync`
- Run example: `python -m examples.stdio_loop`
- Run tests: `uv run python -m unittest discover -s tests -p "test_*.py"`
