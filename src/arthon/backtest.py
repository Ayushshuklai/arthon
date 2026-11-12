"""Backtest of the analyst's trend rule vs buy-and-hold and the benchmark.

Rule (evaluated at close, position taken next day — no look-ahead):
long when close > SMA50 and RSI < 75, otherwise flat.

Costs: asset- and broker-aware, via arthon.costs — the charge
depends on what is being traded (Indian delivery equity pays 0.1% STT
per side; index futures a fraction of that; crypto exchange fees are
higher). Entries are charged the profile's buy-side bps, exits the
sell-side bps. The legacy flat 20 bps per change survives only as the
"flat_20bps_stress" comparison profile; it is NOT the default.

Survivorship note: this backtests a single chosen ticker, so results are
conditional on having picked that ticker — they cannot be read as the
performance of a strategy across a universe.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from .indicators import max_drawdown
from .costs import get_profile, describe

COST_BPS = 20  # legacy flat stress rate, kept for comparisons only

def _stats(returns: pd.Series) -> dict:
    returns = returns.dropna()
    if len(returns) < 10: return {}
    equity = (1 + returns).cumprod()
    years = len(returns) / 252
    cagr = float(equity.iloc[-1] ** (1 / years) - 1) if years > 0 else 0.0
    sharpe = float(returns.mean() / returns.std() * np.sqrt(252)) if returns.std() > 0 else 0.0
    downside = returns[returns < 0]
    sortino = float(returns.mean() / downside.std() * np.sqrt(252)) if len(downside) > 1 and downside.std() > 0 else 0.0
    return {"total_return_pct": round(float(equity.iloc[-1] - 1) * 100, 1), "cagr_pct": round(cagr * 100, 1),
            "sharpe": round(sharpe, 2), "sortino": round(sortino, 2),
            "max_drawdown_pct": round(max_drawdown(equity) * 100, 1)}

def run_backtest(df: pd.DataFrame, benchmark: pd.DataFrame | None = None,
                 symbol: str | None = None, cost_profile: str | None = None) -> dict:
    prof = get_profile(symbol, cost_profile)
    df = df.dropna(subset=["sma_50", "rsi_14"]).copy()
    df["signal"] = ((df["close"] > df["sma_50"]) & (df["rsi_14"] < 75)).astype(int)
    df["position"] = df["signal"].shift(1).fillna(0)
    diff = df["position"].diff().fillna(0)
    per_day_cost = ((diff == 1) * prof["buy_bps"] + (diff == -1) * prof["sell_bps"]) / 10000
    df["strategy_return"] = df["position"] * df["daily_return"] - per_day_cost
    out = {"period": f"{df['date'].iloc[0].date()} to {df['date'].iloc[-1].date()}",
           "trading_days": int(len(df)), "entries": int((df["position"].diff().fillna(0) == 1).sum()),
           "time_in_market_pct": round(float(df["position"].mean() * 100), 1),
           "cost_assumption": describe(symbol, cost_profile),
           "cost_profile": prof["name"],
           "strategy_after_costs": _stats(df["strategy_return"]), "buy_and_hold": _stats(df["daily_return"])}
    if benchmark is not None and not benchmark.empty:
        bench = benchmark.copy(); bench["bench_return"] = bench["close"].pct_change()
        aligned = pd.merge(df[["date", "daily_return"]], bench[["date", "bench_return"]], on="date", how="inner")
        out["benchmark_buy_and_hold"] = _stats(aligned["bench_return"])
        out["benchmark_symbol_note"] = "Benchmark buy-and-hold over the same dates (see report header for symbol)."
    return out
