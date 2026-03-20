# wealthfolio-actualbudget-sync

Convert Actual Budget CSV exports into Wealthfolio import files.

## Overview

Actual Budget is the single source of truth.

The tool produces multiple output files optimized for Wealthfolio import:

- **wealthfolio-<account>-<currency>.csv**: One file per account and currency

## Architecture

### Directory Structure

```
.
├── data/
│   ├── actual-sek.csv                # Actual Budget transactions for SEK (input)
│   ├── actual-eur.csv                # Actual Budget transactions for EUR (input)
│   ├── ...                           # One Actual file per currency: actual-<currency>.csv
│   └── ...
├── output/
│   └── wealthfolio-<account-name>-<currency>.csv # One file per account and currency for Wealthfolio import
└── src/actual_wealthfolio_sync/
    ├── converter.py       # Actual -> Wealthfolio converter
    └── main.py            # Main orchestration

```

### Data Flow

1. **Load** Actual transaction files matching `data/actual-<currency>.csv`
2. **Convert** each account to Wealthfolio format
3. **Write** `output/wealthfolio-<account>-<currency>.csv` for non-empty outputs

## Installation

```bash
uv sync
```

## Usage

```bash
uv run wealthfolio-actualbudget-sync
```

Or run as a module:

```bash
uv run python -m actual_wealthfolio_sync
```

This tool is intentionally opinionated and always reads from `data/` and writes
to `output/`.

## Development Status

Actual -> Wealthfolio processing uses `src/actual_wealthfolio_sync/converter.py`.

For `wealthfolio-<account>-<currency>.csv`, output `Type` values are limited to:

- `Withdrawal`
- `Deposit`
- `Transfer in`
- `Transfer out`
- `Buy`
- `Sell`

Current behavior includes:

- Filtering split transaction rows
- Normalizing transaction categories
- Auto-categorizing transfers for empty categories
- Mapping `Stock sales` and `Stock purchases` rows to `Sell`/`Buy`
- Extracting `Quantity` and `Unit price` values from the `Notes` column for trades
