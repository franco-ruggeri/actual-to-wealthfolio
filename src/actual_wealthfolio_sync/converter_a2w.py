from pathlib import Path
import re

import pandas as pd


class ConverterA2W:
    DATA_DIR = Path("data")
    OUTPUT_DIR = Path("output")

    def _get_currency_input_paths(self) -> list[tuple[str, Path]]:
        input_paths: list[tuple[str, Path]] = []
        for path in sorted(self.DATA_DIR.glob("actual-*.csv")):
            match = re.fullmatch(r"actual-([a-z0-9]+)", path.stem)
            if not match:
                continue
            currency = match.group(1)
            input_paths.append((currency, path))

        if not input_paths:
            raise FileNotFoundError(
                f"No currency input files found in {self.DATA_DIR} (expected actual-<currency>.csv)"
            )

        return input_paths

    def _load_actual_data(self, input_path: Path) -> pd.DataFrame:
        if not input_path.exists():
            raise FileNotFoundError(f"Actual data file not found: {input_path}")
        return pd.read_csv(input_path)

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
        data["Symbol"] = None
        data["Quantity"] = None
        data["Unit_Price"] = None
        data = data[["Date", "Symbol", "Notes", "Category", "Amount", "Quantity", "Unit_Price"]]
        return data.rename(columns={"Notes": "Comment", "Category": "Type"})

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
        currency_input_paths = self._get_currency_input_paths()
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        outputs: dict[str, Path] = {}
        for currency, input_path in currency_input_paths:
            actual_data = self._load_actual_data(input_path)
            for account_name in cash_accounts:
                cash_data = actual_data[actual_data["Account"] == account_name].copy()
                if cash_data.empty:
                    continue

                converted_data = self._convert_dataframe(cash_data)
                if converted_data.empty:
                    continue

                safe_name = self._sanitize_account_name(account_name)
                output_path = self.OUTPUT_DIR / f"wealthfolio-{currency}-{safe_name}.csv"
                converted_data.to_csv(output_path, index=False)
                outputs[f"{currency}:{account_name}"] = output_path

        return outputs
