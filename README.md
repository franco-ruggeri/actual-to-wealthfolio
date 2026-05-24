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

### Supported Wealthfolio transaction types

Only the following Wealthfolio transaction types are used:

| Type          | When                                      |
| ------------- | ----------------------------------------- |
| `Buy`         | Trade category with negative amount       |
| `Sell`        | Trade category with positive amount       |
| `Deposit`     | Non-trade category with positive amount   |
| `Withdrawal`  | Non-trade category with negative amount   |
| `Transfer in` | Empty category with positive amount       |
| `Transfer out`| Empty category with negative amount       |

Types such as `Tax`, `Fee`, `Dividend`, and `Interest` are not used. A tax
return (positive amount) becomes `Deposit`; a tax payment (negative amount)
becomes `Withdrawal`.

### Trade categories

Categories listed in `input/config.yaml` are treated as stock transactions.
The type is inferred from the amount sign: negative → `Buy`, positive → `Sell`.
The `Payee` field is used as the ticker symbol.

All other categories fall through to `Deposit`, `Withdrawal`, `Transfer in`,
or `Transfer out` based on amount sign — no configuration needed.

### Trade notes

For trade categories, the `Notes` field in Actual must include:

- `Quantity: X; Unit price: Y`

Example:

- `Quantity: 10; Unit price: 123.45`

## Installation

```bash
pip install .
```

You can also use `uv`.

## Configuration

`input/config.yaml` is a YAML list of Actual Budget category names that
represent stock transactions. The file is required — the tool raises an error
if it is absent. It is gitignored so your personal config stays local.

```yaml
- stock purchases - funds
- stock purchases - espp
- stock sales
```

Category matching is case-insensitive. An example is provided in
[`input/example-config.yaml`](input/example-config.yaml).

## Usage

1. Edit configuration `input/config.yaml` with your Actual Budget category
   names.

   ```bash
   cp input/example-config.yaml input/config.yaml
   # edit input/config.yaml
   ```

1. For each budget file, go to _All accounts_ > three dots > _Export_.
1. Move the exported CSV files into `input/` and name them
   `actual-<budget-file>.csv`, where `<budget-file>` is the name of the budget
   file.
1. Run:

   ```bash
   actual-to-wealthfolio
   ```

1. The converted CSV files are `output/wealthfolio-<account>-<budget-file>.csv`.
   There is one CSV file for each account.
1. Import the CSV files in Wealthfolio.

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
