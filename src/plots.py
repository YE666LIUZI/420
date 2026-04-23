from __future__ import annotations

from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd


def make_plots(nav_df: pd.DataFrame, trades: pd.DataFrame, out_dir: str) -> dict[str, str]:
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    outputs = {}

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(nav_df["trade_date"], nav_df["nav"], label="NAV")
    ax.set_title("Equity Curve")
    ax.legend()
    p1 = Path(out_dir) / "equity_curve.png"
    fig.savefig(p1, bbox_inches="tight")
    plt.close(fig)
    outputs["equity_curve"] = str(p1)

    dd = nav_df["nav"] / nav_df["nav"].cummax() - 1
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(nav_df["trade_date"], dd, color="red", label="Drawdown")
    ax.set_title("Drawdown")
    ax.legend()
    p2 = Path(out_dir) / "drawdown.png"
    fig.savefig(p2, bbox_inches="tight")
    plt.close(fig)
    outputs["drawdown"] = str(p2)

    if not trades.empty:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.hist(trades["qty"] * trades["price"], bins=20)
        ax.set_title("Trade Notional Distribution")
        p3 = Path(out_dir) / "trade_distribution.png"
        fig.savefig(p3, bbox_inches="tight")
        plt.close(fig)
        outputs["trade_distribution"] = str(p3)
    return outputs
