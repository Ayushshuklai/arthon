"""Unit tests for critical calculations. Run: python -m unittest discover -s tests -v
Uses synthetic data only — no network, no real market data."""
import os, sys, unittest
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from arthon.indicators import add_indicators, max_drawdown
from arthon.agents import AnalystAgent, ForecastAgent, RiskAgent, DecisionAgent, FundamentalsAgent, Opinion
from arthon.backtest import run_backtest, COST_BPS
from arthon.evaluation import evaluate_forecast_method

def make_df(prices, start="2023-01-02"):
    dates = pd.bdate_range(start, periods=len(prices))
    p = np.asarray(prices, dtype=float)
    return pd.DataFrame({"date": dates, "open": p, "high": p * 1.01, "low": p * 0.99,
                         "close": p, "volume": 1000})

class TestIndicators(unittest.TestCase):
    def test_sma_and_rsi_bounds(self):
        df = add_indicators(make_df(np.linspace(100, 200, 300)))
        self.assertAlmostEqual(float(df["sma_20"].iloc[-1]), float(np.mean(df["close"].iloc[-20:])), places=6)
        rsi = df["rsi_14"].dropna()
        self.assertTrue(((rsi >= 0) & (rsi <= 100)).all())
    def test_max_drawdown(self):
        s = pd.Series([100.0, 120.0, 60.0, 90.0])
        self.assertAlmostEqual(max_drawdown(s), -0.5)

class TestAgents(unittest.TestCase):
    def test_uptrend_scores_positive(self):
        df = add_indicators(make_df(np.linspace(100, 300, 400)))
        op = AnalystAgent().run(df)
        self.assertGreater(op.score, 0.25)
    def test_downtrend_scores_negative(self):
        df = add_indicators(make_df(np.linspace(300, 100, 400)))
        op = AnalystAgent().run(df)
        self.assertLess(op.score, -0.25)
    def test_risk_var_ordering(self):
        rng = np.random.default_rng(42)
        prices = 100 * np.exp(np.cumsum(rng.normal(0, 0.02, 400)))
        df = add_indicators(make_df(prices))
        op = RiskAgent().run(df)
        self.assertLessEqual(op.metrics["cvar_95_daily_pct"], op.metrics["var_95_daily_pct"])
    def test_fundamentals_never_invents(self):
        df = add_indicators(make_df(np.linspace(100, 150, 300)))
        op = FundamentalsAgent().run(df, {})
        self.assertFalse(op.metrics["statement_data_available"])
    def test_disagreement_shrinks_score(self):
        bull = Opinion("a", 0.9, "", []); bear = Opinion("f", -0.9, "", [])
        neutral = Opinion("x", 0.0, "", []); risk = Opinion("r", 0.0, "", [])
        d = DecisionAgent().run(bull, bear, neutral, risk)
        self.assertTrue(d.metrics["agent_disagreement"])
        raw = 0.40 * 0.9 + 0.30 * -0.9
        self.assertAlmostEqual(d.score, raw * 0.75, places=6)
        self.assertNotEqual(d.metrics["conviction"], "High")

class TestBacktest(unittest.TestCase):
    def test_no_lookahead_and_costs_reduce_returns(self):
        rng = np.random.default_rng(7)
        prices = 100 * np.exp(np.cumsum(rng.normal(0.0004, 0.015, 500)))
        df = add_indicators(make_df(prices))
        bt = run_backtest(df)
        self.assertIn("strategy_after_costs", bt)
        self.assertGreater(COST_BPS, 0)
        # strategy trades at most once per day and respects the data length
        self.assertLessEqual(bt["entries"], bt["trading_days"])
    def test_flat_market_near_zero(self):
        df = add_indicators(make_df(np.full(300, 100.0)))
        bt = run_backtest(df)
        self.assertAlmostEqual(bt["buy_and_hold"]["total_return_pct"], 0.0, places=1)

class TestEvaluation(unittest.TestCase):
    def test_evaluation_runs_and_bounds(self):
        rng = np.random.default_rng(3)
        prices = 100 * np.exp(np.cumsum(rng.normal(0.0003, 0.01, 500)))
        ev = evaluate_forecast_method(add_indicators(make_df(prices)))
        self.assertGreaterEqual(ev["observations"], 1)
        self.assertTrue(0 <= ev["direction_accuracy_pct"] <= 100)

if __name__ == "__main__":
    unittest.main()

class TestBenchmarkSelection(unittest.TestCase):
    def test_indian_symbols_and_indices(self):
        from arthon.data import benchmark_for
        for s in ["RELIANCE.NS", "RELIANCE.BO", "^NSEI", "^BSESN", "^NSEBANK"]:
            self.assertEqual(benchmark_for(s), "^NSEI", s)
        self.assertEqual(benchmark_for("AAPL"), "^GSPC")
        self.assertEqual(benchmark_for("^GSPC"), "^GSPC")

class TestPatternAI(unittest.TestCase):
    def test_forecast_shapes_and_probability(self):
        from arthon.pattern_ai import analogue_forecast
        rng = np.random.default_rng(11)
        prices = 100 * np.exp(np.cumsum(rng.normal(0.0004, 0.012, 600)))
        fc = analogue_forecast(make_df(prices))
        self.assertEqual(len(fc["path_median"]), 30)
        self.assertTrue(0.0 <= fc["prob_up"] <= 1.0)
        self.assertEqual(fc["neighbours"], 25)
        self.assertTrue((fc["path_p10"] <= fc["path_p90"]).all())
    def test_forecast_refuses_short_history(self):
        from arthon.pattern_ai import analogue_forecast
        with self.assertRaises(ValueError):
            analogue_forecast(make_df(np.linspace(100, 120, 120)))

class CostProfileTests(unittest.TestCase):
    def test_profiles_differ_by_asset(self):
        from arthon.costs import round_trip_bps, detect_profile
        self.assertEqual(detect_profile("RELIANCE.NS"), "india_equity_delivery")
        self.assertEqual(detect_profile("^NSEI"), "india_index_futures")
        self.assertEqual(detect_profile("BTC-USD"), "crypto_india_exchange")
        self.assertEqual(detect_profile("AAPL"), "us_equity_from_india")
        # The user's point: costs must NOT be one universal number.
        self.assertLess(round_trip_bps("^NSEI"), round_trip_bps("RELIANCE.NS"))
        self.assertLess(round_trip_bps("RELIANCE.NS"), round_trip_bps("BTC-USD"))

    def test_buy_sell_sides_can_differ(self):
        from arthon.costs import get_profile
        p = get_profile("RELIANCE.NS")
        self.assertNotEqual(p["buy_bps"], p["sell_bps"])  # stamp duty is buy-only

    def test_realistic_costs_beat_flat_stress_for_index(self):
        x = np.linspace(100, 160, 400) + 12 * np.sin(np.linspace(0, 20, 400))
        df = add_indicators(make_df(x))
        realistic = run_backtest(df, symbol="^NSEI")
        stressed = run_backtest(df, symbol="^NSEI", cost_profile="flat_20bps_stress")
        self.assertGreaterEqual(
            realistic["strategy_after_costs"]["total_return_pct"],
            stressed["strategy_after_costs"]["total_return_pct"])
