from pathlib import Path
import re

import pandas as pd
import yaml


class Converter:
    _INPUT_DIR = Path("input")
    _OUTPUT_DIR = Path("output")
    _CONFIG_PATH = Path("input/config.yaml")
    _DUPLICATE_AMOUNT_EPSILON = 0.000001
    _INTERNAL_CATEGORIES = {"transfer in", "transfer out", "deposit", "withdrawal"}

    def __init__(self) -> None:
        self._stock_set = {c.lower() for c in self._load_stock_categories()}
        self._known_set = self._stock_set | self._INTERNAL_CATEGORIES

    def _load_stock_categories(self) -> list[str]:
        if not self._CONFIG_PATH.exists():
            raise FileNotFoundError(f"Configuration file not found: {self._CONFIG_PATH}")
        with open(self._CONFIG_PATH) as f:
            raw = yaml.safe_load(f)
        if not isinstance(raw, list):
            raise ValueError(f"{self._CONFIG_PATH}: must be a YAML sequence at the top level")
        categories: list[str] = []
        for i, item in enumerate(raw):
            if not isinstance(item, str):
                raise ValueError(f"{self._CONFIG_PATH}: [{i}]: each entry must be a string (Actual category name)")
            categories.append(item)
        return categories

    def _is_stock_category(self, normalized: pd.Series) -> pd.Series:
        return normalized.isin(self._stock_set)

    def _is_known_category(self, normalized: pd.Series) -> pd.Series:
        return normalized.isin(self._known_set)

    def _get_budget_file_input_paths(self) -> list[tuple[str, Path]]:
        input_paths: list[tuple[str, Path]] = []
        for path in sorted(self._INPUT_DIR.glob("actual-*.csv")):
            budget_file_name = path.stem.removeprefix("actual-").strip()
            if not budget_file_name or budget_file_name == path.stem:
                continue
            input_paths.append((budget_file_name, path))

        if not input_paths:
            raise FileNotFoundError(
                f"No budget input files found in {self._INPUT_DIR} (expected actual-<budget-file>.csv)"
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
        normalized_category = data["Category"].fillna("").astype(str).str.strip().str.lower()
        non_standard = ~self._is_known_category(normalized_category)
        data.loc[non_standard & (data["Amount"] < 0), "Category"] = "Withdrawal"
        data.loc[non_standard & (data["Amount"] > 0), "Category"] = "Deposit"
        return data

    def _extract_stock_values_from_notes(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()
        notes = data["Notes"].fillna("").astype(str)
        normalized_category = data["Category"].fillna("").astype(str).str.strip().str.lower()
        is_stock_category = self._is_stock_category(normalized_category)
        quantity = notes.str.extract(r"(?i)quantity\s*[:=]\s*(-?\d+(?:\.\d+)?)", expand=False)
        unit_price = notes.str.extract(r"(?i)unit[_\s]*price\s*[:=]\s*(-?\d+(?:\.\d+)?)", expand=False)
        data["Quantity"] = quantity.where(is_stock_category)
        data["Unit_Price"] = unit_price.where(is_stock_category)
        return data

    def _apply_stock_types(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()
        normalized_category = data["Category"].fillna("").astype(str).str.strip().str.lower()
        is_stock = self._is_stock_category(normalized_category)
        data.loc[is_stock & (data["Amount"] < 0), "Category"] = "Buy"
        data.loc[is_stock & (data["Amount"] > 0), "Category"] = "Sell"
        return data

    def _set_symbol_from_payee(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()
        normalized_category = data["Category"].fillna("").astype(str).str.strip().str.lower()
        use_payee_as_symbol = self._is_stock_category(normalized_category)
        payee = data["Payee"].fillna("").astype(str).str.strip()
        data["Symbol"] = payee.where(use_payee_as_symbol, "")
        return data

    def _drop_zero_amount_rows(self, data: pd.DataFrame) -> pd.DataFrame:
        return data[(data["Amount"] > 0) | (data["Amount"] < 0)].copy()

    def _to_wealthfolio_columns(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()
        data["Type"] = data["Category"]
        data = data[["Date", "Symbol", "Notes", "Type", "Amount", "Quantity", "Unit_Price"]]
        return data.rename(columns={"Notes": "Comment"})

    def _sanitize_account_name(self, account_name: str) -> str:
        kebab = re.sub(r"[^a-z0-9]+", "-", account_name.lower())
        return kebab.strip("-")

    def _sanitize_budget_file_name(self, budget_file_name: str) -> str:
        kebab = re.sub(r"[^a-z0-9]+", "-", budget_file_name.lower())
        return kebab.strip("-")

    def _convert_dataframe(self, data: pd.DataFrame) -> pd.DataFrame:
        converted_data = self._filter_split_rows(data)
        converted_data = self._update_empty_categories(converted_data)
        converted_data = self._extract_stock_values_from_notes(converted_data)
        converted_data = self._normalize_categories(converted_data)
        converted_data = self._set_symbol_from_payee(converted_data)
        converted_data = self._apply_stock_types(converted_data)
        converted_data = self._drop_zero_amount_rows(converted_data)
        converted_data = self._to_wealthfolio_columns(converted_data)
        return self._deduplicate_same_day_amount_category(converted_data)

    def _deduplicate_same_day_amount_category(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()
        duplicate_group = ["Date", "Type", "Amount"]
        duplicate_index = data.groupby(duplicate_group).cumcount()
        data["Amount"] = data["Amount"] + (duplicate_index * self._DUPLICATE_AMOUNT_EPSILON)
        return data

    def convert(self) -> dict[str, Path]:
        budget_file_input_paths = self._get_budget_file_input_paths()
        self._OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        outputs: dict[str, Path] = {}

        for budget_file_name, input_path in budget_file_input_paths:
            actual_data = self._load_actual_data(input_path)
            account_names = sorted(actual_data["Account"].dropna().astype(str).str.strip().unique())
            for account_name in account_names:
                if not account_name:
                    continue

                cash_data = actual_data[actual_data["Account"] == account_name].copy()
                if cash_data.empty:
                    continue

                converted_data = self._convert_dataframe(cash_data)
                if converted_data.empty:
                    continue

                safe_name = self._sanitize_account_name(account_name)
                safe_budget_file_name = self._sanitize_budget_file_name(budget_file_name)
                output_path = self._OUTPUT_DIR / f"wealthfolio-{safe_name}-{safe_budget_file_name}.csv"
                converted_data.to_csv(output_path, index=False)
                outputs[f"{budget_file_name}:{safe_name}"] = output_path

        return outputs
