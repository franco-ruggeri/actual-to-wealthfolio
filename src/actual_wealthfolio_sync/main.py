import argparse

from actual_wealthfolio_sync.converter import Converter


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert Actual Budget CSV to Wealthfolio CSV"
    )
    parser.add_argument(
        "input",
        type=str,
        help="Path to the Actual Budget CSV file",
    )
    parser.add_argument(
        "output",
        type=str,
        help="Path where the Wealthfolio CSV should be saved",
    )

    args = parser.parse_args()

    try:
        converter = Converter(args.input)
        converter.process(args.output)
        print(f"✓ Conversion complete: {args.output}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        exit(1)
    except Exception as e:
        print(f"Error during conversion: {e}")
        exit(1)
