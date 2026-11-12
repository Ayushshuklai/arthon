"""Asset- and broker-aware transaction cost profiles.

Why this exists (Ayush's challenge, 2026-10-31): trading costs are NOT a
universal constant. They differ by asset class, instrument and broker —
STT alone is 0.1% per side on Indian delivery equity but 0.025% (sell
only) intraday; an Indian crypto exchange charges ~0.2% per trade; a US
stock bought from India pays almost no brokerage but a real FX spread.

Each profile below itemises the typical published schedule of a low-cost
discount broker/exchange (Zerodha-style for India) in basis points per
side. These are modelled approximations of public charge schedules, not
quotes: exact paise depend on order size (flat-fee caps), state stamp
rules and the broker chosen. The legacy flat 20 bps stress profile is
kept for comparison — it overstates delivery-equity and index-futures
costs and understates nothing except crypto fees.

Component references (typical published schedules):
- India equity delivery (NSE, discount broker):
  brokerage 0; STT 0.1% buy+sell; exchange txn 0.00297%; SEBI 0.0001%;
  stamp duty 0.015% buy; GST 18% on (brokerage + txn + SEBI).
  -> buy ~11.9 bps, sell ~10.4 bps (round trip ~22.3 bps)
- India equity intraday: brokerage 0.03% (or flat Rs 20/order, modelled
  as % here); STT 0.025% sell only; stamp 0.003% buy; txn/SEBI/GST as
  above -> buy ~4.2 bps, sell ~6.4 bps (round trip ~10.6 bps)
- India index futures (the tradable proxy for ^NSEI/^NSEBANK/^BSESN):
  brokerage 0.03%; STT 0.02% sell; stamp 0.002% buy; F&O txn charges
  -> buy ~3.4 bps, sell ~5.4 bps (round trip ~8.8 bps)
- Crypto on an Indian exchange: ~0.2% fee per side. The 1% TDS on
  sales is a tax withholding (adjustable against final tax), so it is
  NOT counted as a cost here, but it is a real cash-flow drag.
- US equity bought from India (app-based): ~zero brokerage; the real
  cost is the INR<->USD conversion markup, modelled at 30 bps per side.
- Generic futures (e.g. GC=F gold): low exchange/broker charges,
  modelled ~4 bps per side; contract-specific, approximate.
"""
from __future__ import annotations

COST_PROFILES: dict[str, dict] = {
    "india_equity_delivery": {
        "buy_bps": 11.9, "sell_bps": 10.4,
        "label": "India equity delivery (discount broker, STT-incl.)",
    },
    "india_equity_intraday": {
        "buy_bps": 4.2, "sell_bps": 6.4,
        "label": "India equity intraday (discount broker, STT-incl.)",
    },
    "india_index_futures": {
        "buy_bps": 3.4, "sell_bps": 5.4,
        "label": "India index futures (tradable proxy for index symbols)",
    },
    "crypto_india_exchange": {
        "buy_bps": 20.0, "sell_bps": 20.0,
        "label": "Crypto, Indian exchange fee (excl. 1% TDS withholding)",
    },
    "us_equity_from_india": {
        "buy_bps": 30.0, "sell_bps": 30.0,
        "label": "US equity via Indian app (FX conversion markup model)",
    },
    "futures_generic": {
        "buy_bps": 4.0, "sell_bps": 4.0,
        "label": "Generic futures (approximate exchange + broker charges)",
    },
    "flat_20bps_stress": {
        "buy_bps": 20.0, "sell_bps": 20.0,
        "label": "Legacy flat 20 bps per side (conservative stress test)",
    },
}

_INDEX_SYMBOLS = {"^NSEI", "^NSEBANK", "^BSESN", "^GSPC", "^IXIC", "^DJI"}


def detect_profile(symbol: str | None) -> str:
    """Pick the cost profile for a symbol. Deliberately simple and open."""
    if not symbol:
        return "india_equity_delivery"
    s = symbol.upper()
    if s in _INDEX_SYMBOLS or s.startswith("^"):
        return "india_index_futures"
    if s.endswith((".NS", ".BO")):
        return "india_equity_delivery"
    if s.endswith("-USD") or s.endswith("-INR"):
        return "crypto_india_exchange"
    if "=F" in s:
        return "futures_generic"
    return "us_equity_from_india"  # plain ticker, e.g. AAPL


def get_profile(symbol: str | None = None, profile: str | None = None) -> dict:
    """Resolve a profile dict for a symbol (or an explicit profile name)."""
    name = profile or detect_profile(symbol)
    p = COST_PROFILES[name]
    return {"name": name, **p}


def round_trip_bps(symbol: str | None = None, profile: str | None = None) -> float:
    p = get_profile(symbol, profile)
    return round(p["buy_bps"] + p["sell_bps"], 1)


def describe(symbol: str | None = None, profile: str | None = None) -> str:
    p = get_profile(symbol, profile)
    return (f"{p['label']}: buy {p['buy_bps']} bps + sell {p['sell_bps']} bps "
            f"per round trip = {p['buy_bps'] + p['sell_bps']:.1f} bps "
            f"(profile: {p['name']}; modelled from typical published charge "
            f"schedules, not a broker quote)")
