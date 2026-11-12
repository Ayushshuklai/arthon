"""Markdown investment-committee style report with full traceability."""
from __future__ import annotations
from .agents import Opinion

def _section(o: Opinion) -> list[str]:
    lines = [f"### {o.agent}", f"**{o.headline}** (score {o.score:+.2f})", ""]
    lines += [f"- {e}" for e in o.evidence]
    if o.metrics:
        lines += ["", "| Metric | Value |", "|---|---|"]
        lines += [f"| {k} | {v} |" for k, v in o.metrics.items() if k not in ("bull_points", "bear_points")]
    lines.append("")
    return lines

def build_report(symbol: str, meta: dict, opinions: list[Opinion], decision: Opinion,
                 backtest: dict, forecast_eval: dict) -> str:
    L = [f"# Finance AI — Analysis Report: {symbol}", "",
         f"- **Analysis date:** {meta['analysis_date']}",
         f"- **Data range:** {meta['data_range']} ({meta['sessions']} sessions)",
         f"- **Data source:** Yahoo Finance public chart API ({meta['currency_note']}); benchmark: {meta['benchmark']}",
         "- **Methodology:** Four statistical agents (quantitative/technical, fundamentals-context, forecast, risk) "
         "combined by a decision agent with disagreement handling; trend-rule backtest with transaction costs. "
         "Full methodology: docs/ARCHITECTURE.md in the project repository.",
         "- **Assumptions & limits:** Free delayed/end-of-day data; statement fundamentals may be unavailable from the "
         "free endpoint and are then scored neutral, never invented; forecasts are simple trend models, not predictions. "
         "Educational project — not financial advice.", "",
         "## Decision", f"**{decision.headline}**", ""]
    L += [f"- {e}" for e in decision.evidence]
    bulls = decision.metrics.get("bull_points") or []
    bears = decision.metrics.get("bear_points") or []
    if bulls: L += ["", "**Bull case**"] + [f"- {b}" for b in bulls]
    if bears: L += ["", "**Bear / caution case**"] + [f"- {b}" for b in bears]
    L += ["", "## Agent Opinions", ""]
    for o in opinions: L += _section(o)
    L += ["## Forecast method — out-of-sample check", ""]
    if forecast_eval.get("observations"):
        L += [f"Walk-forward trials: {forecast_eval['observations']} · Mean absolute error: "
              f"{forecast_eval['mean_absolute_error_pct_points']} percentage points · Direction accuracy: "
              f"{forecast_eval['direction_accuracy_pct']}%",
              f"_{forecast_eval['note']}_", "", "| Origin | Predicted | Actual | Direction right? |", "|---|---:|---:|:--:|"]
        for t in forecast_eval["trials"]:
            L.append(f"| {t['origin_date']} | {t['predicted_pct']:+.2f}% | {t['actual_pct']:+.2f}% | {'Yes' if t['direction_correct'] else 'No'} |")
    else:
        L.append(forecast_eval.get("note", "Not evaluated."))
    L += ["", "## Backtest — trend rule (after costs) vs buy-and-hold vs benchmark", "",
          f"Period: {backtest.get('period')} · {backtest.get('trading_days')} trading days · "
          f"{backtest.get('entries')} entries · in the market {backtest.get('time_in_market_pct')}% of the time · "
          f"Costs: {backtest.get('cost_assumption')}.", "",
          "| | Total return | CAGR | Sharpe | Sortino | Max drawdown |", "|---|---:|---:|---:|---:|---:|"]
    for label, key in [("Trend strategy (after costs)", "strategy_after_costs"), ("Buy and hold (this stock)", "buy_and_hold"),
                       ("Buy and hold (benchmark)", "benchmark_buy_and_hold")]:
        s = backtest.get(key)
        if s: L.append(f"| {label} | {s.get('total_return_pct')}% | {s.get('cagr_pct')}% | {s.get('sharpe')} | {s.get('sortino')} | {s.get('max_drawdown_pct')}% |")
    L += ["", "_Backtest caveats: single-ticker test (survivorship-conditional), costs are a stated assumption not a broker quote, "
          "past performance does not predict future results. Backtested performance is simulation, not live trading._", ""]
    return "\n".join(L)
