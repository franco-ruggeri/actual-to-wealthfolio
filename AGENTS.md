# AGENTS.md

Operational guide for coding agents working in `actual-to-wealthfolio`.

## 1) Repository Snapshot (as of this guide)

- Python project with `pyproject.toml` using src-layout structure.
- Package location: `src/actual_to_wealthfolio/`.
- Main dependencies: pandas >=3.0.1
- Dev dependencies: ruff, mypy, basedpyright, pandas-stubs.
- Line length configured to 120 characters in `pyproject.toml`.
- Project purpose: Convert Actual Budget CSV exports to Wealthfolio-compatible format.
- Entry point: `actual_to_wealthfolio.main:main` (console script).
- No test files are currently present.
- No Cursor rules found in `.cursor/rules/`.
- No `.cursorrules` file found.
- No Copilot instructions file found at `.github/copilot-instructions.md`.

Because the repo is minimal right now, this guide defines **default standards** to follow for all new code.

## 2) Command Reference

Use these commands unless the repository evolves with explicit alternatives.

### Environment and setup

- Check Python version: `uv run python --version`
- Project requires: Python `>=3.13` (see `pyproject.toml`).
- Sync dependencies: `uv sync`
- Add a new dependency: `uv add <package>`
- Add a dev dependency: `uv add --dev <package>`

### Run application

- Run via console script: `uv run actual-to-wealthfolio <input.csv> <output.csv>`
- Run as module: `uv run python -m actual_to_wealthfolio <input.csv> <output.csv>`

### Tests

- Run all tests: `uv run pytest`
- Run a test file: `uv run pytest tests/test_example.py`
- Run a single test (node id): `uv run pytest tests/test_example.py::test_specific_case`
- Run a single test method in class: `uv run pytest tests/test_example.py::TestClass::test_specific_case`
- Run tests matching keyword: `uv run pytest -k "sync and not slow"`
- Stop after first failure: `uv run pytest -x`
- Show extra summary info: `uv run pytest -ra`

### Lint and formatting

- Lint check: `uv run ruff check .`
- Lint with auto-fix: `uv run ruff check . --fix`
- Format check: `uv run ruff format . --check`
- Apply formatting: `uv run ruff format .`

### Type checking

- Type check project: `uv run mypy .`
- Type check single file: `uv run mypy main.py`

### Build/package

- Build sdist/wheel: `uv build`

## 3) Definition of Done for Agent Changes

Before finishing code changes, run this sequence when relevant:

1. `uv run ruff check .`
2. `uv run ruff format . --check`
3. `uv run mypy .`
4. `uv run pytest`

If tools are not installed in the environment, report that clearly and include the exact install command used or needed.

## 4) Code Style Guidelines

### General principles

- Prefer clarity over cleverness.
- Keep functions small and single-purpose.
- Avoid hidden side effects.
- Minimize global mutable state.
- Make behavior explicit at call sites.

### Imports

- Use absolute imports from project package roots.
- Group imports in this order: standard library, third-party, local.
- Separate groups with one blank line.
- Prefer explicit imports over wildcard imports.
- Do not import inside functions unless it prevents cycles or improves startup cost materially.

### Formatting

- Follow PEP 8 and let formatter enforce details.
- Line length target: 120 characters (configured in `pyproject.toml`).
- Use double quotes for strings unless project style changes.
- Keep one logical statement per line.
- Preserve trailing newline at end of files.

### Types

- Add type hints to all new public functions and methods.
- Add return types for non-trivial private functions.
- Prefer built-in generics (`list[str]`, `dict[str, int]`) on Python 3.9+.
- Use `typing` constructs only when needed (`Protocol`, `TypedDict`, etc.).
- Avoid `Any`; when unavoidable, isolate and document why.
- Model optional values explicitly with `X | None`.

### Naming conventions

- Modules/files: `snake_case.py`.
- Functions/variables: `snake_case`.
- Classes: `PascalCase`.
- Constants: `UPPER_SNAKE_CASE`.
- Private helpers: leading underscore (e.g., `_parse_payload`).
- Test functions: `test_<behavior>`.

### Function and API design

- Prefer dependency injection over hard-coded dependencies.
- Keep argument lists short; use dataclasses/config objects when large.
- Avoid boolean flag arguments that alter behavior significantly.
- Return structured values rather than overloaded tuples.
- Document non-obvious invariants in docstrings.

### Error handling

- Fail fast on invalid input.
- Raise specific exceptions; avoid broad `Exception` unless re-raising with context.
- Do not silently swallow exceptions.
- Add context when re-raising (`raise ... from exc`).
- Keep error messages actionable and include key identifiers.

### Logging

- Use logging for operational events, not `print`, except tiny scripts.
- Log with structured, contextual messages.
- Never log secrets, credentials, or tokens.
- Use `warning`/`error` levels intentionally; avoid noisy logs.

### Testing standards

- Add/adjust tests for every behavior change.
- Prefer deterministic tests; avoid network/time randomness without controls.
- Use fixtures for repeated setup.
- Assert observable behavior, not private implementation details.
- Include at least one negative/error-path test for non-trivial logic.

### Documentation and comments

- Write docstrings for public modules/classes/functions.
- Keep comments for rationale, not obvious mechanics.
- Update README or module docs when behavior/usage changes.

## 5) Git and Change Hygiene for Agents

- Keep changes scoped to the requested task.
- Do not refactor unrelated code in the same change unless requested.
- Preserve existing user changes in dirty worktrees.
- If you discover unrelated issues, report them separately.
- Make commit messages explain **why** the change exists.

## 6) Config-Specific Instructions Discovery

Agents must check these files/directories on task start:

1. `.cursor/rules/`
2. `.cursorrules`
3. `.github/copilot-instructions.md`

Current status in this repository:

- `.cursor/rules/`: not present
- `.cursorrules`: not present
- `.github/copilot-instructions.md`: not present

If any appear later, their instructions should be merged into this guide and treated as high-priority constraints.

## 7) Practical Defaults for This Repo Today

- Start with simple scripts and pure functions.
- Introduce package structure when code grows beyond a single file.
- Add `tests/` alongside new logic immediately.
- Standardize on `pytest + ruff + mypy` unless maintainers choose otherwise.
- Keep CI command set aligned with Section 2.

End of guide.
