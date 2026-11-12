# Finance AI — Analysis Report: HDFCBANK.NS

- **Analysis date:** 2026-10-30
- **Data range:** 2024-10-30 to 2026-10-29 (495 sessions)
- **Data source:** Yahoo Finance public chart API (INR (NSE/BSE)); benchmark: ^NSEI
- **Methodology:** Four statistical agents (quantitative/technical, fundamentals-context, forecast, risk) combined by a decision agent with disagreement handling; trend-rule backtest with transaction costs. Full methodology: docs/ARCHITECTURE.md in the project repository.
- **Assumptions & limits:** Free delayed/end-of-day data; statement fundamentals may be unavailable from the free endpoint and are then scored neutral, never invented; forecasts are simple trend models, not predictions. Educational project — not financial advice.

## Decision
**SELL / AVOID — Medium conviction**

- Weighted team score before disagreement adjustment: -0.38 (Analyst -0.75×0.40, Forecast -0.17×0.30, Fundamentals +0.05×0.10, Risk -0.15×0.20).
- Rating: SELL / AVOID with medium conviction.

**Bear / caution case**
- Price 683.30 is below the 20-day average (703.82) — downtrend pressure.
- Price 683.30 is below the 50-day average (712.66) — downtrend pressure.
- Trend slope over 120 sessions implies -0.6% over the next 30 trading days.
- 20-day momentum is -5.5%; blended expected return: -2.9%.
- Annualised volatility (30-day): 22.2%.

## Agent Opinions

### Analyst Agent (quantitative / technical)
**Bearish technical picture** (score -0.75)

- Price 683.30 is below the 20-day average (703.82) — downtrend pressure.
- Price 683.30 is below the 50-day average (712.66) — downtrend pressure.
- Price 683.30 is below the 200-day average (790.81) — downtrend pressure.
- 20-day average below 50-day average (short-term trend weaker than medium-term).
- RSI is 46 — momentum is in the neutral zone.
- MACD is below its signal line — bearish momentum confirmation.
- Return over the last ~3 months: -8.7%.

| Metric | Value |
|---|---|
| price | 683.3 |
| rsi_14 | 45.7 |
| return_3m_pct | -8.67 |

### Fundamentals Agent
**Fundamentals neutral or unavailable** (score +0.05)

- Statement fundamentals (P/E, ROE, margins) are not available from the free data endpoint (it requires authenticated access), so this agent scores neutral and relies on price-range context only. See docs/DATA_SOURCES.md.
- Price sits at 4% of its 52-week range (669.20 – 1,020.50).
- Near the bottom of the 52-week range — expectations already low (context only, not a buy signal).

| Metric | Value |
|---|---|
| position_in_52w_range_pct | 4.0 |
| statement_data_available | False |

### Forecast Agent
**Forecast is roughly flat** (score -0.17)

- Trend slope over 120 sessions implies -0.6% over the next 30 trading days.
- 20-day momentum is -5.5%; blended expected return: -2.9%.
- Point forecast: 663.78 (indicative band 603.10 – 724.46). Treat the band, not the point, as the forecast.

| Metric | Value |
|---|---|
| forecast_price_30d | 663.78 |
| expected_return_30d_pct | -2.86 |
| band_low | 603.1 |
| band_high | 724.46 |

### Risk Agent
**Risk rating: Moderate** (score -0.15)

- Annualised volatility (30-day): 22.2%.
- Worst peak-to-trough drawdown in the period: -32.8%.
- Historical daily VaR (95%): -2.10% — on about 1 day in 20, losses were this large or worse.
- Historical daily CVaR (95%): -2.81% — the average of those worst days.
- Beta versus benchmark: 1.07 (correlation 0.72) — moves broadly with the market.
- Volatility-target guide: keep any single position near or below ~6.8% of the portfolio.
- Overall risk rating: Moderate.

| Metric | Value |
|---|---|
| var_95_daily_pct | -2.1 |
| cvar_95_daily_pct | -2.81 |
| beta_vs_benchmark | 1.07 |
| correlation_vs_benchmark | 0.72 |
| volatility_annualised_pct | 22.2 |
| max_drawdown_pct | -32.8 |
| risk_rating | Moderate |
| suggested_max_position_pct | 6.8 |

## Forecast method — out-of-sample check

Walk-forward trials: 5 · Mean absolute error: 3.29 percentage points · Direction accuracy: 100.0%
_Small sample (<=6 origins) and one market regime at most — treat this as a sanity check on the method, not proof of predictive power._

| Origin | Predicted | Actual | Direction right? |
|---|---:|---:|:--:|
| 2026-03-19 | -1.16% | -0.27% | Yes |
| 2026-05-07 | -5.83% | -2.04% | Yes |
| 2026-06-19 | -8.68% | -3.44% | Yes |
| 2026-08-03 | -7.80% | -4.84% | Yes |
| 2026-09-15 | -1.07% | -4.64% | Yes |

## Backtest — trend rule (after costs) vs buy-and-hold vs benchmark

Period: 2025-01-10 to 2026-10-29 · 446 trading days · 21 entries · in the market 39.7% of the time · Costs: 20 bps charged per position change (entry and exit).

| | Total return | CAGR | Sharpe | Sortino | Max drawdown |
|---|---:|---:|---:|---:|---:|
| Trend strategy (after costs) | -10.2% | -5.9% | -0.47 | -0.44 | -19.2% |
| Buy and hold (this stock) | -18.1% | -10.6% | -0.47 | -0.68 | -32.8% |
| Buy and hold (benchmark) | -2.5% | -1.4% | -0.04 | -0.07 | -15.6% |

_Backtest caveats: single-ticker test (survivorship-conditional), costs are a stated assumption not a broker quote, past performance does not predict future results. Backtested performance is simulation, not live trading._
