# Arthon — Analysis Report: MRF.NS

- **Analysis date:** 2026-10-30
- **Data range:** 2021-11-01 to 2026-10-29 (1234 sessions)
- **Data source:** Yahoo Finance public chart API (INR (NSE/BSE)); benchmark: ^NSEI
- **Methodology:** Four statistical agents (quantitative/technical, fundamentals-context, forecast, risk) combined by a decision agent with disagreement handling; trend-rule backtest with transaction costs. Full methodology: docs/ARCHITECTURE.md in the project repository.
- **Assumptions & limits:** Free delayed/end-of-day data; statement fundamentals may be unavailable from the free endpoint and are then scored neutral, never invented; forecasts are simple trend models, not predictions. Educational project — not financial advice.

## Decision
**HOLD / WATCH — Low conviction**

- Weighted team score before disagreement adjustment: -0.21 (Analyst -0.60×0.40, Forecast +0.10×0.30, Fundamentals +0.05×0.10, Risk -0.05×0.20).
- Rating: HOLD / WATCH with low conviction.

**Bull case**
- Trend slope over 120 sessions implies +5.0% over the next 30 trading days.
- 20-day momentum is -4.1%; blended expected return: +1.7%.

**Bear / caution case**
- Price 118,065.00 is below the 20-day average (121,371.75) — downtrend pressure.
- Price 118,065.00 is below the 50-day average (125,946.20) — downtrend pressure.
- Annualised volatility (30-day): 10.5%.

## Agent Opinions

### Analyst Agent (quantitative / technical)
**Bearish technical picture** (score -0.60)

- Price 118,065.00 is below the 20-day average (121,371.75) — downtrend pressure.
- Price 118,065.00 is below the 50-day average (125,946.20) — downtrend pressure.
- Price 118,065.00 is below the 200-day average (132,089.35) — downtrend pressure.
- 20-day average below 50-day average (short-term trend weaker than medium-term).
- RSI is 21 — oversold, mean-reversion bounce is plausible.
- MACD is below its signal line — bearish momentum confirmation.
- Return over the last ~3 months: -12.0%.

| Metric | Value |
|---|---|
| price | 118065.0 |
| rsi_14 | 21.3 |
| return_3m_pct | -12.02 |

### Fundamentals Agent
**Fundamentals neutral or unavailable** (score +0.05)

- Statement fundamentals (P/E, ROE, margins) are not available from the free data endpoint (it requires authenticated access), so this agent scores neutral and relies on price-range context only. See docs/DATA_SOURCES.md.
- Price sits at 6% of its 52-week range (115,190.00 – 163,600.00).
- Near the bottom of the 52-week range — expectations already low (context only, not a buy signal).

| Metric | Value |
|---|---|
| position_in_52w_range_pct | 5.9 |
| statement_data_available | False |

### Forecast Agent
**Forecast is roughly flat** (score +0.10)

- Trend slope over 120 sessions implies +5.0% over the next 30 trading days.
- 20-day momentum is -4.1%; blended expected return: +1.7%.
- Point forecast: 120,058.28 (indicative band 108,609.92 – 131,506.64). Treat the band, not the point, as the forecast.

| Metric | Value |
|---|---|
| forecast_price_30d | 120058.28 |
| expected_return_30d_pct | 1.69 |
| band_low | 108609.92 |
| band_high | 131506.64 |

### Risk Agent
**Risk rating: Low** (score -0.05)

- Annualised volatility (30-day): 10.5%.
- Worst peak-to-trough drawdown in the period: -31.9%.
- Historical daily VaR (95%): -2.08% — on about 1 day in 20, losses were this large or worse.
- Historical daily CVaR (95%): -3.00% — the average of those worst days.
- Beta versus benchmark: 0.68 (correlation 0.42) — moves dampen the market.
- Volatility-target guide: keep any single position near or below ~14.3% of the portfolio.
- Overall risk rating: Low.

| Metric | Value |
|---|---|
| var_95_daily_pct | -2.08 |
| cvar_95_daily_pct | -3.0 |
| beta_vs_benchmark | 0.68 |
| correlation_vs_benchmark | 0.42 |
| volatility_annualised_pct | 10.5 |
| max_drawdown_pct | -31.9 |
| risk_rating | Low |
| suggested_max_position_pct | 14.3 |

## Forecast method — out-of-sample check

Walk-forward trials: 5 · Mean absolute error: 4.28 percentage points · Direction accuracy: 60.0%
_Small sample (<=6 origins) and one market regime at most — treat this as a sanity check on the method, not proof of predictive power._

| Origin | Predicted | Actual | Direction right? |
|---|---:|---:|:--:|
| 2026-03-19 | -3.67% | -0.44% | Yes |
| 2026-05-07 | -2.86% | -1.02% | Yes |
| 2026-06-19 | -5.11% | +3.95% | No |
| 2026-08-03 | -5.96% | -5.93% | Yes |
| 2026-09-15 | +1.09% | -6.14% | No |

## Backtest — trend rule (after costs) vs buy-and-hold vs benchmark

Period: 2022-01-11 to 2026-10-29 · 1185 trading days · 57 entries · in the market 43.6% of the time · Costs: 20 bps charged per position change (entry and exit).

| | Total return | CAGR | Sharpe | Sortino | Max drawdown |
|---|---:|---:|---:|---:|---:|
| Trend strategy (after costs) | -5.5% | -1.2% | -0.01 | -0.02 | -26.0% |
| Buy and hold (this stock) | 58.9% | 10.4% | 0.55 | 0.85 | -31.9% |
| Buy and hold (benchmark) | 27.4% | 5.3% | 0.44 | 0.62 | -16.5% |

_Backtest caveats: single-ticker test (survivorship-conditional), costs are a stated assumption not a broker quote, past performance does not predict future results. Backtested performance is simulation, not live trading._
