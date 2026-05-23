from pathlib import Path

import pytest
import pandas as pd

from actual_to_wealthfolio.config import RemapConfig, RemapEntry
from actual_to_wealthfolio.converter import Converter


def _write_actual_csv(path: Path, rows: list[dict[str, object]]) -> None:
    pd.DataFrame(rows).to_csv(path, index=False)


def _standard_config() -> RemapConfig:
    """Return the standard remap config used across converter tests."""
    return RemapConfig(
        remaps=[
            RemapEntry(from_category="dividends", to_type="Dividend", trade=True),
            RemapEntry(from_category="interests", to_type="Interest", trade=False),
            RemapEntry(from_category="income taxes", to_type="Tax", trade=False),
            RemapEntry(from_category="banking fees", to_type="Fee", trade=False),
            RemapEntry(from_category="stock purchases", to_type="Buy", trade=True),
            RemapEntry(from_category="stock sales", to_type="Sell", trade=True),
        ]
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

    outputs = Converter(remap_config=_standard_config()).convert()

    output_key = "main:main-account"
    assert output_key in outputs
    output_path = outputs[output_key]
    assert output_path == Path("output/wealthfolio-main-account-main.csv")
    assert output_path.exists()


def test_convert_remaps_trade_category_to_buy_and_extracts_trade_fields(
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

    outputs = Converter(remap_config=_standard_config()).convert()
    output_path = outputs["investing:brokerage"]
    converted = pd.read_csv(output_path)

    assert converted.loc[0, "Type"] == "Buy"
    assert converted.loc[0, "Symbol"] == "AAPL"
    assert pd.to_numeric(converted.loc[0, "Quantity"]) == pytest.approx(3.0)
    assert pd.to_numeric(converted.loc[0, "Unit_Price"]) == pytest.approx(150.0)


def test_convert_remaps_stock_sales_to_sell(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
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

    outputs = Converter(remap_config=_standard_config()).convert()
    output_path = outputs["investing:brokerage"]
    converted = pd.read_csv(output_path)

    assert converted.loc[0, "Type"] == "Sell"
    assert converted.loc[0, "Symbol"] == "ERIC-B"
    assert pd.to_numeric(converted.loc[0, "Quantity"]) == pytest.approx(50.0)
    assert pd.to_numeric(converted.loc[0, "Unit_Price"]) == pytest.approx(10.0)


def test_convert_raises_when_no_budget_input_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "input").mkdir()

    with pytest.raises(FileNotFoundError, match=r"expected actual-<budget-file>\.csv"):
        Converter(remap_config=_standard_config()).convert()


def test_convert_uses_custom_category_remap(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Converter respects a RemapConfig with a user-defined remap entry."""
    monkeypatch.chdir(tmp_path)
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    _write_actual_csv(
        input_dir / "actual-main.csv",
        [
            {
                "Date": "2026-04-01",
                "Account": "Savings",
                "Payee": "Bank",
                "Notes": "interest payment",
                "Category": "interest income",
                "Amount": 10.0,
            }
        ],
    )

    custom_config = RemapConfig(remaps=[RemapEntry(from_category="interest income", to_type="Interest", trade=False)])
    outputs = Converter(remap_config=custom_config).convert()
    output_path = outputs["main:savings"]
    converted = pd.read_csv(output_path)

    assert converted.loc[0, "Type"] == "Interest"
