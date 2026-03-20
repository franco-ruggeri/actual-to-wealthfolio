# Contributing

Thanks for your interest in contributing to actual-to-wealthfolio.

## Development setup

1. Fork and clone the repository.
2. Install dependencies:

```bash
uv sync --group dev
```

3. Run checks before opening a pull request:

```bash
uv run ruff check .
uv run ruff format . --check
uv run mypy .
uv run pytest
```

## Pull request guidelines

- Keep changes focused and small.
- Add or update tests for behavior changes.
- Update README/docs when CLI behavior or assumptions change.
- Use clear Conventional Commit messages when possible.

## Reporting bugs

Open a GitHub issue and include:

- Expected behavior
- Actual behavior
- Steps to reproduce
- Sample input CSV (sanitized)

## Code style

- Python 3.13+
- Ruff formatting/linting
- MyPy type checks
- Absolute imports from `actual_to_wealthfolio`
