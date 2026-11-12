# Architecture

```mermaid
flowchart LR
    A[Yahoo Finance<br/>public chart API] --> B[Market Data Engine<br/>data.py: fetch, validate, cache]
    B --> C[Indicators<br/>indicators.py: SMA/EMA, RSI, MACD,<br/>Bollinger, volatility, drawdown]
    C --> D1[Analyst Agent<br/>trend & momentum]
    C --> D2[Fundamentals Agent<br/>valuation context, honest<br/>about unavailable data]
    C --> D3[Forecast Agent<br/>30-day trend model]
    C --> D4[Risk Agent<br/>vol, VaR/CVaR, beta,<br/>drawdown, sizing guide]
    D3 --> E[Forecast evaluation<br/>evaluation.py: walk-forward<br/>out-of-sample check]
    D1 --> F[Decision Agent<br/>weighted vote +<br/>disagreement handling]
    D2 --> F
    D3 --> F
    D4 --> F
    C --> G[Backtesting Engine<br/>backtest.py: no look-ahead,<br/>costs, benchmark, Sortino]
    F --> H[Reporting Engine<br/>report.py: Markdown<br/>committee-style report]
    E --> H
    G --> H
```

## Design rules
1. **Structured opinions.** Every agent returns an `Opinion` (score in
   [-1, +1], headline, evidence strings, metrics dict). The report renders
   evidence verbatim — claims in the output are traceable to the agent and
   the formula that produced them.
2. **No blind acceptance.** The Decision Agent checks the Analyst–Forecast
   spread; above 1.0 it shrinks the combined score by 25%, caps conviction,
   and records the disagreement in the report.
3. **Honest degradation.** Missing data (e.g. statement fundamentals)
   produces a neutral score plus an explicit note — never an estimate
   dressed up as data.
4. **No look-ahead.** Backtest signals are computed at the close and
   executed the next day; forecast evaluation is walk-forward.
5. **Costs are explicit and asset-aware.** Each asset class carries its own
   buy/sell bps profile (STT, brokerage, exchange charges; `costs.py`), a
   documented assumption — see `backtest.py`.

## Portfolio analytics
`cli.py --watchlist A,B,C` runs the full pipeline per ticker and ranks by
team score, writing one report per ticker. (Position-level portfolio
optimisation is intentionally not claimed; it is a roadmap item.)
