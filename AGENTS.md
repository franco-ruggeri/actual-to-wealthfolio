# AGENTS.md

Operational guide for coding agents working in `actual-to-wealthfolio`.

## Repository Snapshot

- Python `src/` layout; package at `src/actual_to_wealthfolio/`.
- Entry point: `actual-to-wealthfolio` → `actual_to_wealthfolio.main:main`.
- Build backend: Hatchling. Python `>=3.13`.
- Runtime deps: `pandas>=3.0.1`, `pyyaml>=6.0`.
- Dev deps (`[dependency-groups].dev`): `ruff`, `mypy`, `basedpyright`, `pandas-stubs`, `pytest`, `types-PyYAML`.
- Ruff line length: 120. No `[tool.mypy]` or `[tool.pytest.ini_options]` — both run with defaults.
- `basedpyright` installs a Node.js binary (~55 MB via `nodejs-wheel-binaries`); expect heavier `uv sync` in fresh environments. **CI does not run basedpyright** — only `mypy` is gated.

## Setup

```bash
uv sync --group dev   # installs all dev deps including pytest
```

Bare `uv sync` omits dev dependencies. Use `--group dev` for any development work.

## Commands

```bash
# Run
uv run actual-to-wealthfolio
uv run python -m actual_to_wealthfolio

# Lint / format
uv run ruff check .
uv run ruff check . --fix
uv run ruff format . --check
uv run ruff format .

# Type check (mypy only; basedpyright is not in CI)
uv run mypy .

# Test
uv run pytest
uv run pytest tests/test_converter.py
uv run pytest tests/test_converter.py::test_writes_output_files
uv run pytest -k "config" -x
```

## Definition of Done

Run in this order before finishing any non-docs change:

1. `uv run ruff check .`
2. `uv run ruff format . --check`
3. `uv run mypy .`
4. `uv run pytest`

## Architecture

```
src/actual_to_wealthfolio/
    main.py        # CLI orchestration only
    converter.py   # all CSV transformation logic (Converter class)
    config.py      # YAML config loading (load_config, RemapConfig, RemapEntry)
    __main__.py    # enables python -m actual_to_wealthfolio
```

Data flow: `input/config.yaml` + `input/actual-<budget-file>.csv` → `output/wealthfolio-<account>-<budget-file>.csv`.

## Non-Obvious Quirks

**CWD-relative paths.** `Converter.INPUT_DIR = Path("input")` and `OUTPUT_DIR = Path("output")` are class-level constants resolved against the current working directory, not constructor parameters. Tests must call `monkeypatch.chdir(tmp_path)` and create `input/`/`output/` subdirectories inside `tmp_path` — there is no way to inject paths via the constructor.

**Output key format.** `Converter.convert()` returns `dict[str, Path]` with keys like `"<budget-file>:<sanitized-account>"` (e.g. `"main:main-account"`).

**Duplicate-amount deduplication.** `Converter` adds `DUPLICATE_AMOUNT_EPSILON = 0.000001` to disambiguate same-day, same-type, same-amount rows. Tests asserting exact amounts must account for this.

**`input/*.csv` and `output/` are gitignored.** They contain personal financial data. Never commit them. Only `input/config.yaml` is tracked.

## Testing Patterns

- Tests live in `tests/test_config.py` and `tests/test_converter.py`.
- No `conftest.py`; shared setup uses plain helper functions (e.g. `_standard_config()`), not `@pytest.fixture`.
- Converter tests use `monkeypatch.chdir(tmp_path)` (see CWD quirk above).
- Cover both happy paths and at least one error/edge case per behavior.

## Code Conventions

- Absolute imports from `actual_to_wealthfolio`; stdlib → third-party → local, separated by blank lines.
- Type hints on all public functions and non-trivial private helpers. Use `X | None` over `Optional[X]`, built-in generics (`list[str]`), avoid `Any`.
- Private helpers: leading underscore (`_load_actual_data`).
- Keep CLI/orchestration in `main.py`; keep transformation logic in `converter.py`.
- Raise specific exceptions (`FileNotFoundError`, `ValueError`); fail fast; add context with `raise ... from exc`.
- Update `README.md` when CLI usage, file naming, or behavior changes.

## Git Hygiene

- Keep diffs scoped to the requested task; note unrelated issues separately.
- Commit messages centered on why the change exists.
- Do not push or rewrite history unless explicitly requested.

## Additional Instruction Files

Check before making changes — none currently present, but treat as high-priority if added:

- `.cursor/rules/`
- `.cursorrules`
- `.github/copilot-instructions.md`
- `opencode.json`
