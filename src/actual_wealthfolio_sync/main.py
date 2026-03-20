import sys

from actual_wealthfolio_sync.converter_a2w import ConverterA2W
from actual_wealthfolio_sync.converter_w2a import ConverterW2A


def main() -> None:
    try:
        converter_a2w = ConverterA2W()
        converter_w2a = ConverterW2A()

        print("\nProcessing data...")
        wealthfolio_outputs = converter_a2w.convert()
        actual_outputs = converter_w2a.convert()

        print("\nWriting processed data...")
        for account_key, wealthfolio_output in wealthfolio_outputs.items():
            print(f"  Wealthfolio ({account_key}): {wealthfolio_output}")

        for account_key, actual_output in actual_outputs.items():
            print(f"  Actual ({account_key}): {actual_output}")

        print("\nProcessing complete!")

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error during processing: {e}", file=sys.stderr)
        sys.exit(1)
