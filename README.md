# actual-to-wealthfolio

Convert Actual Budget CSV exports to Wealthfolio-compatible format.

## Installation

```bash
uv sync
```

## Usage

```bash
uv run python -m actual_to_wealthfolio input.csv output.csv
```

## Features

- Filters split transaction rows
- Normalizes transaction categories
- Validates stock purchase format: `(QUANTITY=X, UNIT_PRICE=Y)`
- Auto-categorizes transfers for empty categories
