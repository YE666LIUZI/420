from __future__ import annotations

import pandas as pd

from portfolio import Portfolio


def run_backtest(df: pd.DataFrame, signals: pd.DataFrame, cfg: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    portfolio = Portfolio(cash=cfg["execution"]["initial_cash"])
    slippage = cfg["execution"]["slippage_bps"] / 10000
    comm = cfg["execution"]["commission_bps"] / 10000
    stamp = cfg["execution"]["stamp_duty_bps"] / 10000

    trades = []
    nav_rows = []

    signal_map = signals.groupby("trade_date") if not signals.empty else {}

    for date, day in df.groupby("trade_date"):
        price_map = dict(zip(day["ticker"], day["close"]))
        daily_signals = signal_map.get_group(date) if hasattr(signal_map, "groups") and date in signal_map.groups else pd.DataFrame()

        for _, s in daily_signals.iterrows():
            ticker = s["ticker"]
            if ticker not in price_map:
                continue
            px = price_map[ticker]
            px_buy = px * (1 + slippage)
            px_sell = px * (1 - slippage)
            pos = portfolio.get_position(ticker)

            # target sizing as fraction of nav
            nav = portfolio.cash + portfolio.market_value(price_map)
            qty_target = (nav * float(s["size"])) / max(px, 1e-9)

            if s["action"] == "buy":
                cost = qty_target * px_buy
                fee = cost * comm
                total = cost + fee
                if total <= portfolio.cash:
                    portfolio.cash -= total
                    pos.buy(qty_target, pd.Timestamp(date), s["mode"])
                    trades.append({"trade_date": date, "ticker": ticker, "action": "buy", "qty": qty_target, "price": px_buy, "fee": fee, "reason": s["reason"], "inventory_source": "new"})
            else:
                sellable = pos.sell_t1(qty_target, pd.Timestamp(date))
                if sellable > 0:
                    proceeds = sellable * px_sell
                    fee = proceeds * (comm + stamp)
                    portfolio.cash += proceeds - fee
                    trades.append({"trade_date": date, "ticker": ticker, "action": "sell", "qty": sellable, "price": px_sell, "fee": fee, "reason": s["reason"], "inventory_source": "overnight"})

        nav = portfolio.cash + portfolio.market_value(price_map)
        nav_rows.append({"trade_date": date, "cash": portfolio.cash, "market_value": portfolio.market_value(price_map), "nav": nav})

    return pd.DataFrame(nav_rows), pd.DataFrame(trades)
