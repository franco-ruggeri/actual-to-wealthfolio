# actual-to-wealthfolio

Convert Actual Budget CSV exports into Wealthfolio import files.

## Overview

Actual Budget is the single source of truth. From Actual Budget transactions,
the tool generates transactions that can be imported in Wealthfolio.

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

## Architecture

### Directory Structure

```bash
.
├── README.md
├── pyproject.toml
├── data/
│   ├── actual-se.csv                     # Input export for one budget file
│   ├── actual-joint.csv                  # Input export for another budget file
│   └── actual-<budget-file>.csv          # Required naming pattern
├── output/
│   └── wealthfolio-<account>-<budget-file>.csv
│                                        # One output file per account per budget file
└── src/actual_to_wealthfolio/
    ├── __main__.py                         # Enables python -m actual_to_wealthfolio
    ├── converter.py                        # CSV transformation logic
    └── main.py                             # CLI orchestration

```

### Data Flow

1. Load Actual transaction files matching `data/actual-<budget-file>.csv`
2. Convert each account to Wealthfolio format
3. Write `output/wealthfolio-<account>-<budget-file>.csv` for non-empty outputs
