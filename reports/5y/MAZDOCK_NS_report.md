# Finance AI — Analysis Report: MAZDOCK.NS

- **Analysis date:** 2026-10-30
- **Data range:** 2021-11-01 to 2026-10-29 (1235 sessions)
- **Data source:** Yahoo Finance public chart API (INR (NSE/BSE)); benchmark: ^NSEI
- **Methodology:** Four statistical agents (quantitative/technical, fundamentals-context, forecast, risk) combined by a decision agent with disagreement handling; trend-rule backtest with transaction costs. Full methodology: docs/ARCHITECTURE.md in the project repository.
- **Assumptions & limits:** Free delayed/end-of-day data; statement fundamentals may be unavailable from the free endpoint and are then scored neutral, never invented; forecasts are simple trend models, not predictions. Educational project — not financial advice.

## Decision
**SELL / AVOID — Medium conviction**

- Weighted team score before disagreement adjustment: -0.33 (Analyst -0.75×0.40, Forecast +0.15×0.30, Fundamentals +0.05×0.10, Risk -0.40×0.20).
- Rating: SELL / AVOID with medium conviction.

**Bull case**
- Trend slope over 120 sessions implies +13.6% over the next 30 trading days.
- 20-day momentum is -15.5%; blended expected return: +2.5%.

**Bear / caution case**
- Price 1,762.70 is below the 20-day average (1,992.05) — downtrend pressure.
- Price 1,762.70 is below the 50-day average (2,233.77) — downtrend pressure.
- Annualised volatility (30-day): 35.4%.

## Agent Opinions

### Analyst Agent (quantitative / technical)
**Bearish technical picture** (score -0.75)

- Price 1,762.70 is below the 20-day average (1,992.05) — downtrend pressure.
- Price 1,762.70 is below the 50-day average (2,233.77) — downtrend pressure.
- Price 1,762.70 is below the 200-day average (2,388.33) — downtrend pressure.
- 20-day average below 50-day average (short-term trend weaker than medium-term).
- RSI is 31 — momentum is in the neutral zone.
- MACD is below its signal line — bearish momentum confirmation.
- Return over the last ~3 months: -23.6%.

| Metric | Value |
|---|---|
| price | 1762.7 |
| rsi_14 | 30.6 |
| return_3m_pct | -23.62 |

### Fundamentals Agent
**Fundamentals neutral or unavailable** (score +0.05)

- Statement fundamentals (P/E, ROE, margins) are not available from the free data endpoint (it requires authenticated access), so this agent scores neutral and relies on price-range context only. See docs/DATA_SOURCES.md.
- Price sits at 6% of its 52-week range (1,687.50 – 2,881.80).
- Near the bottom of the 52-week range — expectations already low (context only, not a buy signal).

| Metric | Value |
|---|---|
| position_in_52w_range_pct | 6.3 |
| statement_data_available | False |

### Forecast Agent
**Forecast is roughly flat** (score +0.15)

- Trend slope over 120 sessions implies +13.6% over the next 30 trading days.
- 20-day momentum is -15.5%; blended expected return: +2.5%.
- Point forecast: 1,806.84 (indicative band 1,477.77 – 2,135.92). Treat the band, not the point, as the forecast.

| Metric | Value |
|---|---|
| forecast_price_30d | 1806.84 |
| expected_return_30d_pct | 2.5 |
| band_low | 1477.77 |
| band_high | 2135.92 |

### Risk Agent
**Risk rating: Elevated** (score -0.40)

- Annualised volatility (30-day): 35.4%.
- Worst peak-to-trough drawdown in the period: -53.8%.
- Historical daily VaR (95%): -4.10% — on about 1 day in 20, losses were this large or worse.
- Historical daily CVaR (95%): -5.95% — the average of those worst days.
- Beta versus benchmark: 1.39 (correlation 0.38) — moves amplify the market.
- Drawdown history is severe — position size should be small.
- Volatility-target guide: keep any single position near or below ~4.2% of the portfolio.
- Overall risk rating: Elevated.

| Metric | Value |
|---|---|
| var_95_daily_pct | -4.1 |
| cvar_95_daily_pct | -5.95 |
| beta_vs_benchmark | 1.39 |
| correlation_vs_benchmark | 0.38 |
| volatility_annualised_pct | 35.4 |
| max_drawdown_pct | -53.8 |
| risk_rating | Elevated |
| suggested_max_position_pct | 4.2 |

## Forecast method — out-of-sample check

Walk-forward trials: 5 · Mean absolute error: 11.81 percentage points · Direction accuracy: 40.0%
_Small sample (<=6 origins) and one market regime at most — treat this as a sanity check on the method, not proof of predictive power._

| Origin | Predicted | Actual | Direction right? |
|---|---:|---:|:--:|
| 2026-03-19 | -6.94% | +13.63% | No |
| 2026-05-07 | -1.82% | -6.13% | Yes |
| 2026-06-19 | +0.54% | -5.11% | No |
| 2026-08-03 | -0.54% | -6.44% | Yes |
| 2026-09-15 | +1.47% | -21.17% | No |

## Backtest — trend rule (after costs) vs buy-and-hold vs benchmark

Period: 2022-01-11 to 2026-10-29 · 1186 trading days · 67 entries · in the market 39.7% of the time · Costs: 20 bps charged per position change (entry and exit).

| | Total return | CAGR | Sharpe | Sortino | Max drawdown |
|---|---:|---:|---:|---:|---:|
| Trend strategy (after costs) | 168.9% | 23.4% | 0.77 | 0.96 | -42.9% |
| Buy and hold (this stock) | 1158.6% | 71.3% | 1.3 | 2.34 | -53.8% |
| Buy and hold (benchmark) | 27.4% | 5.3% | 0.44 | 0.62 | -16.5% |

_Backtest caveats: single-ticker test (survivorship-conditional), costs are a stated assumption not a broker quote, past performance does not predict future results. Backtested performance is simulation, not live trading._
