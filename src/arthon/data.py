"""Market data layer.

Primary source: Yahoo Finance's public chart API (no API key). Works for
NSE (.NS), BSE (.BO) and global tickers, plus indices such as ^NSEI.
Responses are cached as CSV locally. NOTE: cached Yahoo data is for local
use under Yahoo's terms — it is deliberately NOT redistributed in the
public repository (see docs/DATA_SOURCES.md).

Fundamentals: Yahoo's quoteSummary endpoint currently requires an
authenticated crumb and returns 401 for anonymous callers, so
fetch_fundamentals() fails soft and reports availability honestly rather
than fabricating statement data.
"""
from __future__ import annotations
import json, logging, os, urllib.request, urllib.parse
import pandas as pd

log = logging.getLogger(__name__)
CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "cache")
_UA = {"User-Agent": "Mozilla/5.0"}

def _cache_path(symbol: str, years: int) -> str:
    safe = symbol.replace("^", "IDX_").replace("/", "_")
    return os.path.normpath(os.path.join(CACHE_DIR, f"{safe}_{years}y.csv"))

def fetch_prices(symbol: str, years: int = 2, use_cache: bool = True) -> pd.DataFrame:
    """Daily OHLCV for `symbol`. Raises ValueError on empty/invalid data."""
    if not symbol or not isinstance(symbol, str):
        raise ValueError("symbol must be a non-empty string")
    path = _cache_path(symbol, years)
    if use_cache and os.path.exists(path):
        return pd.read_csv(path, parse_dates=["date"])
    rng = f"{years}y" if years <= 10 else "max"
    url = ("https://query1.finance.yahoo.com/v8/finance/chart/"
           + urllib.parse.quote(symbol, safe="")
           + f"?range={rng}&interval=1d")
    req = urllib.request.Request(url, headers=_UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    try:
        result = payload["chart"]["result"][0]
        q = result["indicators"]["quote"][0]
        df = pd.DataFrame({
            "date": pd.to_datetime(result["timestamp"], unit="s").tz_localize(None).normalize(),
            "open": q["open"], "high": q["high"], "low": q["low"],
            "close": q["close"], "volume": q["volume"],
        }).dropna(subset=["close"]).reset_index(drop=True)
    except (TypeError, KeyError, IndexError) as e:
        raise ValueError(f"Unexpected data format for {symbol}: {e}") from e
    if df.empty:
        raise ValueError(f"No price data returned for {symbol}")
    if (df["close"] <= 0).any():
        log.warning("%s: non-positive prices present; keeping rows but flagging data quality", symbol)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    return df

def fetch_fundamentals(symbol: str) -> dict:
    """Best-effort statement fundamentals.

    Returns {} when the free endpoint refuses anonymous access (the usual
    case in 2026). Callers must treat {} as 'not available', never invent
    values.
    """
    modules = "defaultKeyStatistics,financialData"
    url = (f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/"
           + urllib.parse.quote(symbol, safe="") + f"?modules={modules}")
    try:
        req = urllib.request.Request(url, headers=_UA)
        with urllib.request.urlopen(req, timeout=20) as r:
            payload = json.load(r)
        result = (payload.get("quoteSummary") or {}).get("result") or []
        if not result:
            return {}
        ks = result[0].get("defaultKeyStatistics") or {}
        fd = result[0].get("financialData") or {}
        def raw(d, k):
            v = d.get(k) or {}
            return v.get("raw") if isinstance(v, dict) else None
        out = {"trailing_pe": raw(ks, "trailingPE"), "price_to_book": raw(ks, "priceToBook"),
               "roe": raw(fd, "returnOnEquity"), "debt_to_equity": raw(fd, "debtToEquity"),
               "revenue_growth": raw(fd, "revenueGrowth"), "profit_margin": raw(fd, "profitMargins")}
        return {k: v for k, v in out.items() if v is not None}
    except Exception as e:  # network / 401 / parse — all mean 'unavailable'
        log.info("Fundamentals unavailable for %s (%s)", symbol, type(e).__name__)
        return {}

def benchmark_for(symbol: str) -> str:
    s = symbol.upper()
    # Indian listings (.NS/.BO) and Indian indices (^NSEI, ^BSESN, ^NSEBANK...)
    if s.endswith((".NS", ".BO")) or s.startswith(("^NSE", "^BSE")):
        return "^NSEI"
    return "^GSPC"
