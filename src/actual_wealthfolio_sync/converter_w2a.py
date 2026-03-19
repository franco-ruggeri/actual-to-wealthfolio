from pathlib import Path

import pandas as pd


class ConverterW2A:
    INPUT_PATH = Path("data/wealthfolio-activities.csv")
    OUTPUT_DIR = Path("output")

    def _load_wealthfolio_data(self) -> pd.DataFrame:
        if not self.INPUT_PATH.exists():
            raise FileNotFoundError(f"Wealthfolio data file not found: {self.INPUT_PATH}")
        return pd.read_csv(self.INPUT_PATH)

    def _sanitize_account_name(self, account_name: str) -> str:
        return account_name.replace(" ", "-").replace("(", "").replace(")", "").replace("/", "-")

    def run(self, securities_accounts: list[str]) -> dict[str, Path]:
        wealthfolio_data = self._load_wealthfolio_data()
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        outputs: dict[str, Path] = {}
        for account_name in securities_accounts:
            account_data = wealthfolio_data[wealthfolio_data["Account"] == account_name].copy()
            safe_name = self._sanitize_account_name(account_name)
            output_path = self.OUTPUT_DIR / f"actual-{safe_name}.csv"
            account_data.to_csv(output_path, index=False)
            outputs[account_name] = output_path

        return outputs
