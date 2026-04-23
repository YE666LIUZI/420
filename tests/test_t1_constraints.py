import sys
from pathlib import Path
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from portfolio import Position


def test_t1_blocks_same_day_sell():
    p = Position()
    d = pd.Timestamp("2024-01-02")
    p.buy(100, d, "swing")
    sold = p.sell_t1(100, d)
    assert sold == 0
    sold_next = p.sell_t1(50, d + pd.Timedelta(days=1))
    assert sold_next == 50
