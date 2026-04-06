from pathlib import Path

import pytest
import pandas as pd

from actual_to_wealthfolio.converter import Converter


def _write_actual_csv(path: Path, rows: list[dict[str, object]]) -> None:
    pd.DataFrame(rows).to_csv(path, index=False)


def test_convert_writes_output_file_for_budget_input(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    _write_actual_csv(
        data_dir / "actual-main.csv",
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

    outputs = Converter().convert()

    output_key = "main:main-account"
    assert output_key in outputs
    output_path = outputs[output_key]
    assert output_path == Path("output/wealthfolio-main-account-main.csv")
    assert output_path.exists()


def test_convert_remaps_trade_category_to_buy_and_extracts_trade_fields(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    _write_actual_csv(
        data_dir / "actual-investing.csv",
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

    outputs = Converter().convert()
    output_path = outputs["investing:brokerage"]
    converted = pd.read_csv(output_path)

    assert converted.loc[0, "Type"] == "Buy"
    assert converted.loc[0, "Symbol"] == "AAPL"
    assert pd.to_numeric(converted.loc[0, "Quantity"]) == pytest.approx(3.0)
    assert pd.to_numeric(converted.loc[0, "Unit_Price"]) == pytest.approx(150.0)


def test_convert_remaps_stock_purchases_subcategory_to_buy(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Categories that start with 'Stock purchases' (e.g. 'Stock purchases - ERIC-B') are treated as Buy."""
    monkeypatch.chdir(tmp_path)
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    _write_actual_csv(
        data_dir / "actual-investing.csv",
        [
            {
                "Date": "2026-03-15",
                "Account": "Brokerage",
                "Payee": "ERIC-B",
                "Notes": "Quantity: 100; Unit price: 9.50",
                "Category": "Stock purchases - ERIC-B",
                "Amount": -950.0,
            }
        ],
    )

    outputs = Converter().convert()
    output_path = outputs["investing:brokerage"]
    converted = pd.read_csv(output_path)

    assert converted.loc[0, "Type"] == "Buy"
    assert converted.loc[0, "Symbol"] == "ERIC-B"
    assert pd.to_numeric(converted.loc[0, "Quantity"]) == pytest.approx(100.0)
    assert pd.to_numeric(converted.loc[0, "Unit_Price"]) == pytest.approx(9.50)


def test_convert_remaps_stock_sales_subcategory_to_sell(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Categories that start with 'Stock sales' (e.g. 'Stock sales - ERIC-B') are treated as Sell."""
    monkeypatch.chdir(tmp_path)
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    _write_actual_csv(
        data_dir / "actual-investing.csv",
        [
            {
                "Date": "2026-03-20",
                "Account": "Brokerage",
                "Payee": "ERIC-B",
                "Notes": "Quantity: 50; Unit price: 10.00",
                "Category": "Stock sales - ERIC-B",
                "Amount": 500.0,
            }
        ],
    )

    outputs = Converter().convert()
    output_path = outputs["investing:brokerage"]
    converted = pd.read_csv(output_path)

    assert converted.loc[0, "Type"] == "Sell"
    assert converted.loc[0, "Symbol"] == "ERIC-B"
    assert pd.to_numeric(converted.loc[0, "Quantity"]) == pytest.approx(50.0)
    assert pd.to_numeric(converted.loc[0, "Unit_Price"]) == pytest.approx(10.0)


def test_convert_raises_when_no_budget_input_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "data").mkdir()

    with pytest.raises(FileNotFoundError, match=r"expected actual-<budget-file>\.csv"):
        Converter().convert()
