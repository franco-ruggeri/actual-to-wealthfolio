from pathlib import Path

import pandas as pd

from actual_wealthfolio_sync.models import Account, AccountType


class DataLoader:
    def __init__(self, data_dir: Path = Path("data")) -> None:
        self.data_dir = data_dir

    def load_accounts(self) -> dict[str, Account]:
        accounts_path = self.data_dir / "wealthfolio-accounts.csv"
        if not accounts_path.exists():
            raise FileNotFoundError(f"Accounts file not found: {accounts_path}")

        df = pd.read_csv(accounts_path)
        required_columns = {"name", "accountType"}
        missing_columns = required_columns - set(df.columns)
        if missing_columns:
            missing_columns_text = ", ".join(sorted(missing_columns))
            raise ValueError(f"Accounts file missing required columns: {missing_columns_text}")

        accounts = {}
        for row in df.itertuples(index=False):
            account = Account.from_csv_row(str(row.name), str(row.accountType))
            accounts[account.name] = account

        return accounts

    def load_actual_data(self) -> pd.DataFrame:
        actual_path = self.data_dir / "actual-transactions.csv"
        if not actual_path.exists():
            raise FileNotFoundError(f"Actual data file not found: {actual_path}")

        return pd.read_csv(actual_path)

    def load_wealthfolio_data(self) -> pd.DataFrame:
        wealthfolio_path = self.data_dir / "wealthfolio-activities.csv"
        if not wealthfolio_path.exists():
            raise FileNotFoundError(f"Wealthfolio data file not found: {wealthfolio_path}")

        return pd.read_csv(wealthfolio_path)

    def get_cash_accounts(self, accounts: dict[str, Account]) -> list[str]:
        return [name for name, account in accounts.items() if account.account_type == AccountType.CASH]

    def get_securities_accounts(self, accounts: dict[str, Account]) -> list[str]:
        return [name for name, account in accounts.items() if account.account_type == AccountType.SECURITIES]
