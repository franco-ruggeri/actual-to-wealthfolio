from dataclasses import dataclass
from enum import Enum


class AccountType(str, Enum):
    CASH = "cash"
    SECURITIES = "securities"


@dataclass(frozen=True)
class Account:
    name: str
    account_type: AccountType

    @classmethod
    def from_csv_row(cls, account_name: str, account_type: str) -> "Account":
        return cls(name=account_name, account_type=AccountType(account_type))
