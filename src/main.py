from __future__ import annotations

import argparse
from pathlib import Path
import yaml
import pandas as pd

from data_loader import DataLoader
from preprocess import preprocess_panel
from features import add_features
from pattern_rules import PatternParams, detect_longhuitou
from signal_engine import rank_candidates, generate_daily_signals
from backtest import run_backtest
from metrics import compute_metrics, attribution_by_mode
from plots import make_plots


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def generate_sample_data(path: str, n_tickers: int = 5, n_days: int = 120) -> None:
    import numpy as np

    Path(path).parent.mkdir(parents=True, exist_ok=True)
    dates = pd.bdate_range("2023-01-02", periods=n_days)
    rows = []
    rng = np.random.default_rng(42)
    for i in range(n_tickers):
        ticker = f"60{i:04d}"
        px = 10 + i
        for d in dates:
            ret = rng.normal(0.002, 0.03)
            op = px * (1 + rng.normal(0, 0.01))
            cl = max(1, op * (1 + ret))
            hi = max(op, cl) * (1 + abs(rng.normal(0, 0.01)))
            lo = min(op, cl) * (1 - abs(rng.normal(0, 0.01)))
            vol = abs(rng.normal(2e7, 5e6))
            amt = vol * cl
            rows.append({"trade_date": d, "ticker": ticker, "open": op, "high": hi, "low": lo, "close": cl, "volume": vol, "amount": amt, "pct_change": ret})
            px = cl
    pd.DataFrame(rows).to_csv(path, index=False)


def run_pipeline(cfg: dict) -> None:
    loader = DataLoader(cfg["data"]["input_path"])
    raw = loader.load()
    clean = preprocess_panel(raw, cfg["preprocess"]["required_columns"], cfg["preprocess"]["fill_method"])
    feat = add_features(clean, **cfg["features"])
    Path(cfg["data"]["processed_path"]).parent.mkdir(parents=True, exist_ok=True)
    feat.to_csv(cfg["data"]["processed_path"], index=False)

    p = PatternParams(**cfg["pattern"])
    patterns = detect_longhuitou(feat, p, apply_false_filters=cfg["experiment"]["apply_false_filters"])
    ranked = rank_candidates(patterns)
    signals = generate_daily_signals(feat, ranked, cfg)
    nav, trades = run_backtest(feat, signals, cfg)

    metrics = compute_metrics(nav, trades)
    attr = attribution_by_mode(trades)

    out_dir = Path("reports/output")
    out_dir.mkdir(parents=True, exist_ok=True)
    ranked.to_csv(out_dir / "patterns_ranked.csv", index=False)
    signals.to_csv(out_dir / "signals.csv", index=False)
    nav.to_csv(out_dir / "nav.csv", index=False)
    trades.to_csv(out_dir / "trades.csv", index=False)
    metrics.to_csv(out_dir / "metrics.csv", index=False)
    attr.to_csv(out_dir / "attribution.csv", index=False)

    figs = make_plots(nav, trades, str(out_dir))
    report = out_dir / "summary.md"
    with open(report, "w", encoding="utf-8") as f:
        f.write("# 龙回头 Strategy Report\n\n")
        f.write("## Key Questions\n")
        f.write("- Pattern statistical edge: see metrics and experiment comparisons.\n")
        f.write("- T-trading contribution: see attribution table.\n")
        f.write("- Failure modes: inspect trade log reasons and drawdown periods.\n\n")
        f.write("## Metrics\n\n")
        f.write(metrics.to_markdown(index=False))
        f.write("\n\n## Attribution\n\n")
        f.write(attr.to_markdown(index=False) if not attr.empty else "No trades")
        f.write("\n\n## Figures\n")
        for k, v in figs.items():
            f.write(f"- {k}: {v}\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/strategy.yaml")
    parser.add_argument("--generate-sample-data", action="store_true")
    args = parser.parse_args()

    cfg = load_config(args.config)
    if args.generate_sample_data:
        generate_sample_data(cfg["data"]["input_path"])
    run_pipeline(cfg)


if __name__ == "__main__":
    main()
