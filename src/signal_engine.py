from __future__ import annotations

import pandas as pd


def rank_candidates(patterns: pd.DataFrame) -> pd.DataFrame:
    if patterns.empty:
        return patterns
    out = patterns.copy()
    out["rank_score"] = (
        0.30 * out["trend_strength"].rank(pct=True)
        + 0.30 * out["pullback_quality"].rank(pct=True)
        + 0.40 * out["breakout_strength"].rank(pct=True)
    )
    out["daily_rank"] = out.groupby("candidate_date")["rank_score"].rank(ascending=False, method="dense")
    return out


def generate_daily_signals(df: pd.DataFrame, ranked_patterns: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    actions = []
    if ranked_patterns.empty:
        return pd.DataFrame(columns=["trade_date", "ticker", "action", "size", "reason", "mode"])

    score_thr = cfg["signals"]["score_threshold"]
    top_k = cfg["signals"]["top_k"]

    for _, row in ranked_patterns.iterrows():
        if row["rank_score"] < score_thr or row["daily_rank"] > top_k:
            continue
        actions.append(
            {
                "trade_date": row["candidate_date"],
                "ticker": row["ticker"],
                "action": "buy",
                "size": cfg["signals"]["swing_entry_size"],
                "reason": "pattern_confirmed",
                "mode": "swing",
            }
        )

    # T-trading proxies on close data
    for ticker, g in df.groupby("ticker"):
        g = g.sort_values("trade_date")
        for i in range(1, len(g)):
            today = g.iloc[i]
            yday = g.iloc[i - 1]
            gap = today["open"] / yday["close"] - 1
            if gap >= cfg["signals"]["positive_t_gap_threshold"]:
                actions.append(
                    {
                        "trade_date": today["trade_date"],
                        "ticker": ticker,
                        "action": "sell",
                        "size": cfg["signals"]["tactical_max_size"],
                        "reason": "positive_t_strength",
                        "mode": "tactical",
                    }
                )
            weak_open = today["open"] / yday["close"] - 1
            if weak_open <= cfg["signals"]["reverse_t_weak_open_threshold"] and today["close"] > today["open"]:
                actions.append(
                    {
                        "trade_date": today["trade_date"],
                        "ticker": ticker,
                        "action": "buy",
                        "size": cfg["signals"]["tactical_max_size"],
                        "reason": "reverse_t_weakness",
                        "mode": "tactical",
                    }
                )
    out = pd.DataFrame(actions)
    if out.empty:
        return pd.DataFrame(columns=["trade_date", "ticker", "action", "size", "reason", "mode"])
    return out.sort_values(["trade_date", "ticker", "mode", "action"]).reset_index(drop=True)
