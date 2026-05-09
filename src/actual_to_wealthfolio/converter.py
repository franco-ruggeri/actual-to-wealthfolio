from pathlib import Path
import re

import pandas as pd


class Converter:
    INPUT_DIR = Path("input")
    OUTPUT_DIR = Path("output")
    DUPLICATE_AMOUNT_EPSILON = 0.000001
    # Exact-match category → Wealthfolio type mappings.
    CATEGORY_RENAMES = {
        "dividends": "Dividend",
        "interests": "Interest",
        "income taxes": "Tax",
        "banking fees": "Fee",
    }
    # Prefix-match category → Wealthfolio type mappings.
    # Any category whose lowercased value starts with one of these prefixes is mapped to the
    # corresponding type.  This allows sub-categories such as "Stock purchases - ERIC-B".
    CATEGORY_PREFIX_RENAMES = {
        "stock purchases": "Buy",
        "stock sales": "Sell",
    }
    KNOWN_CATEGORIES = {
        "transfer in",
        "transfer out",
        "deposit",
        "withdrawal",
        "dividends",
        "interests",
        "income taxes",
        "banking fees",
    }
    # Prefixes that identify "stock purchases" and "stock sales" family categories.
    TRADE_CATEGORY_PREFIXES = {"stock purchases", "stock sales"}
    # Exact-match categories that are also trade categories.
    TRADE_CATEGORY_NAMES = {"dividends"}

    def _is_trade_category(self, normalized: pd.Series) -> pd.Series:
        """Return a boolean Series that is True for any trade category.

        Exact members of TRADE_CATEGORY_NAMES are matched directly.
        Categories whose lowercased value *starts with* any prefix in
        TRADE_CATEGORY_PREFIXES are also matched (e.g. "stock purchases - ERIC-B").
        """
        exact_match = normalized.isin(self.TRADE_CATEGORY_NAMES)
        prefix_match = normalized.apply(lambda v: any(v.startswith(prefix) for prefix in self.TRADE_CATEGORY_PREFIXES))
        return exact_match | prefix_match

    def _is_known_category(self, normalized: pd.Series) -> pd.Series:
        """Return a boolean Series that is True for any known/recognised category.

        Exact members of KNOWN_CATEGORIES are matched directly.
        Any category that starts with a prefix in CATEGORY_PREFIX_RENAMES is also
        considered known (e.g. "stock purchases - ERIC-B").
        """
        exact_match = normalized.isin(self.KNOWN_CATEGORIES)
        prefix_match = normalized.apply(lambda v: any(v.startswith(prefix) for prefix in self.CATEGORY_PREFIX_RENAMES))
        return exact_match | prefix_match

    def _map_category_to_type(self, category_lower: str) -> str | None:
        """Map a single normalised category string to its Wealthfolio type, or None."""
        if category_lower in self.CATEGORY_RENAMES:
            return self.CATEGORY_RENAMES[category_lower]
        for prefix, type_name in self.CATEGORY_PREFIX_RENAMES.items():
            if category_lower.startswith(prefix):
                return type_name
        return None

    def _get_budget_file_input_paths(self) -> list[tuple[str, Path]]:
        input_paths: list[tuple[str, Path]] = []
        for path in sorted(self.INPUT_DIR.glob("actual-*.csv")):
            budget_file_name = path.stem.removeprefix("actual-").strip()
            if not budget_file_name or budget_file_name == path.stem:
                continue
            input_paths.append((budget_file_name, path))

        if not input_paths:
            raise FileNotFoundError(
                f"No budget input files found in {self.INPUT_DIR} (expected actual-<budget-file>.csv)"
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

    def _extract_trade_values_from_notes(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()
        notes = data["Notes"].fillna("").astype(str)
        normalized_category = data["Category"].fillna("").astype(str).str.strip().str.lower()
        is_trade_category = self._is_trade_category(normalized_category)
        quantity = notes.str.extract(r"(?i)quantity\s*[:=]\s*(-?\d+(?:\.\d+)?)", expand=False)
        unit_price = notes.str.extract(r"(?i)unit[_\s]*price\s*[:=]\s*(-?\d+(?:\.\d+)?)", expand=False)
        data["Quantity"] = quantity.where(is_trade_category)
        data["Unit_Price"] = unit_price.where(is_trade_category)
        return data

    def _map_categories_to_type(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()
        normalized_category = data["Category"].fillna("").astype(str).str.strip().str.lower()
        mapped = normalized_category.apply(self._map_category_to_type)
        data["Category"] = mapped.where(mapped.notna(), data["Category"])
        return data

    def _set_symbol_from_payee(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()
        normalized_category = data["Category"].fillna("").astype(str).str.strip().str.lower()
        use_payee_as_symbol = self._is_trade_category(normalized_category)
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
        converted_data = self._extract_trade_values_from_notes(converted_data)
        converted_data = self._normalize_categories(converted_data)
        converted_data = self._set_symbol_from_payee(converted_data)
        converted_data = self._map_categories_to_type(converted_data)
        converted_data = self._drop_zero_amount_rows(converted_data)
        converted_data = self._to_wealthfolio_columns(converted_data)
        return self._deduplicate_same_day_amount_category(converted_data)

    def _deduplicate_same_day_amount_category(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()
        duplicate_group = ["Date", "Type", "Amount"]
        duplicate_index = data.groupby(duplicate_group).cumcount()
        data["Amount"] = data["Amount"] + (duplicate_index * self.DUPLICATE_AMOUNT_EPSILON)
        return data

    def convert(self) -> dict[str, Path]:
        budget_file_input_paths = self._get_budget_file_input_paths()
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

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
                output_path = self.OUTPUT_DIR / f"wealthfolio-{safe_name}-{safe_budget_file_name}.csv"
                converted_data.to_csv(output_path, index=False)
                outputs[f"{budget_file_name}:{safe_name}"] = output_path

        return outputs
