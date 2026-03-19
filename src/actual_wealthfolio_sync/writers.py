from pathlib import Path

import pandas as pd


class DataWriter:
    def __init__(self, output_dir: Path = Path("output")) -> None:
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def write_actual_account(self, data: pd.DataFrame, account_name: str) -> Path:
        safe_name = account_name.replace(" ", "-").replace("(", "").replace(")", "").replace("/", "-")
        output_path = self.output_dir / f"actual-{safe_name}.csv"
        data.to_csv(output_path, index=False)
        return output_path

    def write_wealthfolio_cash(self, data: pd.DataFrame) -> Path:
        output_path = self.output_dir / "wealthfolio-cash.csv"
        data.to_csv(output_path, index=False)
        return output_path
