import sys
from pathlib import Path
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from backtest import run_backtest


def test_backtest_runs_and_outputs_nav():
    dates = pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04"])
    df = pd.DataFrame(
        {
            "trade_date": dates.tolist() * 1,
            "ticker": ["600000.SH"] * 3,
            "open": [10, 10.2, 10.1],
            "high": [10.3, 10.4, 10.5],
            "low": [9.9, 10.0, 9.8],
            "close": [10.1, 10.3, 10.2],
        }
    )
    signals = pd.DataFrame(
        [
            {"trade_date": dates[0], "ticker": "600000.SH", "action": "buy", "size": 0.3, "reason": "pattern_confirmed", "mode": "swing"},
            {"trade_date": dates[1], "ticker": "600000.SH", "action": "sell", "size": 0.1, "reason": "positive_t_strength", "mode": "tactical"},
        ]
    )
    cfg = {"execution": {"initial_cash": 100000, "slippage_bps": 0, "commission_bps": 0, "stamp_duty_bps": 0}}
    nav, trades = run_backtest(df, signals, cfg)
    assert len(nav) == 3
    assert nav["nav"].iloc[-1] > 0
    assert not trades.empty
