from dataclasses import dataclass
from pathlib import Path

import yaml

DEFAULT_CONFIG_PATH = Path("input/config.yaml")


@dataclass
class RemapEntry:
    """A single category remap rule."""

    from_category: str  # Actual Budget category name (matched case-insensitively).
    to_type: str  # Wealthfolio transaction type.
    trade: bool  # Whether to extract Quantity, Unit_Price, and Symbol for this category.


@dataclass
class RemapConfig:
    """All remap rules loaded from config.yaml."""

    remaps: list[RemapEntry]


def load_config(config_path: Path = DEFAULT_CONFIG_PATH) -> RemapConfig:
    """Load remap configuration from a YAML file.

    Raises:
        FileNotFoundError: if config_path does not exist.
        ValueError: if the file is missing required fields or contains type errors.
        yaml.YAMLError: if the file is not valid YAML.
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path) as f:
        raw = yaml.safe_load(f)

    if not isinstance(raw, list):
        raise ValueError(f"{config_path}: must be a YAML sequence at the top level")

    remaps: list[RemapEntry] = []
    for i, item in enumerate(raw):
        label = f"{config_path}: [{i}]"

        if not isinstance(item, dict):
            raise ValueError(f"{label}: each entry must be a YAML mapping")

        from_category = item.get("from")
        if from_category is None:
            raise ValueError(f"{label}: missing required field 'from'")
        if not isinstance(from_category, str):
            raise ValueError(f"{label}: 'from' must be a string")

        to_type = item.get("to")
        if to_type is None:
            raise ValueError(f"{label}: missing required field 'to'")
        if not isinstance(to_type, str):
            raise ValueError(f"{label}: 'to' must be a string")

        trade = item.get("trade")
        if trade is None:
            raise ValueError(f"{label}: missing required field 'trade'")
        if not isinstance(trade, bool):
            raise ValueError(f"{label}: 'trade' must be a boolean")

        remaps.append(RemapEntry(from_category=from_category, to_type=to_type, trade=trade))

    return RemapConfig(remaps=remaps)
