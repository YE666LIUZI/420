import sys
from pathlib import Path
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from metrics import compute_metrics


def test_metrics_basic_fields():
    nav = pd.DataFrame({"trade_date": pd.date_range("2024-01-01", periods=5), "nav": [100, 101, 102, 103, 105]})
    trades = pd.DataFrame(
        [
            {"action": "buy", "qty": 10, "price": 10},
            {"action": "sell", "qty": 10, "price": 11},
        ]
    )
    m = compute_metrics(nav, trades)
    assert "total_return" in m.columns
    assert m["total_return"].iloc[0] > 0
