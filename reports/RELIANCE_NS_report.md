# Finance AI — Analysis Report: RELIANCE.NS

- **Analysis date:** 2026-10-30
- **Data range:** 2024-10-30 to 2026-10-29 (495 sessions)
- **Data source:** Yahoo Finance public chart API (INR (NSE/BSE)); benchmark: ^NSEI
- **Methodology:** Four statistical agents (quantitative/technical, fundamentals-context, forecast, risk) combined by a decision agent with disagreement handling; trend-rule backtest with transaction costs. Full methodology: docs/ARCHITECTURE.md in the project repository.
- **Assumptions & limits:** Free delayed/end-of-day data; statement fundamentals may be unavailable from the free endpoint and are then scored neutral, never invented; forecasts are simple trend models, not predictions. Educational project — not financial advice.

## Decision
**HOLD / WATCH — Low conviction**

- Weighted team score before disagreement adjustment: -0.25 (Analyst -0.55×0.40, Forecast -0.03×0.30, Fundamentals +0.05×0.10, Risk -0.15×0.20).
- Rating: HOLD / WATCH with low conviction.

**Bear / caution case**
- Price 1,167.40 is below the 20-day average (1,187.52) — downtrend pressure.
- Price 1,167.40 is below the 50-day average (1,239.03) — downtrend pressure.
- Annualised volatility (30-day): 24.4%.

## Agent Opinions

### Analyst Agent (quantitative / technical)
**Bearish technical picture** (score -0.55)

- Price 1,167.40 is below the 20-day average (1,187.52) — downtrend pressure.
- Price 1,167.40 is below the 50-day average (1,239.03) — downtrend pressure.
- Price 1,167.40 is below the 200-day average (1,331.02) — downtrend pressure.
- 20-day average below 50-day average (short-term trend weaker than medium-term).
- RSI is 47 — momentum is in the neutral zone.
- MACD is above its signal line — bullish momentum confirmation.
- Return over the last ~3 months: -8.5%.

| Metric | Value |
|---|---|
| price | 1167.4 |
| rsi_14 | 47.2 |
| return_3m_pct | -8.5 |

### Fundamentals Agent
**Fundamentals neutral or unavailable** (score +0.05)

- Statement fundamentals (P/E, ROE, margins) are not available from the free data endpoint (it requires authenticated access), so this agent scores neutral and relies on price-range context only. See docs/DATA_SOURCES.md.
- Price sits at 3% of its 52-week range (1,152.20 – 1,611.80).
- Near the bottom of the 52-week range — expectations already low (context only, not a buy signal).

| Metric | Value |
|---|---|
| position_in_52w_range_pct | 3.3 |
| statement_data_available | False |

### Forecast Agent
**Forecast is roughly flat** (score -0.03)

- Trend slope over 120 sessions implies +0.1% over the next 30 trading days.
- 20-day momentum is -1.2%; blended expected return: -0.5%.
- Point forecast: 1,161.84 (indicative band 1,078.80 – 1,244.87). Treat the band, not the point, as the forecast.

| Metric | Value |
|---|---|
| forecast_price_30d | 1161.84 |
| expected_return_30d_pct | -0.48 |
| band_low | 1078.8 |
| band_high | 1244.87 |

### Risk Agent
**Risk rating: Moderate** (score -0.15)

- Annualised volatility (30-day): 24.4%.
- Worst peak-to-trough drawdown in the period: -27.3%.
- Historical daily VaR (95%): -2.12% — on about 1 day in 20, losses were this large or worse.
- Historical daily CVaR (95%): -2.80% — the average of those worst days.
- Beta versus benchmark: 1.05 (correlation 0.66) — moves broadly with the market.
- Volatility-target guide: keep any single position near or below ~6.2% of the portfolio.
- Overall risk rating: Moderate.

| Metric | Value |
|---|---|
| var_95_daily_pct | -2.12 |
| cvar_95_daily_pct | -2.8 |
| beta_vs_benchmark | 1.05 |
| correlation_vs_benchmark | 0.66 |
| volatility_annualised_pct | 24.4 |
| max_drawdown_pct | -27.3 |
| risk_rating | Moderate |
| suggested_max_position_pct | 6.2 |

## Forecast method — out-of-sample check

Walk-forward trials: 5 · Mean absolute error: 4.11 percentage points · Direction accuracy: 80.0%
_Small sample (<=6 origins) and one market regime at most — treat this as a sanity check on the method, not proof of predictive power._

| Origin | Predicted | Actual | Direction right? |
|---|---:|---:|:--:|
| 2026-03-19 | +0.56% | +3.71% | Yes |
| 2026-05-07 | -2.45% | -8.82% | Yes |
| 2026-06-19 | -4.16% | +0.73% | No |
| 2026-08-03 | -4.11% | -6.35% | Yes |
| 2026-09-15 | -1.62% | -5.50% | Yes |

## Backtest — trend rule (after costs) vs buy-and-hold vs benchmark

Period: 2025-01-10 to 2026-10-29 · 446 trading days · 25 entries · in the market 34.1% of the time · Costs: 20 bps charged per position change (entry and exit).

| | Total return | CAGR | Sharpe | Sortino | Max drawdown |
|---|---:|---:|---:|---:|---:|
| Trend strategy (after costs) | 1.8% | 1.0% | 0.14 | 0.14 | -15.0% |
| Buy and hold (this stock) | -7.0% | -4.0% | -0.09 | -0.14 | -27.3% |
| Buy and hold (benchmark) | -2.5% | -1.4% | -0.04 | -0.07 | -15.6% |

_Backtest caveats: single-ticker test (survivorship-conditional), costs are a stated assumption not a broker quote, past performance does not predict future results. Backtested performance is simulation, not live trading._
