from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import numpy as np
import pandas as pd


@dataclass
class PatternParams:
    n1_lookback: int
    impulse_return_min: float
    daily_limit_main: float
    daily_limit_chinext: float
    daily_limit_star: float
    pullback_min_days: int
    pullback_max_days: int
    max_pullback: float
    breakout_vol_multiplier: float
    require_above_ma: str


def _board_limit(board: str, p: PatternParams) -> float:
    return {"Main": p.daily_limit_main, "ChiNext": p.daily_limit_chinext, "STAR": p.daily_limit_star}.get(board, p.daily_limit_main)


def detect_longhuitou(df: pd.DataFrame, p: PatternParams, apply_false_filters: bool = True) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for ticker, g in df.groupby("ticker"):
        g = g.reset_index(drop=True)
        for i in range(max(25, p.n1_lookback + p.pullback_max_days), len(g)):
            board = g.at[i, "board"]
            impulse_start = i - p.pullback_max_days - p.n1_lookback
            impulse_end = i - p.pullback_max_days
            impulse = g.iloc[impulse_start:impulse_end]
            if len(impulse) < p.n1_lookback:
                continue

            impulse_ret = impulse["close"].iloc[-1] / impulse["close"].iloc[0] - 1
            has_limit_like = (impulse["pct_change"] >= _board_limit(board, p)).any()
            if impulse_ret < p.impulse_return_min or not has_limit_like:
                continue

            found = False
            for pb_days in range(p.pullback_min_days, p.pullback_max_days + 1):
                pb_start = impulse_end
                pb_end = pb_start + pb_days
                if pb_end >= i:
                    break
                pullback = g.iloc[pb_start:pb_end]
                breakout = g.iloc[pb_end]
                peak = impulse["high"].max()
                trough = pullback["low"].min()
                pb_ratio = (peak - trough) / peak if peak > 0 else 1

                if pb_ratio > p.max_pullback:
                    continue
                if pullback["volume"].mean() >= impulse["volume"].mean():
                    continue

                range_high = pullback["high"].max()
                cond_breakout = breakout["close"] > range_high
                cond_vol = breakout["volume"] > breakout["vol_ma"] * p.breakout_vol_multiplier
                cond_ma = breakout["close"] > breakout.get(p.require_above_ma, breakout["close"] - 1)
                if not (cond_breakout and cond_vol and cond_ma):
                    continue

                if apply_false_filters:
                    weak_close = (breakout["close"] - breakout["low"]) / max(1e-9, breakout["high"] - breakout["low"]) < 0.4
                    pre_break_ma_fail = (g.iloc[pb_start:pb_end]["close"] < g.iloc[pb_start:pb_end]["ma10"]).any()
                    if weak_close or pre_break_ma_fail:
                        continue

                score = 0.3 * min(1.0, impulse_ret / 0.6) + 0.3 * (1 - min(1.0, pb_ratio / p.max_pullback)) + 0.4 * min(
                    1.5, breakout["volume"] / max(1e-9, breakout["vol_ma"])
                ) / 1.5
                rows.append(
                    {
                        "ticker": ticker,
                        "candidate_date": breakout["trade_date"],
                        "impulse_start": impulse["trade_date"].iloc[0],
                        "impulse_end": impulse["trade_date"].iloc[-1],
                        "pullback_start": pullback["trade_date"].iloc[0],
                        "pullback_end": pullback["trade_date"].iloc[-1],
                        "breakout_date": breakout["trade_date"],
                        "pattern_score": float(score),
                        "trend_strength": float(impulse_ret),
                        "pullback_quality": float(1 - pb_ratio),
                        "breakout_strength": float(breakout["volume"] / max(1e-9, breakout["vol_ma"])),
                    }
                )
                found = True
                break
            if found:
                continue
    return pd.DataFrame(rows)
