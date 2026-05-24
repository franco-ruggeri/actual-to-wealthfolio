from pathlib import Path

import pytest
import yaml

from actual_to_wealthfolio.converter import Converter


def _write_yaml(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def test_converter_raises_when_no_config_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "input").mkdir()
    with pytest.raises(FileNotFoundError, match="config.yaml"):
        Converter()


def test_converter_reads_stock_categories(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "input").mkdir()
    _write_yaml(tmp_path / "input" / "config.yaml", "- stock purchases\n- stock sales\n")

    converter = Converter()

    assert converter._stock_set == {"stock purchases", "stock sales"}


def test_converter_allows_empty_stock_categories(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "input").mkdir()
    _write_yaml(tmp_path / "input" / "config.yaml", "[]\n")

    converter = Converter()

    assert converter._stock_set == set()


def test_converter_raises_on_non_sequence_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "input").mkdir()
    _write_yaml(tmp_path / "input" / "config.yaml", "other_key: value\n")

    with pytest.raises(ValueError, match="sequence"):
        Converter()


def test_converter_raises_on_non_string_config_entry(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "input").mkdir()
    _write_yaml(tmp_path / "input" / "config.yaml", "- 42\n")

    with pytest.raises(ValueError, match="string"):
        Converter()


def test_converter_raises_on_invalid_yaml(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "input").mkdir()
    (tmp_path / "input" / "config.yaml").write_text("key: [unclosed\n", encoding="utf-8")

    with pytest.raises(yaml.YAMLError):
        Converter()
