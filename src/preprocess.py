from __future__ import annotations

from typing import Iterable
import pandas as pd


def normalize_ticker(ticker: str) -> str:
    t = str(ticker).strip().upper()
    if t.endswith(".SH") or t.endswith(".SZ"):
        return t
    if t.startswith(("600", "601", "603", "605", "688")):
        return f"{t}.SH"
    return f"{t}.SZ"


def classify_board(ticker: str) -> str:
    code = ticker.split(".")[0]
    if code.startswith("300"):
        return "ChiNext"
    if code.startswith("688"):
        return "STAR"
    return "Main"


def preprocess_panel(df: pd.DataFrame, required_columns: Iterable[str], fill_method: str = "ffill") -> pd.DataFrame:
    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    out = df.copy()
    out["trade_date"] = pd.to_datetime(out["trade_date"])
    out["ticker"] = out["ticker"].map(normalize_ticker)
    out["board"] = out["ticker"].map(classify_board)

    out = out.sort_values(["ticker", "trade_date"]).reset_index(drop=True)
    if fill_method:
        numeric_cols = out.select_dtypes(include="number").columns
        out[numeric_cols] = out.groupby("ticker")[numeric_cols].transform(lambda s: s.fillna(method=fill_method))

    out = out.dropna(subset=["open", "high", "low", "close", "volume"])
    return out
