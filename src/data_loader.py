from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import pandas as pd


@dataclass
class DataLoader:
    input_path: str

    def load(self) -> pd.DataFrame:
        path = Path(self.input_path)
        if not path.exists():
            raise FileNotFoundError(f"Input file not found: {path}")
        df = pd.read_csv(path)
        return df
