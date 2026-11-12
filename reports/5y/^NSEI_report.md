# Arthon — Analysis Report: ^NSEI

- **Analysis date:** 2026-10-30
- **Data range:** 2021-11-01 to 2026-10-29 (1234 sessions)
- **Data source:** Yahoo Finance public chart API (listing currency); benchmark: ^NSEI
- **Methodology:** Four statistical agents (quantitative/technical, fundamentals-context, forecast, risk) combined by a decision agent with disagreement handling; trend-rule backtest with transaction costs. Full methodology: docs/ARCHITECTURE.md in the project repository.
- **Assumptions & limits:** Free delayed/end-of-day data; statement fundamentals may be unavailable from the free endpoint and are then scored neutral, never invented; forecasts are simple trend models, not predictions. Educational project — not financial advice.

## Decision
**HOLD / WATCH — Low conviction**

- Weighted team score before disagreement adjustment: -0.06 (Analyst -0.15×0.40, Forecast +0.02×0.30, Fundamentals +0.00×0.10, Risk -0.05×0.20).
- Rating: HOLD / WATCH with low conviction.

**Bear / caution case**
- Price 22,936.75 is above the 20-day average (22,685.38) — uptrend intact.
- Price 22,936.75 is below the 50-day average (23,276.78) — downtrend pressure.
- Annualised volatility (30-day): 14.2%.

## Agent Opinions

### Analyst Agent (quantitative / technical)
**Mixed / sideways technical picture** (score -0.15)

- Price 22,936.75 is above the 20-day average (22,685.38) — uptrend intact.
- Price 22,936.75 is below the 50-day average (23,276.78) — downtrend pressure.
- Price 22,936.75 is below the 200-day average (24,056.78) — downtrend pressure.
- 20-day average below 50-day average (short-term trend weaker than medium-term).
- RSI is 65 — momentum is in the neutral zone.
- MACD is above its signal line — bullish momentum confirmation.
- Return over the last ~3 months: -5.4%.

| Metric | Value |
|---|---|
| price | 22936.75 |
| rsi_14 | 64.6 |
| return_3m_pct | -5.42 |

### Fundamentals Agent
**Fundamentals neutral or unavailable** (score +0.00)

- Statement fundamentals (P/E, ROE, margins) are not available from the free data endpoint (it requires authenticated access), so this agent scores neutral and relies on price-range context only. See docs/DATA_SOURCES.md.
- Price sits at 18% of its 52-week range (22,179.90 – 26,373.20).

| Metric | Value |
|---|---|
| position_in_52w_range_pct | 18.0 |
| statement_data_available | False |

### Forecast Agent
**Forecast is roughly flat** (score +0.02)

- Trend slope over 120 sessions implies -0.0% over the next 30 trading days.
- 20-day momentum is +1.0%; blended expected return: +0.4%.
- Point forecast: 23,030.64 (indicative band 21,608.06 – 24,453.23). Treat the band, not the point, as the forecast.

| Metric | Value |
|---|---|
| forecast_price_30d | 23030.64 |
| expected_return_30d_pct | 0.41 |
| band_low | 21608.06 |
| band_high | 24453.23 |

### Risk Agent
**Risk rating: Low** (score -0.05)

- Annualised volatility (30-day): 14.2%.
- Worst peak-to-trough drawdown in the period: -16.5%.
- Historical daily VaR (95%): -1.40% — on about 1 day in 20, losses were this large or worse.
- Historical daily CVaR (95%): -2.01% — the average of those worst days.
- Beta versus benchmark: 1.00 (correlation 1.00) — moves broadly with the market.
- Volatility-target guide: keep any single position near or below ~10.6% of the portfolio.
- Overall risk rating: Low.

| Metric | Value |
|---|---|
| var_95_daily_pct | -1.4 |
| cvar_95_daily_pct | -2.01 |
| beta_vs_benchmark | 1.0 |
| correlation_vs_benchmark | 1.0 |
| volatility_annualised_pct | 14.2 |
| max_drawdown_pct | -16.5 |
| risk_rating | Low |
| suggested_max_position_pct | 10.6 |

## Forecast method — out-of-sample check

Walk-forward trials: 5 · Mean absolute error: 3.72 percentage points · Direction accuracy: 60.0%
_Small sample (<=6 origins) and one market regime at most — treat this as a sanity check on the method, not proof of predictive power._

| Origin | Predicted | Actual | Direction right? |
|---|---:|---:|:--:|
| 2026-03-19 | +0.81% | +5.76% | Yes |
| 2026-05-07 | -1.75% | -1.29% | Yes |
| 2026-06-19 | -4.03% | +3.17% | No |
| 2026-08-03 | -3.24% | -6.68% | Yes |
| 2026-09-15 | +1.75% | -0.79% | No |

## Backtest — trend rule (after costs) vs buy-and-hold vs benchmark

Period: 2022-01-11 to 2026-10-29 · 1185 trading days · 72 entries · in the market 46.3% of the time · Costs: 20 bps charged per position change (entry and exit).

| | Total return | CAGR | Sharpe | Sortino | Max drawdown |
|---|---:|---:|---:|---:|---:|
| Trend strategy (after costs) | -11.7% | -2.6% | -0.28 | -0.32 | -17.2% |
| Buy and hold (this stock) | 27.4% | 5.3% | 0.44 | 0.62 | -16.5% |
| Buy and hold (benchmark) | 27.4% | 5.3% | 0.44 | 0.62 | -16.5% |

_Backtest caveats: single-ticker test (survivorship-conditional), costs are a stated assumption not a broker quote, past performance does not predict future results. Backtested performance is simulation, not live trading._
