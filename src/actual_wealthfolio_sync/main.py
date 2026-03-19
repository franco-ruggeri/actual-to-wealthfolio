import sys

from actual_wealthfolio_sync.account_manager import AccountManager
from actual_wealthfolio_sync.converter_a2w import ConverterA2W


def main() -> None:
    try:
        account_manager = AccountManager()
        converter_a2w = ConverterA2W()

        print("Loading account configuration...")
        cash_accounts = account_manager.get_cash_accounts()

        print(f"  Found {len(cash_accounts)} cash account(s)")

        print("\nProcessing data...")
        wealthfolio_outputs = converter_a2w.convert(cash_accounts)

        print("\nWriting processed data...")
        for account_name, wealthfolio_output in wealthfolio_outputs.items():
            print(f"  Wealthfolio ({account_name}): {wealthfolio_output}")

        # for account_name, actual_output in actual_outputs.items():
        #     print(f"  Actual ({account_name}): {actual_output}")

        print("\nProcessing complete!")

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error during processing: {e}", file=sys.stderr)
        sys.exit(1)
