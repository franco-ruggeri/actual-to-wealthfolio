import pandas as pd

from actual_wealthfolio_sync.converter import Converter
from actual_wealthfolio_sync.models import Account


class DataProcessor:
    def __init__(self, accounts: dict[str, Account]) -> None:
        self.accounts = accounts
        self.converter = Converter()

    def process_actual_by_account(
        self, actual_df: pd.DataFrame, wealthfolio_df: pd.DataFrame, securities_accounts: list[str]
    ) -> dict[str, pd.DataFrame]:
        result = {}
        for account_name in securities_accounts:
            account_data = wealthfolio_df[wealthfolio_df["Account"] == account_name].copy()
            result[account_name] = account_data

        return result

    def process_wealthfolio_cash(self, actual_df: pd.DataFrame, cash_accounts: list[str]) -> pd.DataFrame:
        cash_data = actual_df[actual_df["Account"].isin(cash_accounts)].copy()
        return self.converter.convert_dataframe(cash_data)
