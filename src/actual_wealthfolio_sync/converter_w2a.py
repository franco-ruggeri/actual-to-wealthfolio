from pathlib import Path
import re

import pandas as pd


class ConverterW2A:
    INPUT_PATH = Path("data/wealthfolio-activities.csv")
    OUTPUT_DIR = Path("output")
    REQUIRED_WEALTHFOLIO_COLUMNS = ["accountName", "date", "assetSymbol", "comment", "activityType", "amount"]
    ACTUAL_COLUMNS = ["Account", "Date", "Payee", "Notes", "Category", "Amount"]
    OUTPUT_COLUMNS = ["Date", "Payee", "Notes", "Category", "Amount"]
    CATEGORY_MAPPING = {"SELL": "Stock sales", "BUY": "Stock purchases"}
    FEE_CATEGORY = "Banking fees"

    def _round_to_two_decimals(self, amount: float) -> float:
        return round(amount, 2)

    def _first_existing_column(self, data: pd.DataFrame, candidates: list[str]) -> str | None:
        for candidate in candidates:
            if candidate in data.columns:
                return candidate
        return None

    def _load_wealthfolio_data(self) -> pd.DataFrame:
        if not self.INPUT_PATH.exists():
            raise FileNotFoundError(f"Wealthfolio data file not found: {self.INPUT_PATH}")
        return pd.read_csv(self.INPUT_PATH)

    def _sanitize_account_name(self, account_name: str) -> str:
        kebab = re.sub(r"[^a-z0-9]+", "-", account_name.lower())
        return kebab.strip("-")

    def _to_actual_columns(self, data: pd.DataFrame) -> pd.DataFrame:
        missing_columns = [column for column in self.REQUIRED_WEALTHFOLIO_COLUMNS if column not in data.columns]
        if missing_columns:
            missing_columns_text = ", ".join(sorted(missing_columns))
            raise ValueError(f"Wealthfolio activities file missing required columns: {missing_columns_text}")

        actual_data = data[["accountName", "date", "assetSymbol", "comment", "activityType", "amount"]].rename(
            columns={
                "accountName": "Account",
                "date": "Date",
                "assetSymbol": "Payee",
                "comment": "Notes",
                "activityType": "Category",
                "amount": "Amount",
            }
        )

        quantity_column = self._first_existing_column(data, ["quantity", "Quantity"])
        unit_price_column = self._first_existing_column(data, ["unitPrice", "unit_price", "UnitPrice", "Unit_Price"])
        fee_column = self._first_existing_column(data, ["fee", "Fee"])
        notes = actual_data["Notes"].fillna("").astype(str).str.strip()
        quantity_notes = pd.Series("", index=actual_data.index)
        unit_price_notes = pd.Series("", index=actual_data.index)
        fee_amounts = pd.Series(0.0, index=actual_data.index)

        if quantity_column:
            quantity_values = data[quantity_column]
            quantity_text = quantity_values.where(~quantity_values.isna(), "").astype(str).str.strip()
            quantity_notes = quantity_text.map(lambda value: f"Quantity: {value}" if value else "")

        if unit_price_column:
            unit_price_values = data[unit_price_column]
            unit_price_text = unit_price_values.where(~unit_price_values.isna(), "").astype(str).str.strip()
            unit_price_notes = unit_price_text.map(lambda value: f"Unit price: {value}" if value else "")

        if fee_column:
            fee_amounts = pd.to_numeric(data[fee_column], errors="coerce").fillna(0.0)

        detail_notes = []
        for quantity_note, unit_price_note in zip(quantity_notes, unit_price_notes, strict=False):
            parts = [part for part in (quantity_note, unit_price_note) if part]
            detail_notes.append("; ".join(parts))

        actual_data["Notes"] = [
            f"{note} | {detail_note}" if note and detail_note else note or detail_note
            for note, detail_note in zip(notes, detail_notes, strict=False)
        ]

        normalized_category = actual_data["Category"].astype(str).str.strip().str.upper()
        allowed_categories = normalized_category.isin(self.CATEGORY_MAPPING)
        actual_data = actual_data[allowed_categories].copy()
        actual_data["Category"] = normalized_category[allowed_categories].map(self.CATEGORY_MAPPING)
        purchase_rows = actual_data["Category"] == "Stock purchases"
        actual_data.loc[purchase_rows, "Amount"] = -actual_data.loc[purchase_rows, "Amount"].abs()

        fee_amounts = fee_amounts[allowed_categories]
        fee_rows = actual_data[fee_amounts > 0].copy()
        if not fee_rows.empty:
            fee_rows["Category"] = self.FEE_CATEGORY
            fee_rows["Amount"] = -fee_amounts[fee_amounts > 0].abs()
            actual_data = pd.concat([actual_data, fee_rows], ignore_index=True)

        actual_data["Amount"] = pd.to_numeric(actual_data["Amount"], errors="coerce").fillna(0.0)
        actual_data["Amount"] = actual_data["Amount"].map(self._round_to_two_decimals)

        return actual_data[self.ACTUAL_COLUMNS]

    def convert(self) -> dict[str, Path]:
        wealthfolio_data = self._load_wealthfolio_data()
        actual_data = self._to_actual_columns(wealthfolio_data)
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        outputs: dict[str, Path] = {}
        account_names = sorted(actual_data["Account"].dropna().astype(str).str.strip().unique())
        for account_name in account_names:
            if not account_name:
                continue

            account_data = actual_data[actual_data["Account"] == account_name].copy()
            if account_data.empty:
                continue

            safe_name = self._sanitize_account_name(account_name)
            output_path = self.OUTPUT_DIR / f"actual-{safe_name}.csv"
            account_data[self.OUTPUT_COLUMNS].to_csv(output_path, index=False)
            outputs[safe_name] = output_path

        return outputs
