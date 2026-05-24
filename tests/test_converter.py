from pathlib import Path

import pytest
import pandas as pd

from actual_to_wealthfolio.converter import Converter


def _write_actual_csv(path: Path, rows: list[dict[str, object]]) -> None:
    pd.DataFrame(rows).to_csv(path, index=False)


def _write_trade_config(path: Path, categories: list[str]) -> None:
    lines = [f"- {c}" for c in categories]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _setup_config(tmp_path: Path) -> None:
    _write_trade_config(
        tmp_path / "input" / "config.yaml",
        ["stock purchases", "stock sales"],
    )


def test_convert_writes_output_file_for_budget_input(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    _write_actual_csv(
        input_dir / "actual-main.csv",
        [
            {
                "Date": "2026-01-10",
                "Account": "Main Account",
                "Payee": "Local Store",
                "Notes": "weekly groceries",
                "Category": "Groceries",
                "Amount": -42.5,
            }
        ],
    )

    _setup_config(tmp_path)
    outputs = Converter().convert()

    output_key = "main:main-account"
    assert output_key in outputs
    output_path = outputs[output_key]
    assert output_path == Path("output/wealthfolio-main-account-main.csv")
    assert output_path.exists()


def test_convert_negative_trade_amount_becomes_buy_and_extracts_trade_fields(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    _write_actual_csv(
        input_dir / "actual-investing.csv",
        [
            {
                "Date": "2026-01-11",
                "Account": "Brokerage",
                "Payee": "AAPL",
                "Notes": "Quantity: 3; Unit price: 150.00",
                "Category": "Stock purchases",
                "Amount": -450.0,
            }
        ],
    )

    _setup_config(tmp_path)
    outputs = Converter().convert()
    output_path = outputs["investing:brokerage"]
    converted = pd.read_csv(output_path)

    assert converted.loc[0, "Type"] == "Buy"
    assert converted.loc[0, "Symbol"] == "AAPL"
    assert pd.to_numeric(converted.loc[0, "Quantity"]) == pytest.approx(3.0)
    assert pd.to_numeric(converted.loc[0, "Unit_Price"]) == pytest.approx(150.0)


def test_convert_positive_trade_amount_becomes_sell(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    _write_actual_csv(
        input_dir / "actual-investing.csv",
        [
            {
                "Date": "2026-03-20",
                "Account": "Brokerage",
                "Payee": "ERIC-B",
                "Notes": "Quantity: 50; Unit price: 10.00",
                "Category": "Stock sales",
                "Amount": 500.0,
            }
        ],
    )

    _setup_config(tmp_path)
    outputs = Converter().convert()
    output_path = outputs["investing:brokerage"]
    converted = pd.read_csv(output_path)

    assert converted.loc[0, "Type"] == "Sell"
    assert converted.loc[0, "Symbol"] == "ERIC-B"
    assert pd.to_numeric(converted.loc[0, "Quantity"]) == pytest.approx(50.0)
    assert pd.to_numeric(converted.loc[0, "Unit_Price"]) == pytest.approx(10.0)


def test_convert_raises_when_no_budget_input_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "input").mkdir()

    _setup_config(tmp_path)
    with pytest.raises(FileNotFoundError, match=r"expected actual-<budget-file>\.csv"):
        Converter().convert()


def test_convert_non_remapped_positive_amount_becomes_deposit(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A positive amount in a non-trade category (e.g. a tax return) is classified as Deposit."""
    monkeypatch.chdir(tmp_path)
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    _write_actual_csv(
        input_dir / "actual-main.csv",
        [
            {
                "Date": "2026-04-15",
                "Account": "Savings",
                "Payee": "Tax Authority",
                "Notes": "income tax return",
                "Category": "income taxes",
                "Amount": 350.0,
            }
        ],
    )

    _setup_config(tmp_path)
    outputs = Converter().convert()
    output_path = outputs["main:savings"]
    converted = pd.read_csv(output_path)

    assert converted.loc[0, "Type"] == "Deposit"


def test_convert_non_remapped_negative_amount_becomes_withdrawal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A negative amount in a non-trade category (e.g. a tax payment) is classified as Withdrawal."""
    monkeypatch.chdir(tmp_path)
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    _write_actual_csv(
        input_dir / "actual-main.csv",
        [
            {
                "Date": "2026-04-15",
                "Account": "Savings",
                "Payee": "Tax Authority",
                "Notes": "income tax payment",
                "Category": "income taxes",
                "Amount": -500.0,
            }
        ],
    )

    _setup_config(tmp_path)
    outputs = Converter().convert()
    output_path = outputs["main:savings"]
    converted = pd.read_csv(output_path)

    assert converted.loc[0, "Type"] == "Withdrawal"
