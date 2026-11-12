"""Out-of-sample evaluation of the ForecastAgent's method.

Walk-forward: at several historical origins, fit the same trend+momo
blend using only data available at that origin, forecast 30 sessions
ahead, and compare with what actually happened. This measures the method,
not the stock — a method with poor out-of-sample accuracy should lower
how much anyone trusts today's forecast.
"""
from __future__ import annotations
import numpy as np
import pandas as pd

HORIZON = 30

def _forecast_at(df: pd.DataFrame, end_idx: int) -> float:
    window = df.iloc[max(0, end_idx - 120):end_idx]
    y = np.log(window["close"].values); x = np.arange(len(y))
    slope, intercept = np.polyfit(x, y, 1)
    last_price = float(window["close"].iloc[-1])
    trend_ret = float(np.exp(slope * (len(y) + HORIZON - 1) + intercept) / last_price - 1)
    mom_20 = float(window["close"].iloc[-1] / window["close"].iloc[-21] - 1) if len(window) > 21 else 0.0
    return 0.7 * trend_ret + 0.3 * (mom_20 * 1.5)

def evaluate_forecast_method(df: pd.DataFrame) -> dict:
    # `end` is the first index of the forecast window: the forecast is made
    # from data before `end`, and realised over the next HORIZON sessions.
    origins = [len(df) - HORIZON - k for k in (120, 90, 60, 30, 0)]
    rows = []
    for end in origins:
        if end < 130 or end + HORIZON - 1 >= len(df):
            continue
        pred = _forecast_at(df, end)
        actual = float(df["close"].iloc[end + HORIZON - 1] / df["close"].iloc[end - 1] - 1)
        rows.append({"origin_date": str(df["date"].iloc[end - 1].date()),
                     "predicted_pct": round(pred * 100, 2), "actual_pct": round(actual * 100, 2),
                     "direction_correct": bool(np.sign(pred) == np.sign(actual))})
    if not rows:
        return {"observations": 0, "note": "Not enough history to evaluate out-of-sample."}
    errs = [abs(r["predicted_pct"] - r["actual_pct"]) for r in rows]
    hits = sum(r["direction_correct"] for r in rows)
    return {"observations": len(rows), "mean_absolute_error_pct_points": round(float(np.mean(errs)), 2),
            "direction_accuracy_pct": round(hits / len(rows) * 100, 1), "trials": rows,
            "note": ("Small sample (<=6 origins) and one market regime at most — "
                     "treat this as a sanity check on the method, not proof of predictive power.")}
