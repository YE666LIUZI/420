import sys
from pathlib import Path
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from features import add_features
from pattern_rules import PatternParams, detect_longhuitou
from preprocess import preprocess_panel


def test_pattern_detector_finds_synthetic_case():
    rows = []
    dates = pd.bdate_range("2024-01-01", periods=40)
    close = 10.0
    for i, d in enumerate(dates):
        if i < 10:
            close *= 1.035
            pct = 0.035 if i != 5 else 0.10
            vol = 2_000_000
        elif i < 15:
            close *= 0.98
            pct = -0.02
            vol = 1_000_000
        else:
            close *= 1.02
            pct = 0.02
            vol = 2_500_000 if i == 15 else 1_500_000
        rows.append({"trade_date": d, "ticker": "600000", "open": close * 0.99, "high": close * 1.01, "low": close * 0.98, "close": close, "volume": vol, "amount": vol * close, "pct_change": pct})

    df = pd.DataFrame(rows)
    clean = preprocess_panel(df, ["trade_date", "ticker", "open", "high", "low", "close", "volume", "amount", "pct_change"])
    feat = add_features(clean, [5, 10, 20], 5, [5, 10, 20], 20)
    p = PatternParams(10, 0.30, 0.095, 0.19, 0.19, 3, 8, 0.25, 1.3, "ma5")
    out = detect_longhuitou(feat, p)
    assert not out.empty
    assert {"candidate_date", "breakout_date", "pattern_score"}.issubset(out.columns)
