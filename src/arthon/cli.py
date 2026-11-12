"""Command line entry points.

Single stock:   python -m arthon.cli RELIANCE.NS [--years 2] [--out reports]
Watchlist:      python -m arthon.cli --watchlist RELIANCE.NS,TCS.NS,MRF.NS
"""
from __future__ import annotations
import argparse, logging, os, sys
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from arthon.data import fetch_prices, fetch_fundamentals, benchmark_for
from arthon.indicators import add_indicators
from arthon.agents import AnalystAgent, FundamentalsAgent, ForecastAgent, RiskAgent, DecisionAgent
from arthon.backtest import run_backtest
from arthon.evaluation import evaluate_forecast_method
from arthon.report import build_report

logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")

def analyse(symbol: str, years: int = 2) -> tuple[str, dict]:
    symbol = symbol.upper()
    raw = fetch_prices(symbol, years=years)
    if len(raw) < 220:
        raise SystemExit(f"Only {len(raw)} sessions for {symbol}; need ~220+ for the 200-day average. Try --years 5.")
    df = add_indicators(raw)
    bench_symbol = benchmark_for(symbol)
    try:
        bench = fetch_prices(bench_symbol, years=years)
    except Exception:
        bench = None
    fundamentals = fetch_fundamentals(symbol)
    analyst = AnalystAgent().run(df)
    fund = FundamentalsAgent().run(df, fundamentals)
    forecast = ForecastAgent().run(df)
    risk = RiskAgent().run(df, bench)
    decision = DecisionAgent().run(analyst, forecast, fund, risk)
    bt = run_backtest(df, bench, symbol=symbol)
    fe = evaluate_forecast_method(df)
    meta = {"analysis_date": str(date.today()), "data_range": f"{raw['date'].iloc[0].date()} to {raw['date'].iloc[-1].date()}",
            "sessions": len(raw), "benchmark": bench_symbol,
            "currency_note": "INR (NSE/BSE)" if symbol.endswith((".NS", ".BO")) else "listing currency"}
    report = build_report(symbol, meta, [analyst, fund, forecast, risk], decision, bt, fe)
    return report, decision.metrics

def main() -> None:
    p = argparse.ArgumentParser(description="Multi-agent stock analysis")
    p.add_argument("symbol", nargs="?", help="Ticker, e.g. RELIANCE.NS, TCS.NS, AAPL")
    p.add_argument("--watchlist", help="Comma-separated tickers to analyse and rank")
    p.add_argument("--years", type=int, default=2)
    p.add_argument("--out", default="reports")
    args = p.parse_args()
    os.makedirs(args.out, exist_ok=True)
    if args.watchlist:
        rows = []
        for sym in [s.strip() for s in args.watchlist.split(",") if s.strip()]:
            report, m = analyse(sym, args.years)
            path = os.path.join(args.out, f"{sym.upper().replace('.', '_')}_report.md")
            open(path, "w").write(report)
            rows.append((m.get("team_score", 0), sym.upper(), m.get("rating"), m.get("conviction")))
        rows.sort(reverse=True)
        print("Watchlist ranking by team score:")
        for score, sym, rating, conv in rows:
            print(f"  {sym:<14} {score:+.2f}  {rating} ({conv} conviction)")
        return
    if not args.symbol:
        p.error("provide a symbol or --watchlist")
    report, m = analyse(args.symbol, args.years)
    path = os.path.join(args.out, f"{args.symbol.upper().replace('.', '_')}_report.md")
    open(path, "w").write(report)
    print(f"Rating: {m.get('rating')} ({m.get('conviction')} conviction, team score {m.get('team_score')})")
    print(f"Report written to {path}")

if __name__ == "__main__":
    main()
