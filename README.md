# actual-wealthfolio-sync

Convert Actual Budget CSV exports to Wealthfolio-compatible format.

## Installation

```bash
uv sync
```

## Usage

```bash
uv run python -m actual_wealthfolio_sync input.csv output.csv
```

## Assumptions

### Required Note Format

The Actual Budget CSV export must have notes in the format
`(QUANTITY=X, UNIT_PRICE=Y)` for transactions in the following categories:

- Stock purchases
- Stock sales
- Dividends

### Payee Column Requirement

The **Payee** column in your Actual Budget export should contain something that
can be easily recognized and mapped to a stock symbol when importing into
Wealthfolio. The Payee value will be mapped to the **Symbol** column in the
output.

**Example:**

- For Apple stock transactions, you could use `AAPL`, `Apple`, or `Apple Inc.`
- For Microsoft stock transactions, you could use `MSFT`, `Microsoft`, etc.
- For Tesla stock transactions, you could use `TSLA`, `Tesla`, etc.

When importing into Wealthfolio, you'll be able to map these values to the
correct stock symbols in your portfolio.

## Features

- Filters split transaction rows
- Normalizes transaction categories
- Validates stock purchase format: `(QUANTITY=X, UNIT_PRICE=Y)`
- Auto-categorizes transfers for empty categories
- Extracts quantity and unit price from notes into separate columns
