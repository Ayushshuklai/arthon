# Finance AI — Analysis Report: TCS.NS

- **Analysis date:** 2026-10-30
- **Data range:** 2024-10-30 to 2026-10-29 (495 sessions)
- **Data source:** Yahoo Finance public chart API (INR (NSE/BSE)); benchmark: ^NSEI
- **Methodology:** Four statistical agents (quantitative/technical, fundamentals-context, forecast, risk) combined by a decision agent with disagreement handling; trend-rule backtest with transaction costs. Full methodology: docs/ARCHITECTURE.md in the project repository.
- **Assumptions & limits:** Free delayed/end-of-day data; statement fundamentals may be unavailable from the free endpoint and are then scored neutral, never invented; forecasts are simple trend models, not predictions. Educational project — not financial advice.

## Decision
**HOLD / WATCH — Low conviction**

- Weighted team score before disagreement adjustment: +0.24 (Analyst +0.60×0.40, Forecast +0.28×0.30, Fundamentals +0.00×0.10, Risk -0.40×0.20).
- Rating: HOLD / WATCH with low conviction.

**Bull case**
- Price 2,478.00 is above the 20-day average (2,308.16) — uptrend intact.
- Price 2,478.00 is above the 50-day average (2,259.64) — uptrend intact.
- Trend slope over 120 sessions implies -7.4% over the next 30 trading days.
- 20-day momentum is +21.9%; blended expected return: +4.7%.

**Bear / caution case**
- Annualised volatility (30-day): 35.0%.

## Agent Opinions

### Analyst Agent (quantitative / technical)
**Bullish technical picture** (score +0.60)

- Price 2,478.00 is above the 20-day average (2,308.16) — uptrend intact.
- Price 2,478.00 is above the 50-day average (2,259.64) — uptrend intact.
- Price 2,478.00 is above the 200-day average (2,435.74) — uptrend intact.
- 20-day average above 50-day average (short-term trend stronger than medium-term).
- RSI is 80 — overbought, momentum may be stretched.
- MACD is above its signal line — bullish momentum confirmation.
- Return over the last ~3 months: +1.3%.

| Metric | Value |
|---|---|
| price | 2478.0 |
| rsi_14 | 80.2 |
| return_3m_pct | 1.28 |

### Fundamentals Agent
**Fundamentals neutral or unavailable** (score +0.00)

- Statement fundamentals (P/E, ROE, margins) are not available from the free data endpoint (it requires authenticated access), so this agent scores neutral and relies on price-range context only. See docs/DATA_SOURCES.md.
- Price sits at 36% of its 52-week range (1,976.80 – 3,350.00).

| Metric | Value |
|---|---|
| position_in_52w_range_pct | 36.5 |
| statement_data_available | False |

### Forecast Agent
**Forecast points up** (score +0.28)

- Trend slope over 120 sessions implies -7.4% over the next 30 trading days.
- 20-day momentum is +21.9%; blended expected return: +4.7%.
- Point forecast: 2,594.38 (indicative band 2,178.16 – 3,010.61). Treat the band, not the point, as the forecast.

| Metric | Value |
|---|---|
| forecast_price_30d | 2594.38 |
| expected_return_30d_pct | 4.7 |
| band_low | 2178.16 |
| band_high | 3010.61 |

### Risk Agent
**Risk rating: Elevated** (score -0.40)

- Annualised volatility (30-day): 35.0%.
- Worst peak-to-trough drawdown in the period: -55.7%.
- Historical daily VaR (95%): -2.62% — on about 1 day in 20, losses were this large or worse.
- Historical daily CVaR (95%): -3.78% — the average of those worst days.
- Beta versus benchmark: 0.87 (correlation 0.44) — moves broadly with the market.
- Drawdown history is severe — position size should be small.
- Volatility-target guide: keep any single position near or below ~4.3% of the portfolio.
- Overall risk rating: Elevated.

| Metric | Value |
|---|---|
| var_95_daily_pct | -2.62 |
| cvar_95_daily_pct | -3.78 |
| beta_vs_benchmark | 0.87 |
| correlation_vs_benchmark | 0.44 |
| volatility_annualised_pct | 35.0 |
| max_drawdown_pct | -55.7 |
| risk_rating | Elevated |
| suggested_max_position_pct | 4.3 |

## Forecast method — out-of-sample check

Walk-forward trials: 5 · Mean absolute error: 9.99 percentage points · Direction accuracy: 60.0%
_Small sample (<=6 origins) and one market regime at most — treat this as a sanity check on the method, not proof of predictive power._

| Origin | Predicted | Actual | Direction right? |
|---|---:|---:|:--:|
| 2026-03-19 | +3.67% | +1.93% | Yes |
| 2026-05-07 | -9.19% | -11.51% | Yes |
| 2026-06-19 | -11.80% | +16.41% | No |
| 2026-08-03 | -5.11% | -9.00% | Yes |
| 2026-09-15 | -3.69% | +10.08% | No |

## Backtest — trend rule (after costs) vs buy-and-hold vs benchmark

Period: 2025-01-10 to 2026-10-29 · 446 trading days · 18 entries · in the market 26.5% of the time · Costs: 20 bps charged per position change (entry and exit).

| | Total return | CAGR | Sharpe | Sortino | Max drawdown |
|---|---:|---:|---:|---:|---:|
| Trend strategy (after costs) | -24.9% | -15.0% | -1.08 | -0.71 | -30.0% |
| Buy and hold (this stock) | -38.6% | -24.1% | -0.92 | -1.34 | -53.8% |
| Buy and hold (benchmark) | -2.5% | -1.4% | -0.04 | -0.07 | -15.6% |

_Backtest caveats: single-ticker test (survivorship-conditional), costs are a stated assumption not a broker quote, past performance does not predict future results. Backtested performance is simulation, not live trading._
