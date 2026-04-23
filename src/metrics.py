from __future__ import annotations

import numpy as np
import pandas as pd


def compute_metrics(nav_df: pd.DataFrame, trades: pd.DataFrame) -> pd.DataFrame:
    if nav_df.empty:
        return pd.DataFrame([{}])
    s = nav_df["nav"].astype(float)
    rets = s.pct_change().fillna(0)
    total_return = s.iloc[-1] / s.iloc[0] - 1
    ann_return = (1 + total_return) ** (252 / max(1, len(s))) - 1
    cummax = s.cummax()
    dd = s / cummax - 1
    max_dd = dd.min()
    sharpe = (rets.mean() / (rets.std() + 1e-12)) * np.sqrt(252)

    sells = trades[trades["action"] == "sell"] if not trades.empty else pd.DataFrame()
    wins = (sells["price"] > sells["price"].median()).mean() if not sells.empty else 0.0
    pl_ratio = (sells["price"][sells["price"] > sells["price"].median()].mean() / max(1e-9, sells["price"][sells["price"] <= sells["price"].median()].mean())) if len(sells) > 1 else 0.0

    turnover = trades["qty"].sum() / max(1e-9, s.mean()) if not trades.empty else 0.0
    avg_hold = 1.0

    return pd.DataFrame(
        [
            {
                "total_return": total_return,
                "annualized_return": ann_return,
                "max_drawdown": max_dd,
                "sharpe": sharpe,
                "win_rate": wins,
                "profit_loss_ratio": pl_ratio,
                "turnover": turnover,
                "avg_holding_period": avg_hold,
            }
        ]
    )


def attribution_by_mode(trades: pd.DataFrame) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame(columns=["mode", "trade_count", "notional"])
    out = trades.copy()
    out["notional"] = out["qty"] * out["price"]
    return out.groupby(out["reason"].str.contains("t_").map({True: "t_trading", False: "swing"})).agg(trade_count=("qty", "count"), notional=("notional", "sum")).reset_index(names="mode")
