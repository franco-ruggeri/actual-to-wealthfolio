import sys
from pathlib import Path

from actual_wealthfolio_sync.loaders import DataLoader
from actual_wealthfolio_sync.processors import DataProcessor
from actual_wealthfolio_sync.writers import DataWriter


def main() -> None:
    data_dir = Path("data")
    output_dir = Path("output")

    try:
        loader = DataLoader(data_dir=data_dir)
        writer = DataWriter(output_dir=output_dir)

        print("Loading account configuration...")
        accounts = loader.load_accounts()
        cash_accounts = loader.get_cash_accounts(accounts)
        securities_accounts = loader.get_securities_accounts(accounts)

        print(f"  Found {len(cash_accounts)} cash account(s)")
        print(f"  Found {len(securities_accounts)} securities account(s)")

        print("\nLoading transaction data...")
        actual_data = loader.load_actual_data()
        wealthfolio_data = loader.load_wealthfolio_data()

        print(f"  Loaded {len(actual_data)} Actual transactions")
        print(f"  Loaded {len(wealthfolio_data)} Wealthfolio transactions")

        print("\nProcessing data...")
        processor = DataProcessor(accounts)

        actual_by_account = processor.process_actual_by_account(actual_data, wealthfolio_data, securities_accounts)

        wealthfolio_cash = processor.process_wealthfolio_cash(actual_data, cash_accounts)

        print("\nWriting processed data...")

        wealthfolio_output = writer.write_wealthfolio_cash(wealthfolio_cash)
        print(f"  Wealthfolio cash: {wealthfolio_output}")

        for account_name, account_data in actual_by_account.items():
            actual_output = writer.write_actual_account(account_data, account_name)
            print(f"  Actual ({account_name}): {actual_output}")

        print("\nProcessing complete!")

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error during processing: {e}", file=sys.stderr)
        sys.exit(1)
