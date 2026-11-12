"""Ayush's EMA crossover strategy — implemented exactly as specified on
2026-10-31, with the interpretation choices below written down openly
(they were ambiguous in the one-line spec; change them and rerun if the
reading is wrong):

SPEC (user's words): "Use 10 30 and 200 EMA. When 10 EMA cross 30 buy,
and when 30 cross 10 sell. 200 EMA and last swing should be the stop
loss. Also trail the stop loss after every 10 points."

INTERPRETATION:
- Long only, daily candles, same data/costs as the house backtest.
- BUY signal: EMA10 crosses above EMA30 at today's close -> enter at
  tomorrow's open.
- Initial STOP LOSS = the higher of (a) the last confirmed swing low
  (fractal: low lower than the 2 bars on each side, confirmed 2 bars
  later, so no look-ahead) and (b) EMA200 at entry. If that stop is not
  below the entry price (e.g. price is under the 200 EMA), the trade is
  skipped — a stop cannot sit above entry. This makes the 200 EMA a
  regime filter as well as a stop anchor, which is how swing traders
  normally use it.
- SELL: EMA10 crosses below EMA30 ("30 crosses 10") -> exit at the next
  day's open. A stop-loss hit (day's low <= stop) exits that day at the
  stop price, whichever comes first.
- TRAILING STOP: as the highest high since entry advances, the stop is
  raised in 10-point steps — for every full 10 points of advance, the
  stop moves up 10 points. The stop never moves down. Today's stop is
  the one set at yesterday's close (no intrabar look-ahead).
- Costs: asset-aware profile from arthon.costs (buy-side bps on
  entry, sell-side bps on exit — e.g. ~11.9/10.4 bps for Indian delivery
  equity, ~3.4/5.4 for index futures, 20/20 for Indian-exchange crypto).
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from .backtest import _stats, COST_BPS
from .costs import get_profile, describe

TRAIL_POINTS = 10.0

def _prepare(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["close"]
    df["ema_10"] = c.ewm(span=10, adjust=False).mean()
    df["ema_30"] = c.ewm(span=30, adjust=False).mean()
    df["ema_200"] = c.ewm(span=200, adjust=False).mean()
    # Confirmed swing lows: fractal low at bar i is only known at bar i+2.
    low = df["low"]
    is_swing = (low < low.shift(1)) & (low < low.shift(2)) & (low < low.shift(-1)) & (low < low.shift(-2))
    df["swing_low"] = low.where(is_swing)
    df["last_swing_low"] = df["swing_low"].shift(2).ffill()  # usable once confirmed
    return df

def run_user_strategy(df: pd.DataFrame, cost_bps: int | None = None, trail_points: float = TRAIL_POINTS,
                      symbol: str | None = None, cost_profile: str | None = None) -> dict:
    if cost_bps is not None:  # legacy flat override (stress comparisons)
        buy_bps = sell_bps = float(cost_bps)
        cost_note = f"{cost_bps} bps per position change (flat override)"
    else:
        prof = get_profile(symbol, cost_profile)
        buy_bps, sell_bps = prof["buy_bps"], prof["sell_bps"]
        cost_note = describe(symbol, cost_profile)
    df = _prepare(df)
    df = df.dropna(subset=["ema_200"]).reset_index(drop=True)
    n = len(df)
    equity = np.ones(n)
    in_pos = False
    entry_price = stop = highest = anchor_steps = 0.0
    entry_idx = -1
    pending_entry = pending_exit = False
    trades = []
    daily_ret = np.zeros(n)
    days_in = 0

    def close_trade(i, exit_price, reason):
        nonlocal in_pos
        gross = exit_price / entry_price - 1
        net = gross - (buy_bps + sell_bps) / 10000  # entry + exit costs
        trades.append({"entry_date": str(df["date"].iloc[entry_idx].date()), "entry": round(entry_price, 2),
                       "exit_date": str(df["date"].iloc[i].date()), "exit": round(exit_price, 2),
                       "return_pct": round(net * 100, 2), "exit_reason": reason,
                       "initial_stop": round(trades_stop[0], 2)})
        in_pos = False
        return net

    trades_stop = [0.0]
    buy_cost = buy_bps / 10000
    sell_cost = sell_bps / 10000
    for i in range(1, n):
        prev_close = float(df["close"].iloc[i - 1])
        today_open = float(df["open"].iloc[i]) if pd.notna(df["open"].iloc[i]) else prev_close
        # --- execute pending crossover exit at today's open (pay exit cost)
        if in_pos and pending_exit:
            daily_ret[i] = today_open / prev_close - 1 - sell_cost
            close_trade(i, today_open, "EMA 10/30 cross down")
            pending_exit = False
            equity[i] = equity[i - 1] * (1 + daily_ret[i])
            continue
        entered_today = False
        # --- execute pending entry at today's open (pay entry cost today)
        if not in_pos and pending_entry:
            swing = df["last_swing_low"].iloc[i - 1]
            ema200 = float(df["ema_200"].iloc[i - 1])
            if pd.notna(swing):
                s = max(float(swing), ema200)
                if s < today_open:
                    in_pos = True; entry_price = today_open; stop = s; trades_stop[0] = s
                    highest = float(df["high"].iloc[i]); entry_idx = i; anchor_steps = 0
                    entered_today = True
            pending_entry = False
        if in_pos:
            days_in += 1
            base = today_open if entered_today else prev_close
            low_i = float(df["low"].iloc[i])
            if low_i <= stop:
                daily_ret[i] = stop / base - 1 - sell_cost - (buy_cost if entered_today else 0)
                close_trade(i, stop, "Stop loss / trailing stop")
                equity[i] = equity[i - 1] * (1 + daily_ret[i])
                continue
            daily_ret[i] = float(df["close"].iloc[i]) / base - 1 - (buy_cost if entered_today else 0)
            highest = max(highest, float(df["high"].iloc[i]))
            steps = int((highest - entry_price) // trail_points) if highest > entry_price else 0
            if steps > anchor_steps:
                stop = max(stop, trades_stop[0] + trail_points * steps)
                anchor_steps = steps
        equity[i] = equity[i - 1] * (1 + daily_ret[i])
        # --- signals at today's close
        cross_up = df["ema_10"].iloc[i] > df["ema_30"].iloc[i] and df["ema_10"].iloc[i - 1] <= df["ema_30"].iloc[i - 1]
        cross_dn = df["ema_10"].iloc[i] < df["ema_30"].iloc[i] and df["ema_10"].iloc[i - 1] >= df["ema_30"].iloc[i - 1]
        if not in_pos and cross_up:
            pending_entry = True
        elif in_pos and cross_dn:
            pending_exit = True
    if in_pos:
        close_trade(n - 1, float(df["close"].iloc[-1]), "Still open at end of data (marked to last close)")
    rets = pd.Series(daily_ret)
    stats = _stats(rets)
    wins = [t for t in trades if t["return_pct"] > 0]
    return {"period": f"{df['date'].iloc[0].date()} to {df['date'].iloc[-1].date()}",
            "trades": len(trades), "win_rate_pct": round(len(wins) / len(trades) * 100, 1) if trades else None,
            "time_in_market_pct": round(days_in / n * 100, 1),
            "strategy_after_costs": stats, "trade_log": trades,
            "cost_assumption": cost_note, "trail_points": trail_points}
