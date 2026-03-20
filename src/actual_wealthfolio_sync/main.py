import sys

from actual_wealthfolio_sync.converter import Converter


def main() -> None:
    try:
        converter = Converter()

        print("\nProcessing data...")
        wealthfolio_outputs = converter.convert()

        print("\nWriting processed data...")
        for account_key, wealthfolio_output in wealthfolio_outputs.items():
            print(f"  Wealthfolio ({account_key}): {wealthfolio_output}")

        print("\nProcessing complete!")

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error during processing: {e}", file=sys.stderr)
        sys.exit(1)
