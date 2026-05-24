from pathlib import Path

import pytest
import yaml

from actual_to_wealthfolio.config import Config, Entry


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


def test_config_raises_when_no_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "input").mkdir()
    with pytest.raises(FileNotFoundError, match="config.yaml"):
        Config()


def test_config_reads_entries(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "input").mkdir()
    _write_yaml(tmp_path / "input" / "config.yaml", _full_yaml())

    config = Config()

    assert len(config.get_remaps()) == 3
    assert config.get_remaps()[0] == Entry(from_category="dividends", to_type="Dividend", trade=True)
    assert config.get_remaps()[1] == Entry(from_category="interests", to_type="Interest", trade=False)
    assert config.get_remaps()[2] == Entry(from_category="stock purchases", to_type="Buy", trade=True)


def test_config_allows_empty_remaps(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "input").mkdir()
    _write_yaml(tmp_path / "input" / "config.yaml", "[]\n")

    config = Config()

    assert config.get_remaps() == []


def test_config_raises_on_non_sequence_top_level(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "input").mkdir()
    _write_yaml(tmp_path / "input" / "config.yaml", "other_key: value\n")

    with pytest.raises(ValueError, match="sequence"):
        Config()


def test_config_raises_on_missing_from_field(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "input").mkdir()
    _write_yaml(
        tmp_path / "input" / "config.yaml",
        """\
- to: Dividend
  trade: true
""",
    )

    with pytest.raises(ValueError, match="'from'"):
        Config()


def test_config_raises_on_missing_to_field(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "input").mkdir()
    _write_yaml(
        tmp_path / "input" / "config.yaml",
        """\
- from: dividends
  trade: true
""",
    )

    with pytest.raises(ValueError, match="'to'"):
        Config()


def test_config_raises_on_missing_trade_field(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "input").mkdir()
    _write_yaml(
        tmp_path / "input" / "config.yaml",
        """\
- from: dividends
  to: Dividend
""",
    )

    with pytest.raises(ValueError, match="'trade'"):
        Config()


def test_config_raises_on_non_bool_trade(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "input").mkdir()
    _write_yaml(
        tmp_path / "input" / "config.yaml",
        """\
- from: dividends
  to: Dividend
  trade: yes_please
""",
    )

    with pytest.raises(ValueError, match="'trade'"):
        Config()


def test_config_raises_on_invalid_yaml(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "input").mkdir()
    (tmp_path / "input" / "config.yaml").write_text("key: [unclosed\n", encoding="utf-8")

    with pytest.raises(yaml.YAMLError):
        Config()
