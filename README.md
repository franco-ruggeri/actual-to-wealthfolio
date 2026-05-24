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

For stock categories, the `Notes` field in Actual must include:

- `Quantity: X; Unit price: Y`

Example:

- `Quantity: 10; Unit price: 123.45`

## Limitations

Only the following Wealthfolio transaction types are used:

| Type           | When                                    |
| -------------- | --------------------------------------- |
| `Buy`          | Stock category with negative amount     |
| `Sell`         | Stock category with positive amount     |
| `Deposit`      | Non-stock category with positive amount |
| `Withdrawal`   | Non-stock category with negative amount |
| `Transfer in`  | Empty category with positive amount     |
| `Transfer out` | Empty category with negative amount     |

Types such as `Tax`, `Fee`, `Dividend`, and `Interest` are not used. A tax
return (positive amount) becomes `Deposit`; a tax payment (negative amount)
becomes `Withdrawal`.

## Installation

```bash
pip install .
```

You can also use `uv`.

## Configuration

`input/config.yaml` is a YAML list of Actual Budget category names that
represent stock transactions. The file is required — the tool raises an error if
it is absent. It is gitignored so your personal config stays local.

```yaml
- stock purchases
- stock sales
```

Category matching is case-insensitive.

Categories listed in `input/config.yaml` are treated as stock transactions. The
type is inferred from the amount sign: negative → `Buy`, positive → `Sell`. The
`Payee` field is used as the ticker symbol.

All other categories fall through to `Deposit`, `Withdrawal`, `Transfer in`, or
`Transfer out` based on amount sign — no configuration needed.

## Usage

### Prepare inputs

1. Create `input/config.yaml` with your Actual Budget category names.
2. In Actual Budget, for each budget file, go to _All accounts_ > three dots >
   _Export_.
3. Move the exported CSV files into `input/` and name them
   `actual-<budget-file>.csv`, where `<budget-file>` is the name of the budget
   file.

The directory structure should look like this:

```bash
.
├── input/
│   ├── config.yaml
│   ├── actual-<budget-file>.csv
│   └── ...
├── output/
│   ├── wealthfolio-<account>-<budget-file>.csv
│   └── ...
│
└── src/actual_to_wealthfolio/
│   └── ...
```

### Run

Run:

```bash
actual-to-wealthfolio
```

### Use outputs

The converted CSV files are `output/wealthfolio-<account>-<budget-file>.csv`.
There is one CSV file for each account.

Import the CSV files in Wealthfolio.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
