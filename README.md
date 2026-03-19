# actual-wealthfolio-sync

Convert Actual Budget CSV exports to Wealthfolio-compatible format.

## Installation

```bash
uv sync
```

## Usage

```bash
uv run python -m actual_wealthfolio_sync.main input.csv output.csv
```

## Features

- Filters split transaction rows
- Normalizes transaction categories
- Validates stock purchase format: `(UNIT_PRICE=X, QUANTITY=Y)`
- Auto-categorizes transfers for empty categories
