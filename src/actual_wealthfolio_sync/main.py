import sys

from actual_wealthfolio_sync.account_manager import AccountManager
from actual_wealthfolio_sync.converter_a2w import ConverterA2W
from actual_wealthfolio_sync.converter_w2a import ConverterW2A


def main() -> None:
    try:
        account_manager = AccountManager()
        converter_a2w = ConverterA2W()
        converter_w2a = ConverterW2A()

        print("Loading account configuration...")
        cash_accounts = account_manager.get_cash_accounts()
        securities_accounts = account_manager.get_securities_accounts()

        print(f"  Found {len(cash_accounts)} cash account(s)")
        print(f"  Found {len(securities_accounts)} securities account(s)")

        print("\nProcessing data...")
        wealthfolio_output = converter_a2w.run(cash_accounts)
        actual_outputs = converter_w2a.run(securities_accounts)

        print("\nWriting processed data...")
        print(f"  Wealthfolio cash: {wealthfolio_output}")

        for account_name, actual_output in actual_outputs.items():
            print(f"  Actual ({account_name}): {actual_output}")

        print("\nProcessing complete!")

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error during processing: {e}", file=sys.stderr)
        sys.exit(1)
