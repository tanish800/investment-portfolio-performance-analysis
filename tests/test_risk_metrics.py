"""
Unit Tests for Risk Analysis Module
Validates risk and financial formulas using small labeled synthetic test fixtures.
"""

import unittest
import numpy as np
import pandas as pd

from src.risk_analysis import (
    calculate_cagr,
    calculate_annualized_volatility,
    calculate_sharpe_ratio,
    calculate_max_drawdown,
    calculate_var_historical,
    calculate_beta,
    calculate_jensens_alpha,
    calculate_sortino_ratio
)


class TestRiskMetrics(unittest.TestCase):

    def test_cagr_calculation(self):
        """
        Verify CAGR:
        Start = 100, End = 121, Days = 252 * 2 (2 years)
        CAGR = (121 / 100) ^ (1 / 2) - 1 = 1.1 - 1 = 10.0%
        """
        cagr = calculate_cagr(100.0, 121.0, 504)
        self.assertAlmostEqual(cagr, 0.10, places=4)

    def test_cagr_single_year(self):
        """Start = 100, End = 115, Days = 252 -> CAGR = 15.0%"""
        cagr = calculate_cagr(100.0, 115.0, 252)
        self.assertAlmostEqual(cagr, 0.15, places=4)

    def test_annualized_volatility(self):
        """
        Verify Volatility = std * sqrt(252)
        If daily returns have std = 0.01 (1%), annualized = 1% * sqrt(252) ~= 15.8745%
        """
        daily_returns = pd.Series([0.01, -0.01, 0.01, -0.01, 0.01, -0.01])
        sample_std = daily_returns.std()
        expected_vol = sample_std * np.sqrt(252)
        calculated_vol = calculate_annualized_volatility(daily_returns)
        self.assertAlmostEqual(calculated_vol, expected_vol, places=4)

    def test_sharpe_ratio(self):
        """
        Sharpe = (CAGR - Rf) / Volatility
        CAGR = 0.12 (12%), Rf = 0.04 (4%), Vol = 0.16 (16%)
        Sharpe = (0.12 - 0.04) / 0.16 = 0.50
        """
        sharpe = calculate_sharpe_ratio(annualized_return=0.12, annualized_volatility=0.16, risk_free_rate=0.04)
        self.assertAlmostEqual(sharpe, 0.50, places=4)

    def test_max_drawdown_calculation(self):
        """
        Verify Maximum Drawdown:
        Values: 100 -> 120 (peak) -> 90 (trough: -25%) -> 110
        Max Drawdown = (90 / 120) - 1 = -0.25 (-25%)
        """
        values = pd.Series([100.0, 120.0, 90.0, 110.0])
        mdd = calculate_max_drawdown(values)
        self.assertAlmostEqual(mdd, -0.25, places=4)

    def test_var_historical(self):
        """
        Verify 95% Historical VaR corresponds to 5th percentile.
        Series of 100 values from -0.05 to +0.05
        """
        returns = pd.Series(np.linspace(-0.05, 0.05, 101))
        var_95 = calculate_var_historical(returns, confidence_level=0.95)
        expected = np.percentile(returns, 5)
        self.assertAlmostEqual(var_95, expected, places=4)
        self.assertLess(var_95, 0.0)

    def test_beta_calculation(self):
        """
        Verify Beta:
        If asset is exactly identical to benchmark, Beta = 1.0
        If asset has 2x sensitivity, Beta = 2.0
        """
        bench_ret = pd.Series([0.01, -0.02, 0.03, -0.01, 0.02])
        asset_ret_2x = bench_ret * 2.0
        
        beta_1x = calculate_beta(bench_ret, bench_ret)
        self.assertAlmostEqual(beta_1x, 1.0, places=4)
        
        beta_2x = calculate_beta(asset_ret_2x, bench_ret)
        self.assertAlmostEqual(beta_2x, 2.0, places=4)

    def test_jensens_alpha(self):
        """
        Jensen's Alpha = CAGR_p - [Rf + Beta * (CAGR_b - Rf)]
        CAGR_p = 0.15, CAGR_b = 0.10, Rf = 0.03, Beta = 1.0
        Expected Return = 0.03 + 1.0 * (0.10 - 0.03) = 0.10
        Alpha = 0.15 - 0.10 = +0.05 (+5%)
        """
        alpha = calculate_jensens_alpha(portfolio_cagr=0.15, benchmark_cagr=0.10, beta=1.0, risk_free_rate=0.03)
        self.assertAlmostEqual(alpha, 0.05, places=4)


if __name__ == "__main__":
    unittest.main()
