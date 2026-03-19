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

## Assumptions

The Actual Budget CSV export must have notes in the format `(QUANTITY=X, UNIT_PRICE=Y)` for transactions in the following categories:
- Stock purchases
- Dividends

## Features

- Filters split transaction rows
- Normalizes transaction categories
- Validates stock purchase format: `(QUANTITY=X, UNIT_PRICE=Y)`
- Auto-categorizes transfers for empty categories
- Extracts quantity and unit price from notes into separate columns
