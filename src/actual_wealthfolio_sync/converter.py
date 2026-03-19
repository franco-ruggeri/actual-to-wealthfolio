from pathlib import Path

import pandas as pd


class Converter:
    def __init__(self, input_path: str | Path) -> None:
        self.input_path = Path(input_path)
        self._data: pd.DataFrame | None = None

    def load(self) -> None:
        if not self.input_path.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_path}")

        self._data = pd.read_csv(self.input_path)

    def convert(self) -> pd.DataFrame:
        if self._data is None:
            raise ValueError("No data loaded. Call load() first.")

        # TODO: Implement conversion logic once CSV structure is known
        converted_data = self._data.copy()
        return converted_data

    def save(self, output_path: str | Path) -> None:
        if self._data is None:
            raise ValueError("No data loaded. Call load() first.")

        converted_data = self.convert()
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        converted_data.to_csv(output_path, index=False)

    def process(self, output_path: str | Path) -> None:
        self.load()
        self.save(output_path)
