from dataclasses import dataclass
from pathlib import Path

import yaml

DEFAULT_CONFIG_PATH = Path("input/config.yaml")


@dataclass
class Entry:
    from_category: str
    to_type: str
    trade: bool


class Config:
    def __init__(self, config_path: Path = DEFAULT_CONFIG_PATH) -> None:
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_path) as f:
            raw = yaml.safe_load(f)

        if not isinstance(raw, list):
            raise ValueError(f"{config_path}: must be a YAML sequence at the top level")

        remaps: list[Entry] = []
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

            remaps.append(Entry(from_category=from_category, to_type=to_type, trade=trade))

        self._remaps = remaps

    def get_remaps(self) -> list[Entry]:
        return self._remaps
