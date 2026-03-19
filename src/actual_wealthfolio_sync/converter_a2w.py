from pathlib import Path
import re

import pandas as pd


class ConverterA2W:
    INPUT_PATH = Path("data/actual-transactions.csv")
    OUTPUT_DIR = Path("output")

    def _load_actual_data(self) -> pd.DataFrame:
        if not self.INPUT_PATH.exists():
            raise FileNotFoundError(f"Actual data file not found: {self.INPUT_PATH}")
        return pd.read_csv(self.INPUT_PATH)

    def _filter_split_rows(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()
        data = data[~data["Notes"].str.match(r"^\(SPLIT INTO \d+\) ", na=False)]
        data["Notes"] = data["Notes"].str.replace(r"^\(SPLIT \d+ OF \d+\) ", "", regex=True)
        return data

    def _update_empty_categories(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()
        empty_category = data["Category"].isna() | (data["Category"] == "")
        data.loc[empty_category & (data["Amount"] > 0), "Category"] = "Transfer in"
        data.loc[empty_category & (data["Amount"] < 0), "Category"] = "Transfer out"
        return data

    def _normalize_categories(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()
        allowed_categories = ["Transfer in", "Transfer out", "Deposit", "Withdrawal"]
        non_standard = ~data["Category"].isin(allowed_categories)
        data.loc[non_standard & (data["Amount"] < 0), "Category"] = "Withdrawal"
        data.loc[non_standard & (data["Amount"] > 0), "Category"] = "Deposit"
        return data

    def _drop_zero_amount_rows(self, data: pd.DataFrame) -> pd.DataFrame:
        return data[(data["Amount"] > 0) | (data["Amount"] < 0)].copy()

    def _to_wealthfolio_columns(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()
        data["Quantity"] = None
        data["Unit_Price"] = None
        data = data[["Date", "Payee", "Notes", "Category", "Amount", "Quantity", "Unit_Price"]]
        return data.rename(columns={"Payee": "Symbol", "Notes": "Comment", "Category": "Type"})

    def _sanitize_account_name(self, account_name: str) -> str:
        kebab = re.sub(r"[^a-z0-9]+", "-", account_name.lower())
        return kebab.strip("-")

    def _convert_dataframe(self, data: pd.DataFrame) -> pd.DataFrame:
        converted_data = self._filter_split_rows(data)
        converted_data = self._update_empty_categories(converted_data)
        converted_data = self._normalize_categories(converted_data)
        converted_data = self._drop_zero_amount_rows(converted_data)
        return self._to_wealthfolio_columns(converted_data)

    def convert(self, cash_accounts: list[str]) -> dict[str, Path]:
        actual_data = self._load_actual_data()
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        outputs: dict[str, Path] = {}
        for account_name in cash_accounts:
            cash_data = actual_data[actual_data["Account"] == account_name].copy()
            converted_data = self._convert_dataframe(cash_data)
            safe_name = self._sanitize_account_name(account_name)
            output_path = self.OUTPUT_DIR / f"wealthfolio-{safe_name}.csv"
            converted_data.to_csv(output_path, index=False)
            outputs[account_name] = output_path

        return outputs
