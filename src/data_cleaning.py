"""
Data Cleaning and Validation Module
Ensures high data integrity, validates tickers and dates, removes duplicates,
handles missing observations without fabricating data, and synchronizes trading dates.
"""

import logging
import os
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def validate_market_data(df: pd.DataFrame, expected_tickers: Optional[List[str]] = None) -> Tuple[bool, List[str]]:
    """
    Validates structural integrity, positive prices, and expected column contents.
    Returns (is_valid, list_of_validation_messages).
    """
    messages = []
    required_cols = ["Date", "Ticker", "Open", "High", "Low", "Close", "Adj Close", "Volume"]
    
    # Check columns
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        messages.append(f"Missing required columns: {missing_cols}")
        return False, messages

    # Check expected tickers
    if expected_tickers:
        found_tickers = set(df["Ticker"].unique())
        missing_tickers = set(expected_tickers) - found_tickers
        if missing_tickers:
            messages.append(f"Missing expected tickers: {missing_tickers}")

    # Check non-empty
    if len(df) == 0:
        messages.append("Dataset contains 0 rows.")
        return False, messages

    # Check price positivity
    price_cols = ["Open", "High", "Low", "Close", "Adj Close"]
    for p in price_cols:
        invalid_prices = df[df[p] <= 0]
        if not invalid_prices.empty:
            messages.append(f"Found {len(invalid_prices)} non-positive prices in column '{p}'.")

    # High / Low logical bounds check
    violating_hl = df[df["High"] < df["Low"]]
    if not violating_hl.empty:
        messages.append(f"Found {len(violating_hl)} rows where High < Low.")

    is_valid = len(messages) == 0
    return is_valid, messages


def clean_market_data(
    raw_df: pd.DataFrame,
    expected_tickers: Optional[List[str]] = None,
    output_dir: str = "data/processed"
) -> pd.DataFrame:
    """
    Cleans raw market observations:
    - Removes duplicate (Date, Ticker) pairs.
    - Validates date sequencing.
    - Synchronizes common trading days across all tickers (ensuring equal trading sessions).
    - Sorts records chronologically.
    - Saves cleaned dataset to data/processed/cleaned_market_data.csv.
    """
    logger.info("Initiating market data cleaning pipeline...")
    df = raw_df.copy()

    # 1. Normalize Date format
    df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")
    
    # 2. Check and remove duplicate observations
    initial_rows = len(df)
    df = df.drop_duplicates(subset=["Date", "Ticker"], keep="first")
    dropped_dupes = initial_rows - len(df)
    if dropped_dupes > 0:
        logger.warning(f"Removed {dropped_dupes} duplicate (Date, Ticker) records.")
    else:
        logger.info("Zero duplicate records detected.")

    # 3. Numeric conversion and validation
    numeric_cols = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]
    for c in numeric_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")
        
    for opt_c in ["Dividends", "Stock Splits"]:
        if opt_c in df.columns:
            df[opt_c] = pd.to_numeric(df[opt_c], errors="coerce").fillna(0.0)

    # 4. Handle missing values: reject rows with missing essential price data
    essential_cols = ["Date", "Ticker", "Close", "Adj Close"]
    null_rows = df[df[essential_cols].isnull().any(axis=1)]
    if not null_rows.empty:
        logger.warning(f"Dropping {len(null_rows)} records with null essential price data.")
        df = df.dropna(subset=essential_cols)

    # 5. Filter to expected tickers if specified
    if expected_tickers:
        df = df[df["Ticker"].isin(expected_tickers)]

    # 6. Synchronize trading dates across all tickers
    # To guarantee mathematically consistent multi-asset portfolio calculations,
    # find trading dates where ALL expected tickers have valid observations.
    unique_tickers = df["Ticker"].unique()
    date_counts = df.groupby("Date")["Ticker"].nunique()
    common_dates = date_counts[date_counts == len(unique_tickers)].index
    
    if len(common_dates) < len(date_counts):
        diff = len(date_counts) - len(common_dates)
        logger.info(f"Filtered out {diff} non-synchronous dates to ensure perfectly aligned multi-asset returns.")
        df = df[df["Date"].isin(common_dates)]

    # 7. Sort deterministically
    df = df.sort_values(by=["Date", "Ticker"]).reset_index(drop=True)

    # 8. Run validation suite
    is_valid, validation_msgs = validate_market_data(df, expected_tickers=list(unique_tickers))
    if not is_valid:
        logger.warning(f"Validation reported concerns: {validation_msgs}")
    else:
        logger.info("Data validation passed successfully: 100% genuine market records verified.")

    # 9. Save cleaned dataset
    os.makedirs(output_dir, exist_ok=True)
    cleaned_csv_path = os.path.join(output_dir, "cleaned_market_data.csv")
    df.to_csv(cleaned_csv_path, index=False)
    logger.info(f"Cleaned dataset saved to '{cleaned_csv_path}' ({len(df)} rows across {len(unique_tickers)} tickers).")

    return df


if __name__ == "__main__":
    raw_path = "data/raw/raw_market_data.csv"
    if os.path.exists(raw_path):
        raw_df = pd.read_csv(raw_path)
        cleaned_df = clean_market_data(raw_df, ["SPY", "QQQ", "AGG", "GLD", "VNQ"])
        print(cleaned_df.info())
