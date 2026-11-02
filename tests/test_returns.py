"""
Unit Tests for Returns & Portfolio Analysis Module
Uses small labeled synthetic test fixtures to test financial return formulas.
"""

import unittest
import numpy as np
import pandas as pd

from src.portfolio_analysis import (
    calculate_daily_returns,
    calculate_portfolio_performance,
    calculate_benchmark_performance,
    validate_weights
)


class TestPortfolioReturns(unittest.TestCase):

    def setUp(self):
        """Create a small deterministic 3-day test fixture."""
        self.mock_cleaned = pd.DataFrame({
            "Date": ["2024-01-02", "2024-01-02", "2024-01-03", "2024-01-03", "2024-01-04", "2024-01-04"],
            "Ticker": ["SPY", "QQQ", "SPY", "QQQ", "SPY", "QQQ"],
            "Open": [100.0, 200.0, 105.0, 210.0, 110.0, 220.0],
            "High": [105.0, 210.0, 110.0, 220.0, 115.0, 230.0],
            "Low": [95.0, 195.0, 100.0, 200.0, 105.0, 210.0],
            "Close": [100.0, 200.0, 110.0, 210.0, 121.0, 231.0],
            "Adj Close": [100.0, 200.0, 110.0, 210.0, 121.0, 231.0],
            "Volume": [1000, 1000, 1000, 1000, 1000, 1000]
        })
        
        self.mock_daily_returns = pd.DataFrame({
            "Date": ["2024-01-03", "2024-01-04"],
            "SPY": [0.10, 0.10],      # Day 1: +10%, Day 2: +10%
            "QQQ": [0.05, 0.10]       # Day 1: +5%,  Day 2: +10%
        })

    def test_daily_return_calculation(self):
        """Verify daily returns are calculated as (Adj Close_t / Adj Close_{t-1}) - 1."""
        daily_ret = calculate_daily_returns(self.mock_cleaned)
        self.assertEqual(len(daily_ret), 2)
        # SPY: 110/100 - 1 = 0.10
        self.assertAlmostEqual(daily_ret["SPY"].iloc[0], 0.10, places=4)
        # QQQ: 210/200 - 1 = 0.05
        self.assertAlmostEqual(daily_ret["QQQ"].iloc[0], 0.05, places=4)
        # SPY day 2: 121/110 - 1 = 0.10
        self.assertAlmostEqual(daily_ret["SPY"].iloc[1], 0.10, places=4)

    def test_validate_weights_success(self):
        """Verify valid weights summing to 1.0 pass validation."""
        weights = {"SPY": 0.60, "QQQ": 0.40}
        self.assertTrue(validate_weights(weights, ["SPY", "QQQ"]))

    def test_validate_weights_failure_on_sum(self):
        """Verify validate_weights raises ValueError when weights do not sum to 100%."""
        invalid_weights = {"SPY": 0.50, "QQQ": 0.40}  # sums to 0.90
        with self.assertRaises(ValueError):
            validate_weights(invalid_weights, ["SPY", "QQQ"])

    def test_validate_weights_failure_on_negative(self):
        """Verify validate_weights raises ValueError on negative weights."""
        invalid_weights = {"SPY": 1.20, "QQQ": -0.20}
        with self.assertRaises(ValueError):
            validate_weights(invalid_weights, ["SPY", "QQQ"])

    def test_portfolio_performance_growth(self):
        """
        Verify portfolio performance growth:
        Day 1: 0.60 * 0.10 + 0.40 * 0.05 = 0.06 + 0.02 = 0.08 (+8%)
        Day 1 Value: 100,000 * 1.08 = 108,000
        Day 2: 0.60 * 0.10 + 0.40 * 0.10 = 0.10 (+10%)
        Day 2 Value: 108,000 * 1.10 = 118,800
        Cumulative Return: (118,800 / 100,000) - 1 = +18.80%
        """
        weights = {"SPY": 0.60, "QQQ": 0.40}
        perf = calculate_portfolio_performance(self.mock_daily_returns, weights, initial_value=100000.0)
        
        self.assertAlmostEqual(perf["Daily_Return"].iloc[0], 0.08, places=4)
        self.assertAlmostEqual(perf["Portfolio_Value"].iloc[0], 108000.0, places=2)
        self.assertAlmostEqual(perf["Daily_Return"].iloc[1], 0.10, places=4)
        self.assertAlmostEqual(perf["Portfolio_Value"].iloc[1], 118800.0, places=2)
        self.assertAlmostEqual(perf["Cumulative_Return"].iloc[1], 0.1880, places=4)

    def test_benchmark_performance_calculation(self):
        """Verify benchmark performance tracking mirrors SPY column."""
        bench = calculate_benchmark_performance(self.mock_daily_returns, benchmark_ticker="SPY", initial_value=100000.0)
        self.assertEqual(len(bench), 2)
        self.assertAlmostEqual(bench["Benchmark_Value"].iloc[0], 110000.0, places=2)
        self.assertAlmostEqual(bench["Benchmark_Value"].iloc[1], 121000.0, places=2)
        self.assertAlmostEqual(bench["Cumulative_Return"].iloc[1], 0.21, places=4)


if __name__ == "__main__":
    unittest.main()
