from __future__ import annotations

from typing import Iterable
import pandas as pd


def add_features(
    df: pd.DataFrame,
    ma_windows: Iterable[int],
    volume_ma_window: int,
    return_windows: Iterable[int],
    rolling_extrema_window: int,
) -> pd.DataFrame:
    out = df.copy()
    g = out.groupby("ticker", group_keys=False)

    for w in ma_windows:
        out[f"ma{w}"] = g["close"].transform(lambda s: s.rolling(w).mean())
    out["vol_ma"] = g["volume"].transform(lambda s: s.rolling(volume_ma_window).mean())

    for w in return_windows:
        out[f"ret_{w}d"] = g["close"].transform(lambda s: s.pct_change(w))

    out["rolling_high"] = g["high"].transform(lambda s: s.rolling(rolling_extrema_window).max())
    out["rolling_low"] = g["low"].transform(lambda s: s.rolling(rolling_extrema_window).min())
    out["volatility_10d"] = g["pct_change"].transform(lambda s: s.rolling(10).std())
    return out
