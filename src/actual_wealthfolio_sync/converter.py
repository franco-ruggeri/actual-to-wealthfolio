import pandas as pd


class Converter:
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

    def _to_wealthfolio_columns(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()
        data["Quantity"] = None
        data["Unit_Price"] = None
        data = data[["Account", "Date", "Payee", "Notes", "Category", "Amount", "Quantity", "Unit_Price"]]
        data = data.rename(columns={"Payee": "Symbol", "Notes": "Comment", "Category": "Type"})
        return data

    def convert_dataframe(self, data: pd.DataFrame) -> pd.DataFrame:
        converted_data = self._filter_split_rows(data)
        converted_data = self._update_empty_categories(converted_data)
        converted_data = self._normalize_categories(converted_data)
        return self._to_wealthfolio_columns(converted_data)
