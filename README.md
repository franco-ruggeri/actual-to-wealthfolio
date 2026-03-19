# actual-wealthfolio-sync

Synchronize transaction data between Actual Budget and Wealthfolio formats.

## Overview

This tool processes transaction data from both Actual Budget and Wealthfolio,
using each as the source of truth for different account types:

- **Actual Budget CSV**: Ground truth for cash accounts
- **Wealthfolio CSV**: Ground truth for securities accounts

The tool produces multiple output files optimized for import:

- **wealthfolio-<account>-<currency>.csv**: One file per cash account and currency for Wealthfolio import
- **actual-<account>.csv**: One file per securities account in Actual format
  (Actual imports one account at a time)

## Architecture

### Directory Structure

```
.
├── data/
│   ├── wealthfolio-accounts.csv      # Account configuration (name, accountType)
│   ├── actual-sek.csv                # Actual Budget transactions for SEK (input)
│   ├── actual-eur.csv                # Actual Budget transactions for EUR (input)
│   ├── ...                           # One Actual file per currency: actual-<currency>.csv
│   └── wealthfolio-activities.csv    # Wealthfolio transactions (input)
├── output/
│   ├── wealthfolio-<account-name>-<currency>.csv # One file per cash account and currency for Wealthfolio import
│   └── actual-<account-name>.csv      # One file per securities account in Actual format
└── src/actual_wealthfolio_sync/
    ├── account_manager.py # Account loading and filtering
    ├── converter_a2w.py   # Actual cash -> Wealthfolio converter
    ├── converter_w2a.py   # Wealthfolio securities -> Actual converter
    └── main.py           # Main orchestration

```

### Data Flow

1. **Load** account configuration with `AccountManager`
2. **Convert** cash accounts with `ConverterA2W` using `data/actual-<currency>.csv` files
3. **Convert** securities accounts with `ConverterW2A` using `data/wealthfolio-activities.csv`
4. **Write** processed data:
    - `output/wealthfolio-<account>-<currency>.csv`: One file per cash account and currency for Wealthfolio import
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

### Account Name Matching

Account names must match exactly between the Actual input files (`actual-<currency>.csv`)
and `wealthfolio-accounts.csv`.

If an account name differs (including spaces, punctuation, or casing), that account's
rows will not be selected for conversion.

## Development Status

Cash account processing uses `src/actual_wealthfolio_sync/converter_a2w.py`.

For `wealthfolio-<account>-<currency>.csv`, output `Type` values are limited to:

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
