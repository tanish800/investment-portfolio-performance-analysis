"""
Unit Tests for Data Collection & Validation Module
Uses small labeled synthetic test fixtures to test functions deterministically.
"""

import os
import unittest
import numpy as np
import pandas as pd

from src.data_cleaning import clean_market_data, validate_market_data
from src.data_collection import get_yfinance_session


class TestDataCollectionAndValidation(unittest.TestCase):

    def setUp(self):
        """Create small labeled mock test fixtures."""
        self.labeled_mock_raw = pd.DataFrame({
            "Date": ["2024-01-02", "2024-01-02", "2024-01-03", "2024-01-03", "2024-01-03"],
            "Ticker": ["SPY", "QQQ", "SPY", "QQQ", "QQQ"],  # Note duplicate on 2024-01-03 for QQQ
            "Open": [100.0, 200.0, 102.0, 204.0, 204.0],
            "High": [105.0, 205.0, 106.0, 208.0, 208.0],
            "Low": [99.0, 198.0, 101.0, 202.0, 202.0],
            "Close": [104.0, 202.0, 105.0, 206.0, 206.0],
            "Adj Close": [104.0, 202.0, 105.0, 206.0, 206.0],
            "Volume": [1000, 2000, 1100, 2100, 2100],
            "Dividends": [0.0, 0.0, 0.0, 0.0, 0.0],
            "Stock Splits": [0.0, 0.0, 0.0, 0.0, 0.0]
        })

    def test_session_creation(self):
        """Verify session creation executes without error."""
        session = get_yfinance_session()
        self.assertIsNotNone(session)

    def test_validation_detects_missing_columns(self):
        """Verify validate_market_data detects incomplete schema."""
        bad_df = pd.DataFrame({"Date": ["2024-01-02"], "Ticker": ["SPY"]})
        is_valid, msgs = validate_market_data(bad_df)
        self.assertFalse(is_valid)
        self.assertTrue(any("Missing required columns" in m for m in msgs))

    def test_validation_detects_negative_prices(self):
        """Verify validation catches negative price anomalies."""
        invalid_price_df = self.labeled_mock_raw.copy()
        invalid_price_df.loc[0, "Close"] = -50.0
        is_valid, msgs = validate_market_data(invalid_price_df)
        self.assertFalse(is_valid)
        self.assertTrue(any("non-positive prices" in m for m in msgs))

    def test_duplicate_removal_in_cleaning(self):
        """Verify that data cleaning eliminates duplicate (Date, Ticker) observations."""
        cleaned = clean_market_data(self.labeled_mock_raw, expected_tickers=["SPY", "QQQ"])
        self.assertEqual(len(cleaned), 4)  # 5 rows minus 1 duplicate = 4 rows
        # Check no duplicates remain
        dupes = cleaned.duplicated(subset=["Date", "Ticker"]).sum()
        self.assertEqual(dupes, 0)

    def test_synchronous_date_filtering(self):
        """Verify that dates where not all tickers have observations are handled."""
        asymmetric_df = pd.DataFrame({
            "Date": ["2024-01-02", "2024-01-02", "2024-01-03"],
            "Ticker": ["SPY", "QQQ", "SPY"],  # QQQ missing on 2024-01-03
            "Open": [100.0, 200.0, 102.0],
            "High": [105.0, 205.0, 106.0],
            "Low": [99.0, 198.0, 101.0],
            "Close": [104.0, 202.0, 105.0],
            "Adj Close": [104.0, 202.0, 105.0],
            "Volume": [1000, 2000, 1100],
            "Dividends": [0.0, 0.0, 0.0],
            "Stock Splits": [0.0, 0.0, 0.0]
        })
        cleaned = clean_market_data(asymmetric_df, expected_tickers=["SPY", "QQQ"])
        # Should keep only 2024-01-02 where both traded
        self.assertEqual(len(cleaned), 2)
        self.assertTrue((cleaned["Date"] == "2024-01-02").all())


if __name__ == "__main__":
    unittest.main()
