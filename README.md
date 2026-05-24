# Actual to Wealthfolio

[![CI](https://github.com/franco-ruggeri/actual-to-wealthfolio/actions/workflows/ci.yml/badge.svg)](https://github.com/franco-ruggeri/actual-to-wealthfolio/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.13%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

![actual-to-wealthfolio logo](docs/logo.png)

Convert [Actual Budget](https://actualbudget.org) CSV exports into
[Wealthfolio](https://wealthfolio.app) import files — one file per account.

## Workflow

1. Sync transactions in Actual (e.g. via GoCardless).
2. Export each budget file: _All accounts_ > three dots > _Export_.
3. Run this tool to generate Wealthfolio-ready CSVs.
4. Import them in Wealthfolio.

## Setup

Place files in `input/` before running:

```
input/
  config.yaml                    # required: your stock category names
  actual-<budget-file>.csv       # one per Actual budget file
output/
  wealthfolio-<account>-<budget-file>.csv   # generated
```

**`input/config.yaml`** — list the Actual category names that represent stock
transactions (case-insensitive):

```yaml
- stock purchases
- stock sales
```

For stock transactions, the `Notes` field in Actual must include
`Quantity: X; Unit price: Y` (e.g. `Quantity: 10; Unit price: 123.45`), and
`Payee` is used as the ticker symbol.

## Usage

```bash
pip install .
actual-to-wealthfolio
```

## Transaction type mapping

| Actual category | Amount | Wealthfolio type |
| --------------- | ------ | ---------------- |
| Stock           | –      | `Buy`            |
| Stock           | +      | `Sell`           |
| Non-stock       | +      | `Deposit`        |
| Non-stock       | –      | `Withdrawal`     |
| Empty           | +      | `Transfer in`    |
| Empty           | –      | `Transfer out`   |

Types like `Tax`, `Fee`, `Dividend`, and `Interest` are not used.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
