# Finance AI — Analysis Report: INFY.NS

- **Analysis date:** 2026-10-30
- **Data range:** 2021-11-01 to 2026-10-29 (1235 sessions)
- **Data source:** Yahoo Finance public chart API (INR (NSE/BSE)); benchmark: ^NSEI
- **Methodology:** Four statistical agents (quantitative/technical, fundamentals-context, forecast, risk) combined by a decision agent with disagreement handling; trend-rule backtest with transaction costs. Full methodology: docs/ARCHITECTURE.md in the project repository.
- **Assumptions & limits:** Free delayed/end-of-day data; statement fundamentals may be unavailable from the free endpoint and are then scored neutral, never invented; forecasts are simple trend models, not predictions. Educational project — not financial advice.

## Decision
**HOLD / WATCH — Low conviction**

- Weighted team score before disagreement adjustment: +0.04 (Analyst +0.30×0.40, Forecast -0.00×0.30, Fundamentals +0.00×0.10, Risk -0.40×0.20).
- Rating: HOLD / WATCH with low conviction.

**Bull case**
- Price 1,146.50 is above the 20-day average (1,086.08) — uptrend intact.
- Price 1,146.50 is above the 50-day average (1,083.88) — uptrend intact.

**Bear / caution case**
- Annualised volatility (30-day): 33.5%.

## Agent Opinions

### Analyst Agent (quantitative / technical)
**Bullish technical picture** (score +0.30)

- Price 1,146.50 is above the 20-day average (1,086.08) — uptrend intact.
- Price 1,146.50 is above the 50-day average (1,083.88) — uptrend intact.
- Price 1,146.50 is below the 200-day average (1,217.32) — downtrend pressure.
- 20-day average above 50-day average (short-term trend stronger than medium-term).
- RSI is 72 — overbought, momentum may be stretched.
- MACD is above its signal line — bullish momentum confirmation.
- Return over the last ~3 months: -0.8%.

| Metric | Value |
|---|---|
| price | 1146.5 |
| rsi_14 | 72.5 |
| return_3m_pct | -0.79 |

### Fundamentals Agent
**Fundamentals neutral or unavailable** (score +0.00)

- Statement fundamentals (P/E, ROE, margins) are not available from the free data endpoint (it requires authenticated access), so this agent scores neutral and relies on price-range context only. See docs/DATA_SOURCES.md.
- Price sits at 22% of its 52-week range (980.40 – 1,728.00).

| Metric | Value |
|---|---|
| position_in_52w_range_pct | 22.2 |
| statement_data_available | False |

### Forecast Agent
**Forecast is roughly flat** (score -0.00)

- Trend slope over 120 sessions implies -8.4% over the next 30 trading days.
- 20-day momentum is +12.9%; blended expected return: -0.1%.
- Point forecast: 1,145.65 (indicative band 980.39 – 1,310.92). Treat the band, not the point, as the forecast.

| Metric | Value |
|---|---|
| forecast_price_30d | 1145.65 |
| expected_return_30d_pct | -0.07 |
| band_low | 980.39 |
| band_high | 1310.92 |

### Risk Agent
**Risk rating: Elevated** (score -0.40)

- Annualised volatility (30-day): 33.5%.
- Worst peak-to-trough drawdown in the period: -50.7%.
- Historical daily VaR (95%): -2.64% — on about 1 day in 20, losses were this large or worse.
- Historical daily CVaR (95%): -3.82% — the average of those worst days.
- Beta versus benchmark: 0.96 (correlation 0.51) — moves broadly with the market.
- Drawdown history is severe — position size should be small.
- Volatility-target guide: keep any single position near or below ~4.5% of the portfolio.
- Overall risk rating: Elevated.

| Metric | Value |
|---|---|
| var_95_daily_pct | -2.64 |
| cvar_95_daily_pct | -3.82 |
| beta_vs_benchmark | 0.96 |
| correlation_vs_benchmark | 0.51 |
| volatility_annualised_pct | 33.5 |
| max_drawdown_pct | -50.7 |
| risk_rating | Elevated |
| suggested_max_position_pct | 4.5 |

## Forecast method — out-of-sample check

Walk-forward trials: 5 · Mean absolute error: 9.42 percentage points · Direction accuracy: 40.0%
_Small sample (<=6 origins) and one market regime at most — treat this as a sanity check on the method, not proof of predictive power._

| Origin | Predicted | Actual | Direction right? |
|---|---:|---:|:--:|
| 2026-03-19 | +4.61% | -4.76% | No |
| 2026-05-07 | -8.88% | -9.57% | Yes |
| 2026-06-19 | -10.51% | +12.23% | No |
| 2026-08-03 | -6.75% | -8.73% | Yes |
| 2026-09-15 | -5.88% | +6.45% | No |

## Backtest — trend rule (after costs) vs buy-and-hold vs benchmark

Period: 2022-01-11 to 2026-10-29 · 1186 trading days · 56 entries · in the market 42.3% of the time · Costs: 20 bps charged per position change (entry and exit).

| | Total return | CAGR | Sharpe | Sortino | Max drawdown |
|---|---:|---:|---:|---:|---:|
| Trend strategy (after costs) | -19.9% | -4.6% | -0.21 | -0.2 | -30.5% |
| Buy and hold (this stock) | -38.1% | -9.7% | -0.25 | -0.36 | -50.7% |
| Buy and hold (benchmark) | 27.4% | 5.3% | 0.44 | 0.62 | -16.5% |

_Backtest caveats: single-ticker test (survivorship-conditional), costs are a stated assumption not a broker quote, past performance does not predict future results. Backtested performance is simulation, not live trading._
