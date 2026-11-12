"""The agent team.

Architecture inspired by TauricResearch/TradingAgents (specialist roles
whose opinions are combined by a decision agent) and the forecasting brief
of shiyu-coder/Kronos. All implementations here are original, transparent
and statistical: every score can be traced to a stated formula. Agents do
not blindly accept each other — the DecisionAgent detects strong
disagreement between the Analyst and Forecast agents, shrinks the combined
score, caps conviction, and records the disagreement in its evidence.

Scores are always in [-1, +1]: -1 very bearish, +1 very bullish.
For the RiskAgent a negative score means 'risk argues for caution'.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import numpy as np
import pandas as pd
from .indicators import max_drawdown

@dataclass
class Opinion:
    agent: str
    score: float
    headline: str
    evidence: list[str] = field(default_factory=list)
    metrics: dict = field(default_factory=dict)

class AnalystAgent:
    """Trend, momentum and mean-reversion analysis from price action."""
    name = "Analyst Agent (quantitative / technical)"
    def run(self, df: pd.DataFrame) -> Opinion:
        last = df.iloc[-1]; price = float(last["close"])
        ev, score = [], 0.0
        for w, col, label in [(0.20, "sma_20", "20-day"), (0.20, "sma_50", "50-day"), (0.15, "sma_200", "200-day")]:
            sma = last[col]
            if pd.notna(sma):
                if price > sma: score += w; ev.append(f"Price {price:,.2f} is above the {label} average ({sma:,.2f}) — uptrend intact.")
                else: score -= w; ev.append(f"Price {price:,.2f} is below the {label} average ({sma:,.2f}) — downtrend pressure.")
        if pd.notna(last["sma_20"]) and pd.notna(last["sma_50"]):
            if last["sma_20"] > last["sma_50"]: score += 0.10; ev.append("20-day average above 50-day average (short-term trend stronger than medium-term).")
            else: score -= 0.10; ev.append("20-day average below 50-day average (short-term trend weaker than medium-term).")
        rsi = float(last["rsi_14"]) if pd.notna(last["rsi_14"]) else 50.0
        if rsi >= 70: score -= 0.15; ev.append(f"RSI is {rsi:.0f} — overbought, momentum may be stretched.")
        elif rsi <= 30: score += 0.15; ev.append(f"RSI is {rsi:.0f} — oversold, mean-reversion bounce is plausible.")
        else: ev.append(f"RSI is {rsi:.0f} — momentum is in the neutral zone.")
        if pd.notna(last["macd"]) and pd.notna(last["macd_signal"]):
            if last["macd"] > last["macd_signal"]: score += 0.10; ev.append("MACD is above its signal line — bullish momentum confirmation.")
            else: score -= 0.10; ev.append("MACD is below its signal line — bearish momentum confirmation.")
        ret_3m = float(df["close"].iloc[-1] / df["close"].iloc[-64] - 1) if len(df) > 64 else float("nan")
        if pd.notna(ret_3m): ev.append(f"Return over the last ~3 months: {ret_3m*100:+.1f}%.")
        score = float(np.clip(score, -1, 1))
        head = "Bullish technical picture" if score > 0.25 else "Bearish technical picture" if score < -0.25 else "Mixed / sideways technical picture"
        return Opinion(self.name, score, head, ev,
                       {"price": round(price, 2), "rsi_14": round(rsi, 1),
                        "return_3m_pct": round(ret_3m * 100, 2) if pd.notna(ret_3m) else None})

class FundamentalsAgent:
    """Fundamental context — honestly bounded by free data availability.

    Yahoo's statement endpoint refuses anonymous access, so in practice
    this agent works from (a) any statement fields the provider returns,
    scored against plain valuation bands, and (b) the verifiable
    52-week-range position from price data. When neither is meaningful it
    scores 0 (neutral) and says so. It never invents financials.
    """
    name = "Fundamentals Agent"
    def run(self, df: pd.DataFrame, fundamentals: dict | None = None) -> Opinion:
        fundamentals = fundamentals or {}
        ev, score, metrics = [], 0.0, {}
        if fundamentals:
            pe = fundamentals.get("trailing_pe")
            if pe:
                metrics["trailing_pe"] = round(float(pe), 1)
                if pe < 15: score += 0.2; ev.append(f"Trailing P/E {pe:.1f} — inexpensive versus broad market norms.")
                elif pe > 40: score -= 0.2; ev.append(f"Trailing P/E {pe:.1f} — demanding valuation; growth must deliver.")
                else: ev.append(f"Trailing P/E {pe:.1f} — mid-range valuation.")
            roe = fundamentals.get("roe")
            if roe is not None:
                metrics["roe_pct"] = round(float(roe) * 100, 1)
                if roe > 0.15: score += 0.15; ev.append(f"ROE {roe*100:.1f}% — solid capital efficiency.")
                elif roe < 0.05: score -= 0.15; ev.append(f"ROE {roe*100:.1f}% — weak capital efficiency.")
            d2e = fundamentals.get("debt_to_equity")
            if d2e is not None:
                metrics["debt_to_equity"] = round(float(d2e), 2)
                if d2e > 200: score -= 0.15; ev.append(f"Debt/equity {d2e:.0f} — leveraged balance sheet.")
        else:
            ev.append("Statement fundamentals (P/E, ROE, margins) are not available from the free data endpoint "
                      "(it requires authenticated access), so this agent scores neutral and relies on price-range context only. "
                      "See docs/DATA_SOURCES.md.")
        window = df.tail(252)
        hi, lo, price = float(window["high"].max()), float(window["low"].min()), float(df["close"].iloc[-1])
        if hi > lo:
            pos = (price - lo) / (hi - lo)
            metrics["position_in_52w_range_pct"] = round(pos * 100, 1)
            ev.append(f"Price sits at {pos*100:.0f}% of its 52-week range ({lo:,.2f} – {hi:,.2f}).")
            if pos > 0.9: score -= 0.05; ev.append("Near the top of the 52-week range — little margin for disappointing news.")
            elif pos < 0.15: score += 0.05; ev.append("Near the bottom of the 52-week range — expectations already low (context only, not a buy signal).")
        score = float(np.clip(score, -1, 1))
        head = "Fundamentals supportive" if score > 0.15 else "Fundamentals demanding / weak" if score < -0.15 else "Fundamentals neutral or unavailable"
        metrics["statement_data_available"] = bool(fundamentals)
        return Opinion(self.name, score, head, ev, metrics)

class ForecastAgent:
    """30-day price forecast behind a model-agnostic interface.

    v2 method: log-price trend regression over the last 120 sessions
    blended with 20-day momentum, prediction band from residual
    volatility. Known limitation (found in v1 testing): the 120-day
    trend can lag a regime change. The method is evaluated out-of-sample
    in evaluation.py; the ROADMAP swaps this body for Kronos behind the
    same interface.
    """
    name = "Forecast Agent"
    HORIZON = 30
    def run(self, df: pd.DataFrame) -> Opinion:
        window = df.tail(120).copy()
        y = np.log(window["close"].values); x = np.arange(len(y))
        slope, intercept = np.polyfit(x, y, 1)
        resid_vol = float(np.std(y - (slope * x + intercept))) if len(y) > 2 else 0.02
        trend_ret = float(np.exp(slope * (len(y) + self.HORIZON - 1) + intercept) / float(window["close"].iloc[-1]) - 1)
        mom_20 = float(df["close"].iloc[-1] / df["close"].iloc[-21] - 1) if len(df) > 21 else 0.0
        expected_ret = 0.7 * trend_ret + 0.3 * (mom_20 * 1.5)
        last_price = float(df["close"].iloc[-1])
        forecast_price = last_price * (1 + expected_ret)
        band = resid_vol * np.sqrt(self.HORIZON) * 0.5
        lo, hi = forecast_price * (1 - band), forecast_price * (1 + band)
        score = float(np.clip(expected_ret * 6, -1, 1))
        ev = [f"Trend slope over 120 sessions implies {trend_ret*100:+.1f}% over the next {self.HORIZON} trading days.",
              f"20-day momentum is {mom_20*100:+.1f}%; blended expected return: {expected_ret*100:+.1f}%.",
              f"Point forecast: {forecast_price:,.2f} (indicative band {lo:,.2f} – {hi:,.2f}). Treat the band, not the point, as the forecast."]
        head = "Forecast points up" if score > 0.2 else "Forecast points down" if score < -0.2 else "Forecast is roughly flat"
        return Opinion(self.name, score, head, ev,
                       {"forecast_price_30d": round(forecast_price, 2), "expected_return_30d_pct": round(expected_ret * 100, 2),
                        "band_low": round(lo, 2), "band_high": round(hi, 2)})

class RiskAgent:
    """Volatility, drawdown, tail risk (VaR/CVaR) and benchmark beta."""
    name = "Risk Agent"
    def run(self, df: pd.DataFrame, benchmark: pd.DataFrame | None = None) -> Opinion:
        last = df.iloc[-1]
        vol = float(last["volatility_30d"]) if pd.notna(last["volatility_30d"]) else float("nan")
        mdd = max_drawdown(df["close"])
        rets = df["daily_return"].dropna()
        var95 = float(np.percentile(rets, 5)) if len(rets) > 50 else float("nan")
        tail = rets[rets <= var95] if pd.notna(var95) else pd.Series(dtype=float)
        cvar95 = float(tail.mean()) if len(tail) else float("nan")
        ev, metrics = [], {}
        if pd.notna(vol): ev.append(f"Annualised volatility (30-day): {vol*100:.1f}%.")
        ev.append(f"Worst peak-to-trough drawdown in the period: {mdd*100:.1f}%.")
        if pd.notna(var95):
            ev.append(f"Historical daily VaR (95%): {var95*100:.2f}% — on about 1 day in 20, losses were this large or worse.")
            ev.append(f"Historical daily CVaR (95%): {cvar95*100:.2f}% — the average of those worst days.")
            metrics.update({"var_95_daily_pct": round(var95 * 100, 2), "cvar_95_daily_pct": round(cvar95 * 100, 2)})
        if benchmark is not None and not benchmark.empty:
            bench = benchmark.copy()
            bench["bench_return"] = bench["close"].pct_change()
            aligned = pd.merge(df[["date", "daily_return"]], bench[["date", "bench_return"]], on="date", how="inner").dropna()
            if len(aligned) > 50 and aligned["bench_return"].var() > 0:
                beta = float(aligned["daily_return"].cov(aligned["bench_return"]) / aligned["bench_return"].var())
                corr = float(aligned["daily_return"].corr(aligned["bench_return"]))
                metrics.update({"beta_vs_benchmark": round(beta, 2), "correlation_vs_benchmark": round(corr, 2)})
                ev.append(f"Beta versus benchmark: {beta:.2f} (correlation {corr:.2f}) — "
                          + ("moves amplify the market." if beta > 1.15 else "moves dampen the market." if beta < 0.85 else "moves broadly with the market."))
        risk_penalty = 0.0
        if pd.notna(vol):
            if vol > 0.45: risk_penalty, rating = 0.45, "High"
            elif vol > 0.30: risk_penalty, rating = 0.30, "Elevated"
            elif vol > 0.18: risk_penalty, rating = 0.15, "Moderate"
            else: risk_penalty, rating = 0.05, "Low"
        else: rating, risk_penalty = "Unknown", 0.2
        if mdd < -0.40: risk_penalty += 0.10; ev.append("Drawdown history is severe — position size should be small.")
        suggested = None
        if pd.notna(vol) and vol > 0:
            suggested = round(min(25.0, max(2.0, (0.15 / vol) * 10)), 1)
            ev.append(f"Volatility-target guide: keep any single position near or below ~{suggested}% of the portfolio.")
        ev.append(f"Overall risk rating: {rating}.")
        metrics.update({"volatility_annualised_pct": round(vol * 100, 1) if pd.notna(vol) else None,
                        "max_drawdown_pct": round(mdd * 100, 1), "risk_rating": rating,
                        "suggested_max_position_pct": suggested})
        return Opinion(self.name, -risk_penalty, f"Risk rating: {rating}", ev, metrics)

class DecisionAgent:
    """Combines opinions into one rating — with explicit disagreement handling."""
    name = "Decision Agent (portfolio manager)"
    WEIGHTS = {"analyst": 0.40, "forecast": 0.30, "fundamentals": 0.10, "risk": 0.20}
    def run(self, analyst: Opinion, forecast: Opinion, fundamentals: Opinion, risk: Opinion) -> Opinion:
        combined = (self.WEIGHTS["analyst"] * analyst.score + self.WEIGHTS["forecast"] * forecast.score
                    + self.WEIGHTS["fundamentals"] * fundamentals.score + self.WEIGHTS["risk"] * risk.score)
        ev = [f"Weighted team score before disagreement adjustment: {combined:+.2f} "
              f"(Analyst {analyst.score:+.2f}×0.40, Forecast {forecast.score:+.2f}×0.30, "
              f"Fundamentals {fundamentals.score:+.2f}×0.10, Risk {risk.score:+.2f}×0.20)."]
        spread = abs(analyst.score - forecast.score)
        disagreement = spread > 1.0
        if disagreement:
            combined *= 0.75
            ev.append(f"DISAGREEMENT: Analyst ({analyst.score:+.2f}) and Forecast ({forecast.score:+.2f}) strongly disagree "
                      f"(spread {spread:.2f}). Combined score shrunk by 25% to {combined:+.2f} and conviction is capped — "
                      "when the team disagrees this much, the honest answer is lower confidence, not false precision.")
        if combined >= 0.30: rating = "BUY"
        elif combined <= -0.30: rating = "SELL / AVOID"
        else: rating = "HOLD / WATCH"
        conviction = "High" if abs(combined) >= 0.55 else "Medium" if abs(combined) >= 0.30 else "Low"
        if disagreement and conviction == "High": conviction = "Medium"
        ev.append(f"Rating: {rating} with {conviction.lower()} conviction.")
        bulls = [e for o in (analyst, forecast, fundamentals) if o.score > 0.1 for e in o.evidence[:2]]
        bears = [e for o in (analyst, forecast, fundamentals) if o.score < -0.1 for e in o.evidence[:2]] + risk.evidence[:1]
        return Opinion(self.name, float(combined), f"{rating} — {conviction} conviction", ev,
                       {"rating": rating, "conviction": conviction, "team_score": round(float(combined), 3),
                        "agent_disagreement": disagreement, "bull_points": bulls, "bear_points": bears})
