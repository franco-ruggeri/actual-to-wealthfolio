# actual-wealthfolio-sync

Synchronize transaction data between Actual Budget and Wealthfolio formats.

## Overview

This tool processes transaction data from both Actual Budget and Wealthfolio,
using each as the source of truth for different account types:

- **Actual Budget CSV**: Ground truth for cash accounts
- **Wealthfolio CSV**: Ground truth for securities accounts

The tool produces multiple output files optimized for import:

- **wealthfolio-cash.csv**: All cash accounts transformed to Wealthfolio format
- **actual-<account>.csv**: One file per securities account in Actual format
  (Actual imports one account at a time)

## Architecture

### Directory Structure

```
.
├── data/
│   ├── wealthfolio-accounts.csv      # Account configuration (name, accountType)
│   ├── actual-transactions.csv       # Actual Budget transactions (input)
│   └── wealthfolio-activities.csv    # Wealthfolio transactions (input)
├── output/
│   ├── wealthfolio-cash.csv           # Cash accounts in Wealthfolio format
│   └── actual-<account-name>.csv      # One file per securities account in Actual format
└── src/actual_wealthfolio_sync/
    ├── models.py         # Data models (Account, transactions)
    ├── loaders.py        # CSV loading utilities
    ├── processors.py     # Transformation logic
    ├── writers.py        # CSV writing utilities
    └── main.py           # Main orchestration

```

### Data Flow

1. **Load** account configuration from `data/wealthfolio-accounts.csv`
2. **Load** transactions from `data/actual-transactions.csv` and `data/wealthfolio-activities.csv`
3. **Process** each dataset:
   - Wealthfolio cash output: Transform cash accounts from Actual to Wealthfolio
     format
   - Actual per-account outputs: Transform securities accounts from Wealthfolio
     to Actual format (one file per account)
4. **Write** processed data:
   - `output/wealthfolio-cash.csv`: All cash accounts in Wealthfolio format
   - `output/actual-<account>.csv`: One file per securities account in Actual
     format

## Installation

```bash
uv sync
```

## Usage

```bash
uv run actual-wealthfolio-sync
```

Or run as a module:

```bash
uv run python -m actual_wealthfolio_sync
```

This tool is intentionally opinionated and always reads from `data/` and writes
to `output/`.

## Configuration

### wealthfolio-accounts.csv Format

The `data/wealthfolio-accounts.csv` file can contain many columns, but only `name` and
`accountType` are used by this tool.

```csv
id,name,accountType,group,currency,isDefault,isActive,isArchived,trackingMode,createdAt,updatedAt,platformId,accountNumber,meta,provider,providerAccountId
1,Checking Account,cash,Assets,USD,true,true,false,tracking,2024-01-01,2024-01-01,,,,,
2,Savings Account,cash,Assets,USD,false,true,false,tracking,2024-01-01,2024-01-01,,,,,
3,Brokerage Account,securities,Investments,USD,false,true,false,tracking,2024-01-01,2024-01-01,,,,,
4,IRA Account,securities,Investments,USD,false,true,false,tracking,2024-01-01,2024-01-01,,,,,
```

Valid account types: `cash`, `securities`

## Development Status

Cash account processing uses the converter pipeline in
`src/actual_wealthfolio_sync/converter.py`.

For `wealthfolio-cash.csv`, output `Type` values are limited to:

- `Withdrawal`
- `Deposit`
- `Transfer in`
- `Transfer out`

## Legacy Features (To Be Migrated)

The following features from the old converter need to be integrated into the new
processor:

- Filter split transaction rows
- Normalize transaction categories
- Auto-categorize transfers for empty categories
