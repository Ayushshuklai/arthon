# Arthon — Analysis Report: AAPL

- **Analysis date:** 2026-10-30
- **Data range:** 2024-10-31 to 2026-10-30 (501 sessions)
- **Data source:** Yahoo Finance public chart API (listing currency); benchmark: ^GSPC
- **Methodology:** Four statistical agents (quantitative/technical, fundamentals-context, forecast, risk) combined by a decision agent with disagreement handling; trend-rule backtest with transaction costs. Full methodology: docs/ARCHITECTURE.md in the project repository.
- **Assumptions & limits:** Free delayed/end-of-day data; statement fundamentals may be unavailable from the free endpoint and are then scored neutral, never invented; forecasts are simple trend models, not predictions. Educational project — not financial advice.

## Decision
**HOLD / WATCH — Low conviction**

- Weighted team score before disagreement adjustment: +0.28 (Analyst +0.55×0.40, Forecast +0.23×0.30, Fundamentals -0.05×0.10, Risk -0.05×0.20).
- Rating: HOLD / WATCH with low conviction.

**Bull case**
- Price 344.63 is above the 20-day average (342.08) — uptrend intact.
- Price 344.63 is above the 50-day average (333.04) — uptrend intact.
- Trend slope over 120 sessions implies +3.5% over the next 30 trading days.
- 20-day momentum is +3.3%; blended expected return: +3.9%.

**Bear / caution case**
- Annualised volatility (30-day): 16.3%.

## Agent Opinions

### Analyst Agent (quantitative / technical)
**Bullish technical picture** (score +0.55)

- Price 344.63 is above the 20-day average (342.08) — uptrend intact.
- Price 344.63 is above the 50-day average (333.04) — uptrend intact.
- Price 344.63 is above the 200-day average (296.56) — uptrend intact.
- 20-day average above 50-day average (short-term trend stronger than medium-term).
- RSI is 55 — momentum is in the neutral zone.
- MACD is below its signal line — bearish momentum confirmation.
- Return over the last ~3 months: +13.6%.

| Metric | Value |
|---|---|
| price | 344.63 |
| rsi_14 | 54.9 |
| return_3m_pct | 13.58 |

### Fundamentals Agent
**Fundamentals neutral or unavailable** (score -0.05)

- Statement fundamentals (P/E, ROE, margins) are not available from the free data endpoint (it requires authenticated access), so this agent scores neutral and relies on price-range context only. See docs/DATA_SOURCES.md.
- Price sits at 93% of its 52-week range (243.42 – 351.73).
- Near the top of the 52-week range — little margin for disappointing news.

| Metric | Value |
|---|---|
| position_in_52w_range_pct | 93.4 |
| statement_data_available | False |

### Forecast Agent
**Forecast points up** (score +0.23)

- Trend slope over 120 sessions implies +3.5% over the next 30 trading days.
- 20-day momentum is +3.3%; blended expected return: +3.9%.
- Point forecast: 358.09 (indicative band 325.28 – 390.89). Treat the band, not the point, as the forecast.

| Metric | Value |
|---|---|
| forecast_price_30d | 358.09 |
| expected_return_30d_pct | 3.9 |
| band_low | 325.28 |
| band_high | 390.89 |

### Risk Agent
**Risk rating: Low** (score -0.05)

- Annualised volatility (30-day): 16.3%.
- Worst peak-to-trough drawdown in the period: -33.4%.
- Historical daily VaR (95%): -2.66% — on about 1 day in 20, losses were this large or worse.
- Historical daily CVaR (95%): -4.23% — the average of those worst days.
- Beta versus benchmark: 1.07 (correlation 0.60) — moves broadly with the market.
- Volatility-target guide: keep any single position near or below ~9.2% of the portfolio.
- Overall risk rating: Low.

| Metric | Value |
|---|---|
| var_95_daily_pct | -2.66 |
| cvar_95_daily_pct | -4.23 |
| beta_vs_benchmark | 1.07 |
| correlation_vs_benchmark | 0.6 |
| volatility_annualised_pct | 16.3 |
| max_drawdown_pct | -33.4 |
| risk_rating | Low |
| suggested_max_position_pct | 9.2 |

## Forecast method — out-of-sample check

Walk-forward trials: 5 · Mean absolute error: 5.85 percentage points · Direction accuracy: 80.0%
_Small sample (<=6 origins) and one market regime at most — treat this as a sanity check on the method, not proof of predictive power._

| Origin | Predicted | Actual | Direction right? |
|---|---:|---:|:--:|
| 2026-03-27 | +0.22% | +17.64% | Yes |
| 2026-05-11 | -1.77% | +0.14% | No |
| 2026-06-24 | +1.82% | +6.60% | Yes |
| 2026-08-06 | +7.73% | +7.59% | Yes |
| 2026-09-18 | +7.54% | +2.53% | Yes |

## Backtest — trend rule (after costs) vs buy-and-hold vs benchmark

Period: 2025-01-14 to 2026-10-30 · 452 trading days · 27 entries · in the market 50.4% of the time · Costs: 20 bps charged per position change (entry and exit).

| | Total return | CAGR | Sharpe | Sortino | Max drawdown |
|---|---:|---:|---:|---:|---:|
| Trend strategy (after costs) | 29.1% | 15.3% | 0.9 | 0.9 | -12.8% |
| Buy and hold (this stock) | 47.0% | 24.0% | 0.87 | 1.18 | -30.2% |
| Buy and hold (benchmark) | 29.9% | 15.7% | 0.97 | 1.29 | -18.9% |

_Backtest caveats: single-ticker test (survivorship-conditional), costs are a stated assumption not a broker quote, past performance does not predict future results. Backtested performance is simulation, not live trading._
