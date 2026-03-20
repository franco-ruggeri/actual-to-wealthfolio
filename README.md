# Actual to Wealthfolio

[![CI](https://github.com/franco-ruggeri/actual-to-wealthfolio/actions/workflows/ci.yml/badge.svg)](https://github.com/franco-ruggeri/actual-to-wealthfolio/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.13%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/a84d6371-9d55-4664-92d2-fe4d61a191df" />

## Overview

Convert Actual Budget CSV exports into Wealthfolio import files.

Actual Budget is the single source of truth. From Actual Budget transactions,
this tool generates transactions that can be imported in Wealthfolio.

## Assumptions

### Categories

Actual categories are mapped to Wealthfolio categories with the following rules:

```text
stock purchases => Buy
stock sales => Sell
dividends => Dividend
interests => Interest
income taxes => Tax
banking fees => Fee
```

In Actual, make sure you name the categories with the left names. All the other
categories are mapped to `Withdrawal`, `Deposit`, `Transfer in`, and
`Transfer out`, depending on the amount and transaction type.

### Trade notes

For `stock purchases`, `stock sales`, and `dividends`, the `Notes` field in
Actual must include trade annotations in this format:

- `Quantity: X; Unit price: Y`

Example:

- `Quantity: 10; Unit price: 123.45`

## Installation

```bash
pip install .
```

You can also use `uv`.

## Usage

1. For each budget file, go to _All accounts_ > three dots > _Export_.
2. Move the exported CSV files in `data` and name them
   `actual-<budget-file>.csv`, where `<budget-file>` is the name of the budget
   file.
3. Run:

   ```bash
   actual-to-wealthfolio
   ```

4. The converted CSV files are `output/wealthfolio-<account>-<budget-file>.csv`.
   There is one CSV file for each account.
5. Import the CSV files in Wealthfolio.

## Example input -> output

Example input row in `data/actual-main.csv`:

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
├── data/
│   ├── actual-<budget-file>.csv
│   └── ...
├── output/
│   ├── wealthfolio-<account>-<budget-file>.csv
│   └── ...
│
└── src/actual_to_wealthfolio/
    ├── __main__.py                         # Enables python -m actual_to_wealthfolio
    ├── converter.py                        # CSV transformation logic
    └── main.py                             # CLI orchestration

```

### Data Flow

1. Load Actual transaction files matching `data/actual-<budget-file>.csv`
2. Convert each account to Wealthfolio format
3. Write `output/wealthfolio-<account>-<budget-file>.csv` for non-empty outputs
