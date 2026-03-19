from pathlib import Path

import pandas as pd


class Converter:
    def _filter_split_rows(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()

        data = data[~data["Notes"].str.match(r"^\(SPLIT INTO \d+\) ", na=False)]

        is_split = data["Notes"].str.match(r"^\(SPLIT \d+ OF \d+\) ", na=False)

        data.loc[is_split, "Amount"] = data.loc[is_split, "Split_Amount"]

        data["Notes"] = data["Notes"].str.replace(r"^\(SPLIT \d+ OF \d+\) ", "", regex=True)

        return data

    def _validate_notes_format(self, data: pd.DataFrame) -> None:
        categories_requiring_format = ["Stock purchases", "Dividends"]
        rows_to_validate = data[data["Category"].isin(categories_requiring_format)]

        pattern = r"^\(QUANTITY=\d+\.?\d*, UNIT_PRICE=\d+\.?\d*\)$"

        invalid_rows = rows_to_validate[~rows_to_validate["Notes"].str.match(pattern, na=False)]

        if not invalid_rows.empty:
            invalid_data = invalid_rows[["Category", "Notes"]].to_dict("records")
            raise ValueError(
                f"Invalid Notes format for Stock purchases/Dividends. "
                f"Expected format: (QUANTITY=X, UNIT_PRICE=Y). "
                f"Found: {invalid_data}"
            )

    def _update_empty_categories(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()

        empty_category = data["Category"].isna() | (data["Category"] == "")

        data.loc[empty_category & (data["Amount"] > 0), "Category"] = "Transfer in"
        data.loc[empty_category & (data["Amount"] < 0), "Category"] = "Transfer out"

        return data

    def _normalize_categories(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()

        allowed_categories = [
            "Stock purchases",
            "Stock sales",
            "Transfer in",
            "Transfer out",
            "Dividends",
            "Interests",
            "Income taxes",
            "Banking fees",
        ]

        non_standard = ~data["Category"].isin(allowed_categories)

        data.loc[non_standard & (data["Amount"] < 0), "Category"] = "Withdrawal"
        data.loc[non_standard & (data["Amount"] > 0), "Category"] = "Deposit"

        return data

    def convert(self, input_path: str | Path, output_path: str | Path) -> None:
        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        data = pd.read_csv(input_path)

        converted_data = self._filter_split_rows(data)
        converted_data = self._update_empty_categories(converted_data)
        converted_data = self._normalize_categories(converted_data)
        self._validate_notes_format(converted_data)

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        converted_data.to_csv(output_path, index=False)
