import sys

from actual_to_wealthfolio.config import load_config
from actual_to_wealthfolio.converter import Converter


def main() -> None:
    try:
        remap_config = load_config()
        converter = Converter(remap_config=remap_config)

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
