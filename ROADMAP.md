# Roadmap

## v1 — 2026-10-31 (local prototype)
- [x] Yahoo Finance data layer with local caching (NSE/BSE/global)
- [x] Analyst, Forecast, Risk, Decision agents with evidence trails
- [x] Trend-rule backtest vs buy-and-hold (no look-ahead)
- [x] Markdown committee-style reports (6 tickers)

## v2 — 2026-10-31 (this public release)
- [x] Fundamentals Agent with honest data-availability handling
- [x] Risk Agent: historical VaR/CVaR, beta & correlation vs benchmark
- [x] Backtest: asset-aware transaction costs (per-asset broker/STT profiles), Sortino, benchmark comparison
- [x] Forecast method evaluated walk-forward, out-of-sample, in every report
- [x] Decision Agent disagreement detection and conviction capping
- [x] Portfolio/watchlist mode with team-score ranking
- [x] Unit tests (10) + GitHub Actions CI
- [x] Data-licensing gate: Yahoo cached CSVs excluded from the repo
- [x] Fixed RSI undefined on flat price series (neutral-50 convention)

## v3 — next
- [ ] Plug the real Kronos foundation model in behind `ForecastAgent`
- [ ] Licensed fundamentals provider (statement data) behind `fetch_fundamentals`
- [ ] News/Sentiment Agent
- [ ] LLM debate layer (agents argue in natural language before the decision)
- [ ] Survivorship-bias-free universe backtests; portfolio optimisation
- [ ] Choose a licence (pending maintainer decision) and add LICENSE
