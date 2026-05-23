# Actual to Wealthfolio

[![CI](https://github.com/franco-ruggeri/actual-to-wealthfolio/actions/workflows/ci.yml/badge.svg)](https://github.com/franco-ruggeri/actual-to-wealthfolio/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.13%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

![actual-to-wealthfolio logo](docs/logo.png)

## Overview

Convert Actual Budget CSV exports into Wealthfolio import files.

Actual Budget is the single source of truth. From Actual Budget transactions,
this tool generates transactions that can be imported in Wealthfolio.

## Motivation

You only want to add each transaction once and keep data in both apps.

Actual can synchronize transactions from bank accounts for free (for example,
via GoCardless), so a practical workflow is:

1. Sync transactions in Actual.
2. Sync Actual and Wealthfolio with this tool.

## Assumptions

### Categories

Actual categories are mapped to Wealthfolio types as configured in
`input/config.yaml` (see [Configuration](#configuration) below).

All categories not listed in the config are mapped to `Withdrawal`, `Deposit`,
`Transfer in`, or `Transfer out`, depending on the amount and transaction type.

### Trade notes

For categories marked with `trade: true`, the `Notes` field in Actual must
include trade annotations in this format:

- `Quantity: X; Unit price: Y`

Example:

- `Quantity: 10; Unit price: 123.45`

## Installation

```bash
pip install .
```

You can also use `uv`.

## Configuration

Category remaps are defined in `input/config.yaml`. The file is required — the
tool raises an error if it is absent.

Each entry in the `remaps` list has three fields:

| Field   | Type    | Description                                               |
| ------- | ------- | --------------------------------------------------------- |
| `from`  | string  | Actual Budget category name (case-insensitive)            |
| `to`    | string  | Wealthfolio transaction type                              |
| `trade` | boolean | Whether to extract `Quantity`, `Unit_Price`, and `Symbol` |

See [`input/config.yaml`](input/config.yaml) for a working example.

## Usage

1. Edit `input/config.yaml` with your Actual Budget category names.
2. For each budget file, go to _All accounts_ > three dots > _Export_.
3. Move the exported CSV files into `input/` and name them
   `actual-<budget-file>.csv`, where `<budget-file>` is the name of the budget
   file.
4. Run:

   ```bash
   actual-to-wealthfolio
   ```

5. The converted CSV files are `output/wealthfolio-<account>-<budget-file>.csv`.
   There is one CSV file for each account.
6. Import the CSV files in Wealthfolio.

## Example input -> output

Example input row in `input/actual-main.csv`:

```csv
Date,Account,Payee,Notes,Category,Amount
2026-01-11,Brokerage,AAPL,"Quantity: 3; Unit price: 150.00",Stock purchases,-450.00
```

Example output row in `output/wealthfolio-brokerage-main.csv`:

```csv
Date,Symbol,Comment,Type,Amount,Quantity,Unit_Price
2026-01-11,AAPL,"Quantity: 3; Unit price: 150.00",Buy,-450.00,3,150.00
```

## Architecture

### Directory Structure

```bash
.
├── README.md
├── pyproject.toml
├── input/
│   ├── config.yaml
│   ├── actual-<budget-file>.csv
│   └── ...
├── output/
│   ├── wealthfolio-<account>-<budget-file>.csv
│   └── ...
│
└── src/actual_to_wealthfolio/
    ├── __main__.py                         # Enables python -m actual_to_wealthfolio
    ├── config.py                           # Config loading
    ├── converter.py                        # CSV transformation logic
    └── main.py                             # CLI orchestration
```

### Data Flow

1. Load `input/config.yaml`
2. Load Actual transaction files matching `input/actual-<budget-file>.csv`
3. Convert each account to Wealthfolio format
4. Write `output/wealthfolio-<account>-<budget-file>.csv` for non-empty outputs
