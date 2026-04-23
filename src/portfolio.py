from __future__ import annotations

from dataclasses import dataclass, field
import pandas as pd


@dataclass
class Lot:
    qty: float
    buy_date: pd.Timestamp
    mode: str


@dataclass
class Position:
    lots: list[Lot] = field(default_factory=list)

    @property
    def qty(self) -> float:
        return sum(l.qty for l in self.lots)

    def buy(self, qty: float, trade_date: pd.Timestamp, mode: str) -> None:
        if qty <= 0:
            return
        self.lots.append(Lot(qty=qty, buy_date=trade_date, mode=mode))

    def sell_t1(self, qty: float, trade_date: pd.Timestamp) -> float:
        remaining = qty
        sold = 0.0
        self.lots.sort(key=lambda x: x.buy_date)
        for lot in self.lots:
            if remaining <= 0:
                break
            if lot.buy_date >= trade_date:
                continue
            take = min(lot.qty, remaining)
            lot.qty -= take
            remaining -= take
            sold += take
        self.lots = [l for l in self.lots if l.qty > 1e-12]
        return sold


@dataclass
class Portfolio:
    cash: float
    positions: dict[str, Position] = field(default_factory=dict)

    def get_position(self, ticker: str) -> Position:
        if ticker not in self.positions:
            self.positions[ticker] = Position()
        return self.positions[ticker]

    def market_value(self, price_map: dict[str, float]) -> float:
        return sum(self.get_position(t).qty * p for t, p in price_map.items())
