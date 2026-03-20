# AGENTS.md

Operational guide for coding agents working in `actual-to-wealthfolio`.

## 1) Repository Snapshot

- Python project using a `src/` layout and `pyproject.toml`.
- Package path: `src/actual_to_wealthfolio/`.
- Console entry point: `actual-to-wealthfolio` -> `actual_to_wealthfolio.main:main`.
- Build backend: Hatchling.
- Runtime dependency: `pandas`.
- Dev tooling declared: `ruff`, `mypy`, `basedpyright`, `pandas-stubs`.
- Ruff line length: 120.
- Python requirement: `>=3.13`.
- Test suite directory does not currently exist (`tests/` absent at time of writing).

## 2) Rules Discovery (Cursor / Copilot)

Agents must check for additional local instruction files before making changes:

1. `.cursor/rules/`
2. `.cursorrules`
3. `.github/copilot-instructions.md`

Current status in this repository:

- `.cursor/rules/`: not present
- `.cursorrules`: not present
- `.github/copilot-instructions.md`: not present

If any of these files appear later, treat them as high-priority constraints and merge their guidance with this document.

## 3) Environment and Setup Commands

- Sync dependencies: `uv sync`
- Check Python version: `uv run python --version`
- Install project with pip (no uv workflow):
  - `python -m venv .venv`
  - `source .venv/bin/activate`
  - `python -m pip install --upgrade pip`
  - `python -m pip install .`

## 4) Run / Build / Lint / Type / Test Commands

### Run application

- Run CLI: `uv run actual-to-wealthfolio`
- Run module: `uv run python -m actual_to_wealthfolio`

### Build

- Build wheel/sdist: `uv build`

### Lint and formatting

- Lint check: `uv run ruff check .`
- Lint and auto-fix: `uv run ruff check . --fix`
- Format check: `uv run ruff format . --check`
- Apply formatting: `uv run ruff format .`

### Type checking

- Type check project: `uv run mypy .`
- Type check package only: `uv run mypy src/actual_to_wealthfolio`

### Tests

- Run all tests: `uv run pytest`
- Run one file: `uv run pytest tests/test_converter.py`
- Run one test function: `uv run pytest tests/test_converter.py::test_converts_single_account`
- Run one test method: `uv run pytest tests/test_converter.py::TestConverter::test_handles_empty_category`
- Run tests by keyword: `uv run pytest -k "converter and not slow"`
- Stop on first failure: `uv run pytest -x`
- Show extra summary: `uv run pytest -ra`

Note: tests are not present yet; add them under `tests/` for new behavior.

## 5) Definition of Done for Code Changes

Unless the task is docs-only, run this validation sequence before finishing:

1. `uv run ruff check .`
2. `uv run ruff format . --check`
3. `uv run mypy .`
4. `uv run pytest`

If a command cannot run (missing dependency/tool), report exactly what failed and why.

## 6) Code Style Guidelines

### General principles

- Prefer simple, explicit code over clever abstractions.
- Keep functions focused on one responsibility.
- Minimize side effects; isolate I/O from transformation logic.
- Preserve existing project patterns unless there is a clear improvement.

### Imports

- Use absolute imports from `actual_to_wealthfolio`.
- Group imports in this order: stdlib, third-party, local.
- Separate groups with one blank line.
- Avoid wildcard imports.
- Avoid function-local imports except for cycle/performance reasons.

### Formatting

- Follow Ruff formatting defaults and PEP 8.
- Respect max line length 120.
- Use double quotes consistently.
- Keep one logical statement per line.
- Keep trailing newline at end of files.

### Types

- Add type hints for new public functions and methods.
- Add return types for private helpers where behavior is non-trivial.
- Prefer built-in generics (`list[str]`, `dict[str, Path]`).
- Prefer `X | None` over `Optional[X]` unless needed for compatibility.
- Avoid `Any`; if unavoidable, keep it narrow and documented.

### Naming conventions

- Modules/files: `snake_case.py`
- Functions/variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private helpers: leading underscore (example: `_load_actual_data`)
- Tests: `test_<behavior>`

### Data and API design

- Prefer pure transformation helpers for dataframe logic.
- Keep CLI/orchestration code in `main.py`; keep conversion logic in `converter.py`.
- Use small, composable private methods for each transformation step.
- Avoid boolean flags that dramatically change function behavior.

### Error handling

- Fail fast on invalid or missing inputs.
- Raise specific exceptions (`FileNotFoundError`, `ValueError`, etc.).
- Do not silently swallow exceptions.
- Add context when re-raising (`raise ... from exc`) where useful.
- Ensure user-facing errors are actionable.

### Logging and output

- Prefer `logging` for new non-trivial operational code.
- Existing CLI may use `print`; keep style consistent unless refactoring intentionally.
- Never log secrets or sensitive data.

### Testing guidance

- Add or update tests for each behavior change.
- Test both happy paths and at least one failure/edge case.
- Keep tests deterministic; avoid reliance on wall clock/network.
- Prefer fixtures for repeated setup.

### Documentation

- Update `README.md` when CLI usage, file naming, or behavior changes.
- Keep comments focused on rationale, not obvious mechanics.
- Keep terminology consistent with the domain ("budget file" rather than assuming "currency").

## 7) Git and Change Hygiene

- Keep diffs scoped to the requested task.
- Do not revert unrelated user changes in a dirty tree.
- Avoid broad refactors unless requested.
- If you find unrelated issues, note them separately.
- Use clear commit messages centered on why the change exists.
- Do not push or rewrite history unless explicitly requested.

## 8) Practical Defaults for This Repo

- Prefer `uv` commands in automation/docs, but keep `pip/python` usage documented for contributors.
- Place new source under `src/actual_to_wealthfolio/`.
- Place new tests under `tests/` mirroring package structure.
- Keep generated data files out of source directories.

End of guide.
