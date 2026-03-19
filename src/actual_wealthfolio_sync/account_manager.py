from pathlib import Path

import pandas as pd


class AccountManager:
    ACCOUNTS_PATH = Path("data/wealthfolio-accounts.csv")

    def load_accounts(self) -> dict[str, str]:
        if not self.ACCOUNTS_PATH.exists():
            raise FileNotFoundError(f"Accounts file not found: {self.ACCOUNTS_PATH}")

        data = pd.read_csv(self.ACCOUNTS_PATH)
        required_columns = {"name", "accountType"}
        missing_columns = required_columns - set(data.columns)
        if missing_columns:
            missing_columns_text = ", ".join(sorted(missing_columns))
            raise ValueError(f"Accounts file missing required columns: {missing_columns_text}")

        result: dict[str, str] = {}
        for row in data.itertuples(index=False):
            result[str(row.name)] = str(row.accountType)

        return result

    def get_cash_accounts(self) -> list[str]:
        accounts = self.load_accounts()
        return [name for name, account_type in accounts.items() if account_type == "cash"]

    def get_securities_accounts(self) -> list[str]:
        accounts = self.load_accounts()
        return [name for name, account_type in accounts.items() if account_type == "securities"]
