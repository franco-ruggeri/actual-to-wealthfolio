# Actual to Wealthfolio

[![CI](https://github.com/franco-ruggeri/actual-to-wealthfolio/actions/workflows/ci.yml/badge.svg)](https://github.com/franco-ruggeri/actual-to-wealthfolio/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.13%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

![actual-to-wealthfolio logo](docs/logo.png)

Convert [Actual Budget](https://actualbudget.org) CSV exports into
[Wealthfolio](https://wealthfolio.app) import files — one file per account.

## Usage

### 1. Install

```bash
pip install .   # or: uv sync
```

### 2. Configure

Create `input/config.yaml` listing the Actual category names that represent stock transactions (case-insensitive):

```yaml
- stock purchases
- stock sales
```

For stock transactions, the `Notes` field in Actual must include `Quantity: X; Unit price: Y` (e.g. `Quantity: 10; Unit price: 123.45`), and `Payee` is used as the ticker symbol.

### 3. Export from Actual Budget

For each budget file, go to _All accounts_ > three dots > _Export_. Move the exported CSV into `input/` and name it `actual-<budget-file>.csv`.

```
input/
  config.yaml
  actual-<budget-file>.csv   # one per budget file
```

### 4. Run

```bash
actual-to-wealthfolio
```

### 5. Import into Wealthfolio

Output files are written to `output/wealthfolio-<account>-<budget-file>.csv` (one per account). Import each file in Wealthfolio.

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
