"""Technical indicators used by the analyst agent."""
from __future__ import annotations
import numpy as np
import pandas as pd

def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["close"]
    df["sma_20"] = c.rolling(20).mean()
    df["sma_50"] = c.rolling(50).mean()
    df["sma_200"] = c.rolling(200).mean()
    df["ema_12"] = c.ewm(span=12, adjust=False).mean()
    df["ema_26"] = c.ewm(span=26, adjust=False).mean()
    df["macd"] = df["ema_12"] - df["ema_26"]
    df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
    delta = c.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - 100 / (1 + rs)
    # Flat stretches (no gains and no losses) make RSI undefined mathematically;
    # the honest convention is neutral 50, all-gain stretches are 100.
    df["rsi_14"] = rsi.where(loss > 0, np.where(gain > 0, 100.0, 50.0))
    mid = df["sma_20"]; std = c.rolling(20).std()
    df["boll_upper"] = mid + 2 * std
    df["boll_lower"] = mid - 2 * std
    df["daily_return"] = c.pct_change()
    df["volatility_30d"] = df["daily_return"].rolling(30).std() * np.sqrt(252)
    return df

def max_drawdown(close: pd.Series) -> float:
    peak = close.cummax()
    return float(((close - peak) / peak).min())
