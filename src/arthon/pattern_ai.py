"""Pattern AI — analogue (kNN) forecasting engine.

The fusion idea behind this project's flagship feature:
- From TradingView's most-loved free ML script (Lorentzian Classification):
  classify today's market state by finding its nearest historical neighbours
  under a Lorentzian distance, using interpretable features.
- From Kronos: present the forecast the way a foundation model does — as a
  *distribution of possible futures*, not a single line.

Here the neighbours' ACTUAL subsequent price paths become an ensemble
forecast (the 'analogue method', long used in weather forecasting):
  1. Describe every bar with 5 normalised features.
  2. Find the k nearest historical bars (Lorentzian distance) whose future
     is fully known and which end at least `horizon` bars before today
     (no look-ahead, no leakage from overlapping windows).
  3. Their realised next-`horizon` paths, rebased to today's price, form
     the forecast cone: median path + 25-75% and 10-90% bands.
  4. The fraction of neighbours that rose gives an honest probability.

Everything is evaluated walk-forward in evaluation style: accuracy is
reported against the base rate, never as a bare win-rate claim.
"""
from __future__ import annotations
import numpy as np
import pandas as pd

FEATURE_HORIZON = 10

def build_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["close"]
    delta = c.diff()
    gain = delta.clip(lower=0).rolling(14).mean(); loss = (-delta.clip(upper=0)).rolling(14).mean()
    rsi = 100 - 100 / (1 + gain / loss.replace(0, np.nan))
    df["f_rsi"] = (rsi - 50) / 50
    df["f_ret5"] = c.pct_change(5) * 10
    df["f_ret20"] = c.pct_change(20) * 5
    vol = c.pct_change().rolling(20).std()
    df["f_vol"] = vol * 50
    ema10 = c.ewm(span=10, adjust=False).mean(); ema30 = c.ewm(span=30, adjust=False).mean()
    df["f_trend"] = (ema10 - ema30) / c * 20
    feats = df[["f_rsi", "f_ret5", "f_ret20", "f_vol", "f_trend"]]
    # Robust normalisation using the frame's own median/IQR (fitted on the
    # history available at call time; for backtests callers pass slices).
    med = feats.median(); iqr = (feats.quantile(0.75) - feats.quantile(0.25)).replace(0, np.nan)
    return (feats - med) / iqr

def lorentzian(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return np.log1p(np.abs(a - b)).sum(axis=1)

def analogue_forecast(df: pd.DataFrame, horizon: int = 30, k: int = 25) -> dict:
    feats = build_features(df)
    X = feats.values; close = df["close"].values
    today = len(df) - 1
    if today < 250:
        raise ValueError("Need at least ~250 sessions for analogue forecasting")
    query = X[today]
    if np.isnan(query).any():
        raise ValueError("Features unavailable for the latest bar")
    # Candidate neighbours: fully observed future, ending >= horizon bars ago.
    cand_idx = np.arange(60, today - horizon)
    cand = X[cand_idx]
    valid = ~np.isnan(cand).any(axis=1)
    cand_idx, cand = cand_idx[valid], cand[valid]
    dists = lorentzian(cand, np.nan_to_num(query))
    nn = cand_idx[np.argsort(dists)[:k]]
    paths = np.array([close[idx+1: idx+horizon+1] / close[idx] for idx in nn])  # (k, horizon) growth factors
    today_price = float(close[today])
    abs_paths = paths * today_price
    median = np.median(abs_paths, axis=0)
    p25, p75 = np.percentile(abs_paths, 25, axis=0), np.percentile(abs_paths, 75, axis=0)
    p10, p90 = np.percentile(abs_paths, 10, axis=0), np.percentile(abs_paths, 90, axis=0)
    prob_up = float(np.mean(paths[:, -1] > 1.0))
    median_ret = float(median[-1] / today_price - 1)
    return {"today_price": today_price, "horizon": horizon, "neighbours": int(len(nn)),
            "neighbour_dates": [str(df["date"].iloc[i].date()) for i in nn],
            "prob_up": round(prob_up, 3), "median_final": round(float(median[-1]), 2),
            "median_return_pct": round(median_ret * 100, 2),
            "path_median": median, "path_p25": p25, "path_p75": p75, "path_p10": p10, "path_p90": p90,
            "analogue_paths": abs_paths}

def walk_forward_accuracy(df: pd.DataFrame, horizon: int = 10, k: int = 25, trials: int = 12) -> dict:
    """Out-of-sample: at past origins, does the neighbour majority direction
    match what actually happened? Compared with the unconditional base rate."""
    close = df["close"].values
    results, base = [], []
    origins = np.linspace(len(df) - 260, len(df) - horizon - 5, trials).astype(int)
    for o in origins:
        if o < 250: continue
        sub = df.iloc[:o+1].reset_index(drop=True)
        try: fc = analogue_forecast(sub, horizon=horizon, k=k)
        except ValueError: continue
        actual_up = close[o + horizon] > close[o]
        results.append((fc["prob_up"] > 0.5) == bool(actual_up)); base.append(bool(actual_up))
    if not results:
        return {"trials": 0}
    return {"trials": len(results), "direction_accuracy_pct": round(float(np.mean(results)) * 100, 1),
            "base_rate_up_pct": round(float(np.mean(base)) * 100, 1),
            "note": "Accuracy must be read against the base rate; a small edge on few trials is not proof of predictive power."}
