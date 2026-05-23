from pathlib import Path

import pytest
import yaml

from actual_to_wealthfolio.config import RemapConfig, RemapEntry, load_config


def _write_yaml(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def _full_yaml() -> str:
    return """\
- from: dividends
  to: Dividend
  trade: true

- from: interests
  to: Interest
  trade: false

- from: stock purchases
  to: Buy
  trade: true
"""


def test_load_config_raises_when_no_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="config.yaml"):
        load_config(tmp_path / "config.yaml")


def test_load_config_reads_entries(tmp_path: Path) -> None:
    _write_yaml(tmp_path / "config.yaml", _full_yaml())

    config = load_config(tmp_path / "config.yaml")

    assert len(config.remaps) == 3
    assert config.remaps[0] == RemapEntry(from_category="dividends", to_type="Dividend", trade=True)
    assert config.remaps[1] == RemapEntry(from_category="interests", to_type="Interest", trade=False)
    assert config.remaps[2] == RemapEntry(from_category="stock purchases", to_type="Buy", trade=True)


def test_load_config_allows_empty_remaps(tmp_path: Path) -> None:
    _write_yaml(tmp_path / "config.yaml", "[]\n")

    config = load_config(tmp_path / "config.yaml")

    assert config.remaps == []


def test_load_config_raises_on_non_sequence_top_level(tmp_path: Path) -> None:
    _write_yaml(tmp_path / "config.yaml", "other_key: value\n")

    with pytest.raises(ValueError, match="sequence"):
        load_config(tmp_path / "config.yaml")


def test_load_config_raises_on_missing_from_field(tmp_path: Path) -> None:
    _write_yaml(
        tmp_path / "config.yaml",
        """\
- to: Dividend
  trade: true
""",
    )

    with pytest.raises(ValueError, match="'from'"):
        load_config(tmp_path / "config.yaml")


def test_load_config_raises_on_missing_to_field(tmp_path: Path) -> None:
    _write_yaml(
        tmp_path / "config.yaml",
        """\
- from: dividends
  trade: true
""",
    )

    with pytest.raises(ValueError, match="'to'"):
        load_config(tmp_path / "config.yaml")


def test_load_config_raises_on_missing_trade_field(tmp_path: Path) -> None:
    _write_yaml(
        tmp_path / "config.yaml",
        """\
- from: dividends
  to: Dividend
""",
    )

    with pytest.raises(ValueError, match="'trade'"):
        load_config(tmp_path / "config.yaml")


def test_load_config_raises_on_non_bool_trade(tmp_path: Path) -> None:
    _write_yaml(
        tmp_path / "config.yaml",
        """\
- from: dividends
  to: Dividend
  trade: yes_please
""",
    )

    with pytest.raises(ValueError, match="'trade'"):
        load_config(tmp_path / "config.yaml")


def test_load_config_raises_on_invalid_yaml(tmp_path: Path) -> None:
    (tmp_path / "config.yaml").write_text("key: [unclosed\n", encoding="utf-8")

    with pytest.raises(yaml.YAMLError):
        load_config(tmp_path / "config.yaml")


def test_remap_config_stores_entries() -> None:
    entry = RemapEntry(from_category="dividends", to_type="Dividend", trade=True)
    config = RemapConfig(remaps=[entry])

    assert config.remaps[0].from_category == "dividends"
    assert config.remaps[0].to_type == "Dividend"
    assert config.remaps[0].trade is True
